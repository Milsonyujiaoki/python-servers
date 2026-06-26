from contextlib import contextmanager
from datetime import datetime
from typing import AsyncGenerator, Generator
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from app.app import app
from app.database import get_session
from app.models import User, table_registry
from app.security import get_hashed_password


@pytest.fixture
async def session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.close()

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
def client(session: AsyncSession) -> Generator[TestClient, None, None]:

    def get_session_override():
        return session

    async def get_session_async_override():
        yield session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_async_override
        yield client
    app.dependency_overrides.clear()


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

    from sqlalchemy import event

    event.listen(model, "before_insert", fake_time_id_hook)
    yield time, static_uuid
    event.remove(model, "before_insert", fake_time_id_hook)


@pytest.fixture
def mock_db_time_id():
    return _mock_db_time_id


@pytest.fixture
async def user(session: AsyncSession) -> User:
    password = "SenhaValida123"
    # Username is normalized by schema validator (title case)
    db_user = User(
        username="Test_User",
        email="user@example.com",
        cpf_cnpj="18219822821",
        password=get_hashed_password(password),
        birth_date=datetime.strptime("01/01/2000", "%d/%m/%Y").date(),
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    db_user.cleaned_password = password
    return db_user


@pytest.fixture
async def access_token(client: TestClient, user: User) -> str:
    response = client.post(
        "/api/v1/auth/token",
        data={"username": user.email, "password": user.cleaned_password},
    )
    assert response.status_code == 200
    return response.json()["access_token"]
