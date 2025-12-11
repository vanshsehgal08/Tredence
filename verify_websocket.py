import asyncio
import websockets
import json
import requests
from engine.models import GraphDefinition, NodeDefinition, EdgeDefinition

# Helper to create graph via REST API first
def create_graph_via_api():
    nodes = [
        {"id": "step1", "tool_name": "profile_data"},
        {"id": "step2", "tool_name": "identify_anomalies"}
    ]
    edges = [
        {"from_node": "step1", "to_node": "step2"}
    ]
    graph_def = {
        "nodes": nodes,
        "edges": edges,
        "start_node": "step1"
    }
    try:
        response = requests.post("http://localhost:8000/graph/create", json=graph_def)
        response.raise_for_status()
        return response.json()["graph_id"]
    except Exception as e:
        print(f"Failed to create graph: {e}")
        return None

async def test_websocket_stream(graph_id):
    uri = "ws://localhost:8000/graph/stream"
    async with websockets.connect(uri) as websocket:
        print(f"Connected to {uri}")
        
        request = {
            "graph_id": graph_id,
            "initial_state": {"data": [1, 2, 3]}
        }
        await websocket.send(json.dumps(request))
        
        print("Waiting for messages...")
        async for message in websocket:
            data = json.loads(message)
            print(f"Received: {data}")
            if data.get("type") == "finish":
                break

if __name__ == "__main__":
    # We need the server running for this test.
    # Assuming user runs: uvicorn main:app --reload
    print("Ensure server is running on localhost:8000")
    
    # Create graph
    graph_id = create_graph_via_api()
    if graph_id:
        print(f"Created Test Graph: {graph_id}")
        asyncio.run(test_websocket_stream(graph_id))
    else:
        print("Could not create graph via API. Is server running?")
