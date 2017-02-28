# -*- coding: utf-8 -*-
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core import serializers
from django.forms.models import model_to_dict
from django.utils.encoding import force_text
from django.core.serializers.json import DjangoJSONEncoder
import json
import atexit
import datetime

from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim
from tools import pchelper
#######
# from requests.packages.urllib3 import request

from cloudmgmt.settings import *
#######

from models import GlobalConfig, ConfigUtil, BiVirtualMachine, BiCatalog, \
    UserAddInfo, DashboardAlloc, UdGroup, UdVDC, UdServiceRequest
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
# import tools.cli as cli

import ssl
#from ucsm_inventory import get_ucsm_info
from ucsd_library import catalog_list, catalog_list_all, vm_list, vm_action, ucsd_vdcs, ucsd_memory, ucsd_network, \
    ucsd_cloud, ucsd_cpu, ucsd_disk, catalog_order, group_list, group_detail_by_id, vdc_list, vm_details, \
    global_vms, group_vms, available_reports, ucsd_vm_disk, vmware_provision, ucsd_get_all_vms, \
    ucsd_provision_request, ucsd_get_restaccesskey
# Create your views here.
from ux.ucsd_library import ucsd_verify_user, ucsd_add_user, ucsd_add_group, ucsd_create_vdc, \
    ucsd_vmware_system_policy, ucsd_vmware_computing_policy, ucsd_vmware_storage_policy, \
    ucsd_vmware_network_policy, ucsd_get_groupbyname, ucsd_get_service_requests
#from patch_db import patch_data_vcenter_datacenter
from local_config import catalog_type_list

vcenter_content = None
service_instance = None

vm_properties = ["name", "config.uuid", "config.hardware.numCPU",
                 "config.hardware.memoryMB", "guest.guestState",
                 "config.guestFullName", "config.guestId",
                 "guest.disk",
                 "config.version", "summary.quickStats.uptimeSeconds",
                 "summary.quickStats.guestMemoryUsage", "summary.quickStats.overallCpuUsage",
                 "summary.quickStats.sharedMemory", "summary.quickStats.staticCpuEntitlement",
                 "summary.quickStats.staticMemoryEntitlement", "summary.quickStats.uptimeSeconds",
                 "summary.storage.committed", "summary.storage.timestamp", "summary.storage.uncommitted", "summary.storage.unshared"]

class search_form():
    srch_key = ""
    srch_txt = ""

    def __init__(self, request):
        self.srch_key = request.GET.get("srch_key", "name")
        self.srch_txt = request.GET.get("srch_txt", "")


@login_required
def dashboard(request):

    dash1 = DashboardAlloc.objects.all()
    if dash1.count() >0 :
        chart1 = [int(dash1[0].total_vm), int(dash1[0].total_cpu), int(dash1[0].total_mem), int(dash1[0].total_stg)]
        chart1d = [100 - int(dash1[0].total_vm), 100 - int(dash1[0].total_cpu), 100 - int(dash1[0].total_mem),
                   100 - int(dash1[0].total_stg)]
    else :
        chart1 = [0,0,0,0]
        chart1d = [100, 100, 100, 100]


    return render(request, 'dashboard.html', {'chart1': chart1, 'chart1d': chart1d })
                                              


def dashboard_fault_list(request):
    search = search_form(request)
    target_infra = request.GET.get("targetinfra", "")

    if target_infra == "":
        fault_list = BiFaults.objects.all()
    else:
        if search.srch_key == "description":
            # print("search.srch_txt: ", search.srch_txt)
            fault_list = BiFaults.objects.filter(target=target_infra, desc__icontains=search.srch_txt)
        else:
            fault_list = BiFaults.objects.filter(target=target_infra)

    json_list = []
    for fault in fault_list:
        json_list.append(fault.to_dict())
    # json_list = serializers.serialize("json", fault_list)
    return HttpResponse(json.dumps({'list': json_list}), 'application/json')
    # return JsonResponse(json.dumps(json_list), safe=False)


#@login_required
#def hosts(request):
#
#    hlist = BiHost.objects.all()
#    return render(request, "hostList.html", {'list': hlist})



@login_required
def myrequests(request):

    tenant = None
    db_add_info = None
    db_add_info = UserAddInfo.objects.get(user=request.user)
    if db_add_info:
        tenant = db_add_info.group_name
    
    vlist = []
    if tenant:
        vlist = UdServiceRequest.objects.order_by('-srId').filter( group_name = tenant)
    else:
        vlist = UdServiceRequest.objects.order_by('-srId').all()
    paginator = Paginator(vlist, 10)
    page = request.GET.get('page')
    try:
        plist = paginator.page(page)
    except PageNotAnInteger:
        plist = paginator.page(1)
    except EmptyPage:
        plist = paginator.page(paginator.num_pages)

    return render(request, "myRequestsList.html", {'list': plist })


