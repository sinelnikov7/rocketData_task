import os
from datetime import timedelta
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rocketData.settings')
app = Celery('rocketData')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.timezone = 'Europe/Minsk'

app.conf.beat_schedule = { # Запуск увеличения задолженности перед поставщиком каждые 3 часа
    'debt_up-every-3-hours': {
        'task': 'main.tasks.debt_up',
        'schedule': timedelta(hours=3),
    },
}

app.conf.beat_schedule = { # Запуск уменьшения задолженности перед поставщиком каждый день в  6:30
    'debt_down-at-6:30-clock': {
        'task': 'main.tasks.debt_down',
        'schedule': crontab(hour='6', minute='30'),
    },
}
