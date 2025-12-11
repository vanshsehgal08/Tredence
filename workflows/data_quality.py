from engine.registry import registry
import random

# Option C: Data Quality Pipeline Tools

def profile_data(state: dict) -> dict:
    """Simulates profiling data quality."""
    data = state.get("data", [])
    print(f"Profiling {len(data)} records...")
    return {"profile_score": random.randint(50, 90), "record_count": len(data)}

def identify_anomalies(state: dict) -> dict:
    """Identifies anomalies in the dataset."""
    score = state.get("profile_score", 100)
    # Simulate finding anomalies based on score. Lower score = more anomalies
    anomaly_count = max(0, (100 - score) // 5)
    print(f"Identified {anomaly_count} anomalies.")
    return {"anomaly_count": anomaly_count}

def generate_rules(state: dict) -> dict:
    """Generates cleaning rules based on anomalies."""
    count = state.get("anomaly_count", 0)
    rules = [f"Rule_{i}" for i in range(count)]
    print(f"Generated {len(rules)} cleanup rules.")
    return {"active_rules": rules}

def apply_rules(state: dict) -> dict:
    """Applies rules to improve data quality."""
    # Applying rules improves the profile score
    current_score = state.get("profile_score", 0)
    improvement = len(state.get("active_rules", [])) * 5
    new_score = min(100, current_score + improvement)
    print(f"Applied rules. Score improved from {current_score} to {new_score}")
    return {"profile_score": new_score}

# Register tools
def register_data_quality_tools():
    registry.register("profile_data", profile_data)
    registry.register("identify_anomalies", identify_anomalies)
    registry.register("generate_rules", generate_rules)
    registry.register("apply_rules", apply_rules)
