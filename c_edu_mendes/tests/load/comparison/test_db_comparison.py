"""Comparative load tests: SQLite vs PostgreSQL.

This module provides direct comparison between SQLite (aiosqlite) and PostgreSQL (asyncpg)
for various database operations.

Results are printed with timing information for analysis.
"""

import os
import time
from datetime import datetime
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.models import User, table_registry


def get_mock_hashed_password(password: str) -> str:
    """Mock password hash for performance tests - not secure, just for benchmarking."""
    return f"mock_hash_{password}"


DEFAULT_PG_URL = os.environ.get(
    "TEST_PG_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/testdb",
)


class DatabaseComparison:
    """Helper class for database comparison tests."""

    def __init__(self):
        self.results = {"sqlite": {}, "postgresql": {}}

    async def setup_sqlite(self):
        """Setup SQLite database."""
        engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=NullPool,
        )
        async with engine.begin() as conn:
            await conn.run_sync(table_registry.metadata.create_all)
        return async_sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        ), engine

    async def setup_postgresql(self, pg_url):
        """Setup PostgreSQL database."""
        try:
            engine = create_async_engine(
                pg_url,
                poolclass=NullPool,
            )
            async with engine.begin() as conn:
                await conn.run_sync(table_registry.metadata.create_all)
            return async_sessionmaker(
                engine, class_=AsyncSession, expire_on_commit=False
            ), engine
        except Exception:
            return None, None

    async def cleanup(self, engine):
        """Cleanup database."""
        async with engine.begin() as conn:
            await conn.run_sync(table_registry.metadata.drop_all)
        await engine.dispose()

    async def benchmark_insert(self, session_maker, count: int, prefix: str):
        """Benchmark insert operations using batch inserts."""
        start = time.perf_counter()
        async with session_maker() as session:
            users = []
            for i in range(count):
                user = User(
                    username=f"{prefix}_{i}_{uuid4()}",
                    email=f"{prefix}_{i}@test.com",
                    cpf_cnpj=f"{i:011d}",
                    password=get_mock_hashed_password("Password123"),
                    birth_date=datetime(2000, 1, 1).date(),
                )
                users.append(user)
                session.add(user)
            await session.commit()
        return time.perf_counter() - start

    async def benchmark_read(self, session_maker, count: int, prefix: str):
        """Benchmark read operations."""
        from sqlalchemy import select

        # First insert data
        async with session_maker() as session:
            for i in range(count):
                user = User(
                    username=f"{prefix}_r{i}_{uuid4()}",
                    email=f"{prefix}_r{i}@test.com",
                    cpf_cnpj=f"{i:011d}",
                    password=get_mock_hashed_password("Password123"),
                    birth_date=datetime(2000, 1, 1).date(),
                )
                session.add(user)
            await session.commit()

        # Now benchmark reads
        start = time.perf_counter()
        async with session_maker() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()
        elapsed = time.perf_counter() - start
        return elapsed, len(users)

    async def benchmark_update(self, session_maker, count: int, prefix: str):
        """Benchmark update operations."""
        from sqlalchemy import select

        # Insert data first
        async with session_maker() as session:
            for i in range(count):
                user = User(
                    username=f"{prefix}_u{i}_{uuid4()}",
                    email=f"{prefix}_u{i}@test.com",
                    cpf_cnpj=f"{i:011d}",
                    password=get_mock_hashed_password("Password123"),
                    birth_date=datetime(2000, 1, 1).date(),
                )
                session.add(user)
            await session.commit()

        # Benchmark updates
        start = time.perf_counter()
        async with session_maker() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()
            for user in users:
                user.username = f"updated_{user.username}"
            await session.commit()
        return time.perf_counter() - start

    async def benchmark_delete(self, session_maker, count: int, prefix: str):
        """Benchmark delete operations."""
        from sqlalchemy import delete

        # Insert data first
        async with session_maker() as session:
            for i in range(count):
                user = User(
                    username=f"{prefix}_d{i}_{uuid4()}",
                    email=f"{prefix}_d{i}@test.com",
                    cpf_cnpj=f"{i:011d}",
                    password=get_mock_hashed_password("Password123"),
                    birth_date=datetime(2000, 1, 1).date(),
                )
                session.add(user)
            await session.commit()

        # Benchmark deletes
        start = time.perf_counter()
        async with session_maker() as session:
            await session.execute(delete(User))
            await session.commit()
        return time.perf_counter() - start


@pytest.mark.asyncio
async def test_compare_insert_100():
    """Compare insert performance: SQLite vs PostgreSQL."""
    # SQLite
    sqlite_time = await _benchmark_sqlite_insert(100, "lite_i100")

    # PostgreSQL - quick check, skip if not available
    pg_time = await _benchmark_pg_insert_fast(100, "pg_i100")

    if pg_time is not None:
        print("\n=== Insert 100 users ===")
        print(
            f"SQLite:      {sqlite_time:.4f}s ({100 / sqlite_time:.2f} ops/sec)"
        )
        print(f"PostgreSQL:  {pg_time:.4f}s ({100 / pg_time:.2f} ops/sec)")
        print(f"Ratio (PG/SQLite): {pg_time / sqlite_time:.2f}x")
    else:
        print("\n=== Insert 100 users ===")
        print(f"SQLite: {sqlite_time:.4f}s (PostgreSQL not available)")

    assert sqlite_time < 5.0, (
        f"SQLite insert took {sqlite_time:.2f}s, expected < 5s"
    )


async def _benchmark_pg_insert_fast(count: int, prefix: str) -> float | None:
    """Quick benchmark PostgreSQL insert with timeout."""
    import asyncio

    try:
        # Quick connectivity check
        engine = create_async_engine(
            DEFAULT_PG_URL,
            poolclass=NullPool,
        )
        async with engine.begin() as conn:
            await asyncio.wait_for(
                conn.execute(select(1)),
                timeout=2.0,
            )
        await engine.dispose()

        # Run actual benchmark
        return await _benchmark_pg_insert(count, prefix)
    except (Exception, asyncio.TimeoutError):
        return None


async def _benchmark_sqlite_insert(count: int, prefix: str) -> float:
    """Benchmark SQLite insert."""
    from sqlalchemy.pool import StaticPool

    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)
    session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    start = time.perf_counter()
    async with session_maker() as session:
        # Batch insert
        users = []
        for i in range(count):
            user = User(
                username=f"{prefix}_{i}_{uuid4()}",
                email=f"{prefix}_{i}@test.com",
                cpf_cnpj=f"{i:011d}",
                password=get_mock_hashed_password("Password123"),
                birth_date=datetime(2000, 1, 1).date(),
            )
            users.append(user)
            session.add(user)
        await session.commit()
    elapsed = time.perf_counter() - start

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)
    await engine.dispose()
    return elapsed


async def _benchmark_pg_insert(count: int, prefix: str) -> float | None:
    """Benchmark PostgreSQL insert."""
    try:
        engine = create_async_engine(
            DEFAULT_PG_URL,
            poolclass=NullPool,
        )
        async with engine.begin() as conn:
            await conn.run_sync(table_registry.metadata.create_all)
        session_maker = async_sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )

        start = time.perf_counter()
        async with session_maker() as session:
            for i in range(count):
                user = User(
                    username=f"{prefix}_{i}_{uuid4()}",
                    email=f"{prefix}_{i}@test.com",
                    cpf_cnpj=f"{i:011d}",
                    password=get_mock_hashed_password("Password123"),
                    birth_date=datetime(2000, 1, 1).date(),
                )
                session.add(user)
            await session.commit()
        elapsed = time.perf_counter() - start

        async with engine.begin() as conn:
            await conn.run_sync(table_registry.metadata.drop_all)
        await engine.dispose()
        return elapsed
    except Exception:
        return None


@pytest.mark.asyncio
async def test_compare_read_100():
    """Compare read performance: SQLite vs PostgreSQL."""
    sqlite_time, sqlite_count = await _benchmark_sqlite_read(100, "lite_r100")
    pg_result = await _benchmark_pg_read(100, "pg_r100")

    if pg_result is not None:
        pg_time, pg_count = pg_result
        print("\n=== Read 100 users ===")
        print(f"SQLite:      {sqlite_time:.4f}s ({sqlite_count} rows)")
        print(f"PostgreSQL:  {pg_time:.4f}s ({pg_count} rows)")
        print(f"Ratio (PG/SQLite): {pg_time / sqlite_time:.2f}x")
    else:
        print("\n=== Read 100 users ===")
        print(f"SQLite: {sqlite_time:.4f}s (PostgreSQL not available)")

    assert sqlite_time < 5.0