@login_required
def vms(request):
    # user group
    tenant = None
    db_add_info = None
    if not request.user.is_staff:
        try:
            db_add_info = UserAddInfo.objects.get(user=request.user)
            tenant = db_add_info.group_name
        except ObjectDoesNotExist as odne:
            pass

    search = search_form(request)

    vlist = []
    # admin get all list
    if request.user.is_staff:
        if len(search.srch_txt) > 0:
            if search.srch_key == "name":
                vlist = BiVirtualMachine.objects.filter(name__icontains=search.srch_txt)
            elif search.srch_key == "ip":
                vlist = BiVirtualMachine.objects.filter(ipAddress__icontains=search.srch_txt)
            elif search.srch_key == "mac":
                vlist = BiVirtualMachine.objects.filter(macAddress__icontains=search.srch_txt)
            else:
                vlist = BiVirtualMachine.objects.all()
        else:
            vlist = BiVirtualMachine.objects.all()
    else:
        if len(search.srch_txt) > 0:
            if search.srch_key == "name":
                vlist = BiVirtualMachine.objects.filter(name__icontains=search.srch_txt, group_name=tenant)
            elif search.srch_key == "ip":
                vlist = BiVirtualMachine.objects.filter(ipAddress__icontains=search.srch_txt, group_name=tenant)
            elif search.srch_key == "mac":
                vlist = BiVirtualMachine.objects.filter(macAddress__icontains=search.srch_txt, group_name=tenant)
            else:
                vlist = BiVirtualMachine.objects.filter(group_name=tenant)
        else:
            vlist = BiVirtualMachine.objects.filter(group_name=tenant)

    paginator = Paginator(vlist, 10)
    page = request.GET.get('page')
    try:
        plist = paginator.page(page)
    except PageNotAnInteger:
        plist = paginator.page(1)
    except EmptyPage:
        plist = paginator.page(paginator.num_pages)

    return render(request, "vmList.html", {'list': plist, 'search': search})


def vms_ajax(request):
    children = None
    # try:
    #     context = ssl._create_unverified_context()
    #
    #     service_instance = connect.SmartConnect(host="198.18.133.30",
    #                                             user="root",
    #                                             pwd="C1sco12345!",
    #                                             port=int("443"), sslContext=context)
    #
    #     atexit.register(connect.Disconnect, service_instance)
    #
    #     content = service_instance.RetrieveContent()
    #
    #     container = content.rootFolder  # starting point to look into
    #     view_type = [vim.VirtualMachine]  # object types to look for
    #     recursive = True  # whether we should look into it recursively
    #     container_view = content.viewManager.CreateContainerView(
    #         container, view_type, recursive)
    #
    #     children = container_view.view
    #
    # except vmodl.MethodFault as error:
    #     print("Caught vmodl fault : " + error.msg)

    return HttpResponse(json.dumps({'list': children}), 'application/json')

@login_required
def catalogs(request):
    clist = None
    if request.user.useraddinfo.group_name:
        clist = BiCatalog.objects.filter(catalog_type__in=catalog_type_list)\
            .filter(status='OK') \
            .filter(group_name__in=["All Groups", request.user.useraddinfo.group_name])
        glist = [request.user.useraddinfo.group_name] 
        vdclist = UdVDC.objects.filter(group_name = request.user.useraddinfo.group_name)
    else:
        clist = BiCatalog.objects.filter(catalog_type__in=catalog_type_list) \
            .filter(status='OK') \
            .filter(group_name__in=["All Groups"])
        glist = UdGroup.objects.all()
        vdclist = UdVDC.objects.all()

    print(glist)
    paginator = Paginator(clist, 4)
    page = request.GET.get('page')
    try:
        plist = paginator.page(page)
    except PageNotAnInteger:
        plist = paginator.page(1)
    except EmptyPage:
        plist = paginator.page(paginator.num_pages)

    return render(request, "catalogList.html", {'list': plist, 'ucsd_server': ConfigUtil.get_val("UCSD.HOST")
                  , 'group_list': glist, 'vdc_list': vdclist})


