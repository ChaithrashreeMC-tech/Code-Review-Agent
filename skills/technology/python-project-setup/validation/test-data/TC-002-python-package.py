# TC-002: Standard Python Package Layout Fixture
# Recognizes src/ layout, pyproject.toml, py.typed marker

PYPROJECT_PACKAGE_CONFIG = """
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "core-utilities"
version = "1.0.0"
requires-python = ">=3.11"
"""

class StandardPackageDetector:
    def __init__(self, file_tree: list[str]):
        self.file_tree = file_tree

    def is_standard_package(self) -> bool:
        return "pyproject.toml" in self.file_tree and "src/core_utilities/py.typed" in self.file_tree

