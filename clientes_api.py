# backend/clientes_api.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from uuid import uuid4
from pathlib import Path
import json

router = APIRouter(
    prefix="/api/clientes",
    tags=["Clientes"],
)

DATA_DIR  = Path("data")
DATA_FILE = DATA_DIR / "clientes.json"

# Garante que exista o diretório e o arquivo
DATA_DIR.mkdir(exist_ok=True)
if not DATA_FILE.exists():
    DATA_FILE.write_text("[]", encoding="utf-8")

class Endereco(BaseModel):
    logradouro:      str = Field(..., example="Rua das Flores")
    nome_logradouro: str = Field(..., example="Floriano Peixoto")
    numero:          str = Field(..., example="123")
    complemento:     str = Field("", example="Apto 45")
    bairro:          str = Field(..., example="Centro")
    cidade:          str = Field(..., example="São Paulo/SP")
    cep:             str = Field(..., example="01000-000")

class ClienteCreate(BaseModel):
    nome:          str     = Field(..., example="João da Silva")
    nacionalidade: str     = Field(..., example="BRASILEIRO(A)")
    estado_civil:  str     = Field(..., example="CASADO(A)")
    profissao:     str     = Field(..., example="ADVOGADO")
    cpf:           str     = Field(..., example="123.456.789-00")
    endereco:      Endereco

class Cliente(ClienteCreate):
    id: str

def _read_all():
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))

def _write_all(clients):
    DATA_FILE.write_text(json.dumps(clients, ensure_ascii=False, indent=2), encoding="utf-8")

@router.post("/", response_model=Cliente, summary="Cadastrar novo cliente")
def criar_cliente(c: ClienteCreate):
    todos = _read_all()
    novo = c.dict()
    novo["id"] = str(uuid4())
    todos.append(novo)
    _write_all(todos)
    return novo

@router.get("/", response_model=list[Cliente], summary="Listar todos os clientes")
def listar_clientes():
    return _read_all()

@router.get("/{cliente_id}", response_model=Cliente, summary="Buscar cliente por ID")
def buscar_cliente(cliente_id: str):
    todos = _read_all()
    for cli in todos:
        if cli["id"] == cliente_id:
            return cli
    raise HTTPException(status_code=404, detail="Cliente não encontrado")

@router.put("/{cliente_id}", response_model=Cliente, summary="Atualizar cliente")
def atualizar_cliente(cliente_id: str, c: ClienteCreate):
    todos = _read_all()
    for i, cli in enumerate(todos):
        if cli["id"] == cliente_id:
            atualizado = c.dict()
            atualizado["id"] = cliente_id
            todos[i] = atualizado
            _write_all(todos)
            return atualizado
    raise HTTPException(status_code=404, detail="Cliente não encontrado")

@router.delete("/{cliente_id}", summary="Remover cliente")
def deletar_cliente(cliente_id: str):
    todos = _read_all()
    novos = [cli for cli in todos if cli["id"] != cliente_id]
    if len(novos) == len(todos):
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    _write_all(novos)
    return {"detail": "Cliente removido"}
