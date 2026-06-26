"""
Exemplo de teste unitário seguindo TDD para o backend do módulo vertical
Este arquivo demonstra como os testes seriam escritos seguindo TDD para o backend Python
"""

import pytest
from unittest.mock import Mock, patch
from datetime import date, time
from sqlalchemy.orm import Session

from src.modules.appointments.backend.services.booking_service import BookingService
from src.modules.appointments.backend.repositories.availability_repo import AvailabilityRepository
from src.modules.appointments.backend.models.appointment import Appointment
from src.modules.appointments.backend.schemas.appointment import AppointmentCreate, Slot


class TestBookingService:
    """Testes para o serviço de agendamento seguindo TDD"""

    def setup_method(self):
        """Setup executado antes de cada teste"""
        self.mock_db = Mock(spec=Session)
        self.mock_availability_repo = Mock(spec=AvailabilityRepository)
        self.booking_service = BookingService(
            db=self.mock_db,
            availability_repo=self.mock_availability_repo
        )

    def test_get_available_slots_deve_retornar_horarios_disponiveis(self):
        """
        TDD Step 1: Escrever teste FALHANDO
        Dado um serviço e data, quando buscar horários disponíveis,
        então deve retornar lista de horários com status de disponibilidade
        """
        # Arrange
        service_id = 1
        query_date = date(2024, 1, 15)

        # Mock do retorno do repository
        mock_raw_slots = [
            {"time": time(9, 0), "available": True},
            {"time": time(9, 30), "available": True},
            {"time": time(10, 0), "available": False}
        ]
        self.mock_availability_repo.get_available_slots.return_value = mock_raw_slots

        # Act
        result = self.booking_service.get_available_slots(service_id, query_date)

        # Assert
        assert len(result) == 3
        assert all(isinstance(slot, Slot) for slot in result)
        assert result[0].time == time(9, 0)
        assert result[0].available is True
        assert result[2].available is False

        # Verificar que o repository foi chamado corretamente
        self.mock_availability_repo.get_available_slots.assert_called_once_with(
            service_id, query_date
        )

    def test_get_available_slots_deve_tratar_erro_do_repository(self):
        """
        TDD Step 2: Testar caso de erro
        Quando o repository lançar exceção, o serviço deve tratá-la adequadamente
        """
        # Arrange
        service_id = 1
        query_date = date(2024, 1, 15)
        self.mock_availability_repo.get_available_slots.side_effect = Exception("DB Error")

        # Act & Assert
        with pytest.raises(Exception, match="DB Error"):
            self.booking_service.get_available_slots(service_id, query_date)

    def test_create_appointment_deve_criar_agendamento_valido(self):
        """
        TDD Step 3: Teste para criação de agendamento
        Dados válidos de agendamento devem resultar em criação bem-sucedida
        """
        # Arrange
        appointment_data = AppointmentCreate(
            customer_id=1,
            barber_id=2,
            service_id=3,
            appointment_date=date(2024, 1, 15),
            appointment_time=time(14, 30),
            observations="Fade baixo e barba desenhada"
        )

        mock_appointment = Appointment(
            id=1,
            service_id=appointment_data.service_id,
            barber_id=appointment_data.barber_id,
            customer_id=appointment_data.customer_id,
            appointment_date=appointment_data.appointment_date,
            appointment_time=appointment_data.appointment_time,
            observations=appointment_data.observations
        )

        # Mock do comportamento do banco
        self.mock_db.add = Mock()
        self.mock_db.commit = Mock()
        self.mock_db.refresh = Mock()

        # Mock the _check_conflict method to return None (no conflict)
        with patch.object(self.booking_service, '_check_conflict') as mock_check_conflict:
            mock_check_conflict.return_value = None

            # Act
            result = self.booking_service.create_appointment(appointment_data)

        # Assert
        assert result.customer_id == appointment_data.customer_id
        assert result.appointment_date == appointment_data.appointment_date
        assert result.appointment_time == appointment_data.appointment_time

        # Verificar interações com o banco
        self.mock_db.add.assert_called_once()
        self.mock_db.commit.assert_called_once()
        self.mock_db.refresh.assert_called_once()

    def test_create_appointment_deve_verificar_conflito_de_horario(self):
        """
        TDD Step 4: Teste para detecção de conflitos
        Não deve permitir agendamento em horário já ocupado
        """
        # Arrange
        appointment_data = AppointmentCreate(
            customer_id=1,
            barber_id=2,
            service_id=3,
            appointment_date=date(2024, 1, 15),
            appointment_time=time(14, 30)
        )

        # Simular que já existe agendamento neste horário
        existing_appointment = Appointment(
            id=999,
            service_id=3,
            barber_id=2,
            customer_id=1,
            appointment_date=date(2024, 1, 15),
            appointment_time=time(14, 30),
            observations="Existing appointment"
        )

        # Mock da query que verifica conflitos
        with patch.object(self.booking_service, '_check_conflict') as mock_check:
            mock_check.return_value = existing_appointment  # Conflito encontrado

            # Act & Assert
            with pytest.raises(ValueError, match="Horário já ocupado"):
                self.booking_service.create_appointment(appointment_data)

    def test_check_conflict_deve_retornar_none_quando_nao_haver_conflito(self):
        """
        TDD Step 5: Teste para método privado de verificação de conflitos
        Quando não houver conflito, deve retornar None
        """
        # Arrange
        barber_id = 2
        query_date = date(2024, 1, 15)
        query_time = time(14, 30)

        # Mock da query que não retorna resultados (nenhum conflito)
        self.mock_db.query.return_value.filter.return_value.first.return_value = None

        # Act
        result = self.booking_service._check_conflict(barber_id, query_date, query_time)

        # Assert
        assert result is None
        self.mock_db.query.assert_called_once()