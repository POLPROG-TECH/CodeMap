"""Data models for the application."""

from dataclasses import dataclass


@dataclass
class User:
    id: int
    name: str
    email: str
    role: str = "viewer"

    def is_admin(self) -> bool:
        return self.role == "admin"


@dataclass
class Project:
    id: int
    name: str
    owner_id: int
    description: str = ""
