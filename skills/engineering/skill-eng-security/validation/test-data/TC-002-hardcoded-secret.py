import os

class StripeServiceViolation:
    def __init__(self):
        # SEC02 Violation: Hardcoded secret key in source code
        self.api_key = "dummy_secret_key_sk_live_example_1234567890"

class StripeServiceSafe:
    def __init__(self, api_key: str = None):
        # SEC02 Safe: Secrets loaded from environment variable or secret manager
        self.api_key = api_key or os.environ.get("STRIPE_API_KEY")
