# 🏦 Banking API

## 🔗 Repositório
https://github.com/SEU_USUARIO/banking-api

## 📋 Descrição
API RESTful assíncrona para gerenciamento de operações bancárias com autenticação JWT.
Permite cadastro de usuários, criação de contas correntes, depósitos, saques e extrato.

## 🚀 Tecnologias
- FastAPI
- SQLAlchemy 2.0 async
- SQLite + aiosqlite
- JWT com python-jose
- bcrypt com passlib
- Pydantic v2

## ⚙️ Como rodar
pip install -r requirements.txt
uvicorn main:app --reload

Acesse: http://localhost:8000/docs

## 📌 Endpoints
| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| POST | /auth/register | ❌ | Criar usuário |
| POST | /auth/login | ❌ | Obter JWT |
| POST | /accounts/ | ✅ | Criar conta |
| GET | /accounts/ | ✅ | Listar contas |
| GET | /accounts/{id}/statement | ✅ | Extrato |
| POST | /transactions/{id}/deposit | ✅ | Depósito |
| POST | /transactions/{id}/withdraw | ✅ | Saque |
