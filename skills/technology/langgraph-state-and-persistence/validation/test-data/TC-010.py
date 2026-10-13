def ingest_pdf_node(state: dict) -> dict:
    # Defect: raw_binary_payload with large_file_bytes stored in state
    return {"raw_binary_payload": b"%PDF-1.4..." * 1000000, "large_file_bytes": True}

