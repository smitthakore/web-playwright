"""
Centralized logging utility for agent operations
"""

import logging
import sys
from datetime import datetime
from typing import Any, Dict


class AgentLogger:
    """
    Custom logger for LangGraph agent with structured logging
    """
    
    def __init__(self, name: str = "PlaywrightAgent"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Console handler with formatting
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(logging.INFO)
            
            formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(message)s',
                datefmt='%H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def node_start(self, node_name: str, state_info: str = ""):
        """Log when a node starts executing"""
        self.logger.info(f"🔵 NODE START: {node_name} {state_info}")
    
    def node_end(self, node_name: str, result_summary: str = ""):
        """Log when a node completes"""
        self.logger.info(f"✅ NODE END: {node_name} {result_summary}")
    
    def llm_call_start(self, model: str, prompt_preview: str = ""):
        """Log before calling LLM"""
        preview = prompt_preview[:100] + "..." if len(prompt_preview) > 100 else prompt_preview
        self.logger.info(f"🤖 LLM CALL: {model} | Prompt: {preview}")
    
    def llm_call_end(self, tokens: int = 0, response_preview: str = ""):
        """Log after LLM responds"""
        preview = response_preview[:100] + "..." if len(response_preview) > 100 else response_preview
        self.logger.info(f"✨ LLM RESPONSE: {tokens} tokens | {preview}")
    
    def tool_call(self, tool_name: str, params: Dict[str, Any]):
        """Log tool/MCP calls"""
        self.logger.info(f"🔧 TOOL CALL: {tool_name} | Params: {params}")
    
    def tool_result(self, tool_name: str, success: bool, result_preview: str = ""):
        """Log tool results"""
        status = "✅ SUCCESS" if success else "❌ FAILED"
        self.logger.info(f"{status} TOOL RESULT: {tool_name} | {result_preview}")
    
    def error(self, context: str, error: Exception):
        """Log errors"""
        self.logger.error(f"❌ ERROR in {context}: {str(error)}", exc_info=True)
    
    def info(self, message: str):
        """General info logging"""
        self.logger.info(f"ℹ️  {message}")
    
    def debug(self, message: str):
        """Debug logging"""
        self.logger.debug(f"🐛 {message}")
    
    def workflow_start(self, user_prompt: str):
        """Log workflow start"""
        self.logger.info("="*80)
        self.logger.info(f"🚀 WORKFLOW START")
        self.logger.info(f"📝 User Prompt: {user_prompt[:150]}...")
        self.logger.info("="*80)
    
    def workflow_end(self, success: bool, duration: float = 0):
        """Log workflow completion"""
        status = "✅ SUCCESS" if success else "❌ FAILED"
        self.logger.info("="*80)
        self.logger.info(f"{status} WORKFLOW END | Duration: {duration:.2f}s")
        self.logger.info("="*80)


# Singleton instance
agent_logger = AgentLogger()