async def _benchmark_sqlite_read(count: int, prefix: str) -> tuple[float, int]:
    """Benchmark SQLite read."""
    from sqlalchemy import select
    from sqlalchemy.pool import StaticPool

    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)
    session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    # Insert data
    async with session_maker() as session:
        for i in range(count):
            user = User(
                username=f"{prefix}_r{i}_{uuid4()}",
                email=f"{prefix}_r{i}@test.com",
                cpf_cnpj=f"{i:011d}",
                password=get_mock_hashed_password("Password123"),
                birth_date=datetime(2000, 1, 1).date(),
            )
            session.add(user)
        await session.commit()

    # Benchmark reads
    start = time.perf_counter()
    async with session_maker() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
    elapsed = time.perf_counter() - start

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)
    await engine.dispose()
    return elapsed, len(users)


async def _benchmark_pg_read(
    count: int, prefix: str
) -> tuple[float, int] | None:
    """Benchmark PostgreSQL read."""
    from sqlalchemy import select

    try:
        engine = create_async_engine(
            DEFAULT_PG_URL,
            poolclass=NullPool,
        )
        async with engine.begin() as conn:
            await conn.run_sync(table_registry.metadata.create_all)
        session_maker = async_sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )

        # Insert data
        async with session_maker() as session:
            for i in range(count):
                user = User(
                    username=f"{prefix}_r{i}_{uuid4()}",
                    email=f"{prefix}_r{i}@test.com",
                    cpf_cnpj=f"{i:011d}",
                    password=get_mock_hashed_password("Password123"),
                    birth_date=datetime(2000, 1, 1).date(),
                )
                session.add(user)
            await session.commit()

        # Benchmark reads
        start = time.perf_counter()
        async with session_maker() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()
        elapsed = time.perf_counter() - start

        async with engine.begin() as conn:
            await conn.run_sync(table_registry.metadata.drop_all)
        await engine.dispose()
        return elapsed, len(users)
    except Exception:
        return None


@pytest.mark.asyncio
async def test_compare_update_50():
    """Compare update performance: SQLite vs PostgreSQL."""
    sqlite_time = await _benchmark_sqlite_update(50, "lite_u50")
    pg_time = await _benchmark_pg_update(50, "pg_u50")

    if pg_time is not None:
        print("\n=== Update 50 users ===")
        print(f"SQLite:      {sqlite_time:.4f}s")
        print(f"PostgreSQL:  {pg_time:.4f}s")
        print(f"Ratio (PG/SQLite): {pg_time / sqlite_time:.2f}x")
    else:
        print("\n=== Update 50 users ===")
        print(f"SQLite: {sqlite_time:.4f}s (PostgreSQL not available)")

    assert sqlite_time < 5.0


async def _benchmark_sqlite_update(count: int, prefix: str) -> float:
    """Benchmark SQLite update."""
    from sqlalchemy import select
    from sqlalchemy.pool import StaticPool

    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)
    session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    # Insert data
    async with session_maker() as session:
        for i in range(count):
            user = User(
                username=f"{prefix}_u{i}_{uuid4()}",
                email=f"{prefix}_u{i}@test.com",
                cpf_cnpj=f"{i:011d}",
                password=get_mock_hashed_password("Password123"),
                birth_date=datetime(2000, 1, 1).date(),
            )
            session.add(user)
        await session.commit()

    # Benchmark updates
    start = time.perf_counter()
    async with session_maker() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        for user in users:
            user.username = f"updated_{user.username}"
        await session.commit()
    elapsed = time.perf_counter() - start

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)
    await engine.dispose()
    return elapsed


async def _benchmark_pg_update(count: int, prefix: str) -> float | None:
    """Benchmark PostgreSQL update."""
    from sqlalchemy import select

    try:
        engine = create_async_engine(
            DEFAULT_PG_URL,
            poolclass=NullPool,
        )
        async with engine.begin() as conn:
            await conn.run_sync(table_registry.metadata.create_all)
        session_maker = async_sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )

        # Insert data
        async with session_maker() as session:
            for i in range(count):
                user = User(
                    username=f"{prefix}_u{i}_{uuid4()}",
                    email=f"{prefix}_u{i}@test.com",
                    cpf_cnpj=f"{i:011d}",
                    password=get_mock_hashed_password("Password123"),
                    birth_date=datetime(2000, 1, 1).date(),
                )
                session.add(user)
            await session.commit()

        # Benchmark updates
        start = time.perf_counter()
        async with session_maker() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()
            for user in users:
                user.username = f"updated_{user.username}"
            await session.commit()
        elapsed = time.perf_counter() - start

        async with engine.begin() as conn:
            await conn.run_sync(table_registry.metadata.drop_all)
        await engine.dispose()
        return elapsed
    except Exception:
        return None


