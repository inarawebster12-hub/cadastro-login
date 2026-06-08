import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import hash_password
from core.deps import get_current_motorista
from schemas.schemas import MotoristaCreate, MotoristaUpdate, MotoristaResponse
from models.models import Motorista
from PIL import Image

router = APIRouter(prefix="/motoristas", tags=["🚗 Motoristas"])

UPLOAD_DIR = "uploads/motoristas"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/cadastro", response_model=MotoristaResponse, status_code=201, summary="Cadastrar motorista")
def cadastrar_motorista(body: MotoristaCreate, db: Session = Depends(get_db)):
    # Verificar duplicatas
    if db.query(Motorista).filter(Motorista.email == body.email).first():
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")
    if db.query(Motorista).filter(Motorista.cnh == body.cnh).first():
        raise HTTPException(status_code=400, detail="CNH já cadastrada")
    if db.query(Motorista).filter(Motorista.cpf == body.cpf).first():
        raise HTTPException(status_code=400, detail="CPF já cadastrado")
    if body.veiculo_placa and db.query(Motorista).filter(Motorista.veiculo_placa == body.veiculo_placa).first():
        raise HTTPException(status_code=400, detail="Placa já cadastrada")

    motorista = Motorista(
        nome=body.nome,
        email=body.email,
        telefone=body.telefone,
        senha_hash=hash_password(body.senha),
        cpf=body.cpf,
        cnh=body.cnh,
        cnh_categoria=body.cnh_categoria,
        endereco=body.endereco,
        cidade=body.cidade,
        estado=body.estado,
        cep=body.cep,
        veiculo_modelo=body.veiculo_modelo,
        veiculo_placa=body.veiculo_placa,
        veiculo_ano=body.veiculo_ano,
        veiculo_cor=body.veiculo_cor,
        veiculo_capacidade=body.veiculo_capacidade,
    )
    db.add(motorista)
    db.commit()
    db.refresh(motorista)
    return motorista


@router.get("/perfil", response_model=MotoristaResponse, summary="Ver meu perfil")
def ver_perfil(motorista: Motorista = Depends(get_current_motorista)):
    return motorista


@router.put("/perfil", response_model=MotoristaResponse, summary="Atualizar meu perfil")
def atualizar_perfil(
    body: MotoristaUpdate,
    db: Session = Depends(get_db),
    motorista: Motorista = Depends(get_current_motorista),
):
    for campo, valor in body.model_dump(exclude_none=True).items():
        setattr(motorista, campo, valor)
    db.commit()
    db.refresh(motorista)
    return motorista


@router.post("/perfil/foto", response_model=MotoristaResponse, summary="Enviar foto de perfil")
async def upload_foto(
    foto: UploadFile = File(...),
    db: Session = Depends(get_db),
    motorista: Motorista = Depends(get_current_motorista),
):
    # Validar tipo de arquivo
    if foto.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(status_code=400, detail="Apenas imagens JPG, PNG ou WEBP são aceitas")

    # Ler e redimensionar com Pillow (max 400x400)
    contents = await foto.read()
    from io import BytesIO
    img = Image.open(BytesIO(contents))
    img.thumbnail((400, 400))

    # Salvar arquivo
    ext = foto.filename.split(".")[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    img.save(filepath)

    # Apagar foto antiga se existir
    if motorista.foto_perfil and os.path.exists(motorista.foto_perfil):
        os.remove(motorista.foto_perfil)

    motorista.foto_perfil = filepath
    db.commit()
    db.refresh(motorista)
    return motorista


@router.delete("/perfil", summary="Desativar minha conta")
def desativar_conta(
    db: Session = Depends(get_db),
    motorista: Motorista = Depends(get_current_motorista),
):
    motorista.ativo = False
    db.commit()
    return {"mensagem": "Conta desativada com sucesso"}
