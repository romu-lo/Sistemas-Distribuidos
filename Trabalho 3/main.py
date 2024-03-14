from fastapi import FastAPI, HTTPException
import httpx
from httpx import AsyncClient
from typing import List

app = FastAPI()


URLS_SERVICOS = [
    "http://127.0.0.1:8001/",
    "http://127.0.0.1:8002/",
]

# Função para encaminhar a solicitação para os serviços subjacentes
async def forward_request(url: str, path: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{url}/{path}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Failed to forward request: {e}")

# Endpoint para rota raiz
@app.get("/")
async def read_root():
    return {"message": "Hello World"}

# Endpoint para encaminhar a solicitação para os serviços subjacentes com balanceamento de carga
@app.get("/service/{service_name}")
async def forward_to_service(service_name: str):
    try:
        # Selecionar um serviço aleatório da lista de URLs
        selected_service = URLS_SERVICOS[hash(service_name) % len(URLS_SERVICOS)]
        response = await forward_request(selected_service, service_name)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to forward request: {e}")

# Lidar com o caso em que a rota não foi encontrada
@app.exception_handler(404)
async def not_found_exception_handler(request, exc):
    return {"message": "Endpoint not found"}


#######################################################
#######################################################
#######################################################

from typing import List
from fastapi import FastAPI, HTTPException
from httpx import AsyncClient

app = FastAPI()

# Lista de URLs dos serviços disponíveis
SERVICE_URLS = [
    "http://localhost:8001",
    "http://localhost:8002",
    "http://localhost:8003",
]

@app.get("/")
async def read_root():
    return {"message": "Hello World"}

# Implementação do balanceamento de carga
async def balance_load(request):
    async with AsyncClient() as client:
        for url in URLS_SERVICOS:
            try:
                response = await client.get(url + request.url.path)
                if response.status_code == 200:
                    return response.json()
            except Exception as e:
                print(f"Failed to reach {url}: {e}")
                continue
        raise HTTPException(status_code=503, detail="All services are unavailable.")

# Rota para encaminhar solicitações para serviços subjacentes
@app.get("/api/{path:path}")
async def forward_to_services(path: str):
    return await balance_load(request)
