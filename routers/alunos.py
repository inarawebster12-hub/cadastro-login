import os
import uuid
import traceback

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
    try:
        print("\n================ CADASTRO ALUNO ================")
        print("BODY RECEBIDO:", body)

        print("Nome:", repr(body.nome))
        print("Email:", repr(body.email))
        print("Telefone:", repr(body.telefone))
        print("CPF:", repr(body.cpf))
        print("Matricula:", repr(body.matricula))

        print("Senha:", repr(body.senha))
        print("Tipo da senha:", type(body.senha))
        print("Tamanho da senha:", len(body.senha))

        print("================================================")

        if db.query(Aluno).filter(Aluno.email == body.email).first():
            raise HTTPException(status_code=400, detail="E-mail já cadastrado")

        if db.query(Aluno).filter(Aluno.matricula == body.matricula).first():
            raise HTTPException(status_code=400, detail="Matrícula já cadastrada")

        if db.query(Aluno).filter(Aluno.cpf == body.cpf).first():
            raise HTTPException(status_code=400, detail="CPF já cadastrado")

        if body.motorista_id:
            if not db.query(Motorista).filter(
                Motorista.id == body.motorista_id
            ).first():
                raise HTTPException(
                    status_code=404,
                    detail="Motorista não encontrado"
                )

        print("Gerando hash da senha...")

        senha_hash = hash_password(body.senha)

        print("Hash gerado com sucesso!")
        print("Tamanho do hash:", len(senha_hash))

        aluno = Aluno(
            nome=body.nome,
            email=body.email,
            telefone=body.telefone,
            senha_hash=senha_hash,
            cpf=body.cpf,
            matricula=body.matricula,
            escola=body.escola,
            endereco=body.endereco,
            cidade=body.cidade,
            estado=body.estado,
            cep=body.cep,
            motorista_id=body.motorista_id,
        )

        print("Adicionando aluno ao banco...")

        db.add(aluno)

        print("Executando commit...")

        db.commit()

        print("Commit realizado com sucesso!")

        db.refresh(aluno)

        print("Aluno criado com ID:", aluno.id)

        return aluno

    except Exception as e:
        print("\n================ ERRO CADASTRO ================")
        print("TIPO:", type(e)._name_)
        print("ERRO:", str(e))
        traceback.print_exc()
        print("================================================")

        raise


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
        if not db.query(Motorista).filter(
            Motorista.id == dados["motorista_id"]
        ).first():
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
        raise HTTPException(
            status_code=400,
            detail="Apenas imagens JPG, PNG ou WEBP são aceitas",
        )

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
