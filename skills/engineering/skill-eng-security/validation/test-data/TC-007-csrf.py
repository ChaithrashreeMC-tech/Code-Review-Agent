def update_email_handler_violation(request):
    # SEC07 Violation: State-changing POST action relying solely on session cookie without CSRF token verification
    new_email = request.POST.get("email")
    request.user.email = new_email
    request.user.save()

def update_email_handler_safe(request):
    # SEC07 Safe: Verifies anti-CSRF token and SameSite cookie attribute
    if not request.verify_csrf_token():
        raise PermissionError("Invalid CSRF token")
    new_email = request.POST.get("email")
    request.user.email = new_email
    request.user.save()

