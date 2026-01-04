"""
Agent graph nodes with comprehensive logging and locator tracking
"""

import json
import re
from typing import TYPE_CHECKING
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage

from ._state_agent import AgentState
from ..utils.logger import agent_logger
from ..utils._code_extractor import extract_python_code

if TYPE_CHECKING:
    from langchain_groq import ChatGroq


class AgentNodes:
    """
    Collection of graph nodes for the Playwright agent
    """
    
    def __init__(self, llm: "ChatGroq", planner_prompt: str, codegen_prompt: str, 
                 filesystem_tool=None, playwright_tool=None, langchain_tools=None):
        self.llm = llm
        self.planner_prompt = planner_prompt
        self.codegen_prompt = codegen_prompt
        self.filesystem_tool = filesystem_tool
        self.playwright_tool = playwright_tool
        self.langchain_tools = langchain_tools or []
        
        # Log available tools
        agent_logger.info("=== AVAILABLE TOOLS ===")
        for tool in self.langchain_tools:
            agent_logger.info(f"  - {tool.name}: {tool.description[:80]}")
        
        # Custom error handler for tools
        for tool in self.langchain_tools:
            tool.handle_tool_error = True

    def planner_node(self, state: AgentState) -> AgentState:
        """
        Planning node - analyzes user request and coordinates tool usage
        """
        agent_logger.node_start("PLANNER", f"Messages: {len(state['messages'])}, Iteration: {state.get('iteration_count', 0)}")
        
        # Check iteration limit
        iteration = state.get('iteration_count', 0)
        max_iterations = state.get('max_iterations', 10)
        
        if iteration >= max_iterations:
            agent_logger.error("planner_node", Exception(f"Max iterations ({max_iterations}) reached"))
            state['task_type'] = "error"
            state['messages'].append(AIMessage(
                content=f"Maximum iteration limit reached ({max_iterations}). Please simplify your request or break it into smaller tasks."
            ))
            return state
        
        state['iteration_count'] = iteration + 1
        
        # Get last message
        last_message = state["messages"][-1]
        
        # Check if we're resuming after tool execution
        if last_message.type == "tool":
            agent_logger.info(f"Resuming after tool execution: {last_message.name}")
            
            # Try to extract locators from tool result
            if "extract" in last_message.name.lower() or "locator" in last_message.name.lower():
                try:
                    content = last_message.content
                    # Try to parse as JSON
                    if isinstance(content, str) and (content.strip().startswith('{') or content.strip().startswith('[')):
                        locators = json.loads(content)
                        if not state.get('extracted_locators'):
                            state['extracted_locators'] = {}
                        
                        # Merge locators
                        if isinstance(locators, dict):
                            state['extracted_locators'].update(locators)
                        elif isinstance(locators, list):
                            # Convert list to dict
                            for i, loc in enumerate(locators):
                                state['extracted_locators'][f'element_{i}'] = loc
                        
                        agent_logger.info(f"Extracted and stored {len(state['extracted_locators'])} locators")
                except Exception as e:
                    agent_logger.debug(f"Could not parse locators from tool result: {e}")
        
        # Build planning messages with state context
        context_info = f"""
Current State:
- Target URL: {state.get('target_url', 'Not set')}
- Extracted Locators: {len(state.get('extracted_locators', {}))} found
- Navigation Complete: {state.get('navigation_complete', False)}
- Iteration: {iteration + 1}/{max_iterations}

Extracted Locators Summary:
{json.dumps(state.get('extracted_locators', {}), indent=2) if state.get('extracted_locators') else 'None yet'}
"""
        
        messages = [
            SystemMessage(content=self.planner_prompt),
            HumanMessage(content=context_info)
        ] + state["messages"]
        
        # LLM call with logging
        agent_logger.llm_call_start(
            model=self.llm.model_name,
            prompt_preview=str(last_message.content)[:100]
        )
        
        try:
            # Bind tools to LLM
            llm_with_tools = self.llm.bind_tools(self.langchain_tools)
            response = llm_with_tools.invoke(messages)
            
            # Update state with response
            state["messages"].append(response)
            
            agent_logger.llm_call_end(
                tokens=getattr(response, 'response_metadata', {}).get('token_usage', {}).get('total_tokens', 0),
                response_preview=str(response.content)[:100]
            )
            
            # Check for tool calls first
            if response.tool_calls:
                state["task_type"] = "execute_tool"
                agent_logger.info(f"Tool calls detected: {len(response.tool_calls)}")
                
                # Log tool details
                for tc in response.tool_calls:
                    agent_logger.info(f"  → Tool: {tc['name']}")
                    agent_logger.info(f"     Args: {tc['args']}")
                
                # Track navigation state
                for tc in response.tool_calls:
                    if 'navigate' in tc['name'].lower():
                        state['navigation_complete'] = True
                        if 'url' in tc['args']:
                            state['target_url'] = tc['args']['url']
                
                agent_logger.node_end("PLANNER", "Task: execute_tool")
                return state

            # If no tool calls, try to parse JSON plan (for code generation)
            content = str(response.content)
            
            try:
                # Clean JSON from markdown blocks
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                plan = json.loads(content)
                
                state["task_type"] = plan.get("task_type", "unknown")
                state["elements"] = plan.get("elements_to_find", [])
                
                # Store extracted locators if provided in plan
                if plan.get("extracted_locators"):
                    if not state.get('extracted_locators'):
                        state['extracted_locators'] = {}
                    state['extracted_locators'].update(plan['extracted_locators'])
                
                if plan.get("target_url"):
                    state["target_url"] = plan["target_url"]
                
                agent_logger.info(f"Plan: task={state['task_type']}, elements={len(state['elements'])}, locators={len(state.get('extracted_locators', {}))}")
                
            except (json.JSONDecodeError, TypeError, AttributeError) as e:
                # Plain text response - likely clarification
                state["task_type"] = "clarification_needed"
                state["elements"] = []
                agent_logger.info("Plain text response received (clarification)")
                
        except Exception as e:
            agent_logger.error("planner_node", e)
            state["task_type"] = "error"
            state["elements"] = []
        
        agent_logger.node_end("PLANNER", f"Task: {state['task_type']}")
        return state
    
    def code_generator_node(self, state: AgentState) -> AgentState:
        """
        Code generation node - creates 2-file POM (page object + test)
        """
        agent_logger.node_start("CODE_GENERATOR", f"Elements: {len(state.get('elements', []))}, Locators: {len(state.get('extracted_locators', {}))}")
        
        user_request = state["messages"][0].content
        elements = state.get("elements", [])
        extracted_locators = state.get("extracted_locators", {})
        target_url = state.get("target_url", "https://example.com")
        
        agent_logger.info(f"Generating POM with {len(extracted_locators)} real locators")
        
        # Build enhanced prompt with actual locators
        locators_info = "No locators extracted yet - using placeholders" if not extracted_locators else f"Real locators extracted from page:\n{json.dumps(extracted_locators, indent=2)}"
        
        messages = [
            SystemMessage(content=self.codegen_prompt),
            HumanMessage(content=f"""
User Request: {user_request}

Target URL: {target_url}

UI Elements to include: {', '.join(elements) if elements else 'All extracted elements'}

{locators_info}

Generate 2 files:
1. Page Object (pages/<name>_page.py) - Contains locators and page methods
2. Test File (tests/test_<name>.py) - Contains test scenarios using the page object

CRITICAL: Use the REAL EXTRACTED LOCATORS provided above. Do not invent selectors.
"""),
        ]
        
        # LLM call
        agent_logger.llm_call_start(
            model=self.llm.model_name,
            prompt_preview=f"Generate 2-file POM with {len(extracted_locators)} locators"
        )
        
        try:
            response = self.llm.invoke(messages)
            content = response.content
            if isinstance(content, list):
                content = str(content[0]) if content else ""
            
            agent_logger.llm_call_end(
                tokens=getattr(response, 'response_metadata', {}).get('token_usage', {}).get('total_tokens', 0),
                response_preview=content[:100]
            )
            
            # Extract both code files
            generated_files = self._extract_multiple_code_blocks(content)
            
            if len(generated_files) >= 2:
                state["page_object_code"] = generated_files[0]['code']
                state["test_code"] = generated_files[1]['code']
                state["class_name"] = self._extract_class_name(generated_files[0]['code'])
                
                agent_logger.info(f"Generated 2 files: page={len(state['page_object_code'])} chars, test={len(state['test_code'])} chars")
            else:
                # Fallback - single file
                state["page_object_code"] = extract_python_code(content)
                state["test_code"] = ""
                state["class_name"] = self._extract_class_name(state["page_object_code"])
                agent_logger.warning("Only 1 code block found, expected 2 files")
            
            state["messages"].append(AIMessage(content="POM code generated with real locators"))
        
        except Exception as e:
            agent_logger.error("code_generator_node", e)
            state["page_object_code"] = ""
            state["test_code"] = ""
            state["class_name"] = "UnknownPage"
        
        agent_logger.node_end("CODE_GENERATOR", f"Files: page={len(state.get('page_object_code', ''))} chars, test={len(state.get('test_code', ''))} chars")
        return state

    def _extract_multiple_code_blocks(self, content: str) -> list[dict]:
        """Extract multiple Python code blocks from markdown"""
        blocks = []
        pattern = r'```python\n(.*?)```'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for match in matches:
            blocks.append({
                'code': match.strip(),
                'language': 'python'
            })
        
        # Fallback - try without language specifier
        if not blocks:
            pattern = r'```\n(.*?)```'
            matches = re.findall(pattern, content, re.DOTALL)
            for match in matches:
                if 'import' in match or 'class' in match or 'def' in match:
                    blocks.append({
                        'code': match.strip(),
                        'language': 'python'
                    })
        
        return blocks

    def _extract_class_name(self, code: str) -> str:
        """Extract class name from generated Python code"""
        match = re.search(r'class\s+(\w+)', code)
        return match.group(1) if match else "UnknownPage"

    def finalizer_node(self, state: AgentState) -> AgentState:
        """
        Finalizer node - saves files and prepares final response
        """
        agent_logger.node_start("FINALIZER", f"Task: {state['task_type']}")
        
        if state["task_type"] == "generate_pom":
            # Save both files via MCP
            project_id = state.get("project_id", "default")
            class_name = state.get("class_name", "UnknownPage")
            filename = self._class_to_filename(class_name)
            
            page_path = f"workspace/{project_id}/pages/{filename}_page.py"
            test_path = f"workspace/{project_id}/tests/test_{filename}.py"
            
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            saved_files = []
            
            # Save page object
            if state.get("page_object_code") and self.filesystem_tool:
                success = loop.run_until_complete(
                    self.filesystem_tool.write_file(page_path, state["page_object_code"])
                )
                if success:
                    saved_files.append(page_path)
                    agent_logger.info(f"✅ Saved page object: {page_path}")
            
            # Save test file
            if state.get("test_code") and self.filesystem_tool:
                success = loop.run_until_complete(
                    self.filesystem_tool.write_file(test_path, state["test_code"])
                )
                if success:
                    saved_files.append(test_path)
                    agent_logger.info(f"✅ Saved test file: {test_path}")
            
            state["saved_files"] = saved_files
            
            # Build response
            files_info = "\n".join([f"✅ {path}" for path in saved_files]) if saved_files else "⚠️ Failed to save files"
            
            final_message = f"""Playwright Page Object Model Generated!

Files Created:
{files_info}

Real Locators Used: {len(state.get('extracted_locators', {}))}

Page Object Code:
```python
{state.get('page_object_code', 'No code generated')[:500]}...
```

Test Code:
```python
{state.get('test_code', 'No test generated')[:500]}...
```"""
            
        elif state["task_type"] == "clarification_needed":
            last_content = state["messages"][-1].content
            final_message = last_content if isinstance(last_content, str) else str(last_content)
        
        elif state["task_type"] == "error":
            final_message = "An error occurred. Please try again with a simpler request."
        
        else:
            # Default response
            last_content = state["messages"][-1].content
            final_message = last_content if isinstance(last_content, str) else "Task completed."
        
        state["messages"].append(AIMessage(content=final_message))
        agent_logger.node_end("FINALIZER", "Response prepared")
        return state
    
    def _class_to_filename(self, class_name: str) -> str:
        """Convert class name to snake_case"""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', class_name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()