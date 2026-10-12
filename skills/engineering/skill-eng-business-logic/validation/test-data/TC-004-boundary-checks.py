# TC-004: Boundary condition defect
# Spec: specs/subscriptions/business-spec.md Section 1.4
# Rule: Users aged exactly 18 or older (age >= 18) are eligible for standard subscription.

def verify_subscription_age_violation(age: int) -> bool:
    """VIOLATION (BIZ05): Strict inequality (age > 18) excludes users aged exactly 18."""
    return age > 18


def verify_subscription_age_safe(age: int) -> bool:
    """SAFE: Inclusive boundary check (age >= 18) matches business specification."""
    return age >= 18

