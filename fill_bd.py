import datetime
import os
import django
import random
from rocketData.wsgi import *
from faker import Faker

from main.models import Product, Employee, NetworkNode


"""Модуль для запуска заполнения базы данных тестовыми данными"""

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rocketData.settings')
django.setup()
fake = Faker('ru_RU')
product = ['Телевизор', 'Стиральная машина', 'Пылесос', 'Микроволновая печь', 'Стирально-сушильная машина', 'Монитор',
           'Холодильник с морозильником', 'Минисистема', 'Утюг', 'Ноутбук','Щетка','Машина','Пила','Кран',]
model = ['32LQ630B6LA', 'F2J3WS1W', 'F2M5NS6W', 'VC5316NNTS', '55UR78001LJ', 'F2J6HSFW', 'MS2042DARB', '50UR78009LL',
         'OLED65B3RLA', 'F2J3HS2W', 'MS2044V', '55UR78009LL', 'F2J6NM7W', 'F4J6TM7W', '24MP400-B']

for i in range(14):
    Employee.objects.create(
       name=fake.first_name(),
       surname=fake.last_name(),
       position=fake.job()
    )

for i in range(14):
    Product.objects.create(
        name=product.pop(),
        model=model.pop(),
        date_release=fake.date_this_decade()
    )

for i in range(5):
    for n in range(5):
        type = i
        if type == 0:
            supplier = None
        else:
            supplier = NetworkNode.objects.get(pk=random.randint(1, i*5))
        net_obj = NetworkNode.objects.create(
            type=type,
            name=fake.company(),
            email=fake.email(),
            country=fake.country(),
            city=fake.city(),
            street=fake.street_address(),
            house_number=random.randint(0, 100),
            supplier=supplier,
            debt=float(random.randint(0, 1000))/10,
            created_at=datetime.datetime.now(),
            network_endpoint=True,
        )
        net_obj.products.add(Product.objects.get(pk=random.randint(1, 15)))
        net_obj.employees.add(Employee.objects.get(pk=random.randint(1, 15)))
        net_obj.save()
