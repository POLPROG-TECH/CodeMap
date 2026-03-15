"""Business logic services."""

from app.models import Project, User
from app.utils import hash_password, validate_email


class UserService:
    def __init__(self) -> None:
        self._users: dict[int, User] = {}

    def create_user(self, name: str, email: str, password: str) -> User:
        validate_email(email)
        _ = hash_password(password)
        user = User(id=len(self._users) + 1, name=name, email=email)
        self._users[user.id] = user
        return user

    def get_user(self, user_id: int) -> User | None:
        return self._users.get(user_id)


class ProjectService:
    def __init__(self, user_service: UserService) -> None:
        self._user_service = user_service
        self._projects: dict[int, Project] = {}

    def create_project(self, name: str, owner_id: int) -> Project:
        owner = self._user_service.get_user(owner_id)
        if owner is None:
            raise ValueError(f"User {owner_id} not found")
        project = Project(id=len(self._projects) + 1, name=name, owner_id=owner_id)
        self._projects[project.id] = project
        return project