@pytest.mark.asyncio
async def test_compare_delete_50():
    """Compare delete performance: SQLite vs PostgreSQL."""
    sqlite_time = await _benchmark_sqlite_delete(50, "lite_d50")
    pg_time = await _benchmark_pg_delete(50, "pg_d50")

    if pg_time is not None:
        print("\n=== Delete 50 users ===")
        print(f"SQLite:      {sqlite_time:.4f}s")
        print(f"PostgreSQL:  {pg_time:.4f}s")
        print(f"Ratio (PG/SQLite): {pg_time / sqlite_time:.2f}x")
    else:
        print("\n=== Delete 50 users ===")
        print(f"SQLite: {sqlite_time:.4f}s (PostgreSQL not available)")

    assert sqlite_time < 5.0


async def _benchmark_sqlite_delete(count: int, prefix: str) -> float:
    """Benchmark SQLite delete."""
    from sqlalchemy import delete
    from sqlalchemy.pool import StaticPool

    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)
    session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    # Insert data
    async with session_maker() as session:
        for i in range(count):
            user = User(
                username=f"{prefix}_d{i}_{uuid4()}",
                email=f"{prefix}_d{i}@test.com",
                cpf_cnpj=f"{i:011d}",
                password=get_mock_hashed_password("Password123"),
                birth_date=datetime(2000, 1, 1).date(),
            )
            session.add(user)
        await session.commit()

    # Benchmark deletes
    start = time.perf_counter()
    async with session_maker() as session:
        await session.execute(delete(User))
        await session.commit()
    elapsed = time.perf_counter() - start

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)
    await engine.dispose()
    return elapsed


async def _benchmark_pg_delete(count: int, prefix: str) -> float | None:
    """Benchmark PostgreSQL delete."""
    from sqlalchemy import delete

    try:
        engine = create_async_engine(
            DEFAULT_PG_URL,
            poolclass=NullPool,
        )
        async with engine.begin() as conn:
            await conn.run_sync(table_registry.metadata.create_all)
        session_maker = async_sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )

        # Insert data
        async with session_maker() as session:
            for i in range(count):
                user = User(
                    username=f"{prefix}_d{i}_{uuid4()}",
                    email=f"{prefix}_d{i}@test.com",
                    cpf_cnpj=f"{i:011d}",
                    password=get_mock_hashed_password("Password123"),
                    birth_date=datetime(2000, 1, 1).date(),
                )
                session.add(user)
            await session.commit()

        # Benchmark deletes
        start = time.perf_counter()
        async with session_maker() as session:
            await session.execute(delete(User))
            await session.commit()
        elapsed = time.perf_counter() - start

        async with engine.begin() as conn:
            await conn.run_sync(table_registry.metadata.drop_all)
        await engine.dispose()
        return elapsed
    except Exception:
        return None


def print_comparison_summary(results):
    """Print a summary comparison table."""
    print("\n" + "=" * 60)
    print("DATABASE PERFORMANCE COMPARISON SUMMARY")
    print("=" * 60)
    print(
        f"{'Operation':<20} {'SQLite (s)':<15} {'PostgreSQL (s)':<15} {'Ratio':<10}"
    )
    print("-" * 60)
    for op, times in results.items():
        sqlite_t = times.get("sqlite", "N/A")
        pg_t = times.get("postgresql", "N/A")
        ratio = (
            f"{pg_t / sqlite_t:.2f}x"
            if isinstance(sqlite_t, (int, float))
            and isinstance(pg_t, (int, float))
            else "N/A"
        )
        print(
            f"{op:<20} {sqlite_t:<15.4f if isinstance(sqlite_t, (int, float)) else 'N/A':<15} {pg_t:<15.4f if isinstance(pg_t, (int, float)) else 'N/A':<15} {ratio:<10}"
        )
    print("=" * 60)
