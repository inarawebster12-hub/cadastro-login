from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

from core.database import engine, Base
from models import models  # garante que os models são registrados
from routers import auth, motoristas, alunos

# Cria todas as tabelas no banco (se não existirem)
Base.metadata.create_all(bind=engine)

# Cria diretórios de upload
os.makedirs("uploads/motoristas", exist_ok=True)
os.makedirs("uploads/alunos", exist_ok=True)

app = FastAPI(
    title="🚌 Transporte Escolar API",
    description="""
## API de Cadastro e Autenticação

### Funcionalidades
- **Motoristas**: Cadastro, login, perfil completo com veículo e CNH, foto
- **Alunos**: Cadastro, login, perfil com matrícula e escola, foto
- **JWT**: Autenticação segura com tokens de 24h
- **Senhas**: Hash com bcrypt (nunca armazenadas em texto puro)

### Como usar
1. Faça o cadastro em `/motoristas/cadastro` ou `/alunos/cadastro`
2. Faça login em `/auth/motorista/login` ou `/auth/aluno/login`
3. Copie o `access_token` retornado
4. Clique em **Authorize** 🔒 e cole o token
5. Acesse as rotas protegidas normalmente
    """,
    version="1.0.0",
)

# CORS - permite requisições do app mobile/web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Em produção, coloque os domínios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir fotos de perfil como arquivos estáticos
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Registrar routers
app.include_router(auth.router)
app.include_router(motoristas.router)
app.include_router(alunos.router)


@app.get("/", tags=["🏠 Home"])
def home():
    return {
        "status": "online",
        "mensagem": "API Transporte Escolar funcionando!",
        "docs": "/docs",
    }
