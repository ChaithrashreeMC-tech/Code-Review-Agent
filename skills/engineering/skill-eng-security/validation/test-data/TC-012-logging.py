import logging

logger = logging.getLogger(__name__)

def log_user_login_violation(username, password, bearer_token):
    # SEC12 Violation: Sensitive plaintext credentials and tokens logged
    logger.info(f"Login attempt user={username} password={password} token={bearer_token}")

def log_user_login_safe(username, password, bearer_token):
    # SEC12 Safe: Masked credentials before logging
    logger.info(f"Login attempt user={username} password=*** token=***")

