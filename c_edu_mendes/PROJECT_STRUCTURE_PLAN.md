# ESTRUTURA DO PROJETO: BARBERSHOP SAAS (VERSÃO ARQUITETURA ENTERPRISE)
## Arquitetura Monolítica Modular com Camadas Limpas, Vertical Slicing e TDD
### Frontend: React Next.js | Backend: Python (FastAPI + Camadas Limpas)

## 1. ESTRUTURA DE DIRETÓRIOS ATUALIZADA (CAMADAS LIMPAS + VERTICAL SLICING)

```
barbershop-saas/
├── docs/                     # Documentação do projeto
│   ├── PLANO_BARBEARIA_SAAS.md
│   ├── API_SPECS.md
│   └── ARCHITECTURE_DECISIONS.md  # Registro de decisões arquiteturais
├── src/                      # Código-fonte principal (monolito modular)
│   ├── shared/               # Código compartilhado entre módulos (kernels)
│   │   ├── lib/              # Utilitários, helpers, tipos compartilhados
│   │   ├── config/           # Configurações de ambiente
│   │   ├── types/            # Tipos TypeScript compartilhados
│   │   ├── constants/        # Constantes compartilhadas
│   │   ├── hooks/            # Custom hooks reutilizáveis (frontend)
│   │   ├── exceptions/       # Exceções de domínio compartilhadas
│   │   └── events/           # Eventos de domínio compartilhados (para future async)
│   │
│   ├── modules/              # Vertical Slices (feature modules) - CADA UM SEGUE AS CAMADAS LIMPAS
│   │   ├── auth/             # Autenticação e autorização
│   │   │   ├── presentation/     # API FastAPI, schemas, dependências
│   │   │   │   ├── api/          # Rotas (controllers)
│   │   │   │   ├── schemas/      # Schemas Pydantic para validação de entrada/saída
│   │   │   │   └── dependencies.py # Dependências reutilizáveis (auth, paginação)
│   │   │   │
│   │   │   ├── application/      # Casos de uso (use services), application services
│   │   │   │   ├── use_cases/    # Comandos e queries específicos (ex: LoginUseCase)
│   │   │   │   └── services/     # Serviços de aplicação (orquestram múltiplos use cases)
│   │   │   │
│   │   │   ├── domain/           # Modelo de domínio puro (sem dependências de framework)
│   │   │   │   ├── entities/     # Entidades de domínio (User, Role, Permission)
│   │   │   │   ├── value_objects/ # Value Objects (Email, PasswordHash, Token)
│   │   │   │   ├── repositories/ # Interfaces de repositório (portas)
│   │   │   │   └── services/     # Serviços de domínio (regras de negócio complexas)
│   │   │   │
│   │   │   ├── infrastructure/   # Implementações de detalhes externos
│   │   │   │   ├── db/           # Implementações SQLAlchemy dos repositórios
│   │   │   │   ├── cache/        # Implementações Redis (se aplicável)
│   │   │   │   ├── external/     # Gateways para APIs externas (Auth0, etc.)
│   │   │   │   ├── messaging/    # Producers/Consumers para eventos (future)
│   │   │   │   └── persistence/  # Mapeamentos ORM, migrations
│   │   │   │
│   │   │   └── tests/            # Testes específicos do módulo (por camada)
│   │   │       ├── unit/         # Testes unitários (domínio, application)
│   │   │       ├── integration/  # Testes de integração (API + DB)
│   │   │       └── e2e/          # Testes end-to-end (Cypress)
│   │   │
│   │   └── module.py           # Ponto de entrada do módulo (registro de rotas, DI container)
│   │
│   ├── customers/            # Gestão de clientes (segue mesma estrutura acima)
│   ├── barbershops/          # Gestão de barbearias e barbeiros
│   ├── appointments/         # Agendamento de horários
│   ├── payments/             # Processamento de pagamentos
│   ├── notifications/        # Sistema de notificações (WhatsApp/SMS)
│   ├── crm/                  # CRM Inteligente
│   ├── waitlist/             # Fila de espera inteligente
│   ├── dashboard/            # Dashboard de métricas
│   └── facial-analysis/      # Análise facial para sugestões de estilo
│
└── shared/                   # Código compartilhado entre módulos (backend)
    ├── presentation/         # Middleware comum (auth, logging, rate limiting)
    ├── application/          # Serviços de aplicação transversais (ex: EventPublisher)
    ├── domain/               # Kernels de domínio compartilhados (ex: BaseEntity)
    └── infrastructure/       # Configurações compartilhadas (db, cache, clientes externos)
```

