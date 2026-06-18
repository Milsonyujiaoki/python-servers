from datetime import datetime
from sqlalchemy import select
from dataclasses import asdict
from app.models import User
from tests.conftest import mock_db_time_id
from app.schemas import UserPublic, UserDB


def test_create_user(session, mock_db_time_id) -> None:
    data_esperada = datetime.strptime("28/08/2000", "%d/%m/%Y").date()
    with mock_db_time_id(model=User) as (time, static_uuid):
        new_user = User(
            username="test",
            cpf_cnpj="test",
            email="teste@test.com",
            password="senhateste",
            birth_date=data_esperada,
        )
        # breakpoint() 
        session.add(new_user)
        session.commit()

        user = session.scalar(select(User).where(User.username == "test"))

    assert asdict(user) == {
        'id':static_uuid,
        "username": "test",
        'cpf_cnpj':"test",
        'email':"teste@test.com",
        'password':"senhateste",
        'birth_date':data_esperada,
        'created_at': time,
        'updated_at': time,
    }
