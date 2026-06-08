from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import decode_token
from models.models import Motorista, Aluno

bearer_scheme = HTTPBearer()


def get_current_motorista(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Motorista:
    token = credentials.credentials
    payload = decode_token(token)

    if not payload or payload.get("tipo") != "motorista":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou sem permissão de motorista",
        )

    motorista = db.query(Motorista).filter(Motorista.id == payload["sub"]).first()
    if not motorista or not motorista.ativo:
        raise HTTPException(status_code=404, detail="Motorista não encontrado")
    return motorista


def get_current_aluno(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Aluno:
    token = credentials.credentials
    payload = decode_token(token)

    if not payload or payload.get("tipo") != "aluno":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou sem permissão de aluno",
        )

    aluno = db.query(Aluno).filter(Aluno.id == payload["sub"]).first()
    if not aluno or not aluno.ativo:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    return aluno
