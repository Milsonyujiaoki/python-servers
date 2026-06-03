FROM ghcr.io/astral-sh/uv:python3.12-alpine

WORKDIR /app

# Copia os arquivos do seu projeto para dentro do container
COPY . /app

# Sincroniza e instala as dependências do pyproject.toml de forma isolada
RUN uv sync --frozen

ENV PATH="/app/.venv/bin:$PATH"