## 2. PRINCÍPIOS ARQUITETURAIS (PER RENATO AUGUSTO)

### A. Separação Estrita de Responsabilidades (Clean Architecture)
**Regra de Ouro:** Nada na camada de `domain/` sabe de FastAPI, SQLAlchemy ou qualquer framework externo. Dependências apontam **para dentro**.

#### Exemplo Prático: Módulo `appointments/`
```
appointments/
├── domain/
│   ├── entities/
│   │   └── Appointment.py          # Puro: atributos, métodos de negócio (ex: is_valid_time())
│   ├── value_objects/
│   │   ├── AppointmentId.py        # VO imutável
│   │   └── TimeSlot.py             # VO com validação de horário
│   ├── repositories/
│   │   └── AppointmentRepository.py # INTERFACE: define contratos (NÃO implementação)
│   │       def get_by_id(self, id: AppointmentId) -> Optional[Appointment]: ...
│   │       def save(self, appointment: Appointment) -> None: ...
│   │       def find_available_slots(self, service_id: int, date: date) -> List[TimeSlot]: ...
│   └── services/
│       └── BookingPolicy.py        # Serviço de domínio: regras complexas (ex: verificar conflitos, buffers)
│           def can_book(self, appointment: Appointment, existing: List[Appointment]) -> bool: ...
│
├── application/
│   ├── use_cases/
│   │   ├── BookAppointmentUseCase.py   # Orquestra: valida → verifica política → salva
│   │   └── CancelAppointmentUseCase.py
│   └── services/
│       └── AppointmentApplicationService.py # Serviço de aplicação: transações, eventos
│           def book_appointment(self, cmd: BookAppointmentCommand) -> AppointmentId: ...
│
├── presentation/
│   ├── api/
│   │   └── appointment_router.py     # FastAPI: apenas traduz HTTP → comando de aplicação
│   │       @router.post("")
│   │       async def book_appointment(
│   │           cmd: BookAppointmentCommand,  # Valido via Pydantic
│   │           use_case: BookAppointmentUseCase = Depends()
│   │       ): ...
│   ├── schemas/
│   │   ├── BookAppointmentCommand.py   # Entrada da API (dados válidos)
│   │   └── AppointmentResponse.py      # Saída da API
│   └── dependencies.py                # Injeção de dependência (liga ao container)
│
└── infrastructure/
    ├── db/
    │   ├── SQLAlchemyAppointmentRepository.py # IMPLEMENTAÇÃO da interface de domínio
    │   └── mappings/
    │       └── AppointmentMap.py        # Mapeamentos ORM (entidade → tabela)
    └── persistence/
        └── alembic/
            └── versions/
                └── xxx_create_appointments_table.py
```

### B. Padrões de Design Específicos para Nossa Domínio
Selecionamos patterns **por necessidade real**, não por vaidade acadêmica:

| Padrão | Onde Aplicar | Exemplo Barbearia | Por que É Necessário |
|--------|--------------|-------------------|----------------------|
| **Repository** | `domain/repositories/` em todos os módulos | `CustomerRepository`, `BarberRepository` | Isola regras de negócio de detalhes de persistência; permite trocar DB sem afetar domínio |
| **Factory** | `application/services/` ou `domain/services/` | `AppointmentFactory` (cria agendamento com validação de buffers) | Encapsula criação complexa de objetos com regras de negócio (ex: não agendar corte de 60min em slot de 15min) |
| **Strategy** | `application/services/` | `PaymentStrategy`: `PixStrategy`, `CreditCardStrategy`, `CashStrategy` | Permite trocar algoritmo de pagamento em tempo real; isolado de gateways externos |
| **Adapter** | `infrastructure/external/` | `TwilioWhatsAppAdapter`, `MercadoPagoAdapter` | Isola código de domínio de APIs externas específicas; facilita troca de provedor |
| **Observer/Event** | `shared/events/` + `infrastructure/messaging/` | Eventos: `AppointmentBooked`, `CustomerChurnRisk` | Base para futura evolução assíncrona (sem acoplar use cases a implementação de mensageria) |
| **Circuit Breaker** | `infrastructure/external/` | Em gateways de pagamento/WhatsApp | Evita cascata de falhas quando serviço externo cai (ex: WhatsApp API indisponível) |

