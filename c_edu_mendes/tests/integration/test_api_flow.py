"""Integration tests for the complete API flow."""

from fastapi import status
from fastapi.testclient import TestClient


class TestUserFlow:
    """Test complete user lifecycle flow."""

    def test_full_user_crud_flow(self, client: TestClient) -> None:
        """Test complete CRUD flow for a user."""
        # 1. Create user - use valid CPF
        create_payload = {
            "name": "Full Flow User",
            "birth_date": "1995-06-15",
            "cpf_cnpj": "52998224725",  # Valid CPF
            "email": "fullflow@test.com",
            "password": "Password12345",  # 12+ chars with uppercase and digit
        }
        create_response = client.post("/api/v1/users", json=create_payload)
        assert create_response.status_code == status.HTTP_201_CREATED
        user_data = create_response.json()
        user_id = user_data["id"]

        # 2. Read user
        read_response = client.get(f"/api/v1/users/{user_id}")
        assert read_response.status_code == status.HTTP_200_OK
        assert read_response.json()["email"] == "fullflow@test.com"

        # 3. Get token for update
        token_response = client.post(
            "/api/v1/auth/token",
            data={
                "username": "fullflow@test.com",
                "password": "Password12345",
            },
        )
        assert token_response.status_code == status.HTTP_200_OK
        token = token_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 4. Update user - use same CPF (it's the user's own CPF)
        update_payload = {
            "name": "Updated Full Flow User",
            "birth_date": "1995-06-15",
            "cpf_cnpj": "52998224725",  # Same CPF - user updating their own data
            "email": "updated.fullflow@test.com",
            "password": "NewPassword45678",  # 12+ chars with uppercase and digit
        }
        update_response = client.put(
            f"/api/v1/users/{user_id}", json=update_payload, headers=headers
        )
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.json()["name"] == "Updated Full Flow User"

        # 4b. Get new token with updated email (email changed, so need new token)
        token_response = client.post(
            "/api/v1/auth/token",
            data={
                "username": "updated.fullflow@test.com",
                "password": "NewPassword45678",
            },
        )
        assert token_response.status_code == status.HTTP_200_OK
        token = token_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 5. Delete user
        delete_response = client.delete(
            f"/api/v1/users/{user_id}", headers=headers
        )
        assert delete_response.status_code == status.HTTP_200_OK

        # 6. Verify deletion
        verify_response = client.get(f"/api/v1/users/{user_id}")
        assert verify_response.status_code == status.HTTP_404_NOT_FOUND


class TestAuthenticationFlow:
    """Test authentication and authorization flows."""

    def test_protected_endpoint_requires_auth(
        self, client: TestClient
    ) -> None:
        """Test that protected endpoints return 401 without token."""
        response = client.get("/api/v1/users")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_invalid_token_rejected(self, client: TestClient) -> None:
        """Test that invalid tokens are rejected."""
        headers = {"Authorization": "Bearer invalid_token_here"}
        response = client.get("/api/v1/users", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_full_auth_flow(self, client: TestClient) -> None:
        """Test complete authentication flow."""
        # Create user
        client.post(
            "/api/v1/users",
            json={
                "name": "Auth Flow User",
                "birth_date": "1990-01-01",
                "cpf_cnpj": "98765432100",
                "email": "authflow@test.com",
                "password": "SecurePass789",
            },
        )

        # Login
        login_response = client.post(
            "/api/v1/auth/token",
            data={
                "username": "authflow@test.com",
                "password": "SecurePass789",
            },
        )
        assert login_response.status_code == status.HTTP_200_OK
        token = login_response.json()["access_token"]

        # Access protected endpoint
        headers = {"Authorization": f"Bearer {token}"}
        users_response = client.get("/api/v1/users", headers=headers)
        assert users_response.status_code == status.HTTP_200_OK


class TestAPIEndpoints:
    """Test all API endpoints are accessible."""

    def test_root_endpoint(self, client: TestClient) -> None:
        """Test root endpoint returns expected response."""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "Olá Mundo!"}

    def test_health_indicators(self, client: TestClient) -> None:
        """Test various endpoints that indicate API health."""
        # Root
        assert client.get("/").status_code == status.HTTP_200_OK

        # Docs should be accessible
        docs_response = client.get("/docs")
        assert docs_response.status_code == status.HTTP_200_OK

        # OpenAPI schema
        openapi_response = client.get("/openapi.json")
        assert openapi_response.status_code == status.HTTP_200_OK
        assert "openapi" in openapi_response.json()
