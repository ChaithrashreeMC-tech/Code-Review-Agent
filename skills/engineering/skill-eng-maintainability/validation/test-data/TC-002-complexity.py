# TC-002: Complexity and Readability (MAINT02)
# Demonstrates deep nesting, high cyclomatic complexity, and guard-clause refactoring

from typing import Optional, Dict, Any

# --- VIOLATION ---
def process_loan_application_complex(applicant: Dict[str, Any], loan: Dict[str, Any]) -> str:
    """
    VIOLATION: 5 levels of nested conditionals and deeply tangled control flow.
    Cognitively overwhelming and error-prone to modify.
    """
    status = "REJECTED"
    if applicant is not None:
        if applicant.get("age", 0) >= 18:
            if applicant.get("credit_score", 0) > 650:
                if loan.get("amount", 0) > 0:
                    if applicant.get("annual_income", 0) > (loan.get("amount", 0) * 0.3):
                        if not applicant.get("has_active_bankruptcy", False):
                            status = "APPROVED"
                        else:
                            status = "REJECTED_BANKRUPTCY"
                    else:
                        status = "REJECTED_INSUFFICIENT_INCOME"
                else:
                    status = "REJECTED_INVALID_AMOUNT"
            else:
                status = "REJECTED_LOW_CREDIT"
        else:
            status = "REJECTED_UNDERAGE"
    return status


# --- SAFE IMPLEMENTATION ---
def process_loan_application_safe(applicant: Optional[Dict[str, Any]], loan: Dict[str, Any]) -> str:
    """
    SAFE: Flattens complexity using guard clauses and early returns.
    Max nesting depth: 1. Easy to trace and extend.
    """
    if not applicant or applicant.get("age", 0) < 18:
        return "REJECTED_UNDERAGE"
    if applicant.get("credit_score", 0) <= 650:
        return "REJECTED_LOW_CREDIT"
    if loan.get("amount", 0) <= 0:
        return "REJECTED_INVALID_AMOUNT"
    if applicant.get("annual_income", 0) <= (loan.get("amount", 0) * 0.3):
        return "REJECTED_INSUFFICIENT_INCOME"
    if applicant.get("has_active_bankruptcy", False):
        return "REJECTED_BANKRUPTCY"

    return "APPROVED"

