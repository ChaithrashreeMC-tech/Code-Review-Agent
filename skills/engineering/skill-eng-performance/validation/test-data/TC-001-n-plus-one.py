# TC-001: N+1 Query Pattern (PERF02 violation)
# Expected: PERF02 finding, severity=high, confidence=high
# Technology: Python / SQLAlchemy

from sqlalchemy.orm import Session
from models import Order, OrderItem

def get_orders_with_items(db: Session) -> list[dict]:
    """
    VIOLATION: Issues one SELECT per order to fetch items.
    With 500 orders this produces 501 queries.
    """
    orders = db.query(Order).all()  # 1 query

    result = []
    for order in orders:
        # VIOLATION: Lazy-loaded relationship — triggers N additional queries
        items = order.items  # 1 query per order = N queries
        result.append({
            "order_id": order.id,
            "customer": order.customer_name,
            "items": [{"sku": i.sku, "qty": i.quantity} for i in items],
        })
    return result


# --- SAFE IMPLEMENTATION ---
from sqlalchemy.orm import selectinload

def get_orders_with_items_safe(db: Session) -> list[dict]:
    """
    SAFE: Uses selectinload to batch-load items in 2 queries total,
    regardless of order count.
    """
    orders = (
        db.query(Order)
        .options(selectinload(Order.items))  # Eager load in 2 queries
        .all()
    )

    result = []
    for order in orders:
        result.append({
            "order_id": order.id,
            "customer": order.customer_name,
            "items": [{"sku": i.sku, "qty": i.quantity} for i in order.items],
        })
    return result

