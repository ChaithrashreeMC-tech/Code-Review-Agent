def clean_node(state: dict) -> dict:
    # Safe partial return
    return {"cleaned_text": state["raw_text"].strip()}

