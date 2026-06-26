from fastapi import status
from fastapi.testclient import TestClient
from jwt import decode

from app.schemas import UserSchema
from app.security import create_access_token
from app.settings import ALGORITHM, SECRET_KEY


def test_jwt_token_creation() -> None:
    data = {"sub": "test_user"}
    token = create_access_token(data)
    decoded_data = decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert isinstance(token, str)
    assert decoded_data["sub"] == "test_user"
    assert "exp" in decoded_data


def test_jwt_invalid_token() -> None:
    invalid_token = "invalid.token.string"
    try:
        decode(invalid_token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception as e:
        assert isinstance(e, Exception)


def test_get_access_token(client: TestClient, user: UserSchema) -> None:
    response = client.post(
        "/auth/token",
        data={"username": user.email, "password": "SenhaValida123"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_get_access_token_invalid_credentials(client: TestClient) -> None:
    response = client.post(
        "/auth/token",
        data={"username": "invalid_user", "password": "invalid_password"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Credenciais inválidas."}
