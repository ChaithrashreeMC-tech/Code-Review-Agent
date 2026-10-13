# TC-007: Lockfile Drift / Inconsistent Configuration Fixture
# pyproject.toml requests pydantic>=2.6, but uv.lock is missing or out of sync

PYPROJECT_DRIFT_MANIFEST = """
[project]
name = "order-service"
version = "1.2.0"
dependencies = [
    "pydantic>=2.6.0",
    "httpx>=0.27.0",
    "redis>=5.0.0"  # Newly added dependency not present in uv.lock
]
"""

class LockfileValidator:
    def check_drift(self, pyproject_deps: set[str], lockfile_deps: set[str]) -> bool:
        # Detects when pyproject.toml has dependencies missing from lockfile
        missing = pyproject_deps - lockfile_deps
        return len(missing) > 0

