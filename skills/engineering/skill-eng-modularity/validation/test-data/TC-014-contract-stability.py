# TC-014: Contract Stability and API Boundaries

# VIOLATION: Breaking public function signature without deprecation alias or default parameter
def format_user_name_v2_violation(first_name, last_name, middle_name, suffix):
    # Removed optional default values, breaking existing callers passing 2 args
    return f"{first_name} {middle_name} {last_name} {suffix}"


# SAFE: Maintaining backward compatibility using optional parameters with defaults
def format_user_name_safe(first_name: str, last_name: str, middle_name: str = "", suffix: str = "") -> str:
    parts = [first_name, middle_name, last_name, suffix]
    return " ".join([p for p in parts if p])

