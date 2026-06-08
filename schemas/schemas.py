from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
import re


# ─────────────────────────────────────────
#  SCHEMAS COMPARTILHADOS
# ─────────────────────────────────────────

class LoginRequest(BaseModel):
    email: EmailStr
    senha: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    tipo_usuario: str   # "motorista" ou "aluno"
    user_id: int


class EnderecoMixin(BaseModel):
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = Field(None, max_length=2)
    cep: Optional[str] = None

    @field_validator("cep")
    @classmethod
    def validar_cep(cls, v):
        if v and not re.match(r"^\d{5}-?\d{3}$", v):
            raise ValueError("CEP inválido. Use o formato 00000-000")
        return v


def _validar_cpf(cpf: str) -> str:
    """Valida CPF com dígitos verificadores. Aceita '000.000.000-00' ou '00000000000'."""
    numeros = re.sub(r"\D", "", cpf)
    if len(numeros) != 11 or len(set(numeros)) == 1:
        raise ValueError("CPF inválido")
    # Primeiro dígito verificador
    soma = sum(int(numeros[i]) * (10 - i) for i in range(9))
    d1 = 0 if (soma * 10 % 11) >= 10 else (soma * 10 % 11)
    # Segundo dígito verificador
    soma = sum(int(numeros[i]) * (11 - i) for i in range(10))
    d2 = 0 if (soma * 10 % 11) >= 10 else (soma * 10 % 11)
    if int(numeros[9]) != d1 or int(numeros[10]) != d2:
        raise ValueError("CPF inválido")
    # Normalizar para formato com máscara
    return f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}"


# ─────────────────────────────────────────
#  MOTORISTA
# ─────────────────────────────────────────

class MotoristaCreate(EnderecoMixin):
    nome: str = Field(..., min_length=3, max_length=150)
    email: EmailStr
    telefone: str = Field(..., min_length=10, max_length=20)
    senha: str = Field(..., min_length=6)
    cpf: str = Field(..., description="CPF no formato 000.000.000-00 ou só números")
    cnh: str = Field(..., min_length=9, max_length=20)
    cnh_categoria: str = Field(default="B", max_length=5)

    # Veículo (opcional no cadastro)
    veiculo_modelo: Optional[str] = None
    veiculo_placa: Optional[str] = None
    veiculo_ano: Optional[int] = None
    veiculo_cor: Optional[str] = None
    veiculo_capacidade: Optional[int] = None

    @field_validator("cpf")
    @classmethod
    def validar_cpf(cls, v):
        return _validar_cpf(v)

    @field_validator("telefone")
    @classmethod
    def validar_telefone(cls, v):
        numeros = re.sub(r"\D", "", v)
        if len(numeros) < 10:
            raise ValueError("Telefone inválido")
        return v


class MotoristaUpdate(EnderecoMixin):
    nome: Optional[str] = None
    telefone: Optional[str] = None
    cnh_categoria: Optional[str] = None
    veiculo_modelo: Optional[str] = None
    veiculo_placa: Optional[str] = None
    veiculo_ano: Optional[int] = None
    veiculo_cor: Optional[str] = None
    veiculo_capacidade: Optional[int] = None


class MotoristaResponse(EnderecoMixin):
    id: int
    nome: str
    email: str
    telefone: str
    cpf: str
    cnh: str
    cnh_categoria: str
    veiculo_modelo: Optional[str] = None
    veiculo_placa: Optional[str] = None
    veiculo_ano: Optional[int] = None
    veiculo_cor: Optional[str] = None
    veiculo_capacidade: Optional[int] = None
    foto_perfil: Optional[str] = None
    ativo: bool
    criado_em: datetime

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────
#  ALUNO
# ─────────────────────────────────────────

class AlunoCreate(EnderecoMixin):
    nome: str = Field(..., min_length=3, max_length=150)
    email: EmailStr
    telefone: str = Field(..., min_length=10, max_length=20)
    senha: str = Field(..., min_length=6)
    cpf: str = Field(..., description="CPF no formato 000.000.000-00 ou só números")
    matricula: str = Field(..., min_length=3, max_length=30)
    escola: Optional[str] = None
    motorista_id: Optional[int] = None

    @field_validator("cpf")
    @classmethod
    def validar_cpf(cls, v):
        return _validar_cpf(v)

    @field_validator("telefone")
    @classmethod
    def validar_telefone(cls, v):
        numeros = re.sub(r"\D", "", v)
        if len(numeros) < 10:
            raise ValueError("Telefone inválido")
        return v


class AlunoUpdate(EnderecoMixin):
    nome: Optional[str] = None
    telefone: Optional[str] = None
    escola: Optional[str] = None
    motorista_id: Optional[int] = None


class AlunoResponse(EnderecoMixin):
    id: int
    nome: str
    email: str
    telefone: str
    cpf: str
    matricula: str
    escola: Optional[str] = None
    foto_perfil: Optional[str] = None
    motorista_id: Optional[int] = None
    ativo: bool
    criado_em: datetime

    model_config = {"from_attributes": True}
