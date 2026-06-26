"""Tests for authentication and token operations."""

from fastapi import status
from fastapi.testclient import TestClient
from jwt import decode

from app.settings import ALGORITHM, SECRET_KEY


class TestTokenCreation:
    """Test suite for JWT token creation."""

    def test_jwt_token_creation(self) -> None:
        """Test successfully creating a JWT token."""
        from app.security import create_access_token

        data = {"sub": "test_user"}
        token = create_access_token(data)

        assert isinstance(token, str)
        decoded = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == "test_user"
        assert "exp" in decoded

    def test_token_expiration(self) -> None:
        """Test that token has expiration claim."""
        from datetime import datetime, timedelta, timezone

        from app.security import create_access_token

        data = {"sub": "test_user"}
        token = create_access_token(data)
        decoded = decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        assert "exp" in decoded
        # Token should expire in the future (default 30 minutes from now)
        now = int(datetime.now(timezone.utc).timestamp())
        assert decoded["exp"] > now
        # And should be less than 1 hour from now (default is 30 min)
        assert decoded["exp"] < now + int(timedelta(hours=1).total_seconds())


class TestLogin:
    """Test suite for user login."""

    def test_login_success(self, client: TestClient, user) -> None:
        """Test successfully logging in and receiving access token."""
        response = client.post(
            "/api/v1/auth/token",
            data={"username": user.email, "password": user.cleaned_password},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client: TestClient) -> None:
        """Test login with invalid credentials returns 401."""
        response = client.post(
            "/api/v1/auth/token",
            data={
                "username": "nonexistent@email.com",
                "password": "wrongpassword",
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Credenciais inválidas."

    def test_login_wrong_password(self, client: TestClient, user) -> None:
        """Test login with wrong password returns 401."""
        response = client.post(
            "/api/v1/auth/token",
            data={"username": user.email, "password": "wrongpassword123"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Credenciais inválidas."

    def test_login_nonexistent_user(self, client: TestClient) -> None:
        """Test login with non-existent user returns 401."""
        response = client.post(
            "/api/v1/auth/token",
            data={
                "username": "doesnotexist@email.com",
                "password": "Password123",
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_missing_credentials(self, client: TestClient) -> None:
        """Test login with missing credentials returns 422."""
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "test@email.com"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestTokenValidation:
    """Test suite for JWT token validation."""

    def test_invalid_token_format(self, client: TestClient) -> None:
        """Test accessing protected endpoint with invalid token format."""
        headers = {"Authorization": "Bearer invalid.token.here"}

        response = client.get("/api/v1/users", headers=headers)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_missing_token(self, client: TestClient) -> None:
        """Test accessing protected endpoint without token."""
        response = client.get("/api/v1/users")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_expired_token(self, client: TestClient, user) -> None:
        """Test using expired token."""
        from datetime import datetime, timedelta

        from jwt import encode

        # Create expired token
        expired_payload = {
            "sub": user.email,
            "exp": datetime.utcnow() - timedelta(minutes=5),
        }
        expired_token = encode(
            expired_payload, SECRET_KEY, algorithm=ALGORITHM
        )

        headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.get("/api/v1/users", headers=headers)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "expirado" in response.json()["detail"]
