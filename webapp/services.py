import os
import base64
from typing import Dict, Optional


class TokenService:
    def generate(self, length: int = 20) -> str:
        """Generate a pseudo-random token of the specified length."""
        if length < 0:
            raise ValueError("Token length must be non-negative.")

        string = base64.b64encode(os.urandom(64))[:length].decode('utf-8')
        return string


class UserRepository:
    def __init__(self):
        self._users: Dict[int, dict] = {}
        self._next_id: int = 1

    def create(self, name: str, email: str) -> dict:
        """Create a new user and return it."""
        user_id = self._next_id
        self._next_id += 1
        user = {"id": user_id, "name": name, "email": email}
        self._users[user_id] = user
        return user

    def get_by_id(self, user_id: int) -> Optional[dict]:
        """Get a user by ID, or None if not found."""
        return self._users.get(user_id)

    def list_all(self) -> list:
        """Return a list of all users."""
        return list(self._users.values())

    def update(self, user_id: int, name: Optional[str] = None, email: Optional[str] = None) -> Optional[dict]:
        """Update a user's name and/or email. Return None if user not found."""
        user = self._users.get(user_id)
        if not user:
            return None
        if name is not None:
            user["name"] = name
        if email is not None:
            user["email"] = email
        return user

    def delete(self, user_id: int) -> bool:
        """Delete a user by ID. Return True if successful, False if not found."""
        if user_id in self._users:
            del self._users[user_id]
            return True
        return False


# Global instances for dependency injection
_token_service = TokenService()
_user_repository = UserRepository()


def get_token_service() -> TokenService:
    """FastAPI dependency: provide token service."""
    return _token_service


def get_user_repository() -> UserRepository:
    """FastAPI dependency: provide user repository."""
    return _user_repository
