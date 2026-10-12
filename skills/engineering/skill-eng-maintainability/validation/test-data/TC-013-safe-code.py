# TC-013: Safe Code across Multiple Rules (False Positive Guard)
# Demonstrates clean, maintainable code that must NOT trigger maintainability findings.

from dataclasses import dataclass
from typing import List, Optional

@dataclass(frozen=True)
class Customer:
    id: int
    name: str
    email: str
    is_active: bool

class CustomerService:
    """
    SAFE IMPLEMENTATION:
    - Clear single responsibility (Customer filtering & querying)
    - Well-named, descriptive functions and variables (MAINT03 safe)
    - Low cyclomatic complexity with early returns (MAINT02 safe)
    - No duplicated code (MAINT01 safe)
    - Loose coupling and clear boundaries (MAINT05, MAINT06 safe)
    - Deterministic and testable (MAINT09 safe)
    """
    def __init__(self, customers: List[Customer]):
        self._customers = customers

    def find_active_customers(self) -> List[Customer]:
        """Returns all currently active customers."""
        return [c for c in self._customers if c.is_active]

    def get_customer_by_id(self, customer_id: int) -> Optional[Customer]:
        """Finds customer by unique ID or returns None."""
        if customer_id <= 0:
            return None
        for customer in self._customers:
            if customer.id == customer_id:
                return customer
        return None

