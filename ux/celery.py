# coding=utf-8

from __future__ import absolute_import

from celery import Celery


# djano 에서 쓰일 setting 지정 아래의 경우 proj/settings.py 를 사용한다는 뜻
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ux.settings')
from django.conf import settings  # noqa

app = Celery('ux')

# Optional configuration, see the application user guide.
# django.conf:settings 로 django setting 을 celery 의 config 로 불러온다.
app.config_from_object('django.conf:settings')
# INSTALLED_APPS 안에 있는 tasks.py 들을 알아서 import 해 준다.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


app.conf.update(
    CELERY_TASK_RESULT_EXPIRES=3600,
)

if __name__ == '__main__':
    app.start()