### C. Evolução Arquitetural: Das 4 Eras que Você Descreveu
Mapeamos exatamente como isso se aplica ao nosso roadmap:

#### ERA 1 — Foundation (FASES 1-3 no nosso plano atual)
- **Foco:** Modelagem de domínio camada a camada
- **Atividades:**
  - Definir Value Objects (ex: `PhoneNumber`, `ServicePrice`)
  - Mapear invariantes de negócio (ex: "um corte não pode ter duração < 15min")
  - Escrever testes de domínio primeiro (TDD puro)
  - **Nenhum framework tocado ainda** - apenas classes puras de Python/TS

#### ERA 2 — Revenue Engine (FASES 4-6)
- **Foco:** Implementar use cases que geram receita
- **Atividades:**
  - Casos de uso como `ProcessPaymentUseCase`, `SendChurnPreventionMessageUseCase`
  - Integração com gateways via **Adapter Pattern** (não acoplado)
  - Testes de aplicação mockando apenas as portas (repositórios, gateways)
  - API como camada fina de tradução (nenhuma regra de negócio aqui)

#### ERA 3 — Scale (FASES 7-9)
- **Foco:** Otimizar onde dói (medido, não adivinhado)
- **Atividades:**
  - Identificar gargalos reais via observabilidade (ex: consulta de agendamentos lenta)
  - Aplicar **Cache Strategy** apenas no `infrastructure/cache/` (ex: Redis para horários populares)
  - Extrair módulo para próprio serviço **apenas se**: 
    - Taxa de falha >5% após otimizações
    - Throughput necessário >70% da capacidade do monolito
    - Equipe dedicada disponível
  - Usar **Strangler Fig Pattern** para migração gradual

#### ERA 4 — Distributed Systems (FASE 10)
- **Foco:** Escalabilidade horizontal apenas quando comprovado necessário
- **Atividades:**
  - Introduzir **Message Broker** (RabbitMQ/Kafka) apenas para eventos críticos
  - Manter compatibilidade: uso cases continuam funcionando (eles publicam eventos, não sabem se é sync/async)
  - Serviços extraídos compartilham o mesmo kernel de domínio (`shared/domain/`)

### D. Resiliência Engineering Integrada (FASE 7.5)
Conforme sua sugestão, adicionamos desde o início:
- **Retries com Exponential Backoff** em `infrastructure/external/` gateways
- **Timeouts configuráveis** por chamada externa
- **Circuit Breaker** (usando biblioteca como `pycircuitbreaker`) em gateways de pagamento/WhatsApp
- **Fallbacks** (ex: se WhatsApp falhar, enviar SMS; se SMS falhar, logar para retry manual)
- **Dead Letter Queue** implementada como tabela simples no PostgreSQL inicialmente (evolui para Redis Stream/Kafka depois)

## 3. FLUXO DE DESENVLOVIMENTO TDD ATUALIZADO (COM CAMADAS LIMPAS)

Para cada história de usuário, seguimos este ciclo **respeitando as camadas**:

### Fase 1: Domínio Primeiro (TDD Puro)
1. **Escrever teste de unidade para Value Object/Entidade** (ex: `TestAppointmentId`)
   - Nada de mocks, apenas classes puras
2. **Implementar o VO/Entidade** para fazer teste passar
3. **Escrever teste para Serviço de Domínio** (ex: `TestBookingPolicy`)
   - Testa regras de negócio complexas
4. **Implementar o Serviço de Domínio**
5. **Escrever teste para Interface de Repositório** (apenas contrato - opcional)

