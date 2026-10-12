# TC-001: Layer Separation & Separation of Concerns

import sqlite3

# VIOLATION: HTTP Controller handler directly executes raw SQL query strings and handles DB transactions
def handle_get_user_orders_violation(request):
    user_id = request.get("user_id")
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    
    # Raw SQL execution in presentation controller layer
    cursor.execute("SELECT id, total, status FROM orders WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    
    orders = [{"id": r[0], "total": r[1], "status": r[2]} for r in rows]
    conn.close()
    return {"status": 200, "data": orders}


# SAFE: Presentation controller delegates database access to Repository interface
class OrderRepository:
    def get_by_user_id(self, user_id: str):
        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, total, status FROM orders WHERE user_id = ?", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [{"id": r[0], "total": r[1], "status": r[2]} for r in rows]

def handle_get_user_orders_safe(request, order_repo: OrderRepository):
    user_id = request.get("user_id")
    orders = order_repo.get_by_user_id(user_id)
    return {"status": 200, "data": orders}

