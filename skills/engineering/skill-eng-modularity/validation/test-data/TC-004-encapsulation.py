# TC-004: Encapsulation and Information Hiding

# VIOLATION: Exposing internal mutable list directly, allowing external mutation bypass
class BankAccountViolation:
    def __init__(self, owner: str):
        self.owner = owner
        self.transactions = []  # Public mutable list exposed directly

    def add_transaction(self, amount: float):
        self.transactions.append(amount)


# SAFE: Encapsulating transactions behind read-only property and controlled methods
class BankAccountSafe:
    def __init__(self, owner: str):
        self.owner = owner
        self._transactions = []  # Encapsulated internal state

    @property
    def transactions(self):
        return list(self._transactions)  # Return defensive copy

    def deposit(self, amount: float):
        if amount <= 0:
            raise ValueError("Deposit must be positive")
        self._transactions.append(amount)

