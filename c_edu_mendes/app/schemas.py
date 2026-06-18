import random
import re
from datetime import date, datetime
from uuid import UUID, uuid4
import string

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
)

# =====================================================
# CARDS
# =====================================================


class ItemCardSchema(BaseModel):
    titulo: str = Field(..., min_length=3, description="Título do card")

    descricao: str = Field(..., min_length=5, description="Descrição do card")

    @field_validator("titulo")
    @classmethod
    def titulo_nao_vazio(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("O título não pode estar vazio.")

        return value

    @field_validator("descricao")
    @classmethod
    def descricao_nao_vazia(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("A descrição não pode estar vazia.")

        return value


# =====================================================
# USER INPUT
# =====================================================


class UserCreate(BaseModel):
    name: str = Field(
        min_length=3,
        max_length=100,
        default="Yuji",
    )

    birth_date: date = Field(
        default=datetime.strptime("28/08/2000", "%d/%m/%Y").date()
    )

    cpf_cnpj: str = Field(default="18219822821")

    email: EmailStr = Field(default="emailteste@gmail.com")

    password: str = Field(
        min_length=8, default=str( random.choice(string.ascii_uppercase) + str(random.randint(10000000, 99999999)))
    )

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str):

        value = value.strip()

        if not value:
            raise ValueError("Nome não pode estar vazio.")

        return value.title()

    @field_validator("cpf_cnpj")
    @classmethod
    def validate_document(
        cls,
        value: str,
    ) -> str:

        cleaned = re.sub(
            r"\D",
            "",
            value,
        )

        if len(cleaned) == 11:
            if not validar_cpf(cleaned):
                raise ValueError("CPF inválido.")

            return cleaned

        if len(cleaned) == 14:
            if not validar_cnpj(cleaned):
                raise ValueError("CNPJ inválido.")

            return cleaned

        raise ValueError("Informe CPF ou CNPJ válido.")

    @field_validator("email")
    @classmethod
    def normalize_email(
        cls,
        value: EmailStr,
    ) -> str:

        return value.lower().strip()

    @field_validator("password")
    @classmethod
    def validate_password(
        cls,
        value: str,
    ) -> str:

        if not any(c.isupper() for c in value):
            raise ValueError("A senha deve possuir letra maiúscula.")

        if not any(c.isdigit() for c in value):
            raise ValueError("A senha deve possuir número.")

        return value


# =====================================================
# RESPONSE
# =====================================================


class UserPublic(BaseModel):
    id: UUID
    name: str
    email: EmailStr


# =====================================================
# DATABASE MODEL
# =====================================================


class UserDB(BaseModel):
    id: UUID = Field(default_factory=uuid4)

    name: str

    birth_date: date

    cpf_cnpj: str

    email: EmailStr

    password_hash: str


# =====================================================
# HELPERS
# =====================================================


def validar_cpf(documento: str) -> bool:

    if documento == documento[0] * 11:
        return False

    soma = sum(int(documento[i]) * (10 - i) for i in range(9))

    digito_1 = (soma * 10) % 11
    digito_1 = 0 if digito_1 == 10 else digito_1

    soma = sum(int(documento[i]) * (11 - i) for i in range(10))

    digito_2 = (soma * 10) % 11
    digito_2 = 0 if digito_2 == 10 else digito_2

    return int(documento[9]) == digito_1 and int(documento[10]) == digito_2


def validar_cnpj(documento: str) -> bool:

    if documento == documento[0] * 14:
        return False

    pesos_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    pesos_2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    soma = sum(int(documento[i]) * pesos_1[i] for i in range(12))

    resto = soma % 11

    digito_1 = 0 if resto < 2 else 11 - resto

    soma = sum(int(documento[i]) * pesos_2[i] for i in range(13))

    resto = soma % 11

    digito_2 = 0 if resto < 2 else 11 - resto

    return int(documento[12]) == digito_1 and int(documento[13]) == digito_2
