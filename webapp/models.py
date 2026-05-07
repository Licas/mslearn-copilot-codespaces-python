from pydantic import BaseModel, Field
from typing import Optional


class User(BaseModel):
    """User model for responses."""
    id: int
    name: str
    email: str


class UserCreate(BaseModel):
    """User creation request model."""
    name: str
    email: str


class UserUpdate(BaseModel):
    """User update request model."""
    name: Optional[str] = None
    email: Optional[str] = None


class GenerateRequest(BaseModel):
    """Token generation request model."""

    length: int = Field(
        default=20,
        ge=0,
        le=88,
        description="Number of characters to return from the generated token.",
    )
