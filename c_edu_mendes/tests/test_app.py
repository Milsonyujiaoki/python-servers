import random
import string
from dataclasses import asdict
from datetime import datetime
from http import HTTPStatus

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.app import app
from app.models import User


def generate_default_password() -> str:
    return str(
        random.choice(string.ascii_uppercase)  # noqa: S311
        + str(random.randint(10000000, 99999999))  # noqa: S311
    )


def test_landing():
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Olá Mundo!"}


def test_create_user(session, mock_db_time_id) -> None:
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
