from datetime import datetime
from pydantic import BaseModel, EmailStr
import re
import pika
import uuid


class Consulta:
    def __init__(self):
        self.fila_resultados = None
        self.conexao = None
        self.canal = None
        self.resposta = None
        self.corr_id = None

        self.__estabelecer_conexao()

    class Tipo_Consulta(BaseModel):
        nome_paciente: str
        email_paciente: EmailStr
        cpf_paciente: str
        convenio: str
        nome_fono: str
        data_consulta: datetime

    def __estabelecer_conexao(self) -> pika.channel.Channel:
        conexao = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        canal = conexao.channel()
        canal.exchange_declare(exchange='Consultas', exchange_type='fanout')

        resultado = canal.queue_declare(queue='', exclusive=True)
        fila_resultados = resultado.method.queue

        canal.basic_consume(
            queue=fila_resultados, on_message_callback=self.__receber_resposta, auto_ack=True
        )

        self.conexao = conexao
        self.fila_resultados = fila_resultados
        self.canal = canal

    def __receber_resposta(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.resposta = body

    def __publicar(self, mensagem) -> dict | list | None:
        if type(mensagem) == dict:
            mensagem = str(mensagem)

        self.canal.basic_publish(
            exchange='Consultas',
            routing_key='',
            properties=pika.BasicProperties(
                reply_to=self.fila_resultados,
                correlation_id=self.corr_id
            ),
            body=mensagem)

        self.conexao.process_data_events(time_limit=None)

        return eval(self.resposta)

    def __resetar_configs_resposta(self) -> str:
        self.resposta = None
        self.corr_id = str(uuid.uuid4())

    def __filtro_cpf(self, cpf: str) -> bool:
        return True if len(re.findall(r'\d', cpf)) == 11 else False

    def listar_consultas(self) -> list:
        return self.__publicar({"id_operacao": 4})

    def consultas_paciente(self, cpf_paciente: str) -> list:
        self.__resetar_configs_resposta()

        if not self.__filtro_cpf(cpf_paciente):
            return {"status": 400,
                    "error message": "CPF inválido!"}

        cpf_paciente = "".join(re.findall(r'\d', cpf_paciente))

        resposta = self.__publicar({"id_operacao": 5, "cpf_paciente": cpf_paciente})

        return resposta

    def agendar_consulta(self, dados: Tipo_Consulta) -> dict:
        self.__resetar_configs_resposta()

        dic = {
            "id_operacao": 1,
            "nome_paciente": dados.nome_paciente,
            "email_paciente": dados.email_paciente,
            "cpf_paciente": dados.cpf_paciente,
            "convenio": dados.convenio,
            "nome_fono": dados.nome_fono,
            "data_consulta": str(dados.data_consulta.date()),
            "hora_consulta": str(dados.data_consulta.strftime("%H:%M:%S")),
            "tipo_email": "confirmacao"
        }

        if not self.__filtro_cpf(dados.cpf_paciente):
            return {"status": 400,
                    "error message": "CPF inválido!"}

        dados.cpf_paciente = "".join(re.findall(r'\d', dados.cpf_paciente))

        resposta = self.__publicar(dic)

        return resposta

    def cancelar_consulta(self, cpf_paciente: str, email_paciente: str):
        self.__resetar_configs_resposta()

        if not self.__filtro_cpf(cpf_paciente):
            return {"status": 400,
                    "error message": "CPF inválido!"}

        dic = {
            "id_operacao": 2,
            "cpf_paciente": cpf_paciente,
            "email_paciente": email_paciente,
        }

        resposta = self.__publicar(dic)

        return resposta

    def alterar_consulta(self, cpf_paciente: str, dados: Tipo_Consulta):
        self.__resetar_configs_resposta()

        if not self.__filtro_cpf(cpf_paciente):
            return {"status": 400,
                    "error message": "CPF inválido!"}

        cpf_paciente = "".join(re.findall(r'\d', cpf_paciente))

        dados.cpf_paciente = lambda: cpf_paciente if dados.cpf_paciente == "string" else dados.cpf_paciente

        if dados.cpf_paciente != cpf_paciente:
            return {"error message": "CPF do paciente não pode ser alterado!"}

        dic = {
            "id_operacao": 3,
            "cpf_paciente": cpf_paciente,
            "nome_paciente": dados.nome_paciente,
            "email_paciente": dados.email_paciente,
            "nome_fono": dados.nome_fono,
            "data_consulta": str(dados.data_consulta.date()),
            "hora_consulta": str(dados.data_consulta.strftime("%H:%M:%S")),
            "tipo_email": "alteracao"
        }

        resposta = self.__publicar(dic)

        return resposta
