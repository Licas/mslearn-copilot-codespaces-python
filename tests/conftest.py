import pytest
from fastapi.testclient import TestClient
from webapp.main import app
from webapp.services import UserRepository, get_user_repository


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Reset the shared rate limiter around each test."""
    limiter = app.state.rate_limiter
    original_max_requests = limiter.max_requests
    limiter.reset()
    yield
    limiter.reset()
    limiter.max_requests = original_max_requests


@pytest.fixture
def client():
    """Provide a TestClient for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def fresh_user_repo():
    """Provide a fresh UserRepository instance for isolation."""
    repo = UserRepository()
    
    # Override the dependency
    def get_repo_override():
        return repo
    
    app.dependency_overrides[get_user_repository] = get_repo_override
    yield repo
    app.dependency_overrides.clear()
