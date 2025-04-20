# backend/extrair_api.py

from fastapi import APIRouter, UploadFile, File
from typing import List
from openai_helper import analisar_texto_para_procuracao
import fitz         # PyMuPDF
import pytesseract
import cv2
from PIL import Image
from pathlib import Path

router = APIRouter()

def extract_text_from_pdf(pdf_path: Path) -> str:
    texto = ""
    doc = fitz.open(str(pdf_path))
    for page in doc:
        pix = page.get_pixmap(dpi=300)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        texto += pytesseract.image_to_string(img, lang="por") + "\n"
    return texto

def extract_text_from_image(img_path: Path) -> str:
    img = cv2.imread(str(img_path))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return pytesseract.image_to_string(gray, lang="por")

@router.post("/api/extrair-pasta")
async def extrair_pasta(files: List[UploadFile] = File(...)):
    """
    Recebe múltiplos arquivos (PDFs/imagens) de uma pasta,
    executa OCR em cada um, envia todo o texto para a IA
    e retorna um dicionário com os dados extraídos.
    """
    texto_completo = ""
    temp_dir = Path("temp_uploads")
    temp_dir.mkdir(exist_ok=True)

    for f in files:
        temp_path = temp_dir / f.filename
        # Salva temporariamente o arquivo enviado
        with open(temp_path, "wb") as out:
            out.write(await f.read())

        # Extrai texto conforme extensão
        if temp_path.suffix.lower() == ".pdf":
            texto_completo += extract_text_from_pdf(temp_path)
        else:
            texto_completo += extract_text_from_image(temp_path)
        texto_completo += "\n"

        # Remove o arquivo temporário
        temp_path.unlink()

    # Chama a IA para processar todo o texto e extrair campos
    dados = analisar_texto_para_procuracao(texto_completo)
    return dados
