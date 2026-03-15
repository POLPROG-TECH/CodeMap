"""Application entry point."""

from app.services import ProjectService, UserService


def main() -> None:
    user_svc = UserService()
    project_svc = ProjectService(user_svc)

    alice = user_svc.create_user("Alice", "alice@example.com", "secret")
    project_svc.create_project("CodeMap", alice.id)

    print(f"Created user: {alice}")


if __name__ == "__main__":
    main()
