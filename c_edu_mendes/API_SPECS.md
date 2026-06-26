# ESPECIFICAÇÃO DA API BARBEARIA SAAS

Este documento descreve a especificação da API RESTful do Barbearia SaaS, seguindo as convenções do OpenAPI 3.0.

## Visão Geral

A API é organizada por recursos de negócio, com versionamento por URL para garantir compatibilidade futura.

## Convenções

- **Versionamento**: `/api/v{version}/` (ex: `/api/v1/`)
- **Formato de Dados**: JSON para requisições e respostas
- **Codificação**: UTF-8
- **Métodos HTTP**: Seguem padrões RESTful
- **Códigos de Status**: 
  - 200: Sucesso
  - 201: Recurso criado
  - 204: No Content (sucesso sem corpo)
  - 400: Bad Request (erro de validação ou regra de negócio)
  - 401: Unauthorized (autenticação necessária)
  - 403: Forbidden (acesso negado)
  - 404: Not Found (recurso não existe)
  - 409: Conflict (conflito de estado)
  - 422: Unprocessable Entity (erro de validação detalhado)
  - 500: Internal Server Error (erro inesperado)

## Autenticação

A API utiliza autenticação baseada em JWT (JSON Web Tokens):

```
Authorization: Bearer <access_token>
```

Tokens de acesso têm validade curta (15 minutos) e são renovados usando refresh tokens.

## Rate Limiting

Para prevenir abusos, a API implementa rate limiting:
- 100 requisições por minuto por IP para endpoints não autenticados
- 1000 requisições por minuto por usuário autenticado
- Retorna HTTP 429 (Too Many Requests) quando excedido

## Manipulação de Erros

