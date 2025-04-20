# backend/procuracao_api.py

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses   import FileResponse
from pathlib               import Path
import uuid

# Importa a função que você já definiu em gerar_procuracao.py
from gerar_procuracao import preencher_procuracao  
from clientes_api       import router as clientes_router  # <<<

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("temp_uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/api/procuracao")
async def gerar_proc(file: UploadFile = File(...)):
    # 1) Salvamos o upload temporariamente
    temp_id    = uuid.uuid4().hex
    input_path = UPLOAD_DIR / f"{temp_id}_{file.filename}"
    with open(input_path, "wb") as f:
        f.write(await file.read())

    # 2) Chamamos a sua função existente
    output_path = preencher_procuracao(input_path)

    # 3) Devolvemos o .docx gerado
    return FileResponse(
        path=output_path,
        filename=Path(output_path).name,
        media_type=(
          "application/vnd.openxmlformats-"
          "officedocument.wordprocessingml.document"
        )
    )