### Fase 2: Application Layer
1. **Escrever teste de unidade para Use Case** (ex: `TestBookAppointmentUseCase`)
   - Mock apenas repositório e serviços de domínio
2. **Implementar o Use Case**
3. **Escrever teste para Service de Aplicação** (se necessário)
   - Testa transações, publicação de eventos
4. **Implementar o Service de Aplicação**

### Fase 3: Presentation Layer (API)
1. **Escrever teste de contrato** (ex: testar schema de entrada/saída com dados válidos/inválidos)
2. **Escrever teste de integração para API endpoint**
   - Usa TestClient do FastAPI
   - Mock apenas application layer (use cases)
3. **Implementar o Controller/API endpoint**
   - APENAS traduz HTTP → comando de aplicação
   - ZERO regra de negócio

### Fase 4: Infrastructure Layer
1. **Escrever teste de unidade para implementação de repositório**
   - Usa banco em memória (SQLite) ou mocks de chamadas externas
2. **Implementar a Implementação do Repositório**
3. **Escrever teste de contrato para gateway externo** (ex: TwilioAdapter)
4. **Implementar o Adapter**

### Fase 5: Validação de Integração
1. **Executar teste de integração completo** (API + banco real)
2. **Executar teste E2E do fluxo de usuário**
3. **Verificar que nenhuma regra de negócio vazou para camadas externas**

## 4. CHECKLIST DE DECISÃO ARQUITETURAL (NOVO)

Antes de qualquer implementação, responderemos:
- [ ] **Isso pertence ao domain/application/ ou infrastructure/presentation/?**  
  *(Se sim, está no lugar errado)*
- [ ] **Estou vazando detalhes de framework para o domínio?**  
  *(Ex: usando `Request` do FastAPI em uma entidade)*
- [ ] **Este padrão resolve um problema real ou é apenas vaidade técnica?**  
  *(Aplicamos apenas se houver dor medida)*
- [ ] **Como isso evoluirá se precisarmos escalar?**  
  *(Design para substituição futura, não para permanência)*
- [ ] **O teste de domínio mais interno está passando sem mocks de framework?**  
  *(O verdadeiro teste de arquitetura limpa)*

## 5. PRÓXIMOS PASSOS IMEDIATOS (CONSOLIDANDO A FASE 2)

Antes de escrever uma linha de código funcional:
1. **Criar arquivo `ARCHITECTURE_DECISIONS.md`** em `docs/` para registrar:
   - Decisões sobre camadas (por que escolhemos essa estrutura)
   - Padrões adotados e justificativas (ex: "Usamos Repository pois precisamos trocar de PostgreSQL para DynamoDB no futuro sem afetar domínio")
   - Decisões adiantadas (ex: "Não adotamos CQRS inicialmente pois complexidade não justifica para nosso volume inicial")
2. **Implementar o kernel de domínio compartilhado**:
   - `src/shared/domain/kernel.py` com classes base como `BaseEntity`, `DomainEvent`
   - `src/shared/domain/value_objects.py` com VO genéricos (Email, PhoneNumber, etc.)
3. **Definir as primeiras interfaces de repositório** em um módulo de baixo risco (ex: `customers`):
   - `src/modules/customers/domain/repositories/CustomerRepository.py`
4. **Escrever o primeiro teste de domínio puro** (ex: teste de Value Object `PhoneNumber`)
   - Este teste deve rodar **sem nenhum framework instalado** (apenas Python puro)

### Exemplo Prático: Primeiro Teste de Domínio (Customer PhoneNumber)
```python
# tests/unit/domain/value_objects/test_phone_number.py
# NENHUM IMPORT DE FRAMEWORK AQUI - APENAS PYTHON PURO

def test_phone_number_valida_formato_brasileiro():
    # Arrange
    numero_valido = "+55 11 99999-8888"
    
    # Act
    phone = PhoneNumber(numero_valido)
    
    # Assert
    assert phone.country_code == "55"
    assert phone.area_code == "11"
    assert phone.number == "99999-8888"
    assert str(phone) == "+55 11 99999-8888"

def test_phone_number_lanca_erro_para_formato_invalido():
    # Arrange
    numero_invalido = "1199998888"  # faltando +55 e formatação
    
    # Act & Assert
    with pytest.raises(ValueError, match="Formato de telefone inválido"):
        PhoneNumber(numero_invalido)
```

