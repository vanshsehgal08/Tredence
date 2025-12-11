from typing import Callable, Dict, Any

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Callable] = {}

    def register(self, name: str, func: Callable):
        """Registers a tool with a given name."""
        self._tools[name] = func

    def get_tool(self, name: str) -> Callable:
        """Retrieves a tool by name."""
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' not found in registry.")
        return self._tools[name]
    
    def list_tools(self) -> Dict[str, str]:
        """Lists all registered tools."""
        return {name: func.__doc__ or "No description" for name, func in self._tools.items()}

# Global registry instance
registry = ToolRegistry()
