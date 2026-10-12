def get_user_profile_violation(request, profile_id):
    # SEC03 Violation: BOLA / IDOR - fetches profile directly by URL ID without verifying caller ownership
    return db.query("SELECT * FROM profiles WHERE id = ?", profile_id)

def get_user_profile_safe(request, profile_id):
    # SEC03 Safe: Enforces tenant/user ownership check against authenticated session user
    current_user = request.authenticated_user
    if current_user.id != profile_id and not current_user.is_admin:
        raise PermissionError("Access denied")
    return db.query("SELECT * FROM profiles WHERE id = ?", profile_id)
