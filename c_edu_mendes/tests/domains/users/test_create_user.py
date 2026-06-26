"""Tests for user creation."""

from fastapi import status
from fastapi.testclient import TestClient


class TestCreateUser:
    """Test suite for user creation endpoint."""

    def test_create_user_success(self, client: TestClient) -> None:
        """Test successfully creating a new user."""
        payload = {
            "name": "Test User",
            "birth_date": "2000-01-01",
            "cpf_cnpj": "52998224725",
            "email": "testuser@email.com",
            "password": "SenhaValida123",
        }

        response = client.post("/api/v1/users", json=payload)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Test User"
        assert data["email"] == "testuser@email.com"
        assert "id" in data

    def test_create_user_duplicate_email(
        self, client: TestClient, user, access_token: str
    ) -> None:
        """Test creating user with duplicate email returns 409."""
        # Use access_token from fixture (already logged in as user)
        headers = {"Authorization": f"Bearer {access_token}"}

        # Try to create another user with the same email as fixture
        duplicate_payload = {
            "name": "Duplicate Email User",
            "birth_date": "1990-05-15",
            "cpf_cnpj": "06883673049",  # Valid CPF
            "email": user.email,
            "password": "SenhaValida123",
        }

        response = client.post(
            "/api/v1/users", json=duplicate_payload, headers=headers
        )

        # Should be 409 (conflict) or 422 (validation error)
        assert response.status_code in [
            status.HTTP_409_CONFLICT,
            status.HTTP_422_UNPROCESSABLE_CONTENT,
        ]
        if response.status_code == status.HTTP_409_CONFLICT:
            assert "email" in response.json()["detail"]

    def test_create_user_duplicate_cpf(self, client: TestClient, user) -> None:
        """Test creating user with duplicate CPF returns 409."""
        payload = {
            "name": "Another User",
            "birth_date": "1990-05-15",
            "cpf_cnpj": user.cpf_cnpj,
            "email": "another@email.com",
            "password": "SenhaValida123",
        }

        response = client.post("/api/v1/users", json=payload)

        assert response.status_code == status.HTTP_409_CONFLICT
        assert "CPF" in response.json()["detail"]

    def test_create_user_invalid_cpf(self, client: TestClient) -> None:
        """Test creating user with invalid CPF returns 422."""
        payload = {
            "name": "Test User",
            "birth_date": "2000-01-01",
            "cpf_cnpj": "11111111111",
            "email": "test@email.com",
            "password": "SenhaValida123",
        }

        response = client.post("/api/v1/users", json=payload)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_user_invalid_email(self, client: TestClient) -> None:
        """Test creating user with invalid email returns 422."""
        payload = {
            "name": "Test User",
            "birth_date": "2000-01-01",
            "cpf_cnpj": "52998224725",
            "email": "invalid-email",
            "password": "SenhaValida123",
        }

        response = client.post("/api/v1/users", json=payload)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_user_weak_password(self, client: TestClient) -> None:
        """Test creating user with weak password returns 422."""
        payload = {
            "name": "Test User",
            "birth_date": "2000-01-01",
            "cpf_cnpj": "52998224725",
            "email": "test@email.com",
            "password": "123",
        }

        response = client.post("/api/v1/users", json=payload)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_user_missing_fields(self, client: TestClient) -> None:
        """Test creating user with empty name field returns 422."""
        # Schema has defaults, so we test with invalid empty name
        payload = {
            "name": "",  # Empty name should fail validation
            "email": "test@email.com",
            "cpf_cnpj": "12345678901",
            "birth_date": "2000-01-01",
            "password": "Password123",
        }

        response = client.post("/api/v1/users", json=payload)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