def users(request):

    # ajax Add User
    if request.is_ajax():
        rtn_result = 'NO'
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        contact = request.POST.get("contact")
        first_name = request.POST.get("first_name")
        is_staff = request.POST.get("is_staff")
        tenant_id = request.POST.get("tenant")

        # 0. ucsd user add
        # 0.1 get group name
        db_group = UdGroup.objects.get(id=tenant_id)
        group_name = db_group.group_name
        # add user
        ucsd_added = ucsd_add_user(user_id=username, password=password, first_name=first_name, last_name='on cloud ux',
                      email=email, role='Regular', group_name=group_name)

        # 1. create user
        if ucsd_added :
            newuser = User.objects.create_user(username=username, email=email, password=password, first_name=first_name,
                                               is_staff=is_staff, )

            addinfo = UserAddInfo()
            addinfo.contact = contact
            addinfo.user = newuser
            addinfo.tenant_id = db_group.id
            addinfo.save()
            rtn_result = 'OK'

        return HttpResponse(json.dumps({'result': rtn_result}), 'application/json')

    # user list page
    search = search_form(request)

    if len(search.srch_txt) > 0:
        if search.srch_key == "username":
            ulist = User.objects.filter(username__icontains=search.srch_txt)
        elif search.srch_key == "firstname":
            ulist = User.objects.filter(first_name__icontains=search.srch_txt)
        elif search.srch_key == "email":
            ulist = User.objects.filter(email__icontains=search.srch_txt)
        else:
            ulist = User.objects.all()
    else:
        ulist = User.objects.all()
    paginator = Paginator(ulist, 10)
    page = request.GET.get('page')
    try:
        plist = paginator.page(page)
    except PageNotAnInteger:
        plist = paginator.page(1)
    except EmptyPage:
        plist = paginator.page(paginator.num_pages)

    tenantlist = UdGroup.objects.all()

    return render(request, 'userList.html', {'list': plist, 'search': search, 'tenantlist': tenantlist})


def users_idcheck(request):
    if request.is_ajax():
        username = request.GET.get("username")

        # FIXME ucsd user name check

        exist_cnt = User.objects.filter(username=username).count()

        if exist_cnt == 0:
            return HttpResponse(json.dumps({'result': 'OK'}), 'application/json')

    return HttpResponse(json.dumps({'result': 'NO'}), 'application/json')


def users_modify(request):
    p_first_name = request.POST.get("first_name")
    p_username = request.POST.get("username")
    p_email = request.POST.get("email")
    p_contact = request.POST.get("contact")
    p_password = request.POST.get("password")

    user = User.objects.get(username=p_username)
    user.first_name = p_first_name
    user.email = p_email
    if len(p_password) > 0:
        user.set_password(p_password)
    user.useraddinfo.contact = p_contact
    user.useraddinfo.save()
    user.save()

    return HttpResponse(json.dumps({'result': 'NO'}), 'application/json')


def get_vcenter_info():
    host = ConfigUtil.get_val("VC.HOST")
    user = ConfigUtil.get_val("VC.USER")
    pwd = ConfigUtil.get_val("VC.PASS")
    port = ConfigUtil.get_val("VC.PORT")

    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    context.verify_mode = ssl.CERT_NONE
    service_instance = connect.SmartConnect(host=host,
                                            user=user,
                                            pwd=pwd,
                                            port=int(port), sslContext=context)
    atexit.register(connect.Disconnect, service_instance)
    content = service_instance.RetrieveContent()

    return (content, service_instance)


def get_uplink(uplinks):
    vals = []
    # for nic in uplinks:
    #     # vals.append(pnicmap.get(nic))
    #     vals.append('')
    return "[" + ",".join(vals) + "]"


def get_portgroup(portgroups):
    vals = []
    # for pg in portgroups:
    #     # vals.append(pnicmap.get(pg))
    #     vals.append('')
    return "[" + ",".join(vals) + "]"

def merge_virtualmachine(vm, h):
    vportgroup = None
    if BiVirtualMachine.objects.filter(vcenter_vm_id=vm._moId).count() == 0:
        vvm = BiVirtualMachine()
    else:
        vvm = BiVirtualMachine.objects.get(vcenter_vm_id = vm._moId)

    vvm.vcenter_vm_id = vm._moId
    vvm.name = vm.config.name
    vvm.ipAddress = vm.guest.ipAddress
    # vvm.macAddress = ''
    vvm.cpuUsage = vm.summary.quickStats.overallCpuUsage
    vvm.memUsage = vm.summary.quickStats.hostMemoryUsage
    # vvm.netUsage
    # vvm.stgUsage
    vvm.status = vm.summary.overallStatus
    vvm.host = h
    vvm.old = False
    vvm.save()