**Este é o verdadeiro início do TDD arquitetural:** testar regras de negócio em isolamento absoluto antes de tocar em qualquer framework.

## 6. EXEMPLOS CONCRETOS DE IMPLEMENTAÇÃO

### Value Object de Telefone (Domain Layer)
```python
# src/shared/domain/value_objects/phone_number.py
from dataclasses import dataclass
import re

@dataclass(frozen=True)
class PhoneNumber:
    country_code: str
    area_code: str
    number: str
    
    def __post_init__(self):
        if not re.match(r'^\d{2} \d{2} \d{4,5}-\d{4}$', f"{self.country_code} {self.area_code} {self.number}"):
            raise ValueError("Formato de telefone inválido. Use: XX XX XXXXX-XXXX ou XX XX XXXX-XXXX")
    
    @classmethod
    def from_string(cls, phone_str: str) -> 'PhoneNumber':
        # Remove caracteres não numéricos exceto +
        clean = re.sub(r'[^\d+]', '', phone_str)
        if not clean.startswith('+55'):
            raise ValueError("Apenas números brasileiros são suportados (+55)")
        
        # Formata para XX XX XXXX-XXXX ou XX XX XXXXX-XXXX
        digits = clean[3:]  # Remove +55
        if len(digits) == 8:
            formatted = f"{digits[:2]} {digits[2:4]}-{digits[4:]}"
        elif len(digits) == 9:
            formatted = f"{digits[:2]} {digits[2:5]}-{digits[5:]}"
        else:
            raise ValueError("Número de telefone inválido")
        
        parts = formatted.split()
        return cls(country_code="55", area_code=parts[0], number=parts[1])
    
    def __str__(self) -> str:
        return f"+{self.country_code} {self.area_code} {self.number}"
```

### Serviço de Domínio para Políticas de Agendamento
```python
# src/modules/appointments/domain/services/booking_policy.py
from typing import List
from ..entities.appointment import Appointment

class BookingPolicy:
    """Regras de negócio puras para agendamento"""
    
    MIN_APPOINTMENT_DURATION = 15  # minutos
    MAX_APPOINTMENT_DURATION = 180  # minutos
    BUFFER_BETWEEN_APPOINTMENTS = {
        'simple': 5,   # corte simples
        'complex': 10  # corte + barba
    }
    
    def validate_duration(self, duration_minutes: int) -> bool:
        """Valida se a duração está dentro dos limites permitidos"""
        return self.MIN_APPOINTMENT_DURATION <= duration_minutes <= self.MAX_APPOINTMENT_DURATION
    
    def can_book_appointment(self, new_appointment: Appointment, existing_appointments: List[Appointment]) -> bool:
        """Verifica se é possível agendar considerando conflitos e buffers"""
        # Verifica conflitos de horário
        for existing in existing_appointments:
            if self._times_overlap(new_appointment, existing):
                return False
        
        # Verifica buffers necessários
        return self._respects_buffers(new_appointment, existing_appointments)
    
    def _times_overlap(self, a1: Appointment, a2: Appointment) -> bool:
        """Verifica se dois horários se sobrepõem"""
        return not (a1.ends_before(a2.start) or a2.ends_before(a1.start))
    
    def _respects_buffers(self, new_appointment: Appointment, existing: List[Appointment]) -> bool:
        """Verifica se os buffers necessários são respeitados"""
        # Implementação simplificada - verifica se há tempo suficiente entre compromissos
        all_appointments = sorted(existing + [new_appointment], key=lambda x: x.start_time)
        
        for i in range(len(all_appointments) - 1):
            current = all_appointments[i]
            next_appt = all_appointments[i + 1]
            
            gap_minutes = (next_appt.start_time - current.end_time).total_seconds() / 60
            required_buffer = self.BUFFER_BETWEEN_APPOINTMENTS.get(
                current.service_type, 
                self.BUFFER_BETWEEN_APPOINTMENTS['complex']  # padrão conservador
            )
            
            if gap_minutes < required_buffer:
                return False
                
        return True
```

