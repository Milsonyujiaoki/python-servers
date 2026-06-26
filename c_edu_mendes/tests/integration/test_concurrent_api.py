"""Tests for concurrent API operations and race conditions.

Testa cenários de:
- Múltiplas requisições simultâneas
- Race conditions em criações/updates
- Comportamento under load da API
"""

import time
from uuid import uuid4

from fastapi import status
from fastapi.testclient import TestClient

# CPFs válidos para teste (gerados com algoritmo correto)
VALID_CPFS = [
    "00000010073",
    "00000010154",
    "00000010235",
    "00000010316",
    "00000010405",
    "00000010588",
    "00000010669",
    "00000010740",
    "00000010820",
    "00000010901",
    "00000011045",
    "00000011126",
    "00000011207",
    "00000011398",
    "00000011479",
]


class TestConcurrentUserCreation:
    """Test concurrent/sequential user creation scenarios."""

    def test_sequential_user_creations_different_emails(
        self, client: TestClient
    ):
        """Test creating multiple users sequentially with different emails."""
        results = []

        for i in range(10):
            payload = {
                "name": f"Sequential User {i}",
                "birth_date": "2000-01-01",
                "cpf_cnpj": VALID_CPFS[i % len(VALID_CPFS)]
                if i < len(VALID_CPFS)
                else f"CPF{i:011d}",
                "email": f"seq_{i}_{uuid4()}@test.com",
                "password": "SenhaValida123",
            }
            response = client.post("/api/v1/users", json=payload)
            results.append((
                response.status_code,
                response.json() if response.status_code < 400 else None,
            ))

        # All should succeed
        success_count = sum(
            1
            for status_code, _ in results
            if status_code == status.HTTP_201_CREATED
        )
        print(f"\n[API] {success_count}/10 criações sequenciais")
        assert success_count == 10, (
            f"Expected 10 successes, got {success_count}"
        )

    def test_sequential_user_creations_same_email(self, client: TestClient):
        """Test creating multiple users with same email - only one should succeed."""
        same_email = f"race_same_email_{uuid4()}@test.com"
        results = []

        for i in range(5):
            payload = {
                "name": f"Race User {i}",
                "birth_date": "2000-01-01",
                "cpf_cnpj": VALID_CPFS[i],
                "email": same_email,
                "password": "SenhaValida123",
            }
            response = client.post("/api/v1/users", json=payload)
            results.append(response.status_code)

        success_count = sum(
            1 for code in results if code == status.HTTP_201_CREATED
        )
        conflict_count = sum(
            1 for code in results if code == status.HTTP_409_CONFLICT
        )

        print(
            f"\n[API RACE] Mesmo email: {success_count} sucesso(s), {conflict_count} conflitos"
        )

        # Exactly one should succeed
        assert success_count == 1, (
            f"Expected exactly 1 success, got {success_count}"
        )

    def test_sequential_user_creations_same_cpf(self, client: TestClient):
        """Test creating multiple users with same CPF - only one should succeed."""
        same_cpf = "52998224725"
        results = []

        for i in range(5):
            payload = {
                "name": f"Race CPF User {i}",
                "birth_date": "2000-01-01",
                "cpf_cnpj": same_cpf,
                "email": f"race_cpf_{i}_{uuid4()}@test.com",
                "password": "SenhaValida123",
            }
            response = client.post("/api/v1/users", json=payload)
            results.append(response.status_code)

        success_count = sum(
            1 for code in results if code == status.HTTP_201_CREATED
        )
        conflict_count = sum(
            1 for code in results if code == status.HTTP_409_CONFLICT
        )

        print(
            f"\n[API RACE] Mesmo CPF: {success_count} sucesso(s), {conflict_count} conflitos"
        )

        assert success_count == 1, (
            f"Expected exactly 1 success, got {success_count}"
        )


