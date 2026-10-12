# TC-004: Function and Method Responsibility (MAINT04)
# Demonstrates God-method violating Single Responsibility Principle vs. decomposed functions

import json
from typing import Dict, Any

# Mock external services
class Database:
    @staticmethod
    def save_order(order: Dict[str, Any]): pass

class EmailService:
    @staticmethod
    def send(to: str, subject: str, body: str): pass

class PaymentGateway:
    @staticmethod
    def charge(card_token: str, amount: float): pass


# --- VIOLATION ---
def process_checkout_god_method(raw_payload: str, notify_user: bool) -> Dict[str, Any]:
    """
    VIOLATION: Single function does 5 unrelated tasks:
    1. JSON payload parsing
    2. Input validation & tax calculation
    3. Credit card payment processing
    4. Database persistence
    5. Email dispatch conditioned on a boolean flag
    """
    # Task 1: Parsing
    data = json.loads(raw_payload)
    
    # Task 2: Validation & Business calculation
    if "items" not in data or len(data["items"]) == 0:
        raise ValueError("Order must contain at least one item")
    total = sum(i["price"] * i["qty"] for i in data["items"])
    total += total * 0.08  # tax
    
    # Task 3: Payment charge
    PaymentGateway.charge(data["card_token"], total)
    
    # Task 4: Database storage
    order_record = {"customer_id": data["customer_id"], "total": total, "status": "PAID"}
    Database.save_order(order_record)
    
    # Task 5: Notification (flag argument smell)
    if notify_user:
        EmailService.send(data["customer_email"], "Order Placed", f"Total: {total}")
        
    return order_record


# --- SAFE IMPLEMENTATION ---
def parse_and_validate_order(raw_payload: str) -> tuple[Dict[str, Any], float]:
    """SAFE: Focused exclusively on payload parsing and validation."""
    data = json.loads(raw_payload)
    if not data.get("items"):
        raise ValueError("Order must contain at least one item")
    subtotal = sum(item["price"] * item["qty"] for item in data["items"])
    total_with_tax = subtotal * 1.08
    return data, total_with_tax

def process_checkout_safe(raw_payload: str) -> Dict[str, Any]:
    """SAFE: High-level orchestrator delegating to single-responsibility functions."""
    data, total = parse_and_validate_order(raw_payload)
    PaymentGateway.charge(data["card_token"], total)
    order_record = {"customer_id": data["customer_id"], "total": total, "status": "PAID"}
    Database.save_order(order_record)
    return order_record

