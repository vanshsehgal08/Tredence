from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Dict, Any, List
import json

from engine.models import GraphDefinition, RunResult, WorkflowState
from engine.workflow import engine
from engine.registry import registry
from workflows.data_quality import register_data_quality_tools

app = FastAPI(title="Minimal Agent Workflow Engine")

# Register tools on startup
register_data_quality_tools()

class RunRequest(BaseModel):
    graph_id: str
    initial_state: Dict[str, Any]

@app.get("/")
def read_root():
    return {"message": "Workflow Engine Ready", "tools": registry.list_tools()}

@app.post("/graph/create")
def create_graph(definition: GraphDefinition):
    """Creates a new workflow graph."""
    try:
        graph_id = engine.create_graph(definition)
        return {"graph_id": graph_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/graph/run")
async def run_graph(request: RunRequest):
    """Runs a workflow end-to-end (blocking but async)."""
    try:
        result = await engine.run_graph(request.graph_id, request.initial_state)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/graph/state/{run_id}")
def get_run_state(run_id: str):
    """Gets the current state of a workflow run."""
    state = engine.get_run_state(run_id)
    if not state:
        raise HTTPException(status_code=404, detail="Run ID not found")
    return state

@app.websocket("/graph/stream")
async def stream_workflow(websocket: WebSocket):
    """
    WebSocket endpoint to run a graph and stream logs step-by-step.
    Client should send JSON: {"graph_id": "...", "initial_state": {...}}
    """
    await websocket.accept()
    try:
        data = await websocket.receive_text()
        request_data = json.loads(data)
        
        graph_id = request_data.get("graph_id")
        initial_state = request_data.get("initial_state", {})
        
        if not graph_id:
            await websocket.send_json({"type": "error", "message": "graph_id required"})
            await websocket.close()
            return

        async def callback(log_entry: Dict[str, Any]):
            try:
                await websocket.send_json(log_entry)
            except RuntimeError:
                # Connection might be closed
                pass

        await engine.run_graph(graph_id, initial_state, stream_callback=callback)
        await websocket.close()
        
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
            await websocket.close()
        except:
             pass
