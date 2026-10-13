# Multiple symptoms stemming from single root cause: root_cause_router_defect
def broken_master_router(state: dict) -> str:
    # Root cause: router raises unhandled KeyError and returns non-string invalid node type
    # Symptom 1: invalid routing destination
    # Symptom 2: unhandled exception in conditional branch
    # Consolidation: report 1 defect for root_cause_router_defect
    return state["non_existent_key"]

