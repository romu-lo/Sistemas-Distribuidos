from fastapi import FastAPI
from datetime import datetime
import requests
from pydantic import BaseModel, EmailStr
import re

app = FastAPI()

consultas = []

class Dados(BaseModel):
    nome_paciente:str 
    email_paciente:EmailStr 
    cpf_paciente:str 
    convenio:str
    nome_fono:str
    data_consulta:datetime

@app.get("/listar_consultas/")
async def listar_consultas():
    return consultas

@app.post("/agendar_consulta/")
async def agendar_consulta(dados:Dados):
    
    dic = {"nome_paciente" : dados.nome_paciente,
           "email_paciente" : dados.email_paciente,
           "nome_fono" : dados.nome_fono,
           "data_consulta" : str(dados.data_consulta.date()),
           "hora_consulta" : str(dados.data_consulta.strftime("%H:%M:%S")),
           "tipo_email" : "confirmacao"
           }
    
    filtro_cpf = lambda x: True if len(re.findall(r'\d', x)) == 11 else False

    if not filtro_cpf(dados.cpf_paciente):
        return {"status":400, 
                "error message" : "CPF inválido!"}

    dados.cpf_paciente = "".join(re.findall(r'\d', dados.cpf_paciente))

    resposta = requests.post('http://127.0.0.1:8001/enviar_email/', json=dic)

    if resposta.status_code != 200:
        return {"status":400, 
                "error message" : "Erro ao enviar e-mail! Consulta não agendada."}

    consultas.append(dados)

    return {"message": f"Consulta agendada com sucesso para o paciente {dados.nome_paciente}!"}


@app.post("/cancelar_consulta/")
async def cancelar_consulta(cpf_paciente: str):

    filtro_cpf = lambda x: True if len(re.findall(r'\d', x)) == 11 else False

    if not filtro_cpf(cpf_paciente):
        return {"status":400, 
                "error message" : "CPF inválido!"}

    for id_consulta in range(len(consultas)):
        if consultas[id_consulta].cpf_paciente == cpf_paciente:
            consulta_cancelada = consultas.pop(id_consulta)

            dic = {"nome_paciente" : consulta_cancelada.nome_paciente,
                   "email_paciente" : consulta_cancelada.email_paciente,
                   "nome_fono" : consulta_cancelada.nome_fono,
                   "data_consulta" : str(consulta_cancelada.data_consulta.date()),
                   "hora_consulta" : str(consulta_cancelada.data_consulta.strftime("%H:%M:%S")),
                   "tipo_email" : "cancelamento"
                   }
            
            resposta = requests.post('http://127.0.0.1:8001/enviar_email/', json=dic)
            if resposta.status_code != 200:
                    return {"status":400, 
                            "error message" : "Erro ao enviar e-mail! Consulta não cancelada."}
            return {"message": f"Consulta do paciente {consulta_cancelada.nome_paciente} cancelada com sucesso!"}
    
    return {"error message" : "Consulta não encontrada para o CPF " + cpf_paciente}  	

@app.patch("/alterar_consulta/")
async def alterar_consulta(cpf_paciente: str, dados: Dados):

    filtro_cpf = lambda x: True if len(re.findall(r'\d', x)) == 11 else False

    if not filtro_cpf(cpf_paciente):
        return {"status":400, 
                "error message" : "CPF inválido!"}

    cpf_paciente = "".join(re.findall(r'\d', cpf_paciente))

    dados.cpf_paciente = lambda: cpf_paciente if dados.cpf_paciente == "string" else dados.cpf_paciente

    for id_consulta in range(len(consultas)):
        if consultas[id_consulta].cpf_paciente == cpf_paciente:
            dados.nome_paciente = lambda : consultas[id_consulta].nome_paciente if dados.nome_paciente == "string" else dados.nome_paciente
            dados.email_paciente = lambda: consultas[id_consulta].email_paciente if dados.email_paciente == "user@example.com" else dados.email_paciente
            dados.nome_fono = lambda: consultas[id_consulta].nome_fono if dados.nome_fono == "string" else dados.nome_fono
            dados.data_consulta = lambda: consultas[id_consulta].data_consulta if dados.data_consulta == "string" else dados.data_consulta

            consultas[id_consulta] = dados
            return {"message": f"Consulta do paciente {dados.nome_paciente} alterada com sucesso!"}
        

        dic = {"nome_paciente" : dados.nome_paciente,
            "email_paciente" : dados.email_paciente,
            "nome_fono" : dados.nome_fono,
            "data_consulta" : str(dados.data_consulta.date()),
            "hora_consulta" : str(dados.data_consulta.strftime("%H:%M:%S")),
            "tipo_email" : "alteracao"
        }

        resposta = requests.post('http://127.0.0.1:8001/enviar_email/', json=dic)
        if resposta.status_code != 200:
            return {"status":400, 
                    "error message" : "Erro ao enviar e-mail! Consulta não agendada."}
    
    return {"error message" : "Consulta não encontrada para o CPF " + cpf_paciente}