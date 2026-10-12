import random
import secrets

def generate_session_token_violation():
    # SEC11 Violation: Non-cryptographic PRNG (random.random) used for security token generation
    return f"token_{random.randint(100000, 999999)}"

def generate_session_token_safe():
    # SEC11 Safe: Cryptographically secure PRNG (secrets.token_hex) used for tokens
    return f"token_{secrets.token_hex(32)}"