def get_catalog():
    clist = catalog_list_all()
    # FIXME old data
    for catalog in clist:
        if BiCatalog.objects.filter(catalog_id=catalog["Catalog_ID"]).count() == 0:
            entity = BiCatalog()
        else:
            entity = BiCatalog.objects.get(catalog_id=catalog["Catalog_ID"])

        entity.status = catalog["Status"]
        entity.group_name = catalog["Group"]
        entity.template_name = catalog["Template_Name"]
        entity.image = catalog["Image"]
        entity.catalog_name = catalog["Catalog_Name"]
        entity.catalog_type = catalog["Catalog_Type"]
        entity.catalog_id = catalog["Catalog_ID"]
        entity.folder = catalog["Folder"]
        entity.os = catalog["OS"]
        entity.catalog_description = catalog["Catalog_Description"]
        entity.cloud = catalog["Cloud"]
        entity.icon = catalog["Icon"]
        entity.save()


def get_ucsd_vm_list():
    #mark all vm as old=true
    vms = BiVirtualMachine.objects.all()
    for vm in vms:
        vm.old = True
        vm.save()

    vlist = vm_list()
    for vm in vlist:
        dbvm = None
        try:
            dbvm = BiVirtualMachine.objects.get(name=vm["vCenter_VM_Id"])
        except ObjectDoesNotExist as e:
            dbvm = BiVirtualMachine()
            dbvm.imageId = vm["Image_Id"]
            dbvm.created = datetime.datetime.now()
            #print("New VM ", e,  vm["VM_Name"])
        except MultipleObjectsReturned as e:
            continue
        if dbvm:
            dbvm.old = False
            dbvm.name = vm["VM_Name"]
            dbvm.ipAddress = vm["IP_Address"]
            dbvm.group_name = vm["Group_Name"]
            dbvm.ucsd_vm_id = vm["VM_ID"]
            dbvm.guestOSType = vm["Guest_OS_Type"]
            dbvm.provisionTime = vm["Provisioned_Time"]
            dbvm.status = vm["Power_State"]
            dbvm.srId = str(vm["Request_ID"])
            dbvm.vcenter_vm_id = vm["vCenter_VM_Id"]
            dbvm.save()
    #delete vm marked as old = true
    vms = BiVirtualMachine.objects.filter(old = True)
    for vm in vms:
        print('delete vm %s' %vm.name)
        vm.delete()


def get_ucsd_group_list():
    glist = group_list()
    for group in glist:
        # groupId? groupName?
        if UdGroup.objects.filter(group_id=group["groupId"]).count() == 0:
            entity = UdGroup()
        else:
            entity = UdGroup.objects.get(group_id=group["groupId"])

        detail = group_detail_by_id(group["groupId"])
        entity.group_id = group["groupId"]
        entity.group_name = detail["groupName"]
        entity.description = unicode(detail["description"])
        entity.parent_group_id = detail["parentGroupId"]
        entity.parent_group_name = detail["parentGroupName"]
        entity.last_name = unicode(detail["lastName"])
        entity.first_name = unicode(detail["firstName"])
        entity.phone_number = detail["phoneNumber"]
        entity.address = unicode(detail["address"])
        entity.group_type = detail["groupType"]
        entity.enable_budget = detail["enableBudget"]
        entity.old = False
        entity.save()


def get_ucsd_vdc_list():
    vlist = vdc_list('','')
    #mark old for deletion 
    vdcs = UdVDC.objects.all()
    for vdc in vdcs:
        vdc.old = True
        vdc.save()
    for vdc in vlist:
        # get group id
        db_group = UdGroup.objects.get(group_name=vdc["Group"])
        if db_group :
            # check exist data
            if UdVDC.objects.filter(vdc=vdc["vDC"]).count() == 0:
                entity = UdVDC()
            else:
                entity = UdVDC.objects.get(vdc=vdc["vDC"])
            entity.old = False
            entity.status = unicode(vdc["Status"]) if vdc.has_key("Status") else None
            entity.tag = vdc["Tag"] if vdc.has_key("Tag") else None
            entity.vdc_id = vdc["vDC_ID"] if vdc.has_key("vDC_ID") else None
            entity.custom_categories = vdc["Custom_Categories"] if vdc.has_key("Custom_Categories") else None
            entity.total_vms = vdc["Total_VMs"] if vdc.has_key("Total_VMs") else None
            entity.active_vms = vdc["Active_VMs"] if vdc.has_key("Active_VMs") else None
            entity.dcloud = vdc["dCloud"] if vdc.has_key("dCloud") else None
            entity.vdc = vdc["vDC"] if vdc.has_key("vDC") else None
            entity.approvers = vdc["Approvers"] if vdc.has_key("Approvers") else None
            entity.lock_state = vdc["Lock_State"] if vdc.has_key("Lock_State") else None
            entity.type = vdc["Type"] if vdc.has_key("Type") else None
            entity.cloud = vdc["Cloud"] if vdc.has_key("Type") else None
            entity.vdc_description = unicode(vdc["vDC_Description"]) if vdc.has_key("vDC_Description") else None
            entity.group_name = db_group.group_name
            entity.save()
    #remove unmark old as False
    vdcs = UdVDC.objects.filter(old = True)
    for vdc in vdcs:
        print("delete removed vdc %s" %vdc.vdc)
        vdc.delete()


