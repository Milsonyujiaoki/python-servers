"""Tests for user update and delete operations."""

from fastapi import status
from fastapi.testclient import TestClient


class TestUpdateUser:
    """Test suite for updating users."""

    def test_update_user_success(
        self, client: TestClient, user, access_token: str
    ) -> None:
        """Test successfully updating a user."""
        headers = {"Authorization": f"Bearer {access_token}"}
        payload = {
            "name": "Updated Name",
            "email": "updated@email.com",
            "cpf_cnpj": "17261704890",
            "password": "NewPassword123",
            "birth_date": "2000-01-01",
        }

        response = client.put(
            f"/api/v1/users/{user.id}", json=payload, headers=headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["email"] == "updated@email.com"

    def test_update_user_unauthorized(self, client: TestClient, user) -> None:
        """Test updating user without authentication returns 401."""
        payload = {
            "name": "Updated Name",
            "email": "updated@email.com",
            "cpf_cnpj": "17261704890",
            "password": "NewPassword123",
            "birth_date": "2000-01-01",
        }

        response = client.put(f"/api/v1/users/{user.id}", json=payload)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_user_forbidden(
        self, client: TestClient, user, access_token: str
    ) -> None:
        """Test updating another user's data returns 403."""
        from uuid import uuid4

        headers = {"Authorization": f"Bearer {access_token}"}
        payload = {
            "name": "Updated Name",
            "email": "updated@email.com",
            "cpf_cnpj": "17261704890",
            "password": "NewPassword123",
            "birth_date": "2000-01-01",
        }

        other_id = uuid4()
        response = client.put(
            f"/api/v1/users/{other_id}", json=payload, headers=headers
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_user_duplicate_email(
        self, client: TestClient, user, access_token: str
    ) -> None:
        """Test updating user to existing email returns 409."""
        # Get current user data
        headers = {"Authorization": f"Bearer {access_token}"}

        # First create another valid user using a valid CPF and 12+ char password
        other_response = client.post(
            "/api/v1/users",
            json={
                "name": "Other User",
                "email": "other@test.com",
                "cpf_cnpj": "52998224725",  # Valid CPF used in other tests
                "password": "Password1234",  # 12+ characters
                "birth_date": "2000-01-01",
            },
        )
        assert other_response.status_code == status.HTTP_201_CREATED, (
            f"Failed to create other user: {other_response.json()}"
        )

        # Now try to update our user to have the same email as the other user
        payload = {
            "name": "Updated Name",
            "email": "other@test.com",  # Try to use other user's email
            "cpf_cnpj": "17261704890",
            "password": "NewPassword123",
            "birth_date": "2000-01-01",
        }

        response = client.put(
            f"/api/v1/users/{user.id}", json=payload, headers=headers
        )

        assert response.status_code == status.HTTP_409_CONFLICT


class TestDeleteUser:
    """Test suite for deleting users."""

    def test_delete_user_success(
        self, client: TestClient, user, access_token: str
    ) -> None:
        """Test successfully deleting a user."""
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.delete(f"/api/v1/users/{user.id}", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "User deleted with success"

    def test_delete_user_unauthorized(self, client: TestClient, user) -> None:
        """Test deleting user without authentication returns 401."""
        response = client.delete(f"/api/v1/users/{user.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_user_forbidden(
        self, client: TestClient, user, access_token: str
    ) -> None:
        """Test deleting another user's data returns 403."""
        from uuid import uuid4

        headers = {"Authorization": f"Bearer {access_token}"}

        other_id = uuid4()
        response = client.delete(f"/api/v1/users/{other_id}", headers=headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN
