"""
Agent graph nodes with comprehensive logging
"""

import json
from typing import TYPE_CHECKING
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from ._state_agent import AgentState
from ..utils.logger import agent_logger
from ..utils._code_extractor import extract_python_code

if TYPE_CHECKING:
    from langchain_groq import ChatGroq


class AgentNodes:
    """
    Collection of graph nodes for the Playwright agent
    """
    
    def __init__(self, llm: "ChatGroq", planner_prompt: str, codegen_prompt: str):
        self.llm = llm
        self.planner_prompt = planner_prompt
        self.codegen_prompt = codegen_prompt
    
    def planner_node(self, state: AgentState) -> AgentState:
        """
        Planning node - analyzes user request and decides task type
        """
        agent_logger.node_start("PLANNER", f"Messages: {len(state['messages'])}")
        
        user_message = state["messages"][-1].content
        agent_logger.info(f"Analyzing user request: {user_message[:100]}...")
        
        # Build planning messages
        messages = [
            SystemMessage(content=self.planner_prompt),
            HumanMessage(content=f"User Request:\n{user_message}"),
        ]
        
        # LLM call with logging
        agent_logger.llm_call_start(
            model=self.llm.model_name,
            prompt_preview=user_message[:100]
        )
        
        try:
            response = self.llm.invoke(messages)
            
            # Extract content
            content = response.content
            if isinstance(content, list):
                content = str(content[0]) if content else "{}"
            
            agent_logger.llm_call_end(
                tokens=getattr(response, 'response_metadata', {}).get('token_usage', {}).get('total_tokens', 0),
                response_preview=content[:100]
            )
            
            # Parse JSON plan
            try:
                # Clean JSON from markdown blocks
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                plan = json.loads(content)
                
                state["task_type"] = plan.get("task_type", "unknown")
                state["elements"] = plan.get("elements_to_find", [])
                
                agent_logger.info(f"Plan determined: task_type={state['task_type']}, elements={len(state['elements'])}")
                
                state["messages"].append(
                    AIMessage(content=f"Planning complete: {plan.get('reasoning', '')}")
                )
                
            except (json.JSONDecodeError, TypeError, AttributeError) as e:
                agent_logger.error("JSON parsing in planner", e)
                agent_logger.info("Falling back to clarification mode")
                
                state["task_type"] = "clarification_needed"
                state["elements"] = []
                state["messages"].append(AIMessage(content=content))
        
        except Exception as e:
            agent_logger.error("planner_node", e)
            state["task_type"] = "unknown"
            state["elements"] = []
        
        agent_logger.node_end("PLANNER", f"Task: {state['task_type']}")
        return state
    
    def code_generator_node(self, state: AgentState) -> AgentState:
        """
        Code generation node - creates Playwright POM code
        """
        agent_logger.node_start("CODE_GENERATOR", f"Elements: {len(state.get('elements', []))}")
        
        user_request = state["messages"][0].content
        elements = ", ".join(state.get("elements", []))
        
        agent_logger.info(f"Generating code for elements: {elements}")
        
        # Check for existing files (context-aware generation)
        existing_context = ""
        if state.get("existing_files"):
            agent_logger.info(f"Found {len(state['existing_files'])} existing files for context")
            existing_context = "\n\nExisting files in project:\n"
            for path, content in state["existing_files"].items():
                existing_context += f"- {path} ({len(content)} chars)\n"
        
        # Build code generation messages
        messages = [
            SystemMessage(content=self.codegen_prompt),
            HumanMessage(content=f"""
User Request:
{user_request}

Identified UI Elements:
{elements}

{existing_context}
"""),
        ]
        
        # LLM call with logging
        agent_logger.llm_call_start(
            model=self.llm.model_name,
            prompt_preview=f"Generate POM for: {elements[:50]}"
        )
        
        try:
            response = self.llm.invoke(messages)
            
            # Extract content
            content = response.content
            if isinstance(content, list):
                content = str(content[0]) if content else ""
            
            agent_logger.llm_call_end(
                tokens=getattr(response, 'response_metadata', {}).get('token_usage', {}).get('total_tokens', 0),
                response_preview=content[:100]
            )
            
            # Extract Python code
            state["generated_code"] = extract_python_code(content)
            
            # Extract class name for file naming
            state["class_name"] = self._extract_class_name(state["generated_code"])
            
            agent_logger.info(f"Generated {len(state['generated_code'])} chars of code")
            agent_logger.info(f"Class name: {state['class_name']}")
            
            state["messages"].append(
                AIMessage(content="Playwright POM code generated successfully")
            )
        
        except Exception as e:
            agent_logger.error("code_generator_node", e)
            state["generated_code"] = ""
            state["class_name"] = "UnknownPage"
        
        agent_logger.node_end("CODE_GENERATOR", f"Code: {len(state['generated_code'])} chars")
        return state
        
    def _extract_class_name(self, code: str) -> str:
        """
        Extract class name from generated Python code
        
        Args:
            code: Python code string
            
        Returns:
            Class name or 'UnknownPage'
        """
        import re
        
        match = re.search(r'class\s+(\w+)', code)
        if match:
            class_name = match.group(1)
            agent_logger.debug(f"Extracted class name: {class_name}")
            return class_name
        else:
            agent_logger.debug("Could not extract class name from code")
            return "UnknownPage"
        

    def finalizer_node(self, state: AgentState) -> AgentState:
        """
        Finalizer node - prepares final response and saves file via MCP
        """
        agent_logger.node_start("FINALIZER", f"Task: {state['task_type']}")
        
        if state["task_type"] == "generate_pom" and state.get("generated_code"):
            # Save file via MCP
            project_id = state.get("project_id", "default")
            class_name = state.get("class_name", "UnknownPage")
            
            # Convert class name to snake_case for filename
            filename = self._class_to_filename(class_name)
            file_path = f"{project_id}/pages/{filename}.py"
            
            agent_logger.info(f"Saving POM to: {file_path}")
            
            # Save via MCP (synchronous for now, will make async later)
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Import MCP here to avoid circular import
            from ..tools.filesystem_mcp import FilesystemMCP
            mcp = FilesystemMCP()
            
            success = loop.run_until_complete(
                mcp.write_file(file_path, state["generated_code"])
            )
            
            if success:
                state["file_saved_path"] = file_path
                agent_logger.info(f"✅ File saved successfully to {file_path}")
            else:
                agent_logger.error("finalizer_node", Exception("Failed to save file via MCP"))
            
            # Include file save information
            save_info = f"\n\n✅ File saved to: `{file_path}`" if success else "\n\n⚠️ Failed to save file"
            
            final_message = f"""Here is your Playwright Page Object Model:
`````python
{state['generated_code']}
````{save_info}"""
            
            agent_logger.info(f"Prepared final response with {len(state['generated_code'])} chars of code")
        
        elif state["task_type"] == "update_pom":
            final_message = f"""I've updated your Playwright Page Object Model:
```python
{state['generated_code']}
```

Changes were made while preserving your manual edits."""
            
            agent_logger.info("Prepared update response")
        
        else:
            # Clarification or unknown
            last_content = state["messages"][-1].content
            if isinstance(last_content, list):
                final_message = str(last_content[0]) if last_content else "No response"
            else:
                final_message = last_content
            
            agent_logger.info("Prepared clarification response")
        
        state["messages"].append(AIMessage(content=final_message))
        
        agent_logger.node_end("FINALIZER", "Response prepared")
        return state
    
    def _class_to_filename(self, class_name: str) -> str:
        """
        Convert class name to snake_case filename
        Example: LoginPage -> login_page
        """
        import re
        # Insert underscore before capitals
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', class_name)
        # Insert underscore before capitals followed by lowercase
        filename = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
        return filename