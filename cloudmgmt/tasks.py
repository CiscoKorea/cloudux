# coding=utf-8

from __future__ import absolute_import
from cloudmgmt.celery import app
from ux.views import reload_data

@app.task
def update_all():
    print("update_all Start")
    reload_data(request=None)
    print("update_all End")
