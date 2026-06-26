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