class TestLoadEndpoints:
    """Test API endpoints under load."""

    def test_bulk_user_creation_sequential(self, client: TestClient):
        """Test creating users sequentially - measures baseline performance."""
        start = time.perf_counter()

        created_users = []
        for i in range(10):
            payload = {
                "name": f"Sequential User {i}",
                "birth_date": "2000-01-01",
                "cpf_cnpj": VALID_CPFS[i],
                "email": f"seq_{i}_{uuid4()}@test.com",
                "password": "SenhaValida123",
            }
            response = client.post("/api/v1/users", json=payload)
            assert response.status_code == status.HTTP_201_CREATED, (
                f"Failed at user {i}: {response.json()}"
            )
            created_users.append(response.json())

        elapsed = time.perf_counter() - start
        print(
            f"\n[API LOAD] 10 criações sequenciais em {elapsed:.4f}s ({10 / elapsed:.2f} ops/sec)"
        )

        assert len(created_users) == 10
        assert elapsed < 60.0

    def test_bulk_read_operations(
        self, client: TestClient, user, access_token: str
    ):
        """Test multiple read operations under load."""
        headers = {"Authorization": f"Bearer {access_token}"}

        # First create some users
        user_ids = []
        for i in range(5):
            payload = {
                "name": f"Read Load User {i}",
                "birth_date": "2000-01-01",
                "cpf_cnpj": VALID_CPFS[i + 5],
                "email": f"readload_{i}_{uuid4()}@test.com",
                "password": "SenhaValida123",
            }
            response = client.post(
                "/api/v1/users", json=payload, headers=headers
            )
            if response.status_code == status.HTTP_201_CREATED:
                user_ids.append(response.json()["id"])

        # Now measure read performance
        start = time.perf_counter()
        results = []

        for uid in user_ids:
            response = client.get(f"/api/v1/users/{uid}", headers=headers)
            results.append((
                response.status_code,
                response.json() if response.status_code < 400 else None,
            ))

        elapsed = time.perf_counter() - start
        success_count = sum(
            1
            for status_code, _ in results
            if status_code == status.HTTP_200_OK
        )
        print(f"\n[API READ LOAD] {len(user_ids)} leituras em {elapsed:.4f}s")

        assert success_count == len(user_ids)


class TestAuthenticationLoad:
    """Test authentication endpoints under load."""

    def test_sequential_logins(self, client: TestClient):
        """Test multiple sequential login attempts."""
        # Create a user first
        unique_email = f"login_load_{uuid4()}@test.com"
        password = "SenhaValida123"

        create_payload = {
            "name": "Login Load User",
            "birth_date": "2000-01-01",
            "cpf_cnpj": "11122233396",  # Valid CPF
            "email": unique_email,
            "password": password,
        }
        create_response = client.post("/api/v1/users", json=create_payload)
        assert create_response.status_code == status.HTTP_201_CREATED, (
            f"Failed to create user: {create_response.json()}"
        )

        # Sequential login attempts
        results = []
        start = time.perf_counter()

        for i in range(10):
            response = client.post(
                "/api/v1/auth/token",
                data={"username": unique_email, "password": password},
            )
            results.append((
                response.status_code,
                response.json() if response.status_code < 400 else None,
            ))

        elapsed = time.perf_counter() - start
        success_count = sum(
            1
            for status_code, _ in results
            if status_code == status.HTTP_200_OK
        )
        print(f"\n[API AUTH LOAD] {success_count}/10 logins em {elapsed:.4f}s")

        assert success_count == 10, (
            f"Expected 10 successful logins, got {success_count}"
        )

    def test_invalid_login_attempts(self, client: TestClient):
        """Test multiple invalid login attempts."""
        results = []

        for i in range(5):
            response = client.post(
                "/api/v1/auth/token",
                data={
                    "username": f"fake_{i}@test.com",
                    "password": "wrongpassword",
                },
            )
            results.append(response.status_code)

        # All should fail with 401
        unauthorized_count = sum(
            1 for code in results if code == status.HTTP_401_UNAUTHORIZED
        )
        print(
            f"\n[API AUTH] {unauthorized_count}/5 tentativas inválidas retornaram 401"
        )
        assert unauthorized_count == 5
