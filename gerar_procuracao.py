# backend/gerar_procuracao.py

import uuid, json, re
from pathlib import Path
from datetime import date

import fitz            # PyMuPDF
import pytesseract
from PIL import Image
from docxtpl import DocxTemplate

from openai_helper import analisar_texto_para_procuracao

# Paths
MODELO_PATH = Path("modelos/procuracao_modelo.docx")
SAIDA_DIR   = Path("documentos_gerados")
TEMP_DATA   = Path("temp_data")

# Certifica que as pastas existem
for d in (SAIDA_DIR, TEMP_DATA):
    d.mkdir(exist_ok=True)

def extrair_dados_pdf(caminho_pdf: Path) -> dict:
    # 1) Faz OCR de cada página
    texto = ""
    try:
        doc = fitz.open(str(caminho_pdf))
        for pg in doc:
            pix = pg.get_pixmap(dpi=300)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            texto += pytesseract.image_to_string(img, lang="por") + "\n"
    except Exception as e:
        print("Erro durante OCR:", e)

    # 2) Chama a IA para extrair os campos
    dados = analisar_texto_para_procuracao(texto)

    # 3) Fallback regex se algum campo vier vazio ou placeholder
    if not dados.get("nome") or "NÃO ENCONTRADO" in dados["nome"]:
        m = re.search(r"([A-ZÀ-Ÿ][a-zà-ÿ]+(?:\s+[A-ZÀ-Ÿ][a-zà-ÿ]+)+)", texto)
        if m: dados["nome"] = m.group(1).strip()
    if not dados.get("cpf") or "–" in dados["cpf"]:
        m = re.search(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b", texto)
        if m: dados["cpf"] = m.group(0)

    # 4) Salva temporariamente raw + estruturado
    extract_id = uuid.uuid4().hex
    dump = {
        "raw_text": texto,
        "data":      dados
    }
    with open(TEMP_DATA / f"extracted_{extract_id}.json", "w", encoding="utf-8") as f:
        json.dump(dump, f, ensure_ascii=False, indent=2)

    return dados

def preencher_procuracao(arquivo_cliente: Path) -> Path:
    # 1) Extrai / corrige dados
    dados = extrair_dados_pdf(arquivo_cliente)

    # 2) Acrescenta data de hoje
    dados["data"] = date.today().strftime("%d de %B de %Y")

    # 3) Renderiza o template
    tpl = DocxTemplate(str(MODELO_PATH))
    tpl.render(dados)

    # 4) Salva o .docx com nome único
    nome_saida = f"procuracao_{uuid.uuid4().hex}.docx"
    destino    = SAIDA_DIR / nome_saida
    tpl.save(str(destino))

    return destino
