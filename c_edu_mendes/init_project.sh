#!/bin/bash
# Script de inicialização rápida do projeto Barbearia SaaS
# Este script cria a estrutura básica e demonstra que o projeto segue as diretrizes

echo "🚀 Inicializando estrutura do projeto Barbearia SaaS..."

# Criar diretório do projeto se não existir
PROJECT_DIR="barbershop-saas"
if [ ! -d "$PROJECT_DIR" ]; then
  mkdir -p "$PROJECT_DIR"
  echo "✅ Diretório do projeto criado: $PROJECT_DIR"
else
  echo "ℹ️ Diretório do projeto já existe: $PROJECT_DIR"
fi

cd "$PROJECT_DIR"

# Criar estrutura de diretórios
echo "📁 Criando estrutura de diretórios..."

# Docs
mkdir -p docs
mkdir -p specs

# Source code (j docs

# Source compartilhado
mkdir -p src/shared/{lib,config,types,constants,hooks}

# Módulos (exemplo com alguns módulos principais)
MODULES=("auth" "customers" "barbershops" "appointments" "payments" "notifications" "crm" "waitlist" "dashboard")
for module in "${MODULES[@]}"; do
  mkdir -p "src/modules/$module/backend/{api,services,repositories,models,schemas,tests/{unit,integration}}"
  mkdir -p "src/modules/$module/frontend/{components,pages,hooks,lib,styles,tests/{unit,integration,e2e},types}"
done

# Shared backend
mkdir -p src/shared/backend/{database,middleware,utils,exceptions}

# Testes globais
mkdir -p tests/{integration,e2e}

# Scripts
mkdir -p scripts

# Docker
mkdir -p docker

# GitHub
mkdir -p .github/workflows

echo "✅ Estrutura de diretórios criada"

# Criar arquivos de exemplo para demonstrar o padrão

# Package.json
cat > package.json << 'EOF'
{
  "name": "barbershop-saas",
  "version": "1.0.0",
  "private": true,
  "description": "SaaS para barbearias - agendamento inteligente e gestão de negócio",
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "test:unit": "vitest run",
    "test:integration": "vitest run --config vitest.integration.config.ts",
    "test:e2e": "cypress run",
    "test": "npm run test:unit && npm run test:integration && npm run test:e2e"
  },
  "dependencies": {
    "next": "14.0.0",
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "@tanstack/react-query": "^5.0.0",
    " zod": "^3.20.0",
    "react-hook-form": "^7.45.0"
  },
  "devDependencies": {
    "@types/node": "20.0.0",
    "@types/react": "18.0.0",
    "@types/react-dom": "18.0.0",
    "typescript": "5.0.0",
    "vitet": "^1.0.0",
    "@vitest/ui": "^1.0.0",
    "cypress": "^13.0.0",
    "eslint": "^8.0.0",
    "eslint-config-next": "14.0.0",
    "tailwindcss": "^3.0.0",
    "postcss": "^8.0.0",
    "autoprefixer": "^10.0.0"
  }
}
EOF

echo "✅ package.json criado"

# Requirements.txt
cat > requirements.txt << 'EOF'
fastapi==0.104.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.23
alembic==1.13.1
psycopg2-binary==2.9.9
pydantic==2.5.0
pydantic-settings==2.1.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
redis==5.0.1
# Testing
pytest==7.4.3
pytest-asyncio==0.23.2
httpx==0.25.2
# Quality
ruff==0.1.2
mypy==1.7.1
bandit==1.7.9
# DOCS
mkdocs==1.5.3
mkdocs-material==9.4.8
EOF

echo "✅ requirements.txt criado"

# README.md
cat > README.md << 'EOF'
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
EOF

echo "✅ README.md criado"

# Criar .env.example
cat > .env.example << 'EOF'
# Variáveis de Ambiente
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Backend
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/barbershop
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-super-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# APIs Externas
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
STRIPE_SECRET_KEY=your_stripe_secret_key
PIX_MERCHANT_KEY=your_pix_merchant_key

# Feature Flags
ENABLE_FACIAL_ANALYSIS=true
ENABLE_ADVANCED_CRM=true
ENABLE_INTELLIGENT_WAITLIST=true
EOF

echo "✅ .env.example criado"

# Criar docker-compose.yml
mkdir -p docker
cat > docker/docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: barbershop_postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: barbershop
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: barbershop_redis
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
EOF

echo "✅ docker-compose.yml criado"

# Criar main.py do backend (simplificado)
mkdir -p src/shared/backend
cat > src/shared/backend/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="BarberShop SaaS API",
    description="API para sistema de gestão de barbearias",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure adequadamente para produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "BarberShop SaaS API está rodando!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
EOF

echo "✅ main.py do backend criado"

echo "🎉 Inicialização completa!"