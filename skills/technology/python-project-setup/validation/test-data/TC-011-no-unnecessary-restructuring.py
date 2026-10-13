# TC-011: No Unnecessary Restructuring Guardrail Fixture
# Preserves working flat package structure without forcing ConnectRPC reorganization

class LayoutPreservationGuardrail:
    def evaluate_layout_change(self, current_layout: str, user_request: str) -> bool:
        # If current layout is working flat package and user didn't ask for ConnectRPC conversion, keep existing layout
        if current_layout == "flat_package" and "restructure" not in user_request:
            return False  # Do NOT force restructuring
        return True