### Use Case de Aplicação
```python
# src/modules/appointments/application/use_cases/book_appointment_use_case.py
from dataclasses import dataclass
from datetime import date, time
from typing import Optional
from ....shared.domain.value_objects.appointment_id import AppointmentId
from ....modules.appointments.domain.entities.appointment import Appointment
from ....modules.appointments.domain.repositories.appointment_repository import AppointmentRepository
from ....modules.appointments.domain.services.booking_policy import BookingPolicy

@dataclass(frozen=True)
class BookAppointmentCommand:
    customer_id: int
    barber_id: int
    service_id: int
    appointment_date: date
    appointment_time: time
    notes: str = ""

class BookAppointmentUseCase:
    def __init__(
        self,
        appointment_repo: AppointmentRepository,
        booking_policy: BookingPolicy
    ):
        self._appointment_repo = appointment_repo
        self._booking_policy = booking_policy
    
    def execute(self, command: BookAppointmentCommand) -> AppointmentId:
        # Validações de domínio (delegadas para objetos de valor e entidades)
        appointment = Appointment.create(
            customer_id=command.customer_id,
            barber_id=command.barber_id,
            service_id=command.service_id,
            date=command.appointment_date,
            time=command.appointment_time,
            notes=command.notes
        )
        
        # Verifica regras de negócio complexas
        existing_appointments = self._appointment_repo.find_by_barber_and_date(
            command.barber_id, 
            command.appointment_date
        )
        
        if not self._booking_policy.can_book_appointment(appointment, existing_appointments):
            raise ValueError("Horário indisponível devido a conflitos ou buffers insuficientes")
        
        # Persiste (via interface de domínio - não sabe de implementação)
        self._appointment_repo.save(appointment)
        
        return appointment.id
```

### Controller de Apresentação (API)
```python
# src/modules/appoints/presentation/api/appointment_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from .....shared.presentation.dependencies import get_current_user
from ..application.use_cases.book_appointment_use_case import BookAppointmentUseCase, BookAppointmentCommand
from ..application.dependencies import get_book_appointment_use_case
from .schemas import AppointmentResponse

router = APIRouter(prefix="/appointments", tags=["appointments"])

@router.post("", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def book_appointment(
    command: BookAppointmentCommand,
    user_id: int = Depends(get_current_user),  # Auth middleware
    book_appointment_use_case: BookAppointmentUseCase = Depends(get_book_appointment_use_case)
):
    try:
        appointment_id = book_appointment_use_case.execute(command)
        return AppointmentResponse(
            id=appointment_id,
            message="Agendamento criado com sucesso"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao processar agendamento"
        )
```

### Implementação de Repositório (Infrastructure)
```python
# src/modules/appointments/infrastructure/db/sqlalchemy_appointment_repository.py
from typing import List, Optional
from sqlalchemy.orm import Session
from ....domain.entities.appointment import Appointment
from ....domain.value_objects.appointment_id import AppointmentId
from ....domain.repositories.appointment_repository import AppointmentRepository
from ..mappings.appointment_map import AppointmentModel

class SQLAlchemyAppointmentRepository(AppointmentRepository):
    def __init__(self, session: Session):
        self._session = session
    
    def save(self, appointment: Appointment) -> None:
        db_appointment = AppointmentModel.from_domain(appointment)
        self._session.add(db_appointment)
        self._session.commit()
        self._session.refresh(db_appointment)
    
    def get_by_id(self, appointment_id: AppointmentId) -> Optional[Appointment]:
        db_appointment = self._session.query(AppointmentModel).filter(
            AppointmentModel.id == appointment_id.value
        ).first()
        return db_appointment.to_domain() if db_appointment else None
    
    def find_by_barber_and_date(self, barber_id: int, date: date) -> List[Appointment]:
        db_appointments = self._session.query(AppointmentModel).filter(
            AppointmentModel.barber_id == barber_id,
            AppointmentModel.appointment_date == date
        ).all()
        return [apt.to_domain() for apt in db_appointments]
    
    def find_available_slots(self, service_id: int, date: date) -> List['TimeSlot']:
        # Implementação simplificada - em produção seria mais complexa
        booked_slots = self._session.query(AppointmentModel).filter(
            AppointmentModel.service_id == service_id,
            AppointmentModel.appointment_date == date
        ).all()
        
        # Gera slots disponíveis baseado em horário de funcionário e duração do serviço
        # Esta é uma implementação simplificada para demonstrar o conceito
        all_slots = self._generate_time_slots(8, 18)  # 8h às 18h
        booked_times = {appt.appointment_time for appt in booked_slots}
        
        return [slot for slot in all_slots if slot not in booked_times]
    
    def _generate_time_slots(self, start_hour: int, end_hour: int) -> List[time]:
        slots = []
        current_hour = start_hour
        while current_hour < end_hour:
            slots.append(time(hour=current_hour, minute=0))
            slots.append(time(hour=current_hour, minute=30))
            current_hour += 1
        return slots
```

