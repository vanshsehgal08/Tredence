import requests
import json
import time

BASE_URL = "http://localhost:8000"

def create_graph():
    print("Creating graph...")
    # Define Data Quality Pipeline via API
    nodes = [
        {"id": "profile", "tool_name": "profile_data"},
        {"id": "anomalies", "tool_name": "identify_anomalies"},
        {"id": "rules", "tool_name": "generate_rules"},
        {"id": "apply", "tool_name": "apply_rules"},
    ]
    edges = [
        {"from_node": "profile", "to_node": "anomalies"},
        {"from_node": "anomalies", "to_node": "rules", "condition": "state.get('anomaly_count', 0) > 0"},
        {"from_node": "rules", "to_node": "apply"},
        {"from_node": "apply", "to_node": "anomalies"}, # Loop
    ]
    pass_edge = {"from_node": "anomalies", "to_node": "end", "condition": "state.get('anomaly_count', 0) == 0"} # Implicit end
    # Note: Our simple engine stops if no edge matches, so the implicit end works.

    graph_def = {
        "nodes": nodes,
        "edges": edges,
        "start_node": "profile"
    }
    
    response = requests.post(f"{BASE_URL}/graph/create", json=graph_def)
    if response.status_code != 200:
        print(f"Error creating graph: {response.text}")
        return None
    
    graph_id = response.json().get("graph_id")
    print(f"Graph created: {graph_id}")
    return graph_id

def run_graph(graph_id):
    print(f"Running graph {graph_id} (Blocking)...")
    payload = {
        "graph_id": graph_id,
        "initial_state": {"data": [1, 2, 3, 4, 5] * 20} # 100 records
    }
    
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/graph/run", json=payload)
    end_time = time.time()
    
    if response.status_code == 200:
        result = response.json()
        print(f"Run completed in {end_time - start_time:.2f}s")
        print(f"Status: {result.get('status')}")
        print(f"Final State: {result.get('final_state')}")
    else:
        print(f"Error running graph: {response.text}")

if __name__ == "__main__":
    print(f"Testing API at {BASE_URL}")
    try:
        # Check if server is up
        requests.get(BASE_URL)
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server. Is 'uvicorn main:app --reload' running?")
        exit(1)

    graph_id = create_graph()
    if graph_id:
        run_graph(graph_id)
