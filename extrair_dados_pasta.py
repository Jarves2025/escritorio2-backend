#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

import fitz         # PyMuPDF
import pytesseract
import cv2
from PIL import Image

from openai_helper import analisar_texto_para_procuracao

# Se necessário, descomente e ajuste a linha abaixo para apontar ao executável do Tesseract
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

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

def coletar_texto_da_pasta(pasta: Path) -> str:
    texto_completo = ""
    # extensões que vamos processar
    padroes = ["*.pdf", "*.png", "*.jpg", "*.jpeg", "*.tiff", "*.bmp"]
    for padrao in padroes:
        for caminho in pasta.glob(padrao):
            try:
                if caminho.suffix.lower() == ".pdf":
                    texto_completo += extract_text_from_pdf(caminho)
                else:
                    texto_completo += extract_text_from_image(caminho)
                texto_completo += "\n"
            except Exception as e:
                print(f"[!] Erro ao processar {caminho.name}: {e}")
    return texto_completo

def main():
    parser = argparse.ArgumentParser(
        description="Extrai dados de documentos em uma pasta e salva em JSON via IA"
    )
    parser.add_argument(
        "pasta",
        type=str,
        help="Caminho da pasta com os documentos do cliente"
    )
    args = parser.parse_args()

    pasta = Path(args.pasta)
    if not pasta.is_dir():
        print(f"[!] A pasta indicada não existe: {pasta}")
        return

    print(f"> Processando documentos em: {pasta}")
    texto = coletar_texto_da_pasta(pasta)

    print("> Enviando texto para a IA...")
    dados = analisar_texto_para_procuracao(texto)

    # Salva o JSON dentro da mesma pasta
    arquivo_saida = pasta / "dados_extraidos.json"
    with open(arquivo_saida, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

    print(f"✔ Dados extraídos salvos em: {arquivo_saida}")

if __name__ == "__main__":
    main()
