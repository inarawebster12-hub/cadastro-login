from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base


class Motorista(Base):
    __tablename__ = "motoristas"

    id            = Column(Integer, primary_key=True, index=True)
    nome          = Column(String(150), nullable=False)
    email         = Column(String(150), unique=True, index=True, nullable=False)
    telefone      = Column(String(20), nullable=False)
    senha_hash    = Column(String(255), nullable=False)

    # Documento
    cpf           = Column(String(14), unique=True, nullable=False)
    cnh           = Column(String(20), unique=True, nullable=False)
    cnh_categoria = Column(String(5), nullable=False, default="B")

    # Endereço
    endereco      = Column(String(255))
    cidade        = Column(String(100))
    estado        = Column(String(2))
    cep           = Column(String(10))

    # Veículo
    veiculo_modelo = Column(String(100))
    veiculo_placa  = Column(String(10), unique=True)
    veiculo_ano    = Column(Integer)
    veiculo_cor    = Column(String(50))
    veiculo_capacidade = Column(Integer, default=0)

    # Perfil
    foto_perfil   = Column(String(255))   # caminho do arquivo salvo
    ativo         = Column(Boolean, default=True)
    criado_em     = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamento
    alunos = relationship("Aluno", back_populates="motorista")


class Aluno(Base):
    __tablename__ = "alunos"

    id           = Column(Integer, primary_key=True, index=True)
    nome         = Column(String(150), nullable=False)
    email        = Column(String(150), unique=True, index=True, nullable=False)
    telefone     = Column(String(20), nullable=False)
    senha_hash   = Column(String(255), nullable=False)

    # Documento
    cpf          = Column(String(14), unique=True, nullable=False)
    matricula    = Column(String(30), unique=True, nullable=False)
    escola       = Column(String(150))

    # Endereço
    endereco     = Column(String(255))
    cidade       = Column(String(100))
    estado       = Column(String(2))
    cep          = Column(String(10))

    # Perfil
    foto_perfil  = Column(String(255))
    ativo        = Column(Boolean, default=True)
    criado_em    = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamento com motorista (opcional)
    motorista_id = Column(Integer, ForeignKey("motoristas.id"), nullable=True)
    motorista    = relationship("Motorista", back_populates="alunos")
