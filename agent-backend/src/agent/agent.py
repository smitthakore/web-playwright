"""
Main PlaywrightAgent class with LangGraph orchestration - FIXED VERSION
"""
import time
from typing import Optional, Dict
from pydantic import SecretStr
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from ..config import Config
from ._state_agent import AgentState
from .nodes import AgentNodes
from .graph import GraphBuilder
from ..utils._load_prompt import load_prompt
from ..utils.logger import agent_logger
from ..utils.mcp_client_manager import MCPClientManager
from ..tools.filesystem_mcp import FilesystemMCP
from ..tools.playwright_mcp import PlaywrightMCP

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
        agent_logger.info("🚀 Initializing PlaywrightAgent (Lazy Loading)")
        
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
        
        # Initialize MCP client manager (but don't connect yet)
        self.mcp_manager = MCPClientManager()
        
        # State for lazy loading
        self.graph = None
        self.langchain_tools = []
        self.filesystem_tool = None
        self.playwright_tool = None
        
        agent_logger.info("✅ Agent created (waiting for first request to connect)")
        
    async def _initialize(self):
        """Async initialization of tools and graph"""
        if self.graph:
            return

        agent_logger.info("⚡ performing async initialization...")
        
        # Initialize tools with manager
        self.filesystem_tool = FilesystemMCP(self.mcp_manager)
        self.playwright_tool = PlaywrightMCP(self.mcp_manager)
        
        # Ensure connections
        await self.filesystem_tool.ensure_connected()
        await self.playwright_tool.ensure_connected()
        
        # Load LangChain tools
        self.langchain_tools = await self.mcp_manager.get_langchain_tools()
        
        # Enable error handling - FIXED: Use string return instead of raising
        for tool in self.langchain_tools:
            tool.handle_tool_error = lambda e: f"Tool execution failed: {str(e)}. Please try a different approach or ask for help."
            
        agent_logger.info(f"Loaded {len(self.langchain_tools)} LangChain MCP tools")
        
        # Create nodes
        agent_logger.info("Creating agent nodes...")
        self.nodes = AgentNodes(
            llm=self.llm,
            planner_prompt=self.planner_prompt,
            codegen_prompt=self.codegen_prompt,
            filesystem_tool=self.filesystem_tool,
            playwright_tool=self.playwright_tool,
            langchain_tools=self.langchain_tools
        )
        
        # Build graph
        builder = GraphBuilder(self.nodes)
        self.graph = builder.build()
        agent_logger.info("✅ Graph built successfully")
    
    async def process_request_async(
        self,
        user_prompt: str,
        project_id: str = "default",
        existing_files: Optional[Dict[str, str]] = None,
        user_edits: Optional[Dict[str, dict]] = None
    ) -> dict:
        """
        Process user request through the agent graph asynchronously
        """
        # Ensure agent is initialized (lazy loading)
        await self._initialize()
        
        start_time = time.time()
        
        agent_logger.workflow_start(user_prompt)
        
        try:
            # Initialize state with NEW FIELDS
            initial_state: AgentState = {
                "messages": [HumanMessage(content=user_prompt)],
                "task_type": "unknown",
                "target_url": None,
                "elements": [],
                "extracted_locators": {},  # NEW: Store real locators
                "navigation_complete": False,  # NEW: Track navigation
                "page_object_code": "",  # RENAMED from generated_code
                "test_code": "",  # NEW: Separate test file
                "class_name": "",
                "project_id": project_id,
                "existing_files": existing_files or {},
                "user_edits": user_edits or {},
                "saved_files": [],  # NEW: Track saved file paths
                "execution_logs": [],
                "iteration_count": 0,  # NEW: Prevent infinite loops
                "max_iterations": 10,  # NEW: Max allowed iterations
            }
            
            agent_logger.info(f"Initial state: project={project_id}, max_iter=10")
            
            # Run the graph
            agent_logger.info("Starting graph execution...")
            final_state = await self.graph.ainvoke(initial_state)
            
            # Extract final response
            final_content = final_state["messages"][-1].content
            if isinstance(final_content, list):
                final_content = str(final_content[0]) if final_content else "No response"
            
            duration = time.time() - start_time
            agent_logger.workflow_end(success=True, duration=duration)
            
            return {
                "success": True,
                "task_type": final_state["task_type"],
                "page_object_code": final_state.get("page_object_code", ""),
                "test_code": final_state.get("test_code", ""),
                "class_name": final_state.get("class_name", ""),
                "saved_files": final_state.get("saved_files", []),
                "extracted_locators": final_state.get("extracted_locators", {}),
                "response": final_content,
                "duration": duration,
                "iterations": final_state.get("iteration_count", 0),
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

    def process_request(
        self,
        user_prompt: str,
        project_id: str = "default",
        existing_files: Optional[Dict[str, str]] = None,
        user_edits: Optional[Dict[str, dict]] = None
    ) -> dict:
        """
        Sync wrapper for process_request_async
        """
        import asyncio
        import nest_asyncio
        nest_asyncio.apply()
        
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        return loop.run_until_complete(
            self.process_request_async(user_prompt, project_id, existing_files, user_edits)
        )
    
    def reset(self):
        """
        Reset agent (graph is stateless, so this is a no-op)
        """
        agent_logger.info("🔄 Agent reset requested (graph is stateless)")