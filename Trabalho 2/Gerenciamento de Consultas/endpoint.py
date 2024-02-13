from fastapi import FastAPI
from consulta import Consulta
from pydantic import BaseModel, EmailStr
from datetime import datetime

app = FastAPI()

consultas = Consulta()

class Dados(BaseModel):
        nome_paciente: str
        email_paciente: EmailStr
        cpf_paciente: str
        convenio: str
        nome_fono: str
        data_consulta: datetime

@app.get("/listar_consultas/")
async def listar_consultas():
    return consultas.listar_consultas()

@app.get("/consultas_paciente/")
async def consultas_paciente(cpf_paciente: str):
    return consultas.consultas_paciente(cpf_paciente)

@app.post("/agendar_consulta/")
async def agendar_consulta(dados:Dados):
    return consultas.agendar_consulta(dados)

@app.delete("/cancelar_consulta/")
async def cancelar_consulta(cpf_paciente: str, email_paciente: EmailStr):
    return consultas.cancelar_consulta(cpf_paciente, email_paciente)

@app.patch("/alterar_consulta/")
async def alterar_consulta(cpf_paciente: str, dados: Dados):
    return consultas.alterar_consulta(cpf_paciente, dados)