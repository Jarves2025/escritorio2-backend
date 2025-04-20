# backend/ia_helper.py
import openai
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def extrair_dados_com_ia(texto_documento: str) -> dict:
    prompt = f"""
A partir do texto abaixo, extraia apenas os seguintes campos de forma precisa:
- Nome completo
- CPF

Texto do documento:
\"\"\"
{texto_documento}
\"\"\"

Retorne os dados no seguinte formato JSON:
{{ "nome": "...", "cpf": "..." }}
"""

    try:
        resposta = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500,
        )

        conteudo = resposta.choices[0].message["content"]
        return eval(conteudo)
    
    except Exception as e:
        print(f"❌ Erro ao consultar a IA: {e}")
        return {
            "nome": "NOME NÃO IDENTIFICADO",
            "cpf": "CPF NÃO IDENTIFICADO"
        }
