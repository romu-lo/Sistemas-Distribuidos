from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pydantic import BaseModel, EmailStr

class Dados(BaseModel):
    nome_paciente:str
    email_paciente:EmailStr 
    nome_fono:str
    data_consulta:str
    hora_consulta:str
    tipo_email:str

app = FastAPI()
origins = ["http://localhost:8000"]
app.add_middleware(CORSMiddleware, 
                   allow_origins=origins, 
                   allow_credentials=True, 
                   allow_methods=["*"], 
                   allow_headers=["*"])

@app.post("/enviar_email/")
async def enviar_email(dados:Dados):

    nome_paciente = dados.nome_paciente
    email_paciente = dados.email_paciente
    nome_fono = dados.nome_fono
    data_consulta = dados.data_consulta
    hora_consulta = dados.hora_consulta
    tipo_email = dados.tipo_email

    remetente_email = "fonoinga.fono@gmail.com"
    remetente_senha = "ytxn nckj nbrd aexy"

    mensagem = MIMEMultipart()
    mensagem["From"] = remetente_email
    mensagem["To"] = email_paciente
    mensagem["Subject"] = f"FonoIngá - Confirmação da Consulta"

    if tipo_email == "cancelamento":
        corpo_mensagem = email_cancelamento(nome_paciente, nome_fono, data_consulta, hora_consulta)
    
    elif tipo_email == "confirmacao":
        corpo_mensagem = email_confirmacao(nome_paciente, nome_fono, data_consulta, hora_consulta)

    elif tipo_email == "alteracao":
        corpo_mensagem = email_alteracao(nome_paciente, nome_fono, data_consulta, hora_consulta)
    
    mensagem.attach(MIMEText(corpo_mensagem, "plain"))

    servidor_smtp = "smtp.gmail.com"
    porta_smtp = 587
    with smtplib.SMTP(servidor_smtp, porta_smtp) as servidor:
        servidor.ehlo()
        servidor.starttls()
        servidor.ehlo()
        servidor.login(remetente_email, remetente_senha)
        servidor.sendmail(remetente_email, email_paciente, mensagem.as_string())

    return {"message" : "E-mail enviado com sucesso!"}

def email_cancelamento(nome_paciente, nome_fono, data_consulta, hora_consulta):
    return f'''Olá, {nome_paciente}!

Sua consulta no dia {data_consulta}, às {hora_consulta} com o(a) fonoaudiólogo(a) {nome_fono} foi cancelada.

Se surgir alguma dúvida ou se precisar reagendar, estamos aqui para ajudar. Não hesite em nos contatar.

Atenciosamente,
Ameinda Villas-Lobos
Secretária da Clínica FonoIngá
'''

def email_confirmacao(nome_paciente, nome_fono, data_consulta, hora_consulta):
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

def email_alteracao(nome_paciente, nome_fono, data_consulta, hora_consulta):
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