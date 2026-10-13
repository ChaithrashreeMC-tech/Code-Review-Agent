import socket

def socket_node(state: dict) -> dict:
    # Defect: root_cause_unserializable_state storing unpicklable socket object in graph state
    s = socket.socket()
    return {"live_socket": s}

