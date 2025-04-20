from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Servidor do Escritório 2.0 está online ✅"}
