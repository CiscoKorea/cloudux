# coding=utf-8

from __future__ import absolute_import
from cloudmgmt.celery import app


@app.task 
def update_dcs():
	pass

@app.task
def update_clusters():
	pass

@app.task
def update_hosts():
	pass

@app.task
def update_vms():
	pass

@app.task
def update_vswitchs():
	pass

@app.task
def update_portgroups():
	pass


