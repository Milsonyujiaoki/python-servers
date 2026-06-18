from contextlib import contextmanager
from dataclasses import asdict
from datetime import date, datetime
from typing import Generator, Iterator
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, func, select
from sqlalchemy.orm import Mapped, Session, mapped_column, registry

from app.models import User, table_registry
from app.app import app

@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def session() -> Iterator[Session]:
    engine = create_engine("sqlite:///:memory:")
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)


@contextmanager
def _mock_db_time_id(
    model: type[User],
    time: datetime = datetime(2026, 6, 6),
    static_uuid: UUID = uuid4()
) -> Generator[tuple[datetime, UUID], None, None]:
    def fake_time_id_hook(mapper, connection, target):
        atributos = ['created_at','updated_at','id']
        if all(hasattr(target,attr) for attr in atributos):
            target.created_at = time
            target.updated_at = time
            target.id = static_uuid
    event.listen(model, "before_insert", fake_time_id_hook)
    yield time, static_uuid
    event.remove(model, "before_insert", fake_time_id_hook)

@pytest.fixture
def mock_db_time_id():
    return _mock_db_time_id
