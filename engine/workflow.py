import uuid
import time
import asyncio
import inspect
from typing import Dict, Any, Optional, Callable, Awaitable
from .models import GraphDefinition, WorkflowState, RunResult
from .registry import registry

class WorkflowEngine:
    def __init__(self):
        self._graphs: Dict[str, GraphDefinition] = {}
        self._runs: Dict[str, WorkflowState] = {}

    def create_graph(self, definition: GraphDefinition) -> str:
        """Stores a new graph definition and returns its ID."""
        graph_id = str(uuid.uuid4())
        self._graphs[graph_id] = definition
        return graph_id

    async def run_graph(
        self, 
        graph_id: str, 
        initial_state: Dict[str, Any],
        stream_callback: Optional[Callable[[Dict], Awaitable[None]]] = None
    ) -> RunResult:
        """
        Executes a graph end-to-end asynchronously.
        
        Args:
            graph_id: The ID of the graph to run.
            initial_state: The starting state dictionary.
            stream_callback: Optional async function to call with log events.
        """
        if graph_id not in self._graphs:
            raise ValueError(f"Graph {graph_id} not found.")

        graph = self._graphs[graph_id]
        run_id = str(uuid.uuid4())
        
        # Initialize state
        current_state = WorkflowState(
            run_id=run_id,
            current_node=graph.start_node,
            state=initial_state,
            status="running"
        )
        self._runs[run_id] = current_state

        async def emit_log(event_type: str, details: Dict[str, Any]):
            log_entry = {"type": event_type, "timestamp": time.time(), **details}
            current_state.history.append(log_entry)
            if stream_callback:
                await stream_callback(log_entry)

        await emit_log("start", {"run_id": run_id, "graph_id": graph_id})

        # Execution loop
        while current_state.current_node:
            node_id = current_state.current_node
            await emit_log("node_start", {"node": node_id})
            
            # Find node definition
            node_def = next((n for n in graph.nodes if n.id == node_id), None)
            if not node_def:
                 error_msg = f"Node {node_id} not found"
                 await emit_log("error", {"message": error_msg})
                 current_state.status = "failed"
                 break

            # Execute tool
            try:
                tool_func = registry.get_tool(node_def.tool_name)
                start_time = time.time()
                
                # Execute tool (handle both async and sync tools)
                if inspect.iscoroutinefunction(tool_func):
                    updates = await tool_func(current_state.state)
                else:
                    # Run sync blocking functions in a thread pool
                    updates = await asyncio.to_thread(tool_func, current_state.state)

                if updates:
                    current_state.state.update(updates)
                
                duration = time.time() - start_time
                await emit_log("tool_complete", {
                    "node": node_id,
                    "tool": node_def.tool_name,
                    "updates": updates,
                    "duration": duration
                })
                
            except Exception as e:
                await emit_log("error", {"message": str(e), "node": node_id})
                current_state.status = "failed"
                break

            # Determine next node
            next_node_id = None
            
            # Find edges starting from current node
            edges = [e for e in graph.edges if e.from_node == node_id]
            
            for edge in edges:
                if edge.condition:
                    # Evaluate condition
                    try:
                        # Allow condition to access 'state' variable
                        if eval(edge.condition, {}, {"state": current_state.state}):
                            next_node_id = edge.to_node
                            break
                    except Exception as e:
                        print(f"Condition evaluation failed: {e}")
                        continue 
                else:
                    # Unconditional edge
                    next_node_id = edge.to_node
                    break
            
            current_state.current_node = next_node_id
            
            # Loop protection
            if len(current_state.history) > 100:
                await emit_log("error", {"message": "Max steps exceeded"})
                current_state.status = "failed"
                break

        current_state.status = "completed" if current_state.status == "running" else current_state.status
        self._runs[run_id] = current_state # Update final state
        
        await emit_log("finish", {"status": current_state.status, "final_state": current_state.state})

        return RunResult(
            run_id=run_id,
            final_state=current_state.state,
            status=current_state.status,
            log=current_state.history
        )

    def get_run_state(self, run_id: str) -> Optional[WorkflowState]:
        return self._runs.get(run_id)

# Global engine instance
engine = WorkflowEngine()
