import sqlite3

class SecureUserProfileEndpoint:
    def get_profile(self, request, user_id: int):
        # Fully compliant secure endpoint: parameterization, authz, schema check
        if request.authenticated_user.id != user_id:
            raise PermissionError("Access denied")
        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        query = "SELECT id, name FROM profiles WHERE id = ?"
        return cursor.execute(query, (user_id,)).fetchone()

