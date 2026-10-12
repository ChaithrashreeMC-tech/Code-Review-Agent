# TC-010: Extensibility and Open-Closed Principle

# VIOLATION: Giant if-elif chain checking type strings requiring code modification for every new payment type
def process_payment_type_violation(payment_type, amount):
    if payment_type == "credit_card":
        return f"Processing credit card {amount}"
    elif payment_type == "paypal":
        return f"Processing paypal {amount}"
    elif payment_type == "crypto":
        return f"Processing crypto {amount}"
    elif payment_type == "apple_pay":
        return f"Processing apple pay {amount}"
    else:
        raise ValueError(f"Unsupported payment type {payment_type}")


# SAFE: Strategy pattern using dictionary registry allowing extension without modifying core caller
class PaymentStrategyRegistry:
    _strategies = {}

    @classmethod
    def register(cls, payment_type: str, handler_fn):
        cls._strategies[payment_type] = handler_fn

    @classmethod
    def process(cls, payment_type: str, amount: float):
        handler = cls._strategies.get(payment_type)
        if not handler:
            raise ValueError(f"Unsupported payment type {payment_type}")
        return handler(amount)

PaymentStrategyRegistry.register("credit_card", lambda amt: f"Processing credit card {amt}")
PaymentStrategyRegistry.register("paypal", lambda amt: f"Processing paypal {amt}")

