# TC-005: Coupling and Dependency Management (MAINT05)
# Demonstrates tight coupling via hardcoded concrete instantiations vs. dependency injection

from typing import Protocol

# Concrete infrastructure clients
class PostgresClient:
    def __init__(self, dsn: str): self.dsn = dsn
    def query(self, sql: str) -> list: return [{"id": 1, "balance": 500.0}]

class StripeApiClient:
    def __init__(self, api_key: str): self.api_key = api_key
    def charge_customer(self, customer_id: int, amount: float) -> bool: return True


# --- VIOLATION ---
class BillingProcessorViolation:
    """
    VIOLATION: Hardcoded concrete dependencies inside constructor.
    Cannot be unit-tested without real Postgres and Stripe credentials.
    Tightly coupled to specific third-party implementations.
    """
    def __init__(self):
        # VIOLATION: direct instantiation of external infrastructure
        self.db = PostgresClient("postgres://prod-db:5432/finance")
        self.stripe = StripeApiClient("sk_live_secret_key_12345")

    def execute_monthly_billing(self, customer_id: int, amount: float) -> bool:
        records = self.db.query(f"SELECT balance FROM customers WHERE id = {customer_id}")
        if records:
            return self.stripe.charge_customer(customer_id, amount)
        return False


# --- SAFE IMPLEMENTATION ---
class PaymentGateway(Protocol):
    def charge_customer(self, customer_id: int, amount: float) -> bool: ...

class CustomerRepository(Protocol):
    def get_customer_balance(self, customer_id: int) -> float: ...

class BillingProcessorSafe:
    """
    SAFE: Inversion of control via injected abstractions.
    Easily tested with in-memory test doubles.
    """
    def __init__(self, repository: CustomerRepository, payment_gateway: PaymentGateway):
        self._repository = repository
        self._payment_gateway = payment_gateway

    def execute_monthly_billing(self, customer_id: int, amount: float) -> bool:
        balance = self._repository.get_customer_balance(customer_id)
        if balance > 0:
            return self._payment_gateway.charge_customer(customer_id, amount)
        return False

