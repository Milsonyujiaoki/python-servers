from contextlib import contextmanager
from datetime import datetime
from typing import Generator, Iterator
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.app import app
from app.database import get_session
from app.models import User, table_registry


@pytest.fixture
def client(session) -> Generator[TestClient, None, None]:
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def session() -> Iterator[Session]:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)


@contextmanager
def _mock_db_time_id(
    model: type[User],
    time: datetime = datetime(2026, 6, 6),
    static_uuid: UUID | None = None,
) -> Generator[tuple[datetime, UUID | None], None, None]:

    if static_uuid is None:
        static_uuid = uuid4()

    def fake_time_id_hook(mapper, connection, target):
        atributos = ["created_at", "updated_at", "id"]
        if all(hasattr(target, attr) for attr in atributos):
            target.created_at = time
            target.updated_at = time
            target.id = static_uuid

    event.listen(model, "before_insert", fake_time_id_hook)
    yield time, static_uuid
    event.remove(model, "before_insert", fake_time_id_hook)


@pytest.fixture
def mock_db_time_id():
    return _mock_db_time_id


@pytest.fixture
def user(session: Session) -> User:
    db_user = User(
        username="test_user",
        email="user@example.com",
        cpf_cnpj="18219822821",
        password="SenhaValida123",
        birth_date=datetime.strptime("01/01/2000", "%d/%m/%Y").date(),
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