## 7. EXEMPLO DE TESTE DE DOMÍNIO PURO

### Teste para Value Object PhoneNumber
```python
# tests/unit/domain/value_objects/test_phone_number.py
import pytest
from src.shared.domain.value_objects.phone_number import PhoneNumber

def test_phone_number_valida_formato_brasileiro():
    """Testa que números de telefone brasileiros válidos são aceitos"""
    # Act
    phone = PhoneNumber.from_string("+55 11 99999-8888")
    
    # Assert
    assert phone.country_code == "55"
    assert phone.area_code == "11"
    assert phone.number == "99999-8888"
    assert str(phone) == "+55 11 99999-8888"

def test_phone_number_aceita_formato_com_8_digitos():
    """Testa formato antigo de 8 dígitos"""
    phone = PhoneNumber.from_string("+55 11 9999-8888")
    assert phone.country_code == "55"
    assert phone.area_code == "11"
    assert phone.number == "9999-8888"
    assert str(phone) == "+55 11 9999-8888"

def test_phone_number_rejeita_numero_estrangeiro():
    """Testa que números não brasileiros são rejeitados"""
    with pytest.raises(ValueError, match="Apenas números brasileiros são suportados"):
        PhoneNumber.from_string("+1 212 555-1234")

def test_phone_number_rejeita_formato_invalido():
    """Testa que formatos inválidos são rejeitados"""
    with pytest.raises(ValueError, match="Formato de telefone inválido"):
        PhoneNumber.from_string("1199998888")  # faltando +55 e formatação
    
    with pytest.raises(ValueError, match="Formato de telefone inválido"):
        PhoneNumber.from_string("+55 11 99999-888")  # dígitos faltando
```

### Teste para Serviço de Domínio (BookingPolicy)
```python
# tests/unit/domain/services/test_booking_policy.py
import pytest
from datetime import date, time
from src.modules.appointments.domain.entities.appointment import Appointment
from src.modules.appointments.domain.services.booking_policy import BookingPolicy

def test_booking_policy_validates_duration():
    """Testa validação de duração de agendamento"""
    policy = BookingPolicy()
    
    # Durações válidas
    assert policy.validate_duration(15) == True   # mínimo
    assert policy.validate_duration(60) == True   # normal
    assert policy.validate_duration(180) == True  # máximo
    
    # Durações inválidas
    assert policy.validate_duration(10) == False  # muito curto
    assert policy.validate_duration(200) == False # muito longo

def test_booking_policy_detects_overlap():
    """Testa detecção de conflitos de horário"""
    policy = BookingPolicy()
    
    # Cria dois agendamentos que se sobrepõem
    apt1 = Appointment.create(
        customer_id=1, barber_id=1, service_id=1,
        date=date(2024, 1, 15),
        time=time(10, 0),  # 10:00
        notes="Corte"
    )
    
    apt2 = Appointment.create(
        customer_id=2, barber_id=1, service_id=1,
        date=date(2024, 1, 15),
        time=time(10, 30),  # 10:30 - sobrepõe com 10:00-11:00
        notes="Barba"
    )
    
    # Deve detectar conflito
    assert policy.can_book_appointment(apt2, [apt1]) == False
    
    # Teste sem overlap
    apt3 = Appointment.create(
        customer_id=3, barber_id=1, service_id=1,
        date=date(2024, 1, 15),
        time=time(11, 0),  # 11:00 - não sobrepõe
        notes="Corte"
    )
    
    # Sem conflito (assumindo duração padrão de 60min)
    assert policy.can_book_appointment(apt3, [apt1]) == True
```