'''
def get_ucsd_vmdisk_list():
    vmlist = BiVirtualMachine.objects.filter(ucsd_vm_id__isnull=False)
    for vm in vmlist:
        # print(vm.ucsd_vm_id)
        # print(ucsd_vm_disk(str(vm.ucsd_vm_id)))
        vmdisklist = ucsd_vm_disk(str(vm.ucsd_vm_id))
        for vmdisk in vmdisklist:
            if UdVmDisk.objects.filter(disk_id=vmdisk["ID"]).count() == 0:
                disk = UdVmDisk()
            else:
                disk = UdVmDisk.objects.get(disk_id=vmdisk["ID"])
            disk.vm_name = vmdisk["VM_Name"]
            disk.datacenter_name = vmdisk["Datacenter_Name"]
            disk.unit_number = vmdisk["Unit_Number"]
            disk.disk_id = vmdisk["ID"]
            disk.provision_size_gb = vmdisk["Provision_Size_GB"]
            disk.vm_id = vmdisk["VM_ID"]
            disk.datastore_name = vmdisk["Datastore_Name"]
            disk.disk_name = vmdisk["Disk_Name"]
            disk.save()
'''

def get_ucsd_stat1():
    total_vm = 0
    active_vm = 0
    vdc_list = ucsd_vdcs()
    for vdc in vdc_list:
        total_vm += vdc["Total_VMs"]
        active_vm += vdc["Active_VMs"]

    DashboardAlloc.objects.all().delete()
    dash1 = DashboardAlloc()    # FIXME 기존 1행으로 처리 해도 됨
    dash1.total_vm = int(round(active_vm / float(total_vm) * 100)) if total_vm != 0 else 0
    dash1.save()

    total_cpu = 0.0
    prov_cpu = 0.0
    cpu_alloc = ucsd_cpu()
    for cpu in cpu_alloc:
        if cpu["name"].find("Capacity") >= 0 or cpu["name"].find(u"용량") >= 0 :
            total_cpu = float(cpu["value"])
        if cpu["name"].find("Provisioned") >=0 or cpu["name"].find(u"프로비저닝") >=0 :
            prov_cpu = float(cpu["value"])
    dash1.total_cpu = int(round(prov_cpu / total_cpu * 100)) if total_cpu != 0.0 else 0.0
    dash1.save()

    total_mem = 0.0
    prov_mem = 0.0
    mem_alloc = ucsd_memory()
    for mem in mem_alloc:
        if mem["name"].find("Capacity") >= 0 or mem["name"].find(u"용량") >= 0:
            total_mem = float(mem["value"])
        if mem["name"].find("Provisioned") >= 0 or mem["name"].find(u"프로비저닝") >= 0:
            prov_mem = float(mem["value"])
    dash1.total_mem = int(round(prov_mem / total_mem * 100)) if total_mem != 0.0 else 0.0
    dash1.save()

    total_stg = 0.0
    prov_stg = 0.0
    stg_alloc = ucsd_disk()
    for stg in stg_alloc:
        if stg["name"].find("Capacity") >= 0 or stg["name"].find(u"용량") >= 0:
            total_stg = float(stg["value"])
        if stg["name"].find("Provisioned") >= 0 or stg["name"].find(u"프로비저닝") >= 0:
            prov_stg = float(stg["value"])
    dash1.total_stg = int(round(prov_stg / total_stg * 100)) if total_stg != 0.0 else 0.0
    dash1.save()

