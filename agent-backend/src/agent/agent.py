"""
Main PlaywrightAgent class with LangGraph orchestration
"""
import time
from typing import Optional, Dict
from pydantic import SecretStr
from langchain_groq import ChatGroq

from ..config import Config
from ._state_agent import AgentState

from .nodes import AgentNodes
from .graph import GraphBuilder
from ..utils._load_prompt import load_prompt
from ..utils.logger import agent_logger
from langchain_core.messages import HumanMessage


class PlaywrightAgent:
    """
    LangGraph-based agent for generating Playwright Page Object Models
    """
    
    def __init__(
        self,
        planner_prompt: str = Config.PLANNER_PROMPT,
        codegen_prompt: str = Config.CODEGEN_PROMPT,
    ):
        agent_logger.info("="*8)
        agent_logger.info("🚀 Initializing PlaywrightAgent with LangGraph")
        
        # Initialize LLM
        agent_logger.info(f"Loading LLM: {Config.MODEL_NAME}")
        self.llm = ChatGroq(
            model=Config.MODEL_NAME,
            api_key=SecretStr(Config.GROQ_API_KEY or ""),
            temperature=Config.TEMPERATURE,
            max_tokens=Config.MAX_TOKENS,
        )
        
        # Load prompts
        agent_logger.info(f"Loading prompts: {planner_prompt}, {codegen_prompt}")
        self.planner_prompt = load_prompt("playwright", planner_prompt)
        self.codegen_prompt = load_prompt("playwright", codegen_prompt)
        
        # Create nodes
        agent_logger.info("Creating agent nodes...")
        self.nodes = AgentNodes(
            llm=self.llm,
            planner_prompt=self.planner_prompt,
            codegen_prompt=self.codegen_prompt
        )
        
        # Build graph
        builder = GraphBuilder(self.nodes)
        self.graph = builder.build()
        
        agent_logger.info("="*8)
        agent_logger.info("✅ PlaywrightAgent initialization complete")
    
    def process_request(
        self,
        user_prompt: str,
        project_id: str = "default",
        existing_files: Optional[Dict[str, str]] = None,
        user_edits: Optional[Dict[str, dict]] = None
    ) -> dict:
        """
        Process user request through the agent graph
        
        Args:
            user_prompt: User's natural language request
            project_id: Project identifier for file organization
            existing_files: Dict of existing files {path: content} for context
            user_edits: Dict of user edit metadata {path: metadata}
            
        Returns:
            dict with success, response, generated_code, and metadata
        """
        start_time = time.time()
        
        agent_logger.workflow_start(user_prompt)
        
        try:
            # Initialize state
            initial_state: AgentState = {
                "messages": [HumanMessage(content=user_prompt)],
                "task_type": "unknown",
                "elements": [],
                "generated_code": "",
                "class_name": "",
                "project_id": project_id,
                "existing_files": existing_files or {},
                "user_edits": user_edits or {},
                "file_saved_path": None,
                "execution_logs": []
            }
            
            agent_logger.info(f"Initial state: project={project_id}, existing_files={len(existing_files or {})}")
            
            # Run the graph
            agent_logger.info("Starting graph execution...")
            final_state = self.graph.invoke(initial_state)
            
            # Extract final response
            final_content = final_state["messages"][-1].content
            if isinstance(final_content, list):
                final_content = str(final_content[0]) if final_content else "No response"
            
            duration = time.time() - start_time
            agent_logger.workflow_end(success=True, duration=duration)
            
            return {
                "success": True,
                "task_type": final_state["task_type"],
                "generated_code": final_state.get("generated_code", ""),
                "class_name": final_state.get("class_name", ""),
                "file_saved_path": final_state.get("file_saved_path"),
                "response": final_content,
                "duration": duration,
                "graph_steps": len(final_state["messages"]) - 1
            }
        
        except Exception as e:
            duration = time.time() - start_time
            agent_logger.workflow_end(success=False, duration=duration)
            agent_logger.error("process_request", e)
            
            return {
                "success": False,
                "error": str(e),
                "response": f"Error occurred: {e}",
                "duration": duration
            }
    
    def reset(self):
        """
        Reset agent (graph is stateless, so this is a no-op)
        """
        agent_logger.info("🔄 Agent reset requested (graph is stateless)")