"""
Base agent implementation that works without strands_agents.
This provides a simplified agent framework for testing.
"""
from typing import Dict, List, Callable, Any
import asyncio
from functools import wraps


class BaseAgent:
    """Base agent class that can run independently."""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.tools = {}
        self.running = False
    
    def register_tool(self, func: Callable):
        """Register a tool function."""
        self.tools[func.__name__] = func
    
    async def execute_tool(self, tool_name: str, **kwargs):
        """Execute a tool by name."""
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        func = self.tools[tool_name]
        if asyncio.iscoroutinefunction(func):
            return await func(**kwargs)
        else:
            return func(**kwargs)
    
    def get_status(self) -> Dict:
        """Get agent status."""
        return {
            "name": self.name,
            "running": self.running,
            "description": self.description
        }
