"""Tests for the example Python application."""

from app.models import User


def test_user_is_admin():
    user = User(id=1, name="Admin", email="a@b.com", role="admin")
    assert user.is_admin()
