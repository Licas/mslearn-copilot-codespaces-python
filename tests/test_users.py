import pytest
from fastapi.testclient import TestClient
from webapp.main import app
from webapp.services import get_user_repository, UserRepository


class TestUserCRUD:
    def test_create_user(self, client, fresh_user_repo):
        """Test creating a user."""
        response = client.post(
            '/users',
            json={'name': 'Alice', 'email': 'alice@example.com'}
        )
        assert response.status_code == 201
        data = response.json()
        assert data['name'] == 'Alice'
        assert data['email'] == 'alice@example.com'
        assert data['id'] == 1

    def test_list_users(self, client, fresh_user_repo):
        """Test listing users."""
        # Create a couple of users
        client.post('/users', json={'name': 'Alice', 'email': 'alice@example.com'})
        client.post('/users', json={'name': 'Bob', 'email': 'bob@example.com'})
        
        response = client.get('/users')
        assert response.status_code == 200
        users = response.json()
        assert len(users) == 2
        assert users[0]['name'] == 'Alice'
        assert users[1]['name'] == 'Bob'

    def test_list_users_empty(self, client, fresh_user_repo):
        """Test listing users when none exist."""
        response = client.get('/users')
        assert response.status_code == 200
        assert response.json() == []

    def test_get_user(self, client, fresh_user_repo):
        """Test getting a single user."""
        # Create a user
        create_response = client.post(
            '/users',
            json={'name': 'Alice', 'email': 'alice@example.com'}
        )
        user_id = create_response.json()['id']
        
        response = client.get(f'/users/{user_id}')
        assert response.status_code == 200
        data = response.json()
        assert data['id'] == user_id
        assert data['name'] == 'Alice'

    def test_get_user_not_found(self, client, fresh_user_repo):
        """Test getting a non-existent user."""
        response = client.get('/users/999')
        assert response.status_code == 404
        assert 'User not found' in response.json()['detail']

    def test_update_user(self, client, fresh_user_repo):
        """Test updating a user."""
        # Create a user
        create_response = client.post(
            '/users',
            json={'name': 'Alice', 'email': 'alice@example.com'}
        )
        user_id = create_response.json()['id']
        
        # Update the user
        response = client.put(
            f'/users/{user_id}',
            json={'name': 'Alice Updated', 'email': 'alice.new@example.com'}
        )
        assert response.status_code == 200
        data = response.json()
        assert data['name'] == 'Alice Updated'
        assert data['email'] == 'alice.new@example.com'

    def test_update_user_partial(self, client, fresh_user_repo):
        """Test updating a user with only some fields."""
        # Create a user
        create_response = client.post(
            '/users',
            json={'name': 'Alice', 'email': 'alice@example.com'}
        )
        user_id = create_response.json()['id']
        
        # Update only name
        response = client.put(
            f'/users/{user_id}',
            json={'name': 'Alice Updated'}
        )
        assert response.status_code == 200
        data = response.json()
        assert data['name'] == 'Alice Updated'
        assert data['email'] == 'alice@example.com'  # unchanged

    def test_update_user_not_found(self, client, fresh_user_repo):
        """Test updating a non-existent user."""
        response = client.put(
            '/users/999',
            json={'name': 'Non-existent'}
        )
        assert response.status_code == 404

    def test_delete_user(self, client, fresh_user_repo):
        """Test deleting a user."""
        # Create a user
        create_response = client.post(
            '/users',
            json={'name': 'Alice', 'email': 'alice@example.com'}
        )
        user_id = create_response.json()['id']
        
        # Delete the user
        response = client.delete(f'/users/{user_id}')
        assert response.status_code == 204
        
        # Verify it's gone
        get_response = client.get(f'/users/{user_id}')
        assert get_response.status_code == 404

    def test_delete_user_not_found(self, client, fresh_user_repo):
        """Test deleting a non-existent user."""
        response = client.delete('/users/999')
        assert response.status_code == 404


class TestGenerateEndpoint:
    def test_generate_token_default_length(self, client):
        """Test /generate endpoint with default length."""
        response = client.post('/generate', json={})
        assert response.status_code == 200
        data = response.json()
        assert 'token' in data
        assert len(data['token']) == 20

    def test_generate_token_custom_length(self, client):
        """Test /generate endpoint with custom length."""
        response = client.post('/generate', json={'length': 30})
        assert response.status_code == 200
        data = response.json()
        assert len(data['token']) == 30

    def test_generate_token_rejects_negative_length(self, client):
        """Test /generate endpoint rejects invalid lengths."""
        response = client.post('/generate', json={'length': -1})
        assert response.status_code == 422

    def test_generate_token_uses_service(self, client, mocker):
        """Test that /generate endpoint uses the TokenService (using pytest-mock)."""
        from webapp.services import get_token_service
        
        mock_service = mocker.patch.object(
            get_token_service(),
            'generate',
            return_value='mocked_token_value'
        )
        
        response = client.post('/generate', json={'length': 10})
        assert response.status_code == 200
        data = response.json()
        assert data['token'] == 'mocked_token_value'

    def test_rate_limit_blocks_excess_requests(self, client):
        """Test that the middleware returns HTTP 429 after the limit."""
        limiter = app.state.rate_limiter
        original_max_requests = limiter.max_requests
        limiter.max_requests = 2

        try:
            assert client.get('/ping').status_code == 200
            assert client.get('/ping').status_code == 200

            response = client.get('/ping')
            assert response.status_code == 429
            assert response.json()['detail'] == 'Rate limit exceeded. Try again later.'
            assert 'Retry-After' in response.headers
        finally:
            limiter.max_requests = original_max_requests
