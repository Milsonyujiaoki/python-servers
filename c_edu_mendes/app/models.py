from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, registry

table_registry = registry()


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, default_factory=uuid4, init=False
    )

    username: Mapped[str]
    cpf_cnpj: Mapped[str]
    email: Mapped[str]
    password: Mapped[str]
    birth_date: Mapped[date]
    created_at: Mapped[datetime] = mapped_column(
        default_factory=datetime.utcnow, server_default=func.now(), init=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        default_factory=datetime.utcnow, onupdate=func.now(), init=False
    )
