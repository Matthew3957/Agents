"""
Multi-Agent System for Ollama Assistant
"""

from .agent_manager import AgentManager
from .tools import ToolRegistry

__all__ = ['AgentManager', 'ToolRegistry']
