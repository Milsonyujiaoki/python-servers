"""Load tests for SQLite (aiosqlite) database operations.

Testa diferentes faixas de operações:
- Baixa carga: 10-50 operações
- Média carga: 100-500 operações
- Alta carga: 1000+ operações
- Concorrência: múltiplas requisições simultâneas
"""

import asyncio
import time
from datetime import datetime
from uuid import uuid4

import pytest
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from app.models import User, table_registry

# Pre-computed password hash for load tests (avoid repeated expensive hashing)
TEST_PASSWORD_HASH = "$argon2id$v=19$m=65536,t=3,p=4$TestDataSalt123456$TestHashValueForLoadTests123456789"


class TestSqliteLoad:
    """Load test suite for SQLite asynchronous operations."""

    @pytest.fixture(scope="function")
    async def sqlite_engine(self):
        """Create SQLite async engine for tests."""
        engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        async with engine.begin() as conn:
            await conn.run_sync(table_registry.metadata.create_all)
        yield engine
        async with engine.begin() as conn:
            await conn.run_sync(table_registry.metadata.drop_all)
        await engine.dispose()

    @pytest.fixture(scope="function")
    async def sqlite_session_factory(self, sqlite_engine):
        """Create async session factory."""
        return async_sessionmaker(
            sqlite_engine, class_=AsyncSession, expire_on_commit=False
        )

    # ========================================================================
    # BAIXA CARGA (10-50 operações)
    # ========================================================================

    @pytest.mark.asyncio
    async def test_sqlite_insert_low_load_10(self, sqlite_session_factory):
        """Test inserting 10 users - baixa carga."""
        session_maker = sqlite_session_factory
        start = time.perf_counter()

        async with session_maker() as session:
            for i in range(10):
                user = User(
                    username=f"user_low_{i}_{uuid4()}",
                    email=f"user_low{i}@test.com",
                    cpf_cnpj=f"{i:011d}",
                    password=TEST_PASSWORD_HASH,
                    birth_date=datetime(2000, 1, 1).date(),
                )
                session.add(user)
            await session.commit()

        elapsed = time.perf_counter() - start
        print(
            f"\n[BAIXA] SQLite: 10 inserts em {elapsed:.4f}s ({10 / elapsed:.2f} ops/sec)"
        )
        assert elapsed < 2.0

    @pytest.mark.asyncio
    async def test_sqlite_insert_low_load_50(self, sqlite_session_factory):
        """Test inserting 50 users - baixa carga."""
        session_maker = sqlite_session_factory
        start = time.perf_counter()

        async with session_maker() as session:
            for i in range(50):
                user = User(
                    username=f"user_low_{i}_{uuid4()}",
                    email=f"user_low{i}@test.com",
                    cpf_cnpj=f"{i:011d}",
                    password=TEST_PASSWORD_HASH,
                    birth_date=datetime(2000, 1, 1).date(),
                )
                session.add(user)
            await session.commit()

        elapsed = time.perf_counter() - start
        print(
            f"\n[BAIXA] SQLite: 50 inserts em {elapsed:.4f}s ({50 / elapsed:.2f} ops/sec)"
        )
        assert elapsed < 5.0

    @pytest.mark.asyncio
    async def test_sqlite_read_low_load_50(self, sqlite_session_factory):
        """Test reading 50 users - baixa carga."""
        session_maker = sqlite_session_factory

        # Insert data first
        async with session_maker() as session:
            for i in range(50):
                user = User(
                    username=f"read_low_{i}_{uuid4()}",
                    email=f"read_low{i}@test.com",
                    cpf_cnpj=f"{i:011d}",
                    password=TEST_PASSWORD_HASH,
                    birth_date=datetime(2000, 1, 1).date(),
                )
                session.add(user)
            await session.commit()

        # Measure read time
        start = time.perf_counter()

        async with session_maker() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()

        elapsed = time.perf_counter() - start
        print(f"\n[BAIXA] SQLite: Leitura de 50 users em {elapsed:.4f}s")
        assert len(users) >= 50
        assert elapsed < 1.0

    # ========================================================================
    # MÉDIA CARGA (100-500 operações)
    # ========================================================================

    @pytest.mark.asyncio
    async def test_sqlite_insert_medium_load_100(self, sqlite_session_factory):
        """Test inserting 100 users - média carga."""
        session_maker = sqlite_session_factory
        start = time.perf_counter()

        async with session_maker() as session:
            for i in range(100):
                user = User(
                    username=f"user_med_{i}_{uuid4()}",
                    email=f"user_med{i}@test.com",
                    cpf_cnpj=f"{i:011d}",
                    password=TEST_PASSWORD_HASH,
                    birth_date=datetime(2000, 1, 1).date(),
                )
                session.add(user)
            await session.commit()

        elapsed = time.perf_counter() - start
        print(
            f"\n[MÉDIA] SQLite: 100 inserts em {elapsed:.4f}s ({100 / elapsed:.2f} ops/sec)"
        )
        assert elapsed < 5.0

    @pytest.mark.asyncio
    async def test_sqlite_insert_medium_load_500(self, sqlite_session_factory):
        """Test inserting 500 users - média carga."""
        session_maker = sqlite_session_factory
        start = time.perf_counter()

        async with session_maker() as session:
            for i in range(500):
                user = User(
                    username=f"user_med_{i}_{uuid4()}",
                    email=f"user_med{i}@test.com",
                    cpf_cnpj=f"{i:011d}",
                    password=TEST_PASSWORD_HASH,
                    birth_date=datetime(2000, 1, 1).date(),
                )
                session.add(user)
            await session.commit()

        elapsed = time.perf_counter() - start
        print(
            f"\n[MÉDIA] SQLite: 500 inserts em {elapsed:.4f}s ({500 / elapsed:.2f} ops/sec)"
        )
        assert elapsed < 15.0

    @pytest.mark.asyncio
    async def test_sqlite_read_medium_load_500(self, sqlite_session_factory):
        """Test reading 500 users - média carga."""
        session_maker = sqlite_session_factory

        # Insert data first
        async with session_maker() as session:
            for i in range(500):
                user = User(
                    username=f"read_med_{i}_{uuid4()}",
                    email=f"read_med{i}@test.com",
                    cpf_cnpj=f"{i:011d}",
                    password=TEST_PASSWORD_HASH,
                    birth_date=datetime(2000, 1, 1).date(),
                )
                session.add(user)
            await session.commit()

        # Measure read time
        start = time.perf_counter()

        async with session_maker() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()

        elapsed = time.perf_counter() - start
        print(
            f"\n[MÉDIA] SQLite: Leitura de 500 users em {elapsed:.4f}s ({500 / elapsed:.2f} ops/sec)"
        )
        assert len(users) >= 500
        assert elapsed < 5.0

    @pytest.mark.asyncio
    async def test_sqlite_update_medium_load_200(self, sqlite_session_factory):
        """Test updating 200 users - média carga."""
        session_maker = sqlite_session_factory

        # Insert test data
        async with session_maker() as session:
            for i in range(200):
                user = User(
                    username=f"upd_med_{i}_{uuid4()}",
                    email=f"upd_med{i}@test.com",
                    cpf_cnpj=f"{i:011d}",
                    password=TEST_PASSWORD_HASH,
                    birth_date=datetime(2000, 1, 1).date(),
                )
                session.add(user)
            await session.commit()

        # Measure update time
        start = time.perf_counter()

        async with session_maker() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()
            for user in users:
                user.username = f"updated_{user.username}"
            await session.commit()

        elapsed = time.perf_counter() - start
        print(f"\n[MÉDIA] SQLite: Update de 200 users em {elapsed:.4f}s")
        assert elapsed < 5.0

    # ========================================================================
    # ALTA CARGA (1000+ operações)
    # ========================================================================

    @pytest.mark.asyncio
    async def test_sqlite_insert_high_load_1000(self, sqlite_session_factory):
        """Test inserting 1000 users - alta carga."""
        session_maker = sqlite_session_factory
        start = time.perf_counter()

        async with session_maker() as session:
            for i in range(1000):
                user = User(
                    username=f"user_high_{i}_{uuid4()}",
                    email=f"user_high{i}@test.com",
                    cpf_cnpj=f"{i:011d}",
                    password=TEST_PASSWORD_HASH,
                    birth_date=datetime(2000, 1, 1).date(),
                )
                session.add(user)
            await session.commit()

        elapsed = time.perf_counter() - start
        print(
            f"\n[ALTA] SQLite: 1000 inserts em {elapsed:.4f}s ({1000 / elapsed:.2f} ops/sec)"
        )
        assert elapsed < 30.0

    @pytest.mark.asyncio
    async def test_sqlite_insert_high_load_2000(self, sqlite_session_factory):
        """Test inserting 2000 users - alta carga extrema."""
        session_maker = sqlite_session_factory
        start = time.perf_counter()

        async with session_maker() as session:
            for i in range(2000):
                user = User(
                    username=f"user_high_{i}_{uuid4()}",
                    email=f"user_high{i}@test.com",
                    cpf_cnpj=f"{i:011d}",
                    password=TEST_PASSWORD_HASH,
                    birth_date=datetime(2000, 1, 1).date(),
                )
                session.add(user)
            await session.commit()

        elapsed = time.perf_counter() - start
        print(
            f"\n[ALTA] SQLite: 2000 inserts em {elapsed:.4f}s ({2000 / elapsed:.2f} ops/sec)"
        )
        assert elapsed < 60.0

    @pytest.mark.asyncio
    async def test_sqlite_read_high_load_1000(self, sqlite_session_factory):
        """Test reading 1000 users - alta carga."""
        session_maker = sqlite_session_factory

        # Insert data first
        async with session_maker() as session:
            users = []
            for i in range(1000):
                user = User(
                    username=f"read_high_{i}_{uuid4()}",
                    email=f"read_high{i}@test.com",
                    cpf_cnpj=f"{i:011d}",
                    password=TEST_PASSWORD_HASH,
                    birth_date=datetime(2000, 1, 1).date(),
                )
                users.append(user)
            session.add_all(users)
            await session.commit()

        # Measure read time
        start = time.perf_counter()

        async with session_maker() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()

        elapsed = time.perf_counter() - start
        print(
            f"\n[ALTA] SQLite: Leitura de 1000 users em {elapsed:.4f}s ({1000 / elapsed:.2f} ops/sec)"
        )
        assert len(users) >= 1000
        assert elapsed < 10.0

    @pytest.mark.asyncio
    async def test_sqlite_delete_high_load_1000(self, sqlite_session_factory):
        """Test deleting 1000 users - alta carga."""
        session_maker = sqlite_session_factory

        # Insert test data
        async with session_maker() as session:
            users = []
            for i in range(1000):
                user = User(
                    username=f"del_high_{i}_{uuid4()}",
                    email=f"del_high{i}@test.com",
                    cpf_cnpj=f"{i:011d}",
                    password=TEST_PASSWORD_HASH,
                    birth_date=datetime(2000, 1, 1).date(),
                )
                users.append(user)
            session.add_all(users)
            await session.commit()

        # Measure delete time
        start = time.perf_counter()

        async with session_maker() as session:
            await session.execute(delete(User))
            await session.commit()

        elapsed = time.perf_counter() - start
        print(f"\n[ALTA] SQLite: Delete de 1000 users em {elapsed:.4f}s")
        assert elapsed < 10.0

    # ========================================================================
    # TESTES DE CONCORRÊNCIA
    # ========================================================================

    @pytest.mark.asyncio
    async def test_sqlite_concurrent_reads_50(self, sqlite_session_factory):
        """Test 50 concurrent read operations."""
        session_maker = sqlite_session_factory

        # Insert test data
        async with session_maker() as session:
            for i in range(50):
                user = User(
                    username=f"conc_user_{i}_{uuid4()}",
                    email=f"conc_{i}@test.com",
                    cpf_cnpj=f"{i:011d}",
                    password=TEST_PASSWORD_HASH,
                    birth_date=datetime(2000, 1, 1).date(),
                )
                session.add(user)
            await session.commit()

        async def read_user(session_maker, user_id):
            async with session_maker() as session:
                result = await session.execute(
                    select(User).where(User.id == user_id)
                )
                return result.scalar_one_or_none()

        # Get all user IDs
        async with session_maker() as session:
            result = await session.execute(select(User.id))
            user_ids = [row[0] for row in result.all()]

        # Run concurrent reads
        start = time.perf_counter()
        tasks = [read_user(session_maker, uid) for uid in user_ids]
        results = await asyncio.gather(*tasks)
        elapsed = time.perf_counter() - start

        print(
            f"\n[CONCORRÊNCIA] SQLite: 50 leituras concorrentes em {elapsed:.4f}s"
        )
        assert all(r is not None for r in results)
        assert elapsed < 10.0

    @pytest.mark.asyncio
    async def test_sqlite_concurrent_writes_20(self, sqlite_session_factory):
        """Test 20 concurrent write operations."""
        session_maker = sqlite_session_factory

        async def create_user(session_maker, user_id):
            async with session_maker() as session:
                user = User(
                    username=f"conc_write_{user_id}_{uuid4()}",
                    email=f"conc_write_{user_id}@test.com",
                    cpf_cnpj=f"{user_id:011d}",
                    password=TEST_PASSWORD_HASH,
                    birth_date=datetime(2000, 1, 1).date(),
                )
                session.add(user)
                await session.commit()
                return user.id

        start = time.perf_counter()
        tasks = [create_user(session_maker, i) for i in range(20)]
        results = await asyncio.gather(*tasks)
        elapsed = time.perf_counter() - start

        print(
            f"\n[CONCORRÊNCIA] SQLite: 20 escritas concorrentes em {elapsed:.4f}s"
        )
        assert all(r is not None for r in results)
        assert elapsed < 10.0

    @pytest.mark.asyncio
    async def test_sqlite_mixed_operations_concurrent(
        self, sqlite_session_factory
    ):
        """Test concurrent mixed read/write operations."""
        session_maker = sqlite_session_factory

        # Pre-populate some users
        async with session_maker() as session:
            for i in range(20):
                user = User(
                    username=f"mix_user_{i}_{uuid4()}",
                    email=f"mix_{i}@test.com",
                    cpf_cnpj=f"{i:011d}",
                    password=TEST_PASSWORD_HASH,
                    birth_date=datetime(2000, 1, 1).date(),
                )
                session.add(user)
            await session.commit()

        async def read_operation(session_maker, user_id):
            async with session_maker() as session:
                result = await session.execute(
                    select(User).where(User.id == user_id)
                )
                return result.scalar_one_or_none()

        async def write_operation(session_maker, user_id):
            async with session_maker() as session:
                user = User(
                    username=f"mix_write_{user_id}_{uuid4()}",
                    email=f"mix_write_{user_id}@test.com",
                    cpf_cnpj=f"{100 + user_id:011d}",
                    password=TEST_PASSWORD_HASH,
                    birth_date=datetime(2000, 1, 1).date(),
                )
                session.add(user)
                await session.commit()
                return user.id

        # Get existing user IDs for reads
        async with session_maker() as session:
            result = await session.execute(select(User.id))
            existing_ids = [row[0] for row in result.all()[:10]]

        start = time.perf_counter()

        # Mix 10 reads and 10 writes
        read_tasks = [
            read_operation(session_maker, uid) for uid in existing_ids
        ]
        write_tasks = [write_operation(session_maker, i) for i in range(10)]
        all_tasks = read_tasks + write_tasks

        results = await asyncio.gather(*all_tasks)
        elapsed = time.perf_counter() - start

        print(
            f"\n[MISTO] SQLite: 20 operações mistas concorrentes em {elapsed:.4f}s"
        )
        assert len(results) == 20
        assert elapsed < 10.0

    # ========================================================================
    # TESTES DE RACE CONDITIONS
    # ========================================================================

    @pytest.mark.asyncio
    async def test_sqlite_race_condition_same_email(
        self, sqlite_session_factory
    ):
        """Test race condition when inserting users with same email."""
        session_maker = sqlite_session_factory
        same_email = f"race_{uuid4()}@test.com"

        async def try_create_user(session_maker, index):
            try:
                async with session_maker() as session:
                    user = User(
                        username=f"race_user_{index}",
                        email=same_email,
                        cpf_cnpj=f"{900 + index:011d}",
                        password=TEST_PASSWORD_HASH,
                        birth_date=datetime(2000, 1, 1).date(),
                    )
                    session.add(user)
                    await session.commit()
                    return True
            except Exception:
                try:
                    await session.rollback()
                except Exception:
                    pass
                return False

        # Try to create 5 users with same email concurrently
        tasks = [try_create_user(session_maker, i) for i in range(5)]
        results = await asyncio.gather(*tasks)

        # At least one should succeed, others should fail due to unique constraint
        successes = sum(1 for r in results if r)
        print(
            f"\n[RACE] SQLite: {successes} sucesso(s) de 5 tentativas (mesmo email)"
        )
        assert successes >= 1, "At least one insert should succeed"

    @pytest.mark.asyncio
    async def test_sqlite_race_condition_same_cpf(
        self, sqlite_session_factory
    ):
        """Test race condition when inserting users with same CPF."""
        session_maker = sqlite_session_factory
        same_cpf = "12345678901"

        async def try_create_user(session_maker, index):
            try:
                async with session_maker() as session:
                    user = User(
                        username=f"race_cpf_user_{index}_{uuid4()}",
                        email=f"race_cpf_{index}@test.com",
                        cpf_cnpj=same_cpf,
                        password=TEST_PASSWORD_HASH,
                        birth_date=datetime(2000, 1, 1).date(),
                    )
                    session.add(user)
                    await session.commit()
                    return True
            except Exception:
                try:
                    await session.rollback()
                except Exception:
                    pass
                return False

        # Try to create 5 users with same CPF concurrently
        tasks = [try_create_user(session_maker, i) for i in range(5)]
        results = await asyncio.gather(*tasks)

        successes = sum(1 for r in results if r)
        print(
            f"\n[RACE] SQLite: {successes} sucesso(s) de 5 tentativas (mesmo CPF)"
        )
        assert successes >= 1, "At least one insert should succeed"

    @pytest.mark.asyncio
    async def test_sqlite_bulk_insert_with_session_reuse(
        self, sqlite_session_factory
    ):
        """Test bulk insert efficiency with session reuse."""
        session_maker = sqlite_session_factory
        count = 200

        start_reuse = time.perf_counter()
        async with session_maker() as session:
            for i in range(count):
                user = User(
                    username=f"reuse_{i}_{uuid4()}",
                    email=f"reuse_{i}@test.com",
                    cpf_cnpj=f"{200 + i:011d}",
                    password=TEST_PASSWORD_HASH,
                    birth_date=datetime(2000, 1, 1).date(),
                )
                session.add(user)
            await session.commit()
        elapsed_reuse = time.perf_counter() - start_reuse

        print(
            f"\n[EFICIÊNCIA] Session reuse: {count} inserts em {elapsed_reuse:.4f}s"
        )
        assert elapsed_reuse < 10.0
