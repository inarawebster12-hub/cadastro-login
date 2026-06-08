import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import hash_password
from core.deps import get_current_aluno
from schemas.schemas import AlunoCreate, AlunoUpdate, AlunoResponse
from models.models import Aluno, Motorista
from PIL import Image

router = APIRouter(prefix="/alunos", tags=["🎓 Alunos"])

UPLOAD_DIR = "uploads/alunos"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/cadastro", response_model=AlunoResponse, status_code=201, summary="Cadastrar aluno")
def cadastrar_aluno(body: AlunoCreate, db: Session = Depends(get_db)):
    if db.query(Aluno).filter(Aluno.email == body.email).first():
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")
    if db.query(Aluno).filter(Aluno.matricula == body.matricula).first():
        raise HTTPException(status_code=400, detail="Matrícula já cadastrada")
    if db.query(Aluno).filter(Aluno.cpf == body.cpf).first():
        raise HTTPException(status_code=400, detail="CPF já cadastrado")

    # Verificar se motorista existe (se informado)
    if body.motorista_id:
        if not db.query(Motorista).filter(Motorista.id == body.motorista_id).first():
            raise HTTPException(status_code=404, detail="Motorista não encontrado")

    aluno = Aluno(
        nome=body.nome,
        email=body.email,
        telefone=body.telefone,
        senha_hash=hash_password(body.senha),
        cpf=body.cpf,
        matricula=body.matricula,
        escola=body.escola,
        endereco=body.endereco,
        cidade=body.cidade,
        estado=body.estado,
        cep=body.cep,
        motorista_id=body.motorista_id,
    )
    db.add(aluno)
    db.commit()
    db.refresh(aluno)
    return aluno


@router.get("/perfil", response_model=AlunoResponse, summary="Ver meu perfil")
def ver_perfil(aluno: Aluno = Depends(get_current_aluno)):
    return aluno


@router.put("/perfil", response_model=AlunoResponse, summary="Atualizar meu perfil")
def atualizar_perfil(
    body: AlunoUpdate,
    db: Session = Depends(get_db),
    aluno: Aluno = Depends(get_current_aluno),
):
    dados = body.model_dump(exclude_none=True)

    if "motorista_id" in dados and dados["motorista_id"]:
        if not db.query(Motorista).filter(Motorista.id == dados["motorista_id"]).first():
            raise HTTPException(status_code=404, detail="Motorista não encontrado")

    for campo, valor in dados.items():
        setattr(aluno, campo, valor)
    db.commit()
    db.refresh(aluno)
    return aluno


@router.post("/perfil/foto", response_model=AlunoResponse, summary="Enviar foto de perfil")
async def upload_foto(
    foto: UploadFile = File(...),
    db: Session = Depends(get_db),
    aluno: Aluno = Depends(get_current_aluno),
):
    if foto.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(status_code=400, detail="Apenas imagens JPG, PNG ou WEBP são aceitas")

    contents = await foto.read()
    from io import BytesIO
    img = Image.open(BytesIO(contents))
    img.thumbnail((400, 400))

    ext = foto.filename.split(".")[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    img.save(filepath)

    if aluno.foto_perfil and os.path.exists(aluno.foto_perfil):
        os.remove(aluno.foto_perfil)

    aluno.foto_perfil = filepath
    db.commit()
    db.refresh(aluno)
    return aluno


@router.delete("/perfil", summary="Desativar minha conta")
def desativar_conta(
    db: Session = Depends(get_db),
    aluno: Aluno = Depends(get_current_aluno),
):
    aluno.ativo = False
    db.commit()
    return {"mensagem": "Conta desativada com sucesso"}