'''
def get_ucsd_stat2():
    DashboardVswitch.objects.all().delete()
    net_list = ucsd_network()
    for net in net_list:
        vswtc = DashboardVswitch()
        vswtc.portgroup = int(net["Num_Port_Groups"])
        vswtc.switch = net["Switch_Name"]
        vswtc.save()

def get_ucsd_policy_system():
    all_policy = ucsd_vmware_system_policy()
    for pol in all_policy:
        if UdPolicySystem.objects.filter(policy_id=pol["Policy_ID"]).count() ==0:
            policy = UdPolicySystem()
            policy.policy_id = pol["Policy_ID"]
        else:
            policy = UdPolicySystem.objects.get(policy_id=pol["Policy_ID"])
        policy.policy_name = pol["Policy_Name"]
        policy.policy_description = pol["Policy_Description"]
        policy.vdcs = pol["vDCs"]
        policy.save()


def get_ucsd_policy_computing():
    all_policy = ucsd_vmware_computing_policy()
    for pol in all_policy:
        if UdPolicyComputing.objects.filter(policy_id=pol["Policy_ID"]).count() ==0:
            policy = UdPolicyComputing()
            policy.policy_id = pol["Policy_ID"]
        else:
            policy = UdPolicyComputing.objects.get(policy_id=pol["Policy_ID"])
        policy.policy_name = pol["Policy_Name"]
        policy.policy_description = pol["Policy_Description"]
        policy.vdcs = pol["vDCs"]
        policy.save()


def get_ucsd_policy_storage():
    all_policy = ucsd_vmware_storage_policy()
    for pol in all_policy:
        if UdPolicyStorage.objects.filter(policy_id=pol["Policy_ID"]).count() ==0:
            policy = UdPolicyStorage()
            policy.policy_id = pol["Policy_ID"]
        else:
            policy = UdPolicyStorage.objects.get(policy_id=pol["Policy_ID"])
        policy.policy_name = pol["Policy_Name"]
        policy.policy_description = pol["Policy_Description"]
        policy.vdcs = pol["vDCs"]
        policy.cloud_name = pol["Cloud_Name"]
        policy.status = pol["Status"]
        policy.save()


def get_ucsd_policy_network():
    all_policy = ucsd_vmware_network_policy()
    for pol in all_policy:
        if UdPolicyNetwork.objects.filter(policy_id=pol["Policy_ID"]).count() ==0:
            policy = UdPolicyNetwork()
            policy.policy_id = pol["Policy_ID"]
        else:
            policy = UdPolicyNetwork.objects.get(policy_id=pol["Policy_ID"])
        policy.policy_name = pol["Policy_Name"]
        policy.policy_description = pol["Policy_Description"]
        policy.vdcs = pol["vDCs"]
        policy.cloud_name = pol["Cloud_Name"]
        policy.status = pol["Status"]
        policy.save()

'''
def get_ucsd_sr_list():
    udsr_list = ucsd_get_service_requests(None,'')
    for udsr in udsr_list:
        sr = None
        try:
            sr = UdServiceRequest.objects.get(srId= str(udsr["Service_Request_Id"]))
            sr.status = udsr["Request_Status"]
            sr.group_name = udsr["Group"]
            sr.save()
        except ObjectDoesNotExist as e:
            sr = UdServiceRequest()
            sr.srId = str(udsr["Service_Request_Id"])
            sr.requestTime = udsr["Request_Time"]
            sr.requestType = udsr["Request_Type"]
            sr.requester = udsr["Initiating_User"]
            sr.catalogWorkflowName = udsr["Catalog_Workflow_Name"]
            sr.status = udsr["Request_Status"]
            sr.rollbackType = udsr["Rollback_Type"]
            sr.group_name = udsr["Group"]
            sr.save()

def reload_data(request):
    ''' 
    called by celery 
    '''
    get_ucsd_group_list()
    get_ucsd_vdc_list()
    get_catalog()
    get_ucsd_vm_list()
    get_ucsd_sr_list()
    update_vm_stats()
    #update_dashboard()
    return HttpResponse(json.dumps({'result': 'OK'}), 'application/json')


def update_dashboard():
    pass
    
