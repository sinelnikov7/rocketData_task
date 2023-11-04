import os
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import dotenv

from rocketData.celery import app
from .models import NetworkNode

dotenv.load_dotenv()
EMAIL_SENDER = os.environ.get('EMAIL_SENDER')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')


@app.task(bind=True)
def send_email(*args, **kwargs):
    """Отправка кода подтверждения регистрации на email"""
    email_sender = EMAIL_SENDER
    email_password = EMAIL_PASSWORD
    smtp_server = smtplib.SMTP('smtp.yandex.ru', 587)
    smtp_server.starttls()
    msg = MIMEMultipart()
    msg.attach(MIMEText(
        f"Здравствуйте! Для продолжения введите проверочный код регистрации на сайте sportlife"))
    msg["From"] = email_sender
    msg["Subject"] = "Код подтверждения регистрации на сайте sportlife"
    smtp_server.set_debuglevel(1)
    smtp_server.login(email_sender, email_password)
    smtp_server.sendmail(email_sender, 'tsoftin@gmail.com', msg.as_string())
    smtp_server.quit()


@app.task(bind=True)
def debt_up(*args, **kwargs):
    summa = random.randint(5, 500)
    for part_network in NetworkNode.objects.exclude(type=0):
        part_network.debt += summa
        part_network.save()

@app.task(bind=True)
def debt_down(*args, **kwargs):
    summa = random.randint(100, 10000)
    for part_network in NetworkNode.objects.exclude(type=0):
        now_debt = part_network.debt
        if now_debt >= float(summa):
            part_network.debt -= summa
            part_network.save()
        else:
            part_network.debt -= now_debt
            part_network.save()

@app.task(bind=True)
def clear_debt_celery(*args, **kwargs):
    obj_lst = args[1]
    for i in obj_lst:
       obj = NetworkNode.objects.get(id=int(i))
       obj.debt = float(0)
       obj.save()
