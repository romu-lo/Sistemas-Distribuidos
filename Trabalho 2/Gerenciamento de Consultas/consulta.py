from datetime import datetime
from pydantic import BaseModel, EmailStr
import re
import pika

class Consulta:
    def __init__(self):
        self.consultas = []
        self.canal = self.__estabelecer_conexao()

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
        canal.queue_declare(queue='Consultas')
        return canal
    

    def __filtro_cpf(self, cpf: str) -> bool:
        return True if len(re.findall(r'\d', cpf)) == 11 else False


    def listar_consultas(self):
        return self.consultas

    def agendar_consulta(self, dados: Tipo_Consulta):

        dic =   {
                "id_operacao": 1,
                "nome_paciente": dados.nome_paciente,
                "email_paciente": dados.email_paciente,
                "nome_fono": dados.nome_fono,
                "data_consulta": str(dados.data_consulta.date()),
                "hora_consulta": str(dados.data_consulta.strftime("%H:%M:%S")),
                "tipo_email": "confirmacao"
                }

        if not self.__filtro_cpf(dados.cpf_paciente):
            return {"status": 400,
                    "error message": "CPF inválido!"}

        dados.cpf_paciente = "".join(re.findall(r'\d', dados.cpf_paciente))

        self.canal.basic_publish(
            exchange='', routing_key='Consultas', body=str(dic))

        self.consultas.append(dados)

        return {"message": f"Consulta agendada com sucesso para o paciente {dados.nome_paciente}!"}


    def cancelar_consulta(self, cpf_paciente: str):
        if not self.__filtro_cpf(cpf_paciente):
            return {"status": 400,
                    "error message": "CPF inválido!"}

        for id_consulta in range(len(self.consultas)):
            if self.consultas[id_consulta].cpf_paciente == cpf_paciente:
                consulta_cancelada = self.consultas.pop(id_consulta)

                dic = {
                    "id_operacao": 2,
                    "nome_paciente": consulta_cancelada.nome_paciente,
                    "email_paciente": consulta_cancelada.email_paciente,
                    "nome_fono": consulta_cancelada.nome_fono,
                    "data_consulta": str(consulta_cancelada.data_consulta.date()),
                    "hora_consulta": str(consulta_cancelada.data_consulta.strftime("%H:%M:%S")),
                    "tipo_email": "cancelamento"
                    }

                self.canal.basic_publish(
                    exchange='', routing_key='Consultas', body=str(dic))

                return {"message": f"Consulta do paciente {consulta_cancelada.nome_paciente} cancelada com sucesso!"}

        return {"error message": "Consulta não encontrada para o CPF " + cpf_paciente}

    def alterar_consulta(self, cpf_paciente: str, dados: Tipo_Consulta):
        if not self.__filtro_cpf(cpf_paciente):
            return {"status": 400,
                    "error message": "CPF inválido!"}

        cpf_paciente = "".join(re.findall(r'\d', cpf_paciente))

        dados.cpf_paciente = lambda: cpf_paciente if dados.cpf_paciente == "string" else dados.cpf_paciente

        for id_consulta in range(len(self.consultas)):
            if self.consultas[id_consulta].cpf_paciente == cpf_paciente:
                dados.nome_paciente = lambda: self.consultas[
                    id_consulta].nome_paciente if dados.nome_paciente == "string" else dados.nome_paciente
                dados.email_paciente = lambda: self.consultas[
                    id_consulta].email_paciente if dados.email_paciente == "user@example.com" else dados.email_paciente
                dados.nome_fono = lambda: self.consultas[id_consulta].nome_fono if dados.nome_fono == "string" else dados.nome_fono
                dados.data_consulta = lambda: self.consultas[
                    id_consulta].data_consulta if dados.data_consulta == "string" else dados.data_consulta

                self.consultas[id_consulta] = dados
                return {"message": f"Consulta do paciente {dados.nome_paciente} alterada com sucesso!"}

            dic = {
                "id_operacao": 3,
                "nome_paciente": dados.nome_paciente,
                "email_paciente": dados.email_paciente,
                "nome_fono": dados.nome_fono,
                "data_consulta": str(dados.data_consulta.date()),
                "hora_consulta": str(dados.data_consulta.strftime("%H:%M:%S")),
                "tipo_email": "alteracao"
                }

            self.canal.basic_publish(
                exchange='', routing_key='Consultas', body=str(dic))

        return {"error message": "Consulta não encontrada para o CPF " + cpf_paciente}
