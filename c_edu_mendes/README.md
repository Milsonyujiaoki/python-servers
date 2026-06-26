# Barbearia SaaS

Sistema de gestão e agendamento inteligente para barbearias, focado em aumentar receita e reduzir custos através de automação e insights baseados em dados.

## 🏗️ Arquitetura

Este projeto segue os princípios de:
- **Monolito Modular**: Código organizado em módulos independentes mas deployado como unidade única
- **Vertical Slicing**: Cada módulo contém frontend e backend para uma funcionalidade de negócio completa
- **TDD (Test-Driven Development)**: Testes escritos antes da implementação
- **Clean Architecture**: Separação clara de preocupadas

## 📁 Estrutura do Projeto

Veja [specs/PROJECT_STRUCTURE_PLAN.md](specs/PROJECT_STRUCTURE_PLAN.md) para detalhes completos.

## �começando

### Pré-requisitos
- Node.js >= 18
- Python >= 3.11
- Docker e Docker Compose
- PostgreSQL (para desenvolvimento local)
- Redis (para desenvolvimento local)

### Instalação

```bash
# Instalar dependências Node.js
npm install

# Instalar dependências Python
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas configurações

# Iniciar serviços de apoio (PostgreSQL, Redis)
docker-compose up -d

# Executar migrações do banco
python -m alembic upgrade head

# Iniciar aplicação em modo desenvolvimento
npm run dev  # Inicia Next.js em http://localhost:3000
# Em outro terminal:
uvicorn src/shared/backend/main:app --reload  # Inicia FastAPI em http://localhost:8000
```

## 🧪 Testes

```bash
# Executar todos os testes
npm test

# Apenas unitários
npm run test:unit

# Apenas integração
npm run test:integration

# Apenas E2E
npm run test:e2e
```

## 📚 Documentação

- [Plano de Arquitetura e Negócio](specs/PLANO_BARBEARIA_SAAS.md)
- [Plano de Estrutura do Projeto](specs/PROJECT_STRUCTURE_PLAN.md)
- [Especificação da API](docs/API_SPECS.md)
- [Decisões Arquiteturais](docs/ARCHITECTURE_DECISIONS.md)
- API Docs: http://localhost:8000/docs (quando o backend está rodando)

## 📜 Licença

MIT