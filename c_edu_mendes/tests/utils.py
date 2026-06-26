"""Test utilities and helpers for async testing."""

import asyncio
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any, AsyncGenerator, Callable, List, Optional
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)

from app.security import get_hashed_password


@dataclass
class LoadTestResult:
    """Results from a load test operation."""

    operation: str
    total_operations: int
    elapsed_seconds: float
    success_count: int = 0
    failure_count: int = 0
    extra_metrics: dict = field(default_factory=dict)

    @property
    def ops_per_second(self) -> float:
        """Calculate operations per second."""
        if self.elapsed_seconds == 0:
            return 0
        return self.total_operations / self.elapsed_seconds

    def summary(self) -> str:
        """Return a formatted summary string."""
        return (
            f"{self.operation}: {self.total_operations} ops em {self.elapsed_seconds:.4f}s "
            f"({self.ops_per_second:.2f} ops/sec)"
        )


@dataclass
class ConcurrentTestResult:
    """Results from concurrent test operations."""

    task_name: str
    total_tasks: int
    successful: int
    failed: int
    elapsed_seconds: float
    error_details: List[str] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_tasks == 0:
            return 0.0
        return (self.successful / self.total_tasks) * 100

    def summary(self) -> str:
        """Return a formatted summary string."""
        return (
            f"{self.task_name}: {self.successful}/{self.total_tasks} sucesso "
            f"({self.success_rate:.1f}%) em {self.elapsed_seconds:.4f}s"
        )


class LoadTestRunner:
    """Helper class for running load tests."""

    def __init__(self, session_maker: async_sessionmaker):
        self.session_maker = session_maker
        self.results: List[LoadTestResult] = []

    async def run_bulk_insert(
        self,
        count: int,
        user_generator: Optional[Callable[[int], dict]] = None,
        label: str = "bulk_insert",
    ) -> LoadTestResult:
        """Run bulk insert test."""
        from app.models import User

        if user_generator is None:

            def default_generator(i: int) -> dict:
                return {
                    "username": f"load_{label}_{i}_{uuid4()}",
                    "email": f"load_{label}_{i}@test.com",
                    "cpf_cnpj": f"{i:011d}",
                    "password": get_hashed_password("Password123"),
                    "birth_date": "2000-01-01",
                }

        start = time.perf_counter()
        success_count = 0

        async with self.session_maker() as session:
            for i in range(count):
                try:
                    data = user_generator(i)
                    user = User(**data)
                    session.add(user)
                    success_count += 1
                except Exception:
                    continue
            await session.commit()

        elapsed = time.perf_counter() - start

        result = LoadTestResult(
            operation=f"{label}_insert",
            total_operations=success_count,
            elapsed_seconds=elapsed,
            success_count=success_count,
            failure_count=count - success_count,
            extra_metrics={"target_count": count},
        )
        self.results.append(result)
        return result

    async def run_bulk_read(
        self,
        label: str = "bulk_read",
    ) -> LoadTestResult:
        """Run bulk read test."""
        from sqlalchemy import select

        from app.models import User

        start = time.perf_counter()

        async with self.session_maker() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()

        elapsed = time.perf_counter() - start

        result = LoadTestResult(
            operation=f"{label}_read",
            total_operations=len(users),
            elapsed_seconds=elapsed,
            success_count=len(users),
        )
        self.results.append(result)
        return result

    async def run_concurrent_operations(
        self,
        operation: Callable[[AsyncSession, int], Any],
        count: int,
        label: str = "concurrent_op",
    ) -> ConcurrentTestResult:
        """Run concurrent operations test."""
        error_details = []

        async def wrapped_op(index: int):
            try:
                async with self.session_maker() as session:
                    return await operation(session, index)
            except Exception as e:
                error_details.append(f"Index {index}: {str(e)}")
                return None

        start = time.perf_counter()
        tasks = [wrapped_op(i) for i in range(count)]
        results = await asyncio.gather(*tasks)
        elapsed = time.perf_counter() - start

        successful = sum(1 for r in results if r is not None)
        failed = count - successful

        result = ConcurrentTestResult(
            task_name=label,
            total_tasks=count,
            successful=successful,
            failed=failed,
            elapsed_seconds=elapsed,
            error_details=error_details[:10],  # Limit error details
        )
        self.results.append(result)  # type: ignore
        return result

    def get_summary(self) -> str:
        """Get summary of all test results."""
        lines = ["=" * 60, "LOAD TEST SUMMARY", "=" * 60]
        for result in self.results:
            if isinstance(result, LoadTestResult):
                lines.append(result.summary())
            elif isinstance(result, ConcurrentTestResult):
                lines.append(result.summary())
        lines.append("=" * 60)
        return "\n".join(lines)


@asynccontextmanager
async def measure_time(
    operation_name: str = "operation",
) -> AsyncGenerator[None, None]:
    """Context manager to measure execution time."""
    start = time.perf_counter()
    yield
    elapsed = time.perf_counter() - start
    print(f"\n[TIME] {operation_name}: {elapsed:.4f}s")


@pytest.fixture
def load_test_runner():
    """Create a load test runner instance."""

    def _create_runner(session_maker: async_sessionmaker) -> LoadTestRunner:
        return LoadTestRunner(session_maker)

    return _create_runner


@pytest.fixture(scope="module")
def test_user_factory():
    """Factory for generating test user data."""

    def create_user_data(
        email_prefix: str = "test",
        index: int = 0,
        password: str = "SenhaValida123",
        cpf_start: int = 0,
    ) -> dict:
        """Generate user data for testing."""
        return {
            "name": f"Test User {index}",
            "email": f"{email_prefix}_{index}_{uuid4()}@test.com",
            "cpf_cnpj": f"{cpf_start + index:011d}",
            "password": password,
            "birth_date": "2000-01-01",
        }

    return create_user_data
