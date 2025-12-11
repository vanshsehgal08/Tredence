import asyncio
from engine.models import GraphDefinition, NodeDefinition, EdgeDefinition
from engine.workflow import engine
from workflows.data_quality import register_data_quality_tools

# 1. Setup
register_data_quality_tools()

# 2. Define Graph (Data Quality Pipeline)
nodes = [
    NodeDefinition(id="profile", tool_name="profile_data"),
    NodeDefinition(id="anomalies", tool_name="identify_anomalies"),
    NodeDefinition(id="rules", tool_name="generate_rules"),
    NodeDefinition(id="apply", tool_name="apply_rules"),
]

edges = [
    EdgeDefinition(from_node="profile", to_node="anomalies"),
    EdgeDefinition(from_node="anomalies", to_node="rules", condition="state.get('anomaly_count', 0) > 0"),
    EdgeDefinition(from_node="rules", to_node="apply"),
    EdgeDefinition(from_node="apply", to_node="anomalies"), # Loop back
]

graph_def = GraphDefinition(
    nodes=nodes,
    edges=edges,
    start_node="profile"
)

async def main():
    # 3. Create Graph
    graph_id = engine.create_graph(graph_def)
    print(f"Created graph: {graph_id}")

    # 4. Run Graph
    print("Running graph...")
    initial_state = {"data": [1, 2, 3, 4, 5] * 10} # 50 records
    result = await engine.run_graph(graph_id, initial_state)

    # 5. Output Result
    print(f"Run Status: {result.status}")
    print(f"Final State: {result.final_state}")
    print("Execution Log:")
    for step in result.log:
        if "error" in step:
            print(f"  [ERROR] {step}")
        else:
            print(f"  [{step.get('type')}] Node: {step.get('node')} | Details: {step}")

if __name__ == "__main__":
    asyncio.run(main())
