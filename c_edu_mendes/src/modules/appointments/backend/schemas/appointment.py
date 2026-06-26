from pydantic import BaseModel, Field
from datetime import date, time
from uuid import UUID


class AppointmentCreate(BaseModel):
    customer_id: int = Field(..., gt=0)
    barber_id: int = Field(..., gt=0)
    service_id: int = Field(..., gt=0)
    appointment_date: date
    appointment_time: time
    observations: str = Field(default="")


class Slot(BaseModel):
    time: time
    available: bool