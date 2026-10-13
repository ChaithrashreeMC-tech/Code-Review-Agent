import ast

def execute_dynamic_script_insecure(expression: str) -> float:
    # Violation: Dangerous use of eval() flagged by security linters (bandit S307)
    return eval(expression)

def execute_dynamic_script_secure(expression: str) -> float:
    # Safe: Evaluates math expression safely using ast.literal_eval
    return float(ast.literal_eval(expression))