Todos os erros seguem um formato padronizado:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Descrição legível do erro",
    "details": [
      {
        "field": "nome_do_campo",
        "message": "Mensagem específica de validação"
      }
    ]
  }
}
```

## Endpoints

### Autenticação (`/auth`)

#### POST `/api/v1/auth/login`
Autentica um usuário e retorna tokens de acesso e atualização.

**Request Body:**
```json
{
  "email": "usuario@example.com",
  "senha": "senha123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4...",
  "expires_in": 900
}
```

#### POST `/api/v1/auth/refresh`
Renova um token de acesso usando um refresh token válido.

**Request Body:**
```json
{
  "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4..."
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 900
}
```

### Clientes (`/customers`)

#### GET `/api/v1/customers`
Lista todos os clientes com suporte a paginação e filtros.

**Query Parameters:**
- `page`: Número da página (padrão: 1)
- `limit`: Itens por página (padrão: 20, máximo: 100)
- `search`: Termo de busca em nome, email ou telefone
- `active_only`: Filtrar apenas clientes ativos (true/false)

**Response (200):**
```json
{
  "items": [
    {
      "id": 1,
      "nome": "João Silva",
      "email": "joao@example.com",
      "telefone": "+55 11 99999-8888",
      "data_nascimento": "1990-05-15",
      "ativo": true,
      "data_criacao": "2024-01-10T10:30:00Z",
      "data_atualizacao": "2024-01-15T14:22:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total_items": 150,
    "total_pages": 8
  }
}
```

#### GET `/api/v1/customers/{id}`
Obtém detalhes de um cliente específico.

**Response (200):**
```json
{
  "id": 1,
  "nome": "João Silva",
  "email": "joao@example.com",
  "telefone": "+55 11 99999-8888",
  "data_nascimento": "1990-05-15",
  "cpf": "123.456.789-09",
  "ativo": true,
  "preferencias": {
    "corte_preferido": "fade baixo",
    "barba_preferida": "desenhada",
    "observacoes": "Gosta de conversar sobre futebol"
  },
  "historico_visitas": [
    {
      "data": "2024-01-10",
      "servico": "Corte + Barba",
      "valor": 45.00
    }
  ],
  "data_criacao": "2024-01-10T10:30:00Z",
  "data_atualizacao": "2024-01-15T14:22:00Z"
}
```

#### POST `/api/v1/customers`
Cria um novo cliente.

**Request Body:**
```json
{
  "nome": "Maria Oliveira",
  "email": "maria@example.com",
  "telefone": "+55 11 88888-7777",
  "data_nascimento": "1985-08-22",
  "cpf": "987.654.321-00"
}
```

**Response (201):**
```json
{
  "id": 2,
  "mensagem": "Cliente criado com sucesso"
}
```

#### PUT `/api/v1/customers/{id}`
Atualiza um cliente existente.

**Request Body:**
```json
{
  "nome": "Maria Oliveira Santos",
  "telefone": "+55 11 88888-7777",
  "observacoes": "Prefere horários da tarde"
}
```

**Response (200):**
```json
{
  "id": 2,
  "mensagem": "Cliente atualizado com sucesso"
}
```

#### DELETE `/api/v1/customers/{id}`
Desativa um cliente (soft delete).

**Response (204):**
Nenhum corpo de resposta.

### Barbearia e Barbeiros (`/barbershops`)

#### GET `/api/v1/barbershops`
Lista barbearias com suporte a busca por localização.

**Query Parameters:**
- `latitude`: Latitude para busca por proximidade
- `longitude`: Longitude para busca por proximidade
- `raio`: Raio em kilómetros para busca (padrão: 5, máximo: 50)
- `servico`: Filtrar por serviço oferecido (ex: "corte", "barba")
- `dia_semana`: Filtrar por disponibilidade em dia específico (0-6, onde 0=domingo)
- `hora_min`: Hora mínima de funcionamento (HH:MM)
- `hora_max`: Hora máxima de funcionamento (HH:MM)

**Response (200):**
```json
{
  "items": [
    {
      "id": 1,
      "nome": "Barbearia do Zé",
      "endereco": {
        "logradouro": "Rua das Flores, 123",
        "bairro": "Centro",
        "cidade": "São Paulo",
        "estado": "SP",
        "cep": "01000-000"
      },
      "telefone": "+55 11 3333-4444",
      "avaliacao_media": 4.8,
      "total_avaliacoes": 156,
      "horario_funcionamento": {
        "segunda": "08:00-20:00",
        "terca": "08:00-20:00",
        "quarta": "08:00-20:00",
        "quinta": "08:00-20:00",
        "sexta": "08:00-22:00",
        "sabado": "09:00-20:00",
        "domingo": "Fechado"
      },
      "servicos": [
        {
          "id": 1,
          "nome": "Corte Social",
          "descricao": "Corte clássico com acabamento",
          "duracao_minutos": 30,
          "preco": 30.00
        },
        {
          "id": 2,
          "nome": "Corte + Barba",
          "descricao": "Corte completo com barba feita",
          "duracao_minutos": 45,
          "preco": 45.00
        }
      ],
      "distancia_km": 1.2
    }
  ]
}
```

#### GET `/api/v1/barbershops/{id}`
Obtém detalhes de uma barbearia específica.

**Response (200):**
```json
{
  "id": 1,
  "nome": "Barbearia do Zé",
  "descricao": "Barbearia tradicional com mais de 20 anos de experiência",
  "endereco": {
    "logradouro": "Rua das Flores, 123",
    "numero": "123",
    "complemento": "Loja 1",
    "bairro": "Centro",
    "cidade": "São Paulo",
    "estado": "SP",
    "cep": "01000-000",
    "latitude": -23.5505,
    "longitude": -46.6333
  },
  "telefone": "+55 11 3333-4444",
  "email": "contato@barbeariadoze.com.br",
  "cnpj": "12.345.678/0001-90",
  "horario_funcionamento": {
    "segunda": "08:00-20:00",
    "terca": "08:00-20:00",
    "quarta": "08:00-20:00",
    "quinta": "08:00-20:00",
    "sexta": "08:00-22:00",
    "sabado": "09:00-20:00",
    "domingo": "Fechado"
  },
  "barbeiros": [
    {
      "id": 1,
      "nome": "José Silva",
      "foto_perfil": "https://example.com/fotos/jose.jpg",
      "especialidades": ["Corte Americano", "Fade", "Barba Desenhada"],
      "avaliacao_media": 4.9,
      "total_atendimentos": 1250
    }
  ],
  "servicos": [
    {
      "id": 1,
      "nome": "Corte Social",
      "descricao": "Corte clássico com acabamento",
      "duracao_minutos": 30,
      "preco": 30.00,
      "ativo": true
    }
  ]
}
```

### Agendamentos (`/appointments`)

#### GET `/api/v1/appointments`
Lista agendamentos com filtros.

**Query Parameters:**
- `cliente_id`: Filtrar por cliente específico
- `barbeiro_id`: Filtrar por barbeiro específico
- `barbearia_id`: Filtrar por barbearia específica
- `data_inicio`: Data inicial para filtro (YYYY-MM-DD)
- `data_fim`: Data final para filtro (YYYY-MM-DD)
- `status`: Filtrar por status (agendado, confirmado, concluido, cancelado, nao_compareceu)
- `page`: Número da página (padrão: 1)
- `limit`: Itens por página (padrão: 20, máximo: 100)

**Response (200):**
```json
{
  "items": [
    {
      "id": 1,
      "cliente": {
        "id": 1,
        "nome": "João Silva",
        "telefone": "+55 11 99999-8888"
      },
      "barbeiro": {
        "id": 1,
        "nome": "José Silva",
        "foto_perfil": "https://example.com/fotos/jose.jpg"
      },
      "barbearia": {
        "id": 1,
        "nome": "Barbearia do Zé"
      },
      "servico": {
        "id": 1,
        "nome": "Corte + Barba",
        "duracao_minutos": 45
      },
      "data_agendamento": "2024-01-15",
      "hora_agendamento": "14:30:00",
      "status": "confirmado",
      "valor": 45.00,
      "observacoes": "Fade baixo e barba desenhada",
      "data_criacao": "2024-01-10T10:30:00Z",
      "data_atualizacao": "2024-01-12T15:45:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total_items": 85,
    "total_pages": 5
  }
}
```

#### POST `/api/v1/appointments`
Cria um novo agendamento.

**Request Body:**
```json
{
  "cliente_id": 1,
  "barbeiro_id": 1,
  "servico_id": 2,
  "data_agendamento": "2024-01-15",
  "hora_agendamento": "14:30:00",
  "observacoes": "Fade baixo e barba desenhada"
}
```

**Response (201):**
```json
{
  "id": 1,
  "mensagem": "Agendamento criado com sucesso",
  "valor_total": 45.00
}
```

#### PUT `/api/v1/appointments/{id}/status`
Atualiza o status de um agendamento.

**Request Body:**
```json
{
  "status": "concluido"
}
```

**Response (200):**
```json
{
  "id": 1,
  "mensagem": "Status do agendamento atualizado com sucesso"
}
```

#### DELETE `/api/v1/appointments/{id}`
Cancela um agendamento.

**Response (200):**
```json
{
  "id": 1,
  "mensagem": "Agendamento cancelado com sucesso"
}
```

#### GET `/api/v1/barbeiros/{barbeiro_id}/disponibilidade`
Obtem horários disponíveis de um barbeiro em uma data específica.

**Query Parameters:**
- `data`: Data para consulta (YYYY-MM-DD)

**Response (200):**
```json
{
  "barbeiro_id": 1,
  "data": "2024-01-15",
  "horarios_disponiveis": [
    "09:00",
    "09:30",
    "10:00",
    "10:30",
    "11:00",
    "13:00",
    "13:30",
    "14:00",
    "14:30",
    "15:00",
    "15:30",
    "16:00"
  ],
  "horarios_indisponiveis": [
    {
      "hora": "12:00",
      "motivo": "intervalo_almoco"
    },
    {
      "hora": "16:30",
      "motivo": "ja_agendado"
    }
  ]
}
```

### Pagamentos (`/payments`)

#### POST `/api/v1/payments`
Processa um pagamento para um agendamento.

**Request Body:**
```json
{
  "appointment_id": 1,
  "metodo": "pix",
  "valor": 45.00
}
```

**Response (201):**
```json
{
  "id": 1,
  "transaction_id": "txn_1234567890",
  "status": "processado",
  "valor": 45.00,
  "metodo": "pix",
  "qr_code": "00020126360014br.gov.bcb.pix0114+5511999998888520400005303986540545.005802BR5903Maria Silva6009Sao Paulo62070503***6304A8C1",
  "expiracao": "2024-01-15T15:00:00Z"
}
```

#### GET `/api/v1/payments/{id}`
Obtém detalhes de um pagamento específico.

**Response (200):**
```json
{
  "id": 1,
  "appointment_id": 1,
  "valor": 45.00,
  "metodo": "pix",
  "status": "confirmado",
  "data_pagamento": "2024-01-15T14:45:00Z",
  "transaction_id": "txn_1234567890",
  "receipt_url": "https://payments.example.com/receipts/txn_1234567890.pdf"
}
```

### Notificações (`/notifications`)

#### POST `/api/v1/notifications/preferences`
Atualiza preferências de notificação de um cliente.

**Request Body:**
```json
{
  "cliente_id": 1,
  "email": true,
  "sms": false,
  "whatsapp": true,
  "push": true,
  "lembrete_24h": true,
  "lembrete_2h": true,
  "promocoes": true,
  "lembrete_aniversario": true
}
```

**Response (200):**
```json
{
  "cliente_id": 1,
  "mensagem": "Preferências de notificação atualizadas com sucesso"
}
```

#### POST `/api/v1/notifications/test`
Envia uma notificação de teste (apenas para ambientes de desenvolvimento/homologação).

**Request Body:**
```json
{
  "cliente_id": 1,
  "tipo": "whatsapp",
  "titulo": "Teste de Notificação",
  "mensagem": "Esta é uma mensagem de teste"
}
```

**Response (200):**
```json
{
  "message": "Notificação de teste enviada com sucesso",
  "id": "msg_1234567890"
}
```

### Relatórios e Dashboard (`/reports`)

#### GET `/api/v1/reports/dashboard`
Obtem métricas para o dashboard de uma barbearia.

**Query Parameters:**
- `barbearia_id`: ID da barbearia (obrigatório)
- `periodo`: Período para relatório (hoje, semana, mes, ano, personalizado)
- `data_inicio`: Data inicial para período personalizado (YYYY-MM-DD)
- `data_fim`: Data final para período personalizado (YYYY-MM-DD)

**Response (200):**
```json
{
  "barbearia_id": 1,
  "periodo": {
    "inicio": "2024-01-01",
    "fim": "2024-01-31"
  },
  "metricas": {
    "faturamento_total": 12500.00,
    "total_atendimentos": 320,
    "ticket_medio": 39.06,
    "taxa_ocupacao": 0.72,
    "novos_clientes": 45,
    "clientes_retornando": 210,
    "taxa_retencao": 0.66,
    "servicos_mais_populares": [
      {"nome": "Corte Social", "count": 95, "receita": 2850.00},
      {"nome": "Corte + Barba", "count": 80, "receita": 3600.00},
      {"nome": "Barba Tradicional", "count": 60, "receita": 1500.00},
      {"nome": "Tratamento Capilar", "count": 45, "receita": 2250.00},
      {"nome": "Sobrancelha", "count": 40, "receita": 800.00}
    ],
    "horarios_pico": [
      {"hora": "17:00", "count": 45},
      {"hora": "18:00", "count": 52},
      {"hora": "19:00", "count": 48}
    ],
    "cancelamentos": 15,
    "nao_compareceu": 8,
    "taxa_comparecimento": 0.93
  }
}
```

### Health Check (`/health`)

#### GET `/api/v1/health`
Verifica a saúde da API e dependências.

**Response (200):**
```json
{
  "status": "healthy",
  "timestamp": "2024-06-26T10:30:00Z",
  "version": "1.0.0",
  "services": {
    "api": "healthy",
    "database": "healthy",
    "redis": "healthy",
    "external_services": {
      "whatsapp_api": "healthy",
      "payment_gateway": "healthy"
    }
  }
}
```

**Response (503) quando algum serviço está indisponível:**
```json
{
  "status": "unhealthy",
  "timestamp": "2024-06-26T10:30:00Z",
  "version": "1.0.0",
  "services": {
    "api": "healthy",
    "database": "unhealthy",
    "redis": "healthy",
    "error": "Falha na conexão com o banco de dados"
  }
}
```

## WebSocket Events (Para Funcionalidades em Tempo Real)

Para funcionalidades que requerem atualizações em tempo real (como atualização de agenda), oferecemos WebSocket connections em `/ws`.

### Conexão
```
WS: ws://api.barbeirasaas.com/ws?token=<access_token>
```

### Eventos Enviados pelo Servidor

#### `appointment_updated`
Notifica quando um agendamento é criado, atualizado ou cancelado.

```json
{
  "event": "appointment_updated",
  "data": {
    "appointment_id": 1,
    "action": "created", // ou "updated", "cancelled"
    "barbearia_id": 1,
    "barbeiro_id": 1,
    "data": "2024-01-15",
    "hora": "14:30:00"
  }
}
```

#### `queue_update`
Notifica quando há mudanças na fila de espera.

```json
{
  "event": "queue_update",
  "data": {
    "barbearia_id": 1,
    "servico_id": 2,
    "data": "2024-01-15",
    "horario_liberado": "14:30:00",
    "posicao_na_fila": 3
  }
}
```

## Limitações e Considerações

1. **Tamanho de Payload**: Limite de 10MB para requisições e respostas
2. **Timeout**: 30 segundos para operações padrão, 120 segundos para operações pesadas (relatórios)
3. **Codificação de Caracteres**: UTF-8 obrigatório
4. **Idempotência**: Endpoints de criação (POST) não são idempotentes por padrão. Para operações idempotentes, use o header `Idempotency-Key`
5. **Cache-Control**: Respostas incluem cabeçalhos de cache apropriados quando aplicável
6. **CORS**: Configurado para permitir origens específicas em produção (localhost:3000 em desenvolvimento)

## Exemplo de Uso com cURL

### Autenticação
```bash
curl -X POST https://api.barbeirasaas.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"joao@example.com","senha":"senha123"}'
```

### Criando um Agendamento
```bash
curl -X POST https://api.barbeirasaas.com/api/v1/appointments \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "cliente_id": 1,
    "barbeiro_id": 1,
    "servico_id": 2,
    "data_agendamento": "2024-01-15",
    "hora_agendamento": "14:30:00",
    "observacoes": "Fade baixo e barba desenhada"
  }'
```

### Listando Horários Disponíveis
```bash
curl -X GET "https://api.barbeirasaas.com/api/v1/barbeiros/1/disponibilidade?data=2024-01-15" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## Diretrizes para Consumo da API

1. Sempre trate respostas de erro adequadamente usando o formato padronizado
2. Implemente renovação automática de token usando o endpoint `/auth/refresh`
3. Respeite os limites de rate para evitar bloqueios temporários
4. Use paginação para listas grandes de resultados
5. Para operações críticas, considere implementing idempotency usando `Idempotency-Key` header
6. Monitore os cabeçalhos de resposta `Retry-After` quando receber 429 (Too Many Requests)

## Alterações Futuras

Esta especificação está sujeita a mudanças à medida que o produto evolui. Alterações que quebram compatibilidade serão:
- Comunicadas com antecedência mínima de 30 dias
- Versionadas adequadamente (v2, v3, etc.)
- Documentadas detalhadamente neste documento com data de efetivação

*Versão da especificação: 1.0.0*
*Data: 2024-06-26*