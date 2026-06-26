from typing import List, Optional
from unittest.mock import Mock
from datetime import date, time
from sqlalchemy.orm import Session

from src.modules.appointments.backend.repositories.availability_repo import AvailabilityRepository
from src.modules.appointments.backend.models.appointment import Appointment
from src.modules.appointments.backend.schemas.appointment import AppointmentCreate, Slot


class BookingService:
    def __init__(self, db: Session, availability_repo: AvailabilityRepository):
        self.db = db
        self.availability_repo = availability_repo

    def get_available_slots(self, service_id: int, query_date: date) -> List[Slot]:
        """
        Get available time slots for a service on a specific date
        """
        # Get raw slot data from the repository
        raw_slots = self.availability_repo.get_available_slots(service_id, query_date)

        # Convert to Slot objects
        slots = []
        for slot_data in raw_slots:
            slot = Slot(
                time=slot_data["time"],
                available=slot_data["available"]
            )
            slots.append(slot)

        return slots

    def create_appointment(self, appointment_data: AppointmentCreate) -> Appointment:
        """
        Create a new appointment
        """
        # Check if the requested time slot is available
        if not self.availability_repo.is_slot_available(
            appointment_data.service_id,
            appointment_data.appointment_date,
            appointment_data.appointment_time
        ):
            raise ValueError("Horário indisponível")

        # Check for conflicts (double-booking)
        conflict = self._check_conflict(
            appointment_data.barber_id,
            appointment_data.appointment_date,
            appointment_data.appointment_time
        )

        if conflict:
            raise ValueError("Horário já ocupado")

        # Create the appointment
        appointment = Appointment(
            service_id=appointment_data.service_id,
            barber_id=appointment_data.barber_id,
            customer_id=appointment_data.customer_id,
            appointment_date=appointment_data.appointment_date,
            appointment_time=appointment_data.appointment_time,
            observations=appointment_data.observations
        )

        # Save to database
        self.db.add(appointment)
        self.db.commit()
        self.db.refresh(appointment)

        # Mark the time slot as unavailable
        self.availability_repo.mark_slot_as_unavailable(
            appointment_data.service_id,
            appointment_data.appointment_date,
            appointment_data.appointment_time
        )

        return appointment

    def _check_conflict(self, barber_id: int, query_date: date, query_time: time):
        """
        Check if there's already an appointment for the barber at the specified date and time
        Returns the conflicting appointment if found, None otherwise
        """
        # Query the database for existing appointments with the same barber, date, and time
        return self.db.query(Appointment).filter(
            Appointment.barber_id == barber_id,
            Appointment.appointment_date == query_date,
            Appointment.appointment_time == query_time
        ).first()