import sqlite3

def handle_search_users_violation(user_input):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    # SEC01 Violation: Unsanitized user string concatenated directly into raw SQL query
    query = f"SELECT * FROM users WHERE name = '{user_input}'"
    return cursor.execute(query).fetchall()

def handle_search_users_safe(user_input):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    # SEC01 Safe: Parameterized query binding
    query = "SELECT * FROM users WHERE name = ?"
    return cursor.execute(query, (user_input,)).fetchall()

