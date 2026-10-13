# TC-005: Monorepo Service Layout Fixture
# Recognizes multiple services inside services/ or apps/ directory

MONOREPO_CONFIG = """
# Root pyproject.toml workspace
[tool.uv.workspace]
members = ["services/*", "libs/*"]
"""

class MonorepoDetector:
    def __init__(self, file_tree: list[str]):
        self.file_tree = file_tree

    def is_monorepo(self) -> bool:
        return "pyproject.toml" in self.file_tree and "services/auth_service/pyproject.toml" in self.file_tree

