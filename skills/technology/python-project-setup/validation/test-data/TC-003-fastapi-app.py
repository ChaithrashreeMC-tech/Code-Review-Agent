# TC-003: FastAPI / Flask Service Layout Fixture
# Recognizes app/main.py, routers/, and FastAPI app instance

FASTAPI_APP_CODE = """
from fastapi import FastAPI
from app.routers import users, items

app = FastAPI(title="User Microservice API", version="1.0.0")
app.include_router(users.router)
app.include_router(items.router)
"""

class FastAPIDetector:
    def __init__(self, file_tree: list[str]):
        self.file_tree = file_tree

    def is_fastapi_service(self) -> bool:
        return "app/main.py" in self.file_tree and "app/routers/users.py" in self.file_tree

