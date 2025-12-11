# Minimal Agent Workflow Engine

A lightweight, graph-based workflow engine for building agentic pipelines. Supports shared state, conditional branching, looping, asynchronous execution, and real-time log streaming via WebSockets.

## features
- **Graph-Based Execution**: Define workflows as nodes (tools) and edges (transitions).
- **Shared State**: Maintain context across steps.
- **Async Support**: Efficiently handle long-running operations.
- **WebSockets**: Stream execution logs in real-time.
- **Simple Tool Registry**: Easily plug in Python functions as tools.

## Installation

1.  **Clone the repository**
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### 1. Start the Server
Run the FastAPI server:
```bash
uvicorn main:app --reload
```

![Server Startup](media/Server_Setup.png)

### 2. Verify Core Engine
Test the workflow logic directly (bypassing the API):
```bash
python verify_engine.py
```

![Engine Verification](media/Engine_Verification.png)

### 3. Verify APIs (Blocking & Streaming)
Test the REST API and WebSocket streaming:

**Blocking API:**
```bash
python verify_api.py
```

![Blocking API Verification](media/Verify_API.png)

**Streaming API:**
```bash
python verify_websocket.py
```

![WebSocket Streaming](media/Verify_WebSocket.png)


## API Reference

### Create Graph
- **POST** `/graph/create`
- Body: JSON graph definition (nodes, edges, start_node).

### Run Graph (Blocking)
- **POST** `/graph/run`
- Body: `{"graph_id": "...", "initial_state": {...}}`

### Stream Graph (WebSocket)
- **WS** `/graph/stream`
- Send: `{"graph_id": "...", "initial_state": {...}}`

### Get Run State
- **GET** `/graph/state/{run_id}`
- Returns: `{"run_id": "...", "status": "...", "final_state": {...}, "history": [...]}`

## Future Improvements
With more time, I would add:
1.  **Persistent Storage**: Replace in-memory storage with SQLite/PostgreSQL for durability.
2.  **Concurrency Control**: Better locking for shared state in high-concurrency scenarios.
3.  **Dynamic Graph Editing**: APIs to update existing graphs (add/remove nodes).
4.  **UI Visualization**: A frontend to visualize the graph structure and execution flow.
5.  **Error Handling**: More granular error recovery and retry policies for failed nodes.