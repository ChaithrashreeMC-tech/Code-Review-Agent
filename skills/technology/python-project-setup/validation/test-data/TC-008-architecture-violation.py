# TC-008: Clean Architecture Cross-Layer Import Violation Fixture
# Domain module illegally importing from infrastructure persistence layer

# Violation in src/payment_service/domain/payment.py
class PaymentDomainViolation:
    def __init__(self):
        # Violation: Domain layer directly importing and calling Infrastructure DB adapter
        from payment_service.infrastructure.persistence.postgres import PostgresDatabaseSession
        self.db = PostgresDatabaseSession()

# Safe counterpart in src/payment_service/domain/payment.py
class PaymentDomainSafe:
    def __init__(self, amount: float, currency: str):
        # Safe: Pure domain entity relying on primitive values/domain value objects
        self.amount = amount
        self.currency = currency

