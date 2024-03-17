from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from consulta import Consulta
from pydantic import BaseModel, EmailStr
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

consultas = Consulta()

class Dados(BaseModel):
    nome_paciente: str
    email_paciente: EmailStr
    cpf_paciente: str
    convenio: str
    nome_fono: str
    data_consulta: datetime


@app.get("/")
async def root():
    return {"message": "Gerenciamento de Consultas FonoInga"}


@app.get("/listar_consultas/")
async def listar_consultas():

    return consultas.listar_consultas()


@app.get("/consultas_paciente/")
async def consultas_paciente(parametross: dict):
    cpf_paciente = parametross["cpf_paciente"]

    return consultas.consultas_paciente(cpf_paciente)


@app.post("/agendar_consulta/")
async def agendar_consulta(parametros: dict):
    dados = parametros["dados"]

    return consultas.agendar_consulta(dados)


@app.delete("/cancelar_consulta/")
async def cancelar_consulta(parametros: dict):
    cpf_paciente = parametros["cpf_paciente"]
    email_paciente = parametros["email_paciente"]

    return consultas.cancelar_consulta(cpf_paciente, email_paciente)


@app.patch("/alterar_consulta/")
async def alterar_consulta(parametros: dict):
    cpf_paciente = parametros["cpf_paciente"]
    dados = parametros["dados"]

    return consultas.alterar_consulta(cpf_paciente, dados)
