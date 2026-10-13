# TC-010: Handling Missing Optional Tools Fixture
# Distinguishes missing optional binary tools from actual code/config violations

class ToolAvailabilityHandler:
    def handle_tool_check(self, tool_name: str, is_installed: bool) -> dict:
        if not is_installed:
            # Correct behavior: Report tool as UNAVAILABLE, not as a code flaw or security violation
            return {
                "check_name": f"{tool_name}_validation",
                "status": "UNAVAILABLE",
                "message": f"Optional tool '{tool_name}' is not installed in local environment.",
                "is_code_violation": False
            }
        return {"status": "SUCCESS", "is_code_violation": False}

