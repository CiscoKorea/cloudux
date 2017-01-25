from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^dashboard/faults$', views.dashboard_fault_list, name='dashboardfaults'),
    url(r'^hosts$', views.hosts, name='hosts'),
    url(r'^vms$', views.vms, name='vms'),
    url(r'catalogs$', views.catalogs, name='catalogs'),
    url(r'^vnets$', views.vnets, name='vnets'),
    url(r'^volumes$', views.volumes, name='volumes'),
    url(r'^disks$', views.disks, name='disks'),
    url(r'^monitoring$', views.monitoring, name='monitoring'),
    url(r'^users$', views.users, name='users'),
    url(r'^users/idcheck$', views.users_idcheck, name='idcheck'),
    url(r'^users/modify$', views.users_modify, name='usermodify'),
    url(r'^users/groups$', views.users_groups, name='groups'),
    url(r'^reloaddata$', views.reload_data_none, name="reloaddata"),
    url(r'^vm_action$', views.ucsd_vm_action, name="vmaction"),
    url(r'^vm_create$', views.ucsd_vm_create, name="vmcreate"),
    url(r'^catalog_order$', views.catalog_vm_provision, name="catalogorder"),
    url(r'^test$', views.testpage, name="testpage"),
    url(r'^login2$', views.my_login, name="my_login"),
    url(r'^myrequests$', views.myrequests, name="myrequests"),
]