## 8. EXEMPLO DE TESTE DE INTEGRAÇÃO (API + DB)

### Teste de Integração para Endpoint de Agendamento
```python
# tests/integration/test_appointment_api.py
import pytest
from datetime import date, time
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.shared.backend.main import app
from src.shared.backend.database import Base, get_db

# Configuração de banco de teste em memória
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

def test_book_appointment_success(client: TestClient):
    """Testa criação bem-sucedida de agendamento via API"""
    # Arrange
    appointment_data = {
        "customer_id": 1,
        "barber_id": 1,
        "service_id": 1,  # Corte Social
        "appointment_date": "2024-01-15",
        "appointment_time": "10:00:00",
        "notes": "Fade baixo e barba desenhada"
    }
    
    # Act
    response = client.post("/api/v1/appointments", json=appointment_data)
    
    # Assert
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["message"] == "Agendamento criado com sucesso"
    
    # Verifica que foi realmente salvo no banco
    from sqlalchemy.orm import Session
    db = TestingSessionLocal()
    from src.modules.appointments.infrastructure.db.sqlalchemy_appointment_repository import SQLAlchemyAppointmentRepository
    repo = SQLAlchemyAppointmentRepository(db)
    appointment = repo.get_by_id(data["id"])
    assert appointment is not None
    assert appointment.customer_id == 1
    assert appointment.barber_id == 1
    assert appointment.service_id == 1
    db.close()

def test_book_appointment_conflict(client: TestClient):
    """Testa rejeição de agendamento em horário conflitante"""
    # Arrange - cria primeiro agendamento
    appointment1 = {
        "customer_id": 1,
        "barber_id": 1,
        "service_id": 1,
        "appointment_date": "2024-01-15",
        "appointment_time": "10:00:00",
        "notes": "Corte"
    }
    client.post("/api/v1/appointments", json=appointment1)
    
    # Act - tenta criar segundo agendamento em horário sobreposto
    appointment2 = {
        "customer_id": 2,
        "barber_id": 1,
        "service_id": 1,
        "appointment_date": "2024-01-15",
        "appointment_time": "10:30:00",  # Sobrepõe com 10:00-11:00
        "notes": "Barba"
    }
    response = client.post("/api/v1/appointments", json=appointment2)
    
    # Assert
    assert response.status_code == 400
    assert "indisponível" in response.json()["detail"].lower()
```

## 9. PRÓXIMOS PASSOS IMEDIATOS

1. **Criar a estrutura de diretórios conforme especificada acima**
2. **Implementar os kernels de domínio compartilhados** (`src/shared/domain/`)
3. **Definir as primeiras entidades e value objects** (começando com `PhoneNumber`, `Email`)
4. **Estabelecer as primeiras interfaces de repositório** em um módulo simples (ex: `customers`)
5. **Escrever os primeiros testes de domínio puro** (validando que não há dependências de framework)
6. **Implementar o primeiro use case de aplicação** (ex: criar cliente)
7. **Criar o primeiro controller de apresentação** (endpoint API)
8. **Implementar a primeira implementação de repositório** (usando SQLAlchemy)
9. **Escrever testes de integração** validando o fluxo completo API → Application → Domain → Infrastructure → DB
10. **Configurar o pipeline de CI/CD** com testes automatizados

Esta abordagem garante que:
- **Regra de negócio permanece pura e testável** sem dependências de framework
- **Cada camada tem responsabilidade bem definida**
- **A evolução para microserviços é possível** quando necessário (sem reescrever regras de negócio)
- **A qualidade é mantida** através de TDD rigoroso em todas as camadas
- **O valor de negócio é entregue incrementalmente** através do vertical slicing

**Próximo passo:** Executar o setup inicial do projeto, criar a estrutura de diretórios e começar com o kernel de domínio compartilhado.