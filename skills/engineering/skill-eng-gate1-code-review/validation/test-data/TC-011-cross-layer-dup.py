# Deduplication fixture: SQL in API Controller violating both MOD08 and MOD09
# Must be deduplicated into ONE primary finding under MOD08 (Handler Layer Isolation)
class OrderController:
    def handle_checkout(self, request):
        db_conn = request.get_db()
        # Direct SQL execution inside HTTP controller
        cursor = db_conn.cursor()
        cursor.execute("UPDATE inventory SET stock = stock - 1 WHERE item_id = %s", (request.item_id,))
        return {"status": "ok"}

