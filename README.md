# 🚌 Transporte Escolar — API Backend

Sistema completo de cadastro, login e perfil para **motoristas** e **alunos**.

---

## 📁 Estrutura do Projeto

```
app/
├── main.py                  # Ponto de entrada da API
├── requirements.txt         # Dependências
├── core/
│   ├── database.py          # Configuração do banco (SQLite)
│   ├── security.py          # JWT + hash de senha (bcrypt)
│   └── deps.py              # Dependências de autenticação
├── models/
│   └── models.py            # Tabelas do banco (Motorista, Aluno)
├── schemas/
│   └── schemas.py           # Validação de dados (Pydantic)
├── routers/
│   ├── auth.py              # Login
│   ├── motoristas.py        # CRUD motorista
│   └── alunos.py            # CRUD aluno
└── uploads/                 # Fotos de perfil (criado automaticamente)
```

---

## 🚀 Como rodar

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Iniciar o servidor
```bash
cd app
uvicorn main:app --reload
```

### 3. Acessar a documentação automática
```
http://localhost:8000/docs
```

---

## 🔐 Como funciona a autenticação

1. **Cadastre-se** em `/motoristas/cadastro` ou `/alunos/cadastro`
2. **Faça login** em `/auth/motorista/login` ou `/auth/aluno/login`
3. Copie o `access_token` da resposta
4. No Swagger (`/docs`), clique em **Authorize 🔒** e cole o token
5. Pronto! As rotas protegidas já funcionam

---

## 📋 Endpoints

### 🔐 Autenticação
| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/auth/motorista/login` | Login do motorista |
| POST | `/auth/aluno/login` | Login do aluno |

### 🚗 Motoristas
| Método | Rota | Descrição | Auth? |
|--------|------|-----------|-------|
| POST | `/motoristas/cadastro` | Cadastrar motorista | ❌ |
| GET | `/motoristas/perfil` | Ver meu perfil | ✅ |
| PUT | `/motoristas/perfil` | Atualizar perfil | ✅ |
| POST | `/motoristas/perfil/foto` | Upload de foto | ✅ |
| DELETE | `/motoristas/perfil` | Desativar conta | ✅ |

### 🎓 Alunos
| Método | Rota | Descrição | Auth? |
|--------|------|-----------|-------|
| POST | `/alunos/cadastro` | Cadastrar aluno | ❌ |
| GET | `/alunos/perfil` | Ver meu perfil | ✅ |
| PUT | `/alunos/perfil` | Atualizar perfil | ✅ |
| POST | `/alunos/perfil/foto` | Upload de foto | ✅ |
| DELETE | `/alunos/perfil` | Desativar conta | ✅ |

---

## 🗄️ Dados armazenados

### Motorista
- Nome, e-mail, telefone, senha (hash bcrypt)
- CNH e categoria
- Endereço (logradouro, cidade, estado, CEP)
- Veículo (modelo, placa, ano, cor, capacidade)
- Foto de perfil

### Aluno
- Nome, e-mail, telefone, senha (hash bcrypt)
- Matrícula e escola
- Endereço (logradouro, cidade, estado, CEP)
- Foto de perfil
- Motorista vinculado (opcional)

---

## 🔒 Segurança

| Item | Proteção |
|------|----------|
| Senhas | Hash bcrypt (nunca armazenadas em texto puro) |
| Autenticação | JWT com expiração de 24h |
| Rotas protegidas | Bearer Token no header |
| Banco de dados | SQLite local (arquivo `transporte_escolar.db`) |

---

## ⚠️ Antes de ir para produção

1. Troque a `SECRET_KEY` em `core/security.py` por uma chave forte:
   ```bash
   openssl rand -hex 32
   ```
2. Coloque a chave em variável de ambiente (`.env`)
3. Troque o SQLite por PostgreSQL para múltiplos usuários simultâneos
4. Configure CORS com os domínios reais do seu app
