import random
import string
from datetime import datetime

import pytest
from fastapi import Depends, status
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.app import app
from app.database import get_session
from app.models import User
from app.schemas import UserPublic, UserSchema
from app.security import (
    get_hashed_password,
)


def generate_default_password() -> str:
    return str(
        random.choice(string.ascii_uppercase)  # noqa: S311
        + str(random.randint(10000000, 99999999))  # noqa: S311
    )


def test_landing() -> None:
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Olá Mundo!"}


@pytest.mark.asyncio
async def test_create_user(session, mock_db_time_id) -> None:
    data_esperada = datetime.strptime("28/08/2000", "%d/%m/%Y").date()
    senha_test = generate_default_password()
    with mock_db_time_id(model=User) as (time, static_uuid):
        new_user = User(
            username="test",
            email="teste@test.com",
            cpf_cnpj="test",
            password=senha_test,
            birth_date=data_esperada,
        )
        session.add(new_user)
        await session.commit()

        user_found = await session.scalar(
            select(User).where(User.username == "test")
        )
        await session.refresh(user_found)

    assert user_found is not None
    assert user_found.id == static_uuid
    assert user_found.username == "test"
    assert user_found.email == "teste@test.com"
    assert user_found.cpf_cnpj == "test"
    assert user_found.password == senha_test
    assert user_found.birth_date == data_esperada
    assert user_found.created_at == time
    assert user_found.updated_at == time


@pytest.mark.asyncio
async def test_create_user_existing_username(
    client: TestClient, user: UserSchema, access_token: str
) -> None:
    """Test that API properly validates duplicate usernames."""
    # Try to create a user with existing username via API
    response = client.post(
        "/api/v1/users",
        json={
            "name": "test_user",  # Same username as fixture 'user'
            "email": "new_email@test.com",
            "cpf_cnpj": "52998224725",  # Valid CPF (different from fixture)
            "password": "SenhaValida123",
            "birth_date": "2000-01-01",
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )

    # API should return 409 Conflict, not raise IntegrityError
    assert response.status_code == status.HTTP_409_CONFLICT
    assert "nome" in response.json()["detail"].lower()


def test_read_users(client: TestClient, access_token: str) -> None:
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/api/v1/users", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), dict)
    assert "users" in response.json()


def test_read_users_with_users(
    client: TestClient, user: UserSchema, access_token: str
) -> None:
    headers = {"Authorization": f"Bearer {access_token}"}
    user_schema = UserPublic.model_validate(user).model_dump(mode="json")
    response = client.get("/api/v1/users", headers=headers)

    assert response.status_code == status.HTTP_200_OK

    assert response.json() == {"users": [user_schema]}


def test_update_user(
    client: TestClient,
    user: UserSchema,
    access_token: str,
    session: Session = Depends(get_session),
) -> None:
    headers = {"Authorization": f"Bearer {access_token}"}
    payload = {
        "name": "Updated Name",
        "email": "updated@test.com",
        "cpf_cnpj": "17261704890",
        "password": get_hashed_password("UpdatedPassword123"),
        "birth_date": "2000-01-01",
    }
    response = client.put(
        f"/api/v1/users/{user.id}", json=payload, headers=headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": str(user.id),
        "name": "Updated Name",
        "email": "updated@test.com",
    }


def test_put_integrity_error(
    client: TestClient,
    user: UserSchema,
    access_token: str,
) -> None:
    headers = {"Authorization": f"Bearer {access_token}"}
    client.post(
        "/api/v1/users",
        json={
            "name": "Existing User",
            "email": "existing_email@test.com",
            "cpf_cnpj": "44233494859",
            "password": get_hashed_password("SenhaValida123"),
            "birth_date": "2000-01-01",
        },
    )

    payload = {
        "name": "Updated Name",
        "email": "existing_email@test.com",
        "cpf_cnpj": "44233494859",
        "password": get_hashed_password("SenhaValida123"),
        "birth_date": "2000-01-01",
    }
    response = client.put(
        f"/api/v1/users/{user.id}", json=payload, headers=headers
    )
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {
        "detail": "name, email or cpf_cnpj already exists"
    }


def test_delete_user_success(
    client: TestClient,
    user: UserPublic,
    access_token: str,
) -> None:
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.delete(f"/api/v1/users/{user.id}", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "User deleted with success"}
