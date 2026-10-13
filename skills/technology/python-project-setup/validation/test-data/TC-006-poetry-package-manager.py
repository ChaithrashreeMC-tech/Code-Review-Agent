# TC-006: Poetry Package Manager Fixture
# Recognizes poetry.lock and tool.poetry in pyproject.toml

POETRY_CONFIG = """
[tool.poetry]
name = "analytics-engine"
version = "0.1.0"
description = "Analytics pipeline"

[tool.poetry.dependencies]
python = "^3.11"
pandas = "^2.2.0"
"""

class PackageManagerDetector:
    def __init__(self, file_tree: list[str]):
        self.file_tree = file_tree

    def detect_manager(self) -> str:
        if "poetry.lock" in self.file_tree:
            return "poetry"
        elif "uv.lock" in self.file_tree:
            return "uv"
        return "pip"