def update_vm_stats():
    global vcenter_content,service_instance
    if not vcenter_content:
        (vcenter_content,service_instance) = get_vcenter_info()
    try:
        root_folder = vcenter_content.rootFolder
        view = pchelper.get_container_view(service_instance,
                                       obj_type=[vim.VirtualMachine])
        vm_data = pchelper.collect_properties(service_instance, view_ref=view,
                                          obj_type=vim.VirtualMachine,
                                          path_set=vm_properties,
                                          include_mors=True)
    except :
        (vcenter_content,service_instance) = get_vcenter_info()
        root_folder = vcenter_content.rootFolder
        view = pchelper.get_container_view(service_instance,
                                       obj_type=[vim.VirtualMachine])
        vm_data = pchelper.collect_properties(service_instance, view_ref=view,
                                          obj_type=vim.VirtualMachine,
                                          path_set=vm_properties,
                                          include_mors=True)
    dashboard = {}
    #after get all vm 
    for vm in vm_data:
        capa = 0
        free = 0
        for disk in vm["guest.disk"]:
            capa += disk.capacity
            free += disk.freeSpace
        try:
            bivm = BiVirtualMachine.objects.get( vcenter_vm_id = vm["obj"]._moId)
            bivm.cpuUsage = str( vm["summary.quickStats.overallCpuUsage"])
            bivm.memUsage = str( vm["summary.quickStats.guestMemoryUsage"])
            bivm.stgUsage = str( ((capa-free)/1024)/1024)

            bivm.cpuAlloc = str( vm["summary.quickStats.staticCpuEntitlement"])
            bivm.memAlloc = str( vm["summary.quickStats.staticMemoryEntitlement"])
            bivm.stgAlloc = str( (capa/1024)/1024)
            bivm.save()
            '''
            bivm.group_name
            if dashbaord.has_key( bivm.group_name):
                dashboard[ bivm.group_name]['vm.active'] = int(dashboard[ bivm.group_name]['vm.active']) \
                                                        + 1 if bivm.status is 'ON' else 0
                dashboard[ bivm.group_name]['vm.inactive'] = int(dashboard[ bivm.group_name]['vm.inactive']) \
                                                        + 0 if bivm.status is 'ON' else 1
                dashboard[ bivm.group_name]['stg.alloc'] = int(dashboard[ bivm.group_name]['stg.alloc'])                                       
            '''
        except Exception as e:
            print (e)
            pass


@login_required
def update_service_requests(request):
    get_ucsd_sr_list()
    get_ucsd_vm_list()
    return HttpResponse(json.dumps({'result': 'OK'}), 'application/json')

def ucsd_vm_create(request):
    p_catalog = request.POST.get("catalog")     # catalog_
    p_resource = request.POST.get("resource")   # CPU|MEM|DISK format
    resource = p_resource.split("|")
    p_cpu = resource[0]
    p_mem = resource[1]
    p_disk = ""  # FIXME resource[2]
    p_comment = request.POST.get("comment")

    group_name = request.POST.get("group_name")
    # group_name = "Sales"
    vdc_cnt = UdVDC.objects.filter(vdc=group_name).count()
    if vdc_cnt == 0:
        p_vdc = UdVDC.objects.all()[:1].get().vdc
    if vdc_cnt > 0:
        p_vdc = UdVDC.objects.filter(vdc=group_name)[:1].get().vdc

    username = ''
    if not request.user.is_staff:
        username = str(request.user.username)

    rtn = vmware_provision(p_catalog, p_vdc, comment=p_comment, vmname="", vcpus=p_cpu, vram=p_mem,
                     datastores=p_disk, vnics="", username=username)

    if rtn["serviceError"]:
        return HttpResponse(json.dumps({'result': 'NO', 'serviceError': rtn["serviceError"]}), 'application/json')

    return HttpResponse(json.dumps({'result': 'OK', 'serviceResult': rtn["serviceResult"]}), 'application/json')


def ucsd_vm_action(request):
    action = request.GET.get("action")
    vmid = request.GET.get("vmid").split(",")
    comment = "n/a" if request.GET.get("comment") == None else request.GET.get("comment")
    for vm in vmid:
        vm_action(vmid=vm, action=action, comments=comment, restapikey=request.user.useraddinfo.restapikey)
    return HttpResponse(json.dumps({'result': 'OK'}), 'application/json')

@login_required
def vmrc_console(request):
    global vcenter_content, service_instance
    VMRC_FORMAT = "vmrc://clone:{0}@{1}/?moid={2}"
    vmid = request.GET.get("vmid")
    rsp = {}
    if vmid:
        if not vcenter_content:
            (vcenter_content,service_instance) = get_vcenter_info()
        try:
            session = vcenter_content.sessionManager.AcquireCloneTicket()
        except:
            (vcenter_content,service_instance) = get_vcenter_info()
            session = vcenter_content.sessionManager.AcquireCloneTicket()
        rsp['url'] = VMRC_FORMAT.format( session, ConfigUtil.get_val("VC.HOST"), vmid)
        rsp['status'] = 'OK'
        #print(rsp)
        return HttpResponse(json.dumps(rsp), 'application/json')
    else:
        rsp['status'] = 'Error'
        return HttpResponse(json.dumps(rsp), 'application/json')

