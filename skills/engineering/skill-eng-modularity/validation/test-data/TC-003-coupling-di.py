# TC-003: Coupling and Dependency Management

from abc import ABC, abstractmethod

class ConcreteStripeClient:
    def charge(self, amount):
        return f"Stripe charge {amount} success"

# VIOLATION: Business logic directamente instantiates concrete Stripe client
class CheckoutServiceViolation:
    def __init__(self):
        self.payment_gateway = ConcreteStripeClient()  # Hardcoded dependency

    def checkout(self, cart_total):
        return self.payment_gateway.charge(cart_total)


# SAFE: Business logic depends on PaymentGateway abstraction injected via constructor
class IPaymentGateway(ABC):
    @abstractmethod
    def charge(self, amount: float) -> str:
        pass

class CheckoutServiceSafe:
    def __init__(self, payment_gateway: IPaymentGateway):
        self.payment_gateway = payment_gateway

    def checkout(self, cart_total: float):
        return self.payment_gateway.charge(cart_total)

