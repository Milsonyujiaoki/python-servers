"""Tests for user read operations."""

from fastapi import status
from fastapi.testclient import TestClient


class TestReadUser:
    """Test suite for reading user data."""

    def test_get_user_success(
        self, client: TestClient, user, access_token: str
    ) -> None:
        """Test successfully retrieving a user by ID."""
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get(f"/api/v1/users/{user.id}", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(user.id)
        assert data["name"] == user.username
        assert data["email"] == user.email

    def test_get_user_not_found(
        self, client: TestClient, access_token: str
    ) -> None:
        """Test retrieving non-existent user returns 404."""
        from uuid import uuid4

        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get(f"/api/v1/users/{uuid4()}", headers=headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Usuário não encontrado."

    def test_get_all_users_success(
        self, client: TestClient, access_token: str
    ) -> None:
        """Test successfully retrieving all users."""
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/api/v1/users", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "users" in data
        assert isinstance(data["users"], list)

    def test_get_all_users_pagination(
        self, client: TestClient, access_token: str
    ) -> None:
        """Test user list with pagination parameters."""
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get(
            "/api/v1/users?limit=10&offset=0", headers=headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "users" in data
        assert len(data["users"]) <= 10

    def test_get_all_users_unauthorized(self, client: TestClient) -> None:
        """Test retrieving users without authentication returns 401."""
        response = client.get("/api/v1/users")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
