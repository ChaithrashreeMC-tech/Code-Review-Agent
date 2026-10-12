# TC-006: Cohesion and Module Boundaries (MAINT06)
# Demonstrates low-cohesion God-class vs. cohesive single-purpose domain classes

from typing import Dict, Any, List

# --- VIOLATION ---
class AppOmnibusManager:
    """
    VIOLATION: Low cohesion. Combines 4 completely disparate business domains
    into a single 100+ line God class:
    - User authentication & password hashing
    - Warehouse inventory tracking
    - PDF report rendering
    - Email campaign dispatching
    """
    def __init__(self):
        self.auth_token_secret = "secret"
        self.inventory_stock: Dict[str, int] = {}
        self.email_server = "smtp.mail.com"

    # Domain 1: Auth
    def hash_password(self, password: str) -> str:
        return f"hashed_{password}"
    def verify_token(self, token: str) -> bool:
        return token.startswith("valid_")

    # Domain 2: Warehouse
    def deduct_inventory(self, sku: str, quantity: int) -> bool:
        if self.inventory_stock.get(sku, 0) >= quantity:
            self.inventory_stock[sku] -= quantity
            return True
        return False

    # Domain 3: Document Generation
    def generate_pdf_report(self, title: str, rows: List[dict]) -> bytes:
        return f"PDF_BINARY_DATA_{title}_{len(rows)}".encode()

    # Domain 4: Marketing Email
    def send_newsletter(self, subscribers: List[str], campaign_id: str):
        pass


# --- SAFE IMPLEMENTATION ---
class InventoryService:
    """SAFE: High cohesion — focused purely on inventory state."""
    def __init__(self):
        self._stock: Dict[str, int] = {}

    def deduct_stock(self, sku: str, quantity: int) -> bool:
        if self._stock.get(sku, 0) >= quantity:
            self._stock[sku] -= quantity
            return True
        return False

class AuthenticationService:
    """SAFE: High cohesion — focused purely on security tokens."""
    def __init__(self, secret_key: str):
        self._secret_key = secret_key

    def verify_token(self, token: str) -> bool:
        return token.startswith("valid_")

