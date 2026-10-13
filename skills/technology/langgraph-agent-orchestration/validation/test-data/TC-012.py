def faulty_aggregator(state: dict) -> dict:
    # Defect: unhandled_branch_error that crashes_aggregator when a branch fails
    branch_a_res = state["branch_a"]["score"]
    branch_b_res = state["branch_b"]["score"]
    return {"final": (branch_a_res + branch_b_res) / 2}

