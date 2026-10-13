# Polyglot repo: Python backend endpoint
from typing import Dict, Any

def get_product_details(product_id: str) -> Dict[str, Any]:
    return {"id": product_id, "title": "Wireless Mouse", "price": 29.99}

