"""Shared utility functions."""

import hashlib
import re


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def validate_email(email: str) -> bool:
    pattern = r"^[\w.+-]+@[\w-]+\.[\w.]+$"
    if not re.match(pattern, email):
        raise ValueError(f"Invalid email: {email}")
    return True


def truncate(text: str, max_length: int = 100) -> str:
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."
