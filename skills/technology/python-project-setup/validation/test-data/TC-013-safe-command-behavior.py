# TC-013: Safe Command Execution Behavior Fixture
# Prevents running destructive commands or unapproved package installation

class SafeCommandExecutor:
    DESTRUCTIVE_PATTERNS = ["rm -rf", "git reset --hard", "pip install --force-reinstall"]

    def validate_command_safety(self, command: str, authorized: bool) -> bool:
        for pattern in self.DESTRUCTIVE_PATTERNS:
            if pattern in command and not authorized:
                return False  # Block unauthorized destructive command
        return True

