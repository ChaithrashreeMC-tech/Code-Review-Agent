# TC-003: Invalid workflow or state transition
# Spec: specs/orders/business-spec.md Section 4.2
# Rule: An order can transition from DRAFT -> SUBMITTED -> APPROVED -> FULFILLED.
# An order cannot transition directly from DRAFT to APPROVED or from FAILED to FULFILLED.

class OrderStateMachineViolation:
    def approve_order(self, order_status: str) -> str:
        """VIOLATION (BIZ03): Allows approval directly from DRAFT state bypassing SUBMITTED."""
        if order_status in ["DRAFT", "SUBMITTED"]:
            return "APPROVED"
        raise ValueError(f"Cannot approve order in status {order_status}")


class OrderStateMachineSafe:
    def approve_order(self, order_status: str) -> str:
        """SAFE: Strictly requires SUBMITTED state before approval."""
        if order_status == "SUBMITTED":
            return "APPROVED"
        raise ValueError(f"Cannot approve order in status {order_status}")

