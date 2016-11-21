from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^hosts$', views.hosts, name='hosts'),
    url(r'^vms$', views.vms, name='vms'),
    url(r'^vnets$', views.vnets, name='vnets'),
    url(r'^volumes$', views.volumes, name='volumes'),
    url(r'^disks$', views.disks, name='disks'),
    url(r'^monitoring$', views.monitoring, name='monitoring'),
    url(r'^users$', views.users, name='users'),
    url(r'^users/idcheck$', views.users_idcheck, name='idcheck'),
    url(r'^reloaddata$', views.reload_data, name="reloaddata"),
]