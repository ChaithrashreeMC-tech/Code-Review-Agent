# TC-015: Clean Architecture Safe Implementation

from abc import ABC, abstractmethod

class IUserRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id: str):
        pass

class UserService:
    def __init__(self, user_repo: IUserRepository):
        self._user_repo = user_repo

    def get_user_summary(self, user_id: str):
        user = self._user_repo.get_by_id(user_id)
        if not user:
            return None
        return {"id": user["id"], "name": user["name"].title()}

