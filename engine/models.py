from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field

class NodeDefinition(BaseModel):
    id: str
    tool_name: str  # The name of the function/tool to execute
    parameters: Dict[str, Any] = Field(default_factory=dict)

class EdgeDefinition(BaseModel):
    from_node: str
    to_node: str
    condition: Optional[str] = None  # Python expression string, e.g., "state['value'] > 10"

class GraphDefinition(BaseModel):
    nodes: List[NodeDefinition]
    edges: List[EdgeDefinition]
    start_node: str

class WorkflowState(BaseModel):
    run_id: str
    current_node: Optional[str]
    state: Dict[str, Any]
    status: str = "running"  # running, completed, failed
    history: List[Dict[str, Any]] = Field(default_factory=list) # Log of steps

class RunResult(BaseModel):
    run_id: str
    final_state: Dict[str, Any]
    status: str
    log: List[Dict[str, Any]]
