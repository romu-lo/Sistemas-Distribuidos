import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pika
import sys
import os


def get_email_cancelamento(cpf_paciente):
    return f'''Olá!

A consulta agendada para o CPF {cpf_paciente} foi cancelada.

Se surgir alguma dúvida ou se precisar reagendar, estamos aqui para ajudar. Não hesite em nos contatar.

Atenciosamente,
Ameinda Villas-Lobos
Secretária da Clínica FonoIngá
'''


def get_email_confirmacao(nome_paciente, nome_fono, data_consulta, hora_consulta):
    return f'''Olá, {nome_paciente}!
Ótimas notícias! Sua consulta com o(a) fonoaudiólogo(a) {nome_fono} foi agendada com sucesso.

Data: {data_consulta}
Horário: {hora_consulta}

Anote essas informações em sua agenda para não se esquecer. 
Se surgir alguma dúvida ou se precisar reagendar, estamos aqui para ajudar. Não hesite em nos contatar.
A equipe está pronta para oferecer um atendimento de qualidade e tornar sua visita o mais agradável possível.

Nos vemos em breve!

Atenciosamente,
Ameinda Villas-Lobos 
Secretária da Clínica FonoIngá
'''


def get_email_alteracao(nome_paciente, nome_fono, data_consulta, hora_consulta):
    return f'''Olá, {nome_paciente}!

Sua consulta foi alterada com sucesso!

Data: {data_consulta}
Horário: {hora_consulta}
Fonoaudiólogo(a): {nome_fono}

Se surgir alguma dúvida ou se precisar reagendar, estamos aqui para ajudar. Não hesite em nos contatar.

Atenciosamente,
Ameinda Villas-Lobos
Secretária da Clínica FonoIngá
'''


def main():
    conexao = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    canal = conexao.channel()

    canal.exchange_declare(exchange='Consultas', exchange_type='fanout')

    resultado = canal.queue_declare(queue='', exclusive=True)
    nome_fila = resultado.method.queue

    canal.queue_bind(exchange='Consultas', queue=nome_fila)

    def callback(ch, method, properties, body):
        enviar_email(body)

    canal.basic_qos(prefetch_count=1)
    canal.basic_consume(
        queue=nome_fila, on_message_callback=callback, auto_ack=True)

    print('\nENVIO DE EMAIL\nAguardando mensagens. Para sair pressione CTRL+C')
    canal.start_consuming()


def enviar_email(mensagem):
    mensagem = eval(mensagem)

    # print(mensagem)

    tipo_email = mensagem['id_operacao']

    if tipo_email == 4 or tipo_email == 5:
        return {"message": "E-mail não enviado."}
    
    cpf_paciente = mensagem['cpf_paciente']
    email_paciente = mensagem['email_paciente']

    if tipo_email == 1 or tipo_email == 3:
        nome_paciente = mensagem['nome_paciente']
        nome_fono = mensagem['nome_fono']
        data_consulta = mensagem['data_consulta']
        hora_consulta = mensagem['hora_consulta']

    remetente_email = "fonoinga.fono@gmail.com"
    remetente_senha = "ytxn nckj nbrd aexy"

    mensagem = MIMEMultipart()
    mensagem["From"] = remetente_email
    mensagem["To"] = email_paciente
    mensagem["Subject"] = f"FonoIngá - Confirmação da Consulta"

    if tipo_email == 1:
        corpo_mensagem = get_email_confirmacao(
            nome_paciente, nome_fono, data_consulta, hora_consulta)

    elif tipo_email == 2:
        corpo_mensagem = get_email_cancelamento(cpf_paciente)

    elif tipo_email == 3:
        corpo_mensagem = get_email_alteracao(
            nome_paciente, nome_fono, data_consulta, hora_consulta)

    mensagem.attach(MIMEText(corpo_mensagem, "plain"))

    servidor_smtp = "smtp.gmail.com"
    porta_smtp = 587
    with smtplib.SMTP(servidor_smtp, porta_smtp) as servidor:
        servidor.ehlo()
        servidor.starttls()
        servidor.ehlo()
        servidor.login(remetente_email, remetente_senha)
        servidor.sendmail(remetente_email, email_paciente,
                          mensagem.as_string())

    return {"message": "E-mail enviado com sucesso!"}


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nInterrompido\n')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
