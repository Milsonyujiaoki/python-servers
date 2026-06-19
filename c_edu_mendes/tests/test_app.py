import random
import string
from dataclasses import asdict
from datetime import datetime

from fastapi import status
from fastapi.testclient import TestClient

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.app import app
from app.models import User
from app.schemas import UserPublic, UserSchema, UserList

def generate_default_password() -> str:
    return str(
        random.choice(string.ascii_uppercase)  # noqa: S311
        + str(random.randint(10000000, 99999999))  # noqa: S311
    )


def test_landing()-> None:
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Olá Mundo!"}


def test_create_user(session: Session, mock_db_time_id) -> None:
    data_esperada = datetime.strptime("28/08/2000", "%d/%m/%Y").date()
    senha_test = generate_default_password()
    with mock_db_time_id(model=User) as (time, static_uuid):
        new_user = User(
            username="test",
            cpf_cnpj="test",
            email="teste@test.com",
            password=senha_test,
            birth_date=data_esperada,
        )
        # breakpoint()
        session.add(new_user)
        session.commit()

        user = session.scalar(select(User).where(User.username == "test"))
        session.refresh(user)

    assert asdict(user) == {
        "id": static_uuid,
        "username": "test",
        "cpf_cnpj": "test",
        "email": "teste@test.com",
        "password": senha_test,
        "birth_date": data_esperada,
        "created_at": time,
        "updated_at": time,
    }

def test_read_users(client: TestClient) -> None:
    response = client.get("/users")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), dict)
    assert "users" in response.json()

def test_read_users_with_users(client: TestClient, user: UserSchema) -> None:
    user_schema = UserPublic.model_validate(user).model_dump(mode="json")
    response = client.get("/users")

    assert response.status_code == status.HTTP_200_OK

    assert response.json() == {"users": [user_schema]}

def test_put_user(client: TestClient, user: UserSchema) -> None:
    payload = {
        "name": "Updated Name",
        "email": "updated@test.com",
        "cpf_cnpj": "18219822821",
        "password": "UpdatedPassword123",
        "birth_date": "2000-08-28"
    }
    response = client.put(f"/users/{user.id}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": str(user.id),
        "name": "Updated Name",
        "email": "updated@test.com"
    }


def test_delete_user_success(client: TestClient, user: UserSchema) -> None:

    user_id = str(user.id)

    response = client.delete(f"/users/{user_id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "User deleted with success"}

