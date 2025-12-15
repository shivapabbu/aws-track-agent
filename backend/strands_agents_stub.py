"""
Strands-agents compatibility stub.
This allows the code to run without the actual strands_agents package installed.
In production, replace this with the actual strands_agents import.
"""
import asyncio
from typing import Callable, List, Any
from functools import wraps


class Agent:
    """Base Agent class stub."""
    
    def __init__(self, name: str, description: str = "", tools: List = None):
        self.name = name
        self.description = description
        self.tools_dict = {}
        if tools:
            for tool in tools:
                if hasattr(tool, 'func'):
                    self.tools_dict[tool.func.__name__] = tool.func
                elif callable(tool):
                    self.tools_dict[tool.__name__] = tool
        self.tools = tools or []
    
    async def execute_tool(self, tool_name: str, **kwargs):
        """Execute a tool by name."""
        # First check tools_dict
        if tool_name in self.tools_dict:
            func = self.tools_dict[tool_name]
            if asyncio.iscoroutinefunction(func):
                return await func(**kwargs)
            else:
                return func(**kwargs)
        
        # Then check tools list
        for tool in self.tools:
            if hasattr(tool, 'func') and tool.func.__name__ == tool_name:
                func = tool.func
                if asyncio.iscoroutinefunction(func):
                    return await func(**kwargs)
                else:
                    return func(**kwargs)
            elif callable(tool) and tool.__name__ == tool_name:
                if asyncio.iscoroutinefunction(tool):
                    return await tool(**kwargs)
                else:
                    return tool(**kwargs)
        
        raise ValueError(f"Tool '{tool_name}' not found. Available: {list(self.tools_dict.keys())}")


class Tool:
    """Tool wrapper class stub."""
    
    def __init__(self, func: Callable):
        self.func = func
        self.name = func.__name__
        self.description = func.__doc__ or ""


def tool(func: Callable) -> Callable:
    """Decorator to mark a function as a tool."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    wrapper._is_tool = True
    return wrapper