def catalog_vm_provision(request):
    p_catalog_id = request.GET.get("catalog_id")
    p_vmname = request.GET.get("vmname")
    p_vmcount = request.GET.get("vmcount")
    p_vcpus = request.GET.get("vcpus")
    p_vram = request.GET.get("vram")
    p_datastores = request.GET.get("datastores")
    p_vnics = request.GET.get("vnics")
    p_comment = unicode(request.GET.get("comment"))
    p_group = request.GET.get("group")
    p_vdc = request.GET.get("vdc")

    cnt = 1
    sr_num = ''
    while cnt <= int(p_vmcount):
        db_catalog = BiCatalog.objects.filter(catalog_id=p_catalog_id).first()
        # FIXME check catalog type
        l = list()
        l.append(p_vmname)
        l.append("-")
        l.append(str(cnt).zfill(2))
        l.append("-")
        vmname = ''.join(l)

        username = ''
        if not request.user.is_staff:
            username = str(request.user.username)


        # order_status = catalog_order(db_catalog.catalog_name, vdc=p_vdc, group=p_group, comment=p_comment, vmname=vmname,
        #                vcpus=p_vcpus, vram=p_vram, datastores=p_datastores, vnics=p_vnics, username=username)
        order_status = ucsd_provision_request(db_catalog.catalog_name, vdc=p_vdc, comment=p_comment, vmname=vmname,
                       vcpus=p_vcpus, vram=p_vram, datastores=p_datastores, vnics=p_vnics, username=username)


        cnt += 1
        print (order_status)
        sr_num = sr_num + str(order_status['serviceResult']) + ","
    return HttpResponse(json.dumps({'result': 'OK', 'sr_num': sr_num}), 'application/json')


def users_groups(request):
    if request.method == "POST":
        group_name = request.POST.get("group_name")
        email = request.POST.get("email")

        # add ucsd group
        ucsd_add_group(group_name=group_name, first_name=group_name, last_name='on cloud ux', contact_email=email)

        # FIXME only OK
        # refresh ucsd group
        get_ucsd_group_list()

    else:
        pass

    return HttpResponse(json.dumps({'result': 'OK'}), 'application/json')


def testpage(request):
    # print(ucsd_add_user(user_id='test01', password='test00', first_name='kim', last_name='hanguk',
    #                     email='test01@neocyon.com', role='Regular', group_name='Sales Group'))
    #
    # print(ucsd_add_group(group_name='test_group01', first_name='test', last_name='group', contact_email='email@test.com'))
    #
    # print(ucsd_verify_user(user_id='test3', password='test'))

    # from cloudmgmt.tasks import update_dcs
    # result = update_dcs.delay()
    # print("result:", result)
    print("userid :", request.user.username)

    vdc_list('','')

    return render(request, 'test.html', {})


def my_login(request):
    form = AuthenticationForm(request.POST)
    p_username = request.POST.get('username')
    password = request.POST.get('password')
    # tenant_id = request.POST.get("tenant")

    # ucsd verify
    ucsd_user = ucsd_verify_user(user_id=p_username, password=password)
    if ucsd_user == None:
        return HttpResponseRedirect('/login')

    # check user
    if User.objects.filter(username=p_username).count()==0:
        # new User
        t_id = None
        if UdGroup.objects.filter(group_name=ucsd_user["groupName"]).count() ==0:
            t_id = None
        else:
            db_group = UdGroup.objects.get(group_name=ucsd_user["groupName"])
            t_id = db_group.id

        newuser = User.objects.create_user(username=p_username, email=ucsd_user['email'], password=password, first_name=p_username)
        addinfo = UserAddInfo()
        addinfo.contact = ''
        addinfo.user = newuser
        addinfo.group_name = ucsd_user["groupName"]
        addinfo.restapikey = ucsd_get_restaccesskey(p_username)
        addinfo.save()

        user = authenticate(username=p_username, password=password)
    else:
        # user in DB
        # update tenant_id
        user = authenticate(username=p_username, password=password)
        try:
            addinfo = UserAddInfo.objects.get(user=user)
        except ObjectDoesNotExist as odne:
            addinfo = UserAddInfo()
            addinfo.contact = ''
            addinfo.user = user
            addinfo.restapikey = ucsd_get_restaccesskey(p_username)
            addinfo.save()

        t_id = None
        if UdGroup.objects.filter(group_name=ucsd_user["groupName"]).count() == 0:
            t_id = None
        else:
            db_group = UdGroup.objects.get(group_name=ucsd_user["groupName"])
            t_id = db_group.id

        addinfo.group_name = ucsd_user["groupName"]
        addinfo.restapikey = ucsd_get_restaccesskey(p_username)
        addinfo.save()

    user = authenticate(username=p_username, password=password)
    if user is not None:
        login(request, user)
        # Redirect to a success page.
        return HttpResponseRedirect('/')

    else:
        # Return an 'invalid login' error message.
        # messages.error(request, 'Invalid login credentials')
        # return HttpResponseRedirect('/login')
        # form.add_error(error='invalid login')
        variables = {'form': form}
        return render(request, 'registration/login.html', variables)
