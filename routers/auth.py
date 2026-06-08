from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import verify_password, create_access_token
from schemas.schemas import LoginRequest, TokenResponse
from models.models import Motorista, Aluno

router = APIRouter(prefix="/auth", tags=["🔐 Autenticação"])


@router.post("/motorista/login", response_model=TokenResponse, summary="Login do motorista")
def login_motorista(body: LoginRequest, db: Session = Depends(get_db)):
    motorista = db.query(Motorista).filter(Motorista.email == body.email).first()

    if not motorista or not verify_password(body.senha, motorista.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos",
        )
    if not motorista.ativo:
        raise HTTPException(status_code=403, detail="Conta desativada")

    token = create_access_token({"sub": motorista.id, "tipo": "motorista"})
    return TokenResponse(access_token=token, tipo_usuario="motorista", user_id=motorista.id)


@router.post("/aluno/login", response_model=TokenResponse, summary="Login do aluno")
def login_aluno(body: LoginRequest, db: Session = Depends(get_db)):
    aluno = db.query(Aluno).filter(Aluno.email == body.email).first()

    if not aluno or not verify_password(body.senha, aluno.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos",
        )
    if not aluno.ativo:
        raise HTTPException(status_code=403, detail="Conta desativada")

    token = create_access_token({"sub": aluno.id, "tipo": "aluno"})
    return TokenResponse(access_token=token, tipo_usuario="aluno", user_id=aluno.id)
