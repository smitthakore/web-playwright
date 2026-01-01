"""
Agent state definition with comprehensive context tracking
"""

from typing import TypedDict, Annotated, Literal, Optional, Dict, List
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """
    Complete state that flows through the agent graph
    """
    # Conversation
    messages: Annotated[list, add_messages]
    
    # Task tracking
    task_type: Literal["generate_pom", "update_pom", "clarification_needed", "unknown"]
    elements: List[str]
    
    # Code generation
    generated_code: str
    class_name: str
    
    # File context (for context-aware regeneration)
    project_id: str
    existing_files: Dict[str, str]  # {path: content}
    user_edits: Dict[str, dict]     # {path: metadata}
    
    # Execution metadata
    file_saved_path: Optional[str]
    execution_logs: List[str]