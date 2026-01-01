"""
LangGraph workflow builder
"""

from typing import Literal
from langgraph.graph import StateGraph, START, END

from ._state_agent import AgentState
from .nodes import AgentNodes
from ..utils.logger import agent_logger


class GraphBuilder:
    """
    Builds and compiles the LangGraph workflow
    """
    
    def __init__(self, nodes: AgentNodes):
        self.nodes = nodes
    
    def build(self):
        """
        Build the agent graph with nodes and edges
        
        Returns:
            Compiled StateGraph
        """
        agent_logger.info("Building LangGraph workflow...")
        
        graph = StateGraph(AgentState)
        
        # Add nodes
        graph.add_node("planner", self.nodes.planner_node)
        graph.add_node("code_generator", self.nodes.code_generator_node)
        graph.add_node("finalizer", self.nodes.finalizer_node)
        
        agent_logger.debug("Added 3 nodes: planner, code_generator, finalizer")
        
        # Define edges
        graph.add_edge(START, "planner")
        
        graph.add_conditional_edges(
            "planner",
            self._route_from_planner,
            {
                "generate": "code_generator",
                "clarify": "finalizer",
            },
        )
        
        graph.add_edge("code_generator", "finalizer")
        graph.add_edge("finalizer", END)
        
        agent_logger.debug("Added edges with conditional routing from planner")
        
        compiled_graph = graph.compile()
        
        agent_logger.info("✅ LangGraph workflow compiled successfully")
        
        return compiled_graph
    
    def _route_from_planner(self, state: AgentState) -> Literal["generate", "clarify"]:
        """
        Routing logic from planner node
        
        Args:
            state: Current agent state
            
        Returns:
            Next node to execute
        """
        task_type = state.get("task_type", "unknown")
        
        if task_type in ["generate_pom", "update_pom"]:
            agent_logger.debug(f"Routing to code_generator (task: {task_type})")
            return "generate"
        else:
            agent_logger.debug(f"Routing to finalizer for clarification (task: {task_type})")
            return "clarify"