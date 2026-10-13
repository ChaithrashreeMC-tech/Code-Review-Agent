def bad_mutation_node(state: dict) -> dict:
    # Defect: in_place_mutation of shared list
    state['items'].append("item_1")
    return {}

