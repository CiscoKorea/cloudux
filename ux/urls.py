from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^vms$', views.vms, name='vms'),
    url(r'^catalogs$', views.catalogs, name='catalogs'),
    url(r'^reloaddata$', views.reload_data, name="reloaddata"),
    url(r'^vm_action$', views.ucsd_vm_action, name="vmaction"),
    url(r'^vm_create$', views.ucsd_vm_create, name="vmcreate"),
    url(r'^catalog_order$', views.catalog_vm_provision, name="catalogorder"),
    url(r'^test$', views.testpage, name="testpage"),
    url(r'^login2$', views.my_login, name="my_login"),
    url(r'^myrequests$', views.myrequests, name="myrequests"),
    url(r'^approval$', views.approvals, name="approval"),
    url(r'^approve$', views.approve, name="approve"),
    url(r'^vmrc_console$', views.vmrc_console, name="vmrc_console"),
    url(r'^update_order$', views.update_service_requests, name="update_order"),
]