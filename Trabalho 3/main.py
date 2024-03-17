from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
from datetime import datetime
import requests
import random

URLS_ENDPOINTS = [
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8001",
    "http://127.0.0.1:8002",
]

PESOS = [2, 1, 1]

SERVICOS = {
    "listar_consultas": {"url": "/listar_consultas/",
                         "metodo": requests.get},

    "consultas_paciente": {"url": "/consultas_paciente/",
                           "metodo": requests.get},

    "agendar_consulta": {"url": "/agendar_consulta/",
                         "metodo": requests.post},

    "cancelar_consulta": {"url": "/cancelar_consulta/",
                          "metodo": requests.delete},

    "alterar_consulta": {"url": "/alterar_consulta/",
                         "metodo": requests.patch}
}

gateway = FastAPI()


class Dados(BaseModel):
    nome_paciente: str
    email_paciente: EmailStr
    cpf_paciente: str
    convenio: str
    nome_fono: str
    data_consulta: datetime


def escolher_endpoint() -> tuple[str, list]:
    lista_endpoints = URLS_ENDPOINTS.copy()
    pesos = PESOS.copy()

    endpoints_offline = []

    while len(lista_endpoints) > 0:
        endpoint = random.choices(lista_endpoints, weights=pesos)[0]
        pesos.pop(lista_endpoints.index(endpoint))
        lista_endpoints.remove(endpoint)

        try:
            status_endpoint = requests.get(endpoint, timeout=30).status_code

        except:
            endpoints_offline.append(endpoint[-4:])
            continue

        if status_endpoint == 200:
            return endpoint, endpoints_offline

    raise Exception("Nenhum endpoint disponível")


def encaminhar_solicitacao(servico: dict, parametros: dict = None) -> dict:
    endpoint, endpoints_ofline = escolher_endpoint()
    porta_enpoint = endpoint[-4:]
    endpoint_servico = f"{endpoint}{servico['url']}"

    resposta = servico["metodo"](endpoint_servico, json=parametros)

    return {"Endpoints Testados": endpoints_ofline,
            "Endpoint Escolhido": porta_enpoint,
            "Resposta": resposta.json()}


@gateway.get("/")
async def root():
    return {"message": "API Gateway"}


@gateway.get(SERVICOS["listar_consultas"]["url"])
async def listar_consultas():
    return encaminhar_solicitacao(SERVICOS["listar_consultas"])


@gateway.get(SERVICOS["consultas_paciente"]["url"])
async def consultas_paciente(cpf_paciente: str):
    parametros = {"cpf_paciente": cpf_paciente}

    return encaminhar_solicitacao(SERVICOS["consultas_paciente"], parametros)


@gateway.post(SERVICOS["agendar_consulta"]["url"])
async def agendar_consulta(dados: Dados):
    parametros = {"dados": dados.model_dump_json()}

    return encaminhar_solicitacao(SERVICOS["agendar_consulta"], parametros)


@gateway.delete(SERVICOS["cancelar_consulta"]["url"])
async def cancelar_consulta(cpf_paciente: str, email_paciente: EmailStr):
    parametros = {"cpf_paciente": cpf_paciente,
                  "email_paciente": email_paciente}

    return encaminhar_solicitacao(SERVICOS["cancelar_consulta"], parametros)


@gateway.patch(SERVICOS["alterar_consulta"]["url"])
async def alterar_consulta(cpf_paciente: str, dados: Dados):
    parametros = {"cpf_paciente": cpf_paciente, "dados": dados}

    return encaminhar_solicitacao(SERVICOS["alterar_consulta"], parametros)
