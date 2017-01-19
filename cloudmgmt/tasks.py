# coding=utf-8

from __future__ import absolute_import
from cloudmgmt.celery import app
from ux.views import reload_data

@app.task
def update_all():
    print("update_all Start")
    reload_data(request=None)
    print("update_all End")


@app.task
def update_dcs():
    print("update_dcs")
    pass


@app.task
def update_clusters():
    print("update_clusters")
    pass


@app.task
def update_hosts():
    print("update_hosts")
    pass


@app.task
def update_vms():
    print("update_vms")
    pass


@app.task
def update_vswitchs():
    print("update_vswitchs")
    pass


@app.task
def update_portgroups():
    print("update_portgroups")
    pass
