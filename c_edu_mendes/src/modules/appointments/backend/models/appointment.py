from datetime import date, time
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import table_registry


@table_registry.mapped_as_dataclass
class Appointment:
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"))
    barber_id: Mapped[int] = mapped_column(ForeignKey("barbers.id"))  # Assuming barbers table
    customer_id: Mapped[int] = mapped_column(ForeignKey("users.id"))  # Assuming users table
    appointment_date: Mapped[date]
    appointment_time: Mapped[time]
    observations: Mapped[str] = None

    # Relationships would be defined here in a real implementation
    # service = relationship("Service")
    # barber = relationship("Barber")
    # customer = relationship("User")