// Exemplo de teste unitário seguindo TDD para o módulo vertical
// Este arquivo demonstra como os testes seriam escritos seguindo TDD

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { BookingForm } from '@/modules/appointments/frontend/components/BookingForm'
import { useAvailability } from '@/modules/appointments/frontend/hooks/useAvailability'
import api from '@/modules/appointments/frontend/lib/api'

// Mock do hook useAvailability
vi.mock('@/modules/appointments/frontend/hooks/useAvailability')
// Mock do módulo api
vi.mock('@/modules/appointments/frontend/lib/api')

describe('BookingForm - Fluxo de Agendamento (TDD)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('deve exibir formulário de agendamento com serviço e data selecionados', () => {
    // Arrange - Dados de teste
    const mockDate = '2024-01-15'
    const mockServiceId = 1
    const mockSlots = [
      { time: '09:00', available: true },
      { time: '09:30', available: true },
      { time: '10:00', available: false }
    ]

    // Mock do hook de availability
    ;(useAvailability as jest.Mock).mockReturnValue({
      data: mockSlots,
      isLoading: false,
      error: null
    })

    // Act - Renderizar componente
    render(<BookingService serviceId={mockServiceId} date={mockDate} />)

    // Assert - Verificações iniciais
    expect(screen.getByText(/selecione um horário/i)).toBeInTheDocument()

    // Verificar que os horários disponíveis são exibidos
    const availableSlots = screen.getAllByRole('button', { name: /09:00|09:30/i })
    expect(availableSlots).toHaveLength(2)

    // Verificar que horário indisponível está desabilitado
    const unavailableSlot = screen.getByRole('button', { name: /10:00/i })
    expect(unavailableSlot).toBeDisabled()
  })

  it('deve permitir seleção de horário e avançar para confirmação', () => {
    // Arrange
    const mockDate = '2024-01-15'
    const mockServiceId = 1
    const mockSlots = [{ time: '09:30', available: true }]

    ;(useAvailability as jest.Mock).mockReturnValue({
      data: mockSlots,
      isLoading: false,
      error: null
    })

    // Mock da API de agendamento
    ;(api.post as jest.Mock).mockResolvedValue({
      data: { id: 123, status: 'confirmed' }
    })

    // Act
    render(<BookingService serviceId={mockServiceId} date={mockDate} />)

    // Selecionar horário disponível
    const slotButton = screen.getByRole('button', { name: /09:30/i })
    fireEvent.click(slotButton)

    // Clicar no botão de confirmação
    const confirmButton = screen.getByRole('button', { name: /confirmar agendamento/i })
    fireEvent.click(confirmButton)

    // Assert
    expect(api.post).toHaveBeenCalledWith('/appointments', {
      service_id: mockServiceId,
      date: mockDate,
      time: '09:30'
    })

    expect(screen.getByText(/agendamento confirmado!/i)).toBeInTheDocument()
  })

  it('deve lidar com erro de agendamento e exibir mensagem apropriada', () => {
    // Arrange
    const mockDate = '2024-01-15'
    const mockServiceId = 1
    const mockSlots = [{ time: '09:30', available: true }]

    ;(useAvailability as jest.Mock).mockReturnValue({
      data: mockSlots,
      isLoading: false,
      error: null
    })

    // Mock da API retornando erro
    ;(api.post as jest.Mock).mockRejectedValue({
      response: { data: { message: 'Horário não disponível' } }
    })

    // Act
    render(<BookingService serviceId={mockServiceId} date={mockDate} />)

    const slotButton = screen.getByRole('button', { name: /09:30/i })
    fireEvent.click(slotButton)

    const confirmButton = screen.getByRole('button', { name: /confirmar agendamento/i })
    fireEvent.click(configureButton)

    // Assert
    expect(screen.getByText(/horário não disponível/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /tentar novamente/i })).toBeEnabled()
  })
})