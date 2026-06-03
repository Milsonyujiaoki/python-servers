import os
from datetime import datetime
from uuid import uuid4
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel, Field, field_validator
import asyncpg

app = FastAPI(default_response_class=ORJSONResponse)
DB_POOL = None

@app.on_event("startup")
async def startup():
    global DB_POOL
    DB_POOL = await asyncpg.create_pool(
        dsn=os.getenv("DATABASE_URL", "postgres://admin:admin@localhost:5432/rinha"),
        min_size=5,
        max_size=15 
    )

@app.on_event("shutdown")
async def shutdown():
    if DB_POOL:
        await DB_POOL.close()

class UserSchema(BaseModel):
    name: str = Field(..., max_length=100)
    birth_date: str
    cpf: str

    @field_validator('name')
    def normalize_name(cls, v: str):
        if not v.strip():
            raise ValueError()
        return v.title()

    @field_validator('birth_date')
    def parse_birth_date(cls, v: str):
        try:
            return datetime.strptime(v, "%d/%m/%Y").date()
        except ValueError:
            raise ValueError("Use o formato DD/MM/AAAA")

    @field_validator('cpf')
    def validate_and_clean_cpf(cls, v: str):
        cleaned = v.replace(".", "").replace("-", "")
        if len(cleaned) != 11 or not cleaned.isdigit():
            raise ValueError("CPF inválido.")
        return cleaned

@app.post("/pessoas", status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserSchema):
    user_id = uuid4()
    async with DB_POOL.acquire() as conn:
        try:
            await conn.execute(
                "INSERT INTO pessoas (id, name, birth_date, cpf) VALUES ($1, $2, $3, $4)",
                user_id, payload.name, payload.birth_date, payload.cpf
            )
        except asyncpg.exceptions.UniqueViolationError:
            raise HTTPException(status_code=422, detail="CPF já cadastrado.")
            
    return ORJSONResponse(
        status_code=status.HTTP_201_CREATED,
        headers={"Location": f"/pessoas/{user_id}"},
        content={"id": str(user_id)}
    )
