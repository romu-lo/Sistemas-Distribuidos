from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String

import pika
import sys
import os

Base = declarative_base()


class Consultas_agendadas(Base):

    __tablename__ = 'consultas_agendadas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome_paciente = Column(String(100))
    email_paciente = Column(String(100))
    cpf_paciente = Column(String(11))
    convenio = Column(String(100))
    nome_fono = Column(String(100))
    data_consulta = Column(String(10))
    hora_consulta = Column(String(8))

    def __init__(self, id, nome_paciente, email_paciente, cpf_paciente, convenio, nome_fono, data_consulta, hora_consulta):
        self.id = id
        self.nome_paciente = nome_paciente
        self.email_paciente = email_paciente
        self.cpf_paciente = cpf_paciente
        self.convenio = convenio
        self.nome_fono = nome_fono
        self.data_consulta = data_consulta
        self.hora_consulta = hora_consulta

    def __repr__(self):
        return f"<Consultas_agendadas(nome_paciente='{self.nome_paciente}', email_paciente='{self.email_paciente}', cpf_paciente='{self.cpf_paciente}', convenio='{self.convenio}', nome_fono='{self.nome_fono}', data_consulta='{self.data_consulta}', hora_consulta='{self.hora_consulta}')>"


class BDConsultas:
    def __init__(self) -> None:
        Base = declarative_base()

        self.engine = create_engine(
            'mysql+mysqlconnector://root:admin@localhost:3306/trabalho2sd')
        Base.metadata.create_all(bind=self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        self.__estabelecer_comunicação()

        def callback(ch, method, properties, body):
            body = eval(body)
            tipo_operacao = body['id_operacao']

            if tipo_operacao == 1:
                resposta = self.agendar_consulta(body)

            elif tipo_operacao == 2:
                resposta = self.cancelar_consulta(body['cpf_paciente'])

            elif tipo_operacao == 3:
                resposta = self.alterar_consulta(body['cpf_paciente'], body)

            elif tipo_operacao == 4:
                resposta = self.listar_consultas()

            elif tipo_operacao == 5:
                resposta = self.consultas_paciente(body['cpf_paciente'])

            self.__enviar_resposta(ch, method, properties, resposta)

        self.canal.basic_qos(prefetch_count=1)
        self.canal.basic_consume(
            queue=self.nome_fila, on_message_callback=callback)

        print('\nBANCO DE DADOS - CONSULTAS.\nAguardando mensagens. Para sair pressione CTRL+C')
        self.canal.start_consuming()

    def __estabelecer_comunicação(self) -> pika.channel.Channel:
        conexao = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        canal = conexao.channel()

        canal.exchange_declare(exchange='Consultas', exchange_type='fanout')

        resultado = canal.queue_declare(queue='', exclusive=True)
        nome_fila = resultado.method.queue

        canal.queue_bind(exchange='Consultas', queue=nome_fila)

        self.canal = canal
        self.nome_fila = nome_fila

    def __enviar_resposta(self, ch, method, props, resposta: dict):
        ch.basic_publish(exchange='',
                         routing_key=props.reply_to,
                         properties=pika.BasicProperties(
                             correlation_id=props.correlation_id),
                         body=str(resposta))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def __formatar_resposta_consultas(self, consultas: list) -> dict:
        dict_consultas = {"consultas": []}

        for consulta in consultas:
            dict_consultas['consultas'].append({
                "nome_paciente": consulta.nome_paciente,
                "email_paciente": consulta.email_paciente,
                "cpf_paciente": consulta.cpf_paciente,
                "convenio": consulta.convenio,
                "nome_fono": consulta.nome_fono,
                "data_consulta": consulta.data_consulta,
                "hora_consulta": consulta.hora_consulta
            })

        return dict_consultas

    def listar_consultas(self) -> None:
        consultas = self.session.query(Consultas_agendadas).all()

        dict_consultas = self.__formatar_resposta_consultas(consultas)

        return dict_consultas

    def consultas_paciente(self, cpf_paciente: str) -> None:
        consultas = self.session.query(Consultas_agendadas).filter_by(
            cpf_paciente=cpf_paciente).all()

        dict_consultas = self.__formatar_resposta_consultas(consultas)

        return dict_consultas

    def agendar_consulta(self, dados: dict) -> None:
        consulta = Consultas_agendadas(
            id=None,
            nome_paciente=dados['nome_paciente'],
            email_paciente=dados['email_paciente'],
            cpf_paciente=dados['cpf_paciente'],
            convenio=dados['convenio'],
            nome_fono=dados['nome_fono'],
            data_consulta=dados['data_consulta'],
            hora_consulta=dados['hora_consulta']
        )
        self.session.add(consulta)
        self.session.commit()

        return {"status": 200,
                "message": "Consulta agendada com sucesso!"}

    def cancelar_consulta(self, cpf_paciente: str) -> bool:
        try:
            consulta = self.session.query(Consultas_agendadas).filter_by(
                cpf_paciente=cpf_paciente).first()
            self.session.delete(consulta)
            self.session.commit()

            return {"status": 200,
                    "message": "Consulta cancelada com sucesso!"}

        except:
            return {"status": 400,
                    "error message": "Consulta não encontrada!"}

    def alterar_consulta(self, cpf_paciente, dados):
        try:
            consulta = self.session.query(Consultas_agendadas).filter_by(
                cpf_paciente=cpf_paciente).first()

            consulta.nome_paciente = dados['nome_paciente']
            consulta.email_paciente = dados['email_paciente']
            consulta.cpf_paciente = dados['cpf_paciente']
            consulta.convenio = dados['convenio']
            consulta.nome_fono = dados['nome_fono']
            consulta.data_consulta = dados['data_consulta']
            consulta.hora_consulta = dados['hora_consulta']
            self.session.commit()

            return {"status": 200,
                    "message": "Consulta alterada com sucesso!"}

        except:
            return {"status": 400,
                    "error message": "Consulta não encontrada!"}


if __name__ == "__main__":
    try:
        BDConsultas()
    except KeyboardInterrupt:
        print('\nInterrompido\n')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
