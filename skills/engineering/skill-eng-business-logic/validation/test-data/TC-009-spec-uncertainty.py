# TC-009: Missing specification -> Uncertainty note (no deduction)
# TC-010: Contradictory/Ambiguous specifications -> Uncertainty note (no deduction)
# Context: Spec does not state grace period duration for enterprise plan downgrade; Spec A says 14 days, Spec B says 30 days.

def calculate_downgrade_grace_period(plan_type: str) -> int:
    """UNCERTAINTY: Plan downgrade grace period is not documented in available specs/plans/business-spec.md."""
    if plan_type == "ENTERPRISE":
        return 14  # Unconfirmed assumption
    return 0


def calculate_return_window_ambiguous(item_category: str) -> int:
    """UNCERTAINTY: specs/returns/business-spec.md Section 1 says 30 days, Section 4 says 14 days for electronics."""
    if item_category == "ELECTRONICS":
        return 30
    return 14

