# backend/openai_helper.py

import os
import json
from dotenv import load_dotenv
import openai

# Carrega a variável de ambiente
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def analisar_texto_para_procuracao(texto: str) -> dict:
    prompt = f"""
    Abaixo está o texto completo OCR extraído dos documentos de um cliente.
    Extraia *EXATAMENTE* estes campos, e responda somente em JSON válido:

    {{
      "nome": "NOME COMPLETO",
      "nacionalidade": "BRASILEIRO(A)",
      "estado_civil": "CASADO(A)",
      "profissao": "PROFISSÃO",
      "cpf": "000.000.000-00",
      "logradouro": "RUA",
      "nome_logradouro": "NOME DO LOGRADOURO",
      "numero": "123",
      "complemento": "APARTAMENTO 45",
      "bairro": "BAIRRO",
      "cidade": "CIDADE/UF",
      "cep": "00000-000"
    }}

    Texto extraído:
    '''
    {texto}
    '''
    """
    try:
        resp = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        # extrai o JSON da resposta
        content = resp.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        print("Erro OpenAI:", e)
        return {
          "nome":"NOME NÃO ENCONTRADO",
          "nacionalidade":"–",
          "estado_civil":"–",
          "profissao":"–",
          "cpf":"–",
          "logradouro":"–",
          "nome_logradouro":"–",
          "numero":"–",
          "complemento":"–",
          "bairro":"–",
          "cidade":"–",
          "cep":"–"
        }

def perguntar_para_ia(pergunta: str) -> str:
    try:
        resp = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": pergunta}],
            temperature=0.7
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print("Erro perguntar_para_ia:", e)
        return ""
