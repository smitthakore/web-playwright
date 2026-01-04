"""
Agent state definition with locator tracking
"""

from typing import TypedDict, Optional, List, Dict
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """
    State schema for the Playwright agent graph
    """
    
    # Core conversation
    messages: List[BaseMessage]
    
    # Task information
    task_type: str  # generate_pom | execute_tool | clarification_needed | error
    target_url: Optional[str]
    elements: List[str]  # UI elements to include (e.g., "login button")
    
    # Extracted data from tools
    extracted_locators: Dict[str, str]  # Real locators from playwright_extract_locators
    navigation_complete: bool
    
    # Generated code
    page_object_code: str  # Page object class code
    test_code: str  # Test file code
    class_name: str
    
    # File management
    project_id: str
    existing_files: Dict[str, str]
    user_edits: Dict[str, dict]
    saved_files: List[str]  # Paths of successfully saved files
    
    # Execution tracking
    execution_logs: List[str]
    iteration_count: int  # Current iteration number
    max_iterations: int  # Maximum allowed iterations (prevent infinite loops)