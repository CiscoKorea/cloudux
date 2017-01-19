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

from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim
#######
# from requests.packages.urllib3 import request

from cloudmgmt.settings import *
#######

from models import GlobalConfig, ConfigUtil, BiHost, BiVnic, BiVolume, BiVswitch, BiVirtualMachine, BiPnic, \
    BiPortgroup, BiCluster, BiDatacenter, UserAddInfo, BiInventory, BiFaults, BiCatalog, \
    UdCloud, DashboardAlloc, DashboardVswitch, UdGroup, UdVDC, UdVmDisk
from django.core.exceptions import MultipleObjectsReturned ,ObjectDoesNotExist
# import tools.cli as cli

import ssl
from ucsm_inventory import get_ucsm_info
from ucsd_library import catalog_list, catalog_list_all, vm_list, vm_action, ucsd_vdcs, ucsd_memory, ucsd_network, \
    ucsd_cloud, ucsd_cpu, ucsd_disk, catalog_order, group_list, group_detail_by_id, vdc_list, vm_details, \
    global_vms, group_vms, available_reports, ucsd_vm_disk, vmware_provision, ucsd_get_all_vms
# Create your views here.
from ux.ucsd_library import ucsd_verify_user, ucsd_add_user, ucsd_add_group
from patch_db import patch_data_vcenter_datacenter

class search_form():
    srch_key = ""
    srch_txt = ""

    def __init__(self, request):
        self.srch_key = request.GET.get("srch_key", "name")
        self.srch_txt = request.GET.get("srch_txt", "")


@login_required
def dashboard(request):
    # ucsd_vdcs()
    # ucsd_memory()
    # ucsd_network()
    # ucsd_cloud()

    # dcs = get_vcenter_info()  # get all data!!
    # get_ucsm_info()  # get ucsd inventory
    inventory_list = BiInventory.objects.all()
    fault_list = BiFaults.objects.all()

    dash1 = DashboardAlloc.objects.all()
    if dash1.count() >0 :
        chart1 = [int(dash1[0].total_vm), int(dash1[0].total_cpu), int(dash1[0].total_mem), int(dash1[0].total_stg)]
        chart1d = [100 - int(dash1[0].total_vm), 100 - int(dash1[0].total_cpu), 100 - int(dash1[0].total_mem),
                   100 - int(dash1[0].total_stg)]
    else :
        chart1 = [0,0,0,0]
        chart1d = [100, 100, 100, 100]

    chart3 = DashboardVswitch.objects.all()
    chart4 = []
    total_portgroup = 0
    switch_count = 0
    for dbswitch in chart3:
        t = dict()
        t['name'] = dbswitch.switch
        t['pgcount'] = int(dbswitch.portgroup)
        total_portgroup += int(dbswitch.portgroup)
        switch_count += 1
        chart4.append(t)
    if switch_count == 0:
        switch_count = 1

    return render(request, 'dashboard.html', {'inventorylist': inventory_list, 'faultlist': fault_list,
                                              'chart1': chart1, 'chart1d': chart1d,
                                              'chart4': json.dumps(chart4),
                                              'avgport': round(total_portgroup/switch_count, 1)})


def dashboard_fault_list(request):
    search = search_form(request)
    target_infra = request.GET.get("targetinfra", "")

    # search.srch_key = request.GET.get("srch_key", "name")
    # search.srch_txt = request.GET.get("srch_txt", "")

    # json_list = []
    print("search.srch_key: ", search.srch_key)
    if search.srch_key == "description":
        print("search.srch_txt: ", search.srch_txt)
        fault_list = BiFaults.objects.filter(target=target_infra, desc__icontains=search.srch_txt)
    else:
        fault_list = BiFaults.objects.filter(target=target_infra)

    json_list = []
    for fault in fault_list:
        json_list.append(fault.to_dict())
    # json_list = serializers.serialize("json", fault_list)
    return HttpResponse(json.dumps({'list': json_list}), 'application/json')
    # return JsonResponse(json.dumps(json_list), safe=False)


@login_required
def hosts(request):

    hlist = BiHost.objects.all()
    return render(request, "hostList.html", {'list': hlist})


# def hosts_old(request):
#     try:
#
#         config = GlobalConfig.objects.all()
#         context = ssl._create_unverified_context()
#         service_instance = connect.SmartConnect(host=config[0].vc_host,
#                                                 user=config[0].vc_user,
#                                                 pwd=config[0].vc_pass,
#                                                 port=int(config[0].vc_port), sslContext=context)
#
#         atexit.register(connect.Disconnect, service_instance)
#
#         content = service_instance.RetrieveContent()
#
#         container = content.rootFolder  # starting point to look into
#         viewType = [vim.HostSystem]  # object types to look for
#         recursive = True  # whether we should look into it recursively
#         containerView = content.viewManager.CreateContainerView(
#             container, viewType, recursive)
#
#         children = containerView.view
#         results = []
#         for child in children:
#             print("summary :", child.summary)
#             h = BiHost()
#             h.host = child.summary.host
#             h.os = child.summary.config.product.osType
#             h.version = child.summary.config.product.version
#             h.ip = child.summary.managementServerIp
#             h.status = child.summary.overallStatus
#             h.save()
#
#             for vnic in child.summary.host.configManager.networkSystem.networkConfig.vnic:
#                 n = BiVnic()
#                 n.device = vnic.device
#                 n.ipAddress = vnic.spec.ip.ipAddress
#                 n.save()
#                 n.host.add(h)
#
#             for vswitch in child.summary.host.configManager.networkSystem.networkConfig.vswitch:
#                 s = BiVswitch()
#                 s.name = vswitch.name
#                 s.save()
#                 s.host = h
#
#             for vol in child.summary.host.configManager.storageSystem.fileSystemVolumeInfo.mountInfo:
#                 v = BiVolume()
#                 v.name = vol.volume.name
#                 v.save()
#                 v.host.add(h)
#         # print_vm_info(child)
#         #     jsonObject = {}
#         #     jsonObject['Name'] = child.summary.config.name
#         #     jsonObject['IP'] = child.summary.guest.ipAddress
#         #     results.append(jsonObject)
#
#     except vmodl.MethodFault as error:
#         print("Caught vmodl fault : " + error.msg)
#
#     if request.is_ajax():
#         return HttpResponse(json.dumps(results), 'application/json')
#     return render(request, 'hostList.html', {'list': children})

@login_required
def vms(request):
    # print("vm69:", vm_details(vmid="69"))

    # user group
    tenant = None
    db_add_info = None
    if not request.user.is_staff:
        db_add_info = UserAddInfo.objects.get(user=request.user)
    if db_add_info:
        tenant = db_add_info.tenant


    # db_add_info = UserAddInfo.objects.get(user_id=request.user.id)
    # print(request.user.useraddinfo.tenant.group_name);
    # print(request.user.useraddinfo.tenant.id);

    search = search_form(request)
    # search.srch_key = request.GET.get("srch_key", "name")
    # search.srch_txt = request.GET.get("srch_txt", "")

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
                vlist = BiVirtualMachine.objects.filter(name__icontains=search.srch_txt, tenant=tenant)
            elif search.srch_key == "ip":
                vlist = BiVirtualMachine.objects.filter(ipAddress__icontains=search.srch_txt, tenant=tenant)
            elif search.srch_key == "mac":
                vlist = BiVirtualMachine.objects.filter(macAddress__icontains=search.srch_txt, tenant=tenant)
            else:
                vlist = BiVirtualMachine.objects.filter(tenant=tenant)
        else:
            vlist = BiVirtualMachine.objects.filter(tenant=tenant)

    paginator = Paginator(vlist, 10)
    page = request.GET.get('page')
    try:
        plist = paginator.page(page)
    except PageNotAnInteger:
        plist = paginator.page(1)
    except EmptyPage:
        plist = paginator.page(paginator.num_pages)

    clist = BiCatalog.objects.filter(catalog_type='Standard')
    return render(request, "vmList.html", {'list': plist, 'search': search, 'clist': clist})

# def vms_old(request):
#
#     try:
#
#         config = GlobalConfig.objects.all()
#         context = ssl._create_unverified_context()
#         service_instance = connect.SmartConnect(host=config[0].vc_host,
#                                                 user=config[0].vc_user,
#                                                 pwd=config[0].vc_pass,
#                                                 port=int(config[0].vc_port), sslContext=context)
#
#         atexit.register(connect.Disconnect, service_instance)
#
#         content = service_instance.RetrieveContent()
#
#         container = content.rootFolder  # starting point to look into
#         viewType = [vim.VirtualMachine]  # object types to look for
#         recursive = True  # whether we should look into it recursively
#         containerView = content.viewManager.CreateContainerView(
#             container, viewType, recursive)
#
#         children = containerView.view
#         results = []
#         for child in children:
#             #print_vm_info(child)
#             jsonObject = {}
#             jsonObject['Name'] = child.summary.config.name
#             jsonObject['IP'] = child.summary.guest.ipAddress
#             results.append(jsonObject)
#
#             vm = BiVirtualMachine()
#             vm.name = child.summary.config.name
#             vm.ipAddress = child.summary.guest.ipAddress
#             vm.macAddress = None
#             vm.cpuUsage = child.summary.quickStats.overallCpuUsage
#             vm.memUsage = child.summary.quickStats.guestMemoryUsage
#             vm.netUsage = None
#             vm.stgUsage = child.summary.storage.committed
#             vm.status = None
#             vm.save()
#
#     except vmodl.MethodFault as error:
#         print("Caught vmodl fault : " + error.msg)
#
#     if request.is_ajax():
#         return HttpResponse(json.dumps(results), 'application/json')
#     return render(request, 'vmList.html', {'list': children})  # {'list': children}


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
    clist = BiCatalog.objects.all()

    paginator = Paginator(clist, 4)
    page = request.GET.get('page')
    try:
        plist = paginator.page(page)
    except PageNotAnInteger:
        plist = paginator.page(1)
    except EmptyPage:
        plist = paginator.page(paginator.num_pages)

    glist = UdGroup.objects.all()
    vdclist = UdVDC.objects.all()

    return render(request, "catalogList.html", {'list': plist, 'ucsd_server': ConfigUtil.get_val("UCSD.HOST")
                  , 'group_list': glist, 'vdc_list': vdclist})


@login_required
def vnets(request):

    slist = BiVswitch.objects.all()
    return render(request, 'virtualNetworkList.html', {'list': slist})


@login_required
def volumes(request):

    slist = BiVolume.objects.all()
    return render(request, 'volumeList.html', {'list': slist})


# def volumes_old(request):
#     try:
#
#         config = GlobalConfig.objects.all()
#         context = ssl._create_unverified_context()
#         service_instance = connect.SmartConnect(host=config[0].vc_host,
#                                                 user=config[0].vc_user,
#                                                 pwd=config[0].vc_pass,
#                                                 port=int(config[0].vc_port), sslContext=context)
#
#         atexit.register(connect.Disconnect, service_instance)
#
#         content = service_instance.RetrieveContent()
#
#         container = content.rootFolder  # starting point to look into
#         viewType = [vim.HostSystem]  # object types to look for
#         recursive = True  # whether we should look into it recursively
#         containerView = content.viewManager.CreateContainerView(
#             container, viewType, recursive)
#
#         children = containerView.view
#         results = []
#         for child in children:
#             print("mountInfo :", child.configManager.storageSystem.fileSystemVolumeInfo.mountInfo)
#             # print_vm_info(child)
#         #     jsonObject = {}
#         #     jsonObject['Name'] = child.summary.config.name
#         #     jsonObject['IP'] = child.summary.guest.ipAddress
#         #     results.append(jsonObject)
#
#     except vmodl.MethodFault as error:
#         print("Caught vmodl fault : " + error.msg)
#
#     if request.is_ajax():
#         return HttpResponse(json.dumps(results), 'application/json')
#     return render(request, 'volumeList.html', {'list': children})


def disks(request):
    dlist = UdVmDisk.objects.all()

    paginator = Paginator(dlist, 10)
    page = request.GET.get('page')
    try:
        plist = paginator.page(page)
    except PageNotAnInteger:
        plist = paginator.page(1)
    except EmptyPage:
        plist = paginator.page(paginator.num_pages)

    return render(request, 'vmDiskList.html', {'list': plist})


def monitoring(request):
    # return render(request, 'Mmonitoring.html', {})
    return "Not Now"


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
    # search.srch_key = request.GET.get("srch_key", "username")
    # search.srch_txt = request.GET.get("srch_txt", "")

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


def print_vm_info(virtual_machine):
    """
    Print information for a particular virtual machine or recurse into a
    folder with depth protection
    """
    summary = virtual_machine.summary
    print("Name       : ", summary.config.name)
    print("Template   : ", summary.config.template)
    print("Path       : ", summary.config.vmPathName)
    print("Guest      : ", summary.config.guestFullName)
    print("Instance UUID : ", summary.config.instanceUuid)
    print("Bios UUID     : ", summary.config.uuid)

    ##################

    settings.t1 = 2

    ##################
     
    annotation = summary.config.annotation
    if annotation:
        print("Annotation : ", annotation)
    print("State      : ", summary.runtime.powerState)
    if summary.guest is not None:
        ip_address = summary.guest.ipAddress
        tools_version = summary.guest.toolsStatus
        if tools_version is not None:
            print("VMware-tools: ", tools_version)
        else:
            print("Vmware-tools: None")
        if ip_address:
            print("IP         : ", ip_address)
        else:
            print("IP         : None")
    if summary.runtime.question is not None:
        print("Question  : ", summary.runtime.question.text)
    print("")


def get_vcenter_info():
    # global content, hosts, hostPgDict#
    # config = GlobalConfig.objects.all()
    host = ConfigUtil.get_val("VC.HOST")
    user = ConfigUtil.get_val("VC.USER")
    pwd = ConfigUtil.get_val("VC.PASS")
    port = ConfigUtil.get_val("VC.PORT")
    print (host,user,pwd,port)
    # host, user, password = GetArgs()
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    context.verify_mode = ssl.CERT_NONE
    service_instance = connect.SmartConnect(host=host,
                                            user=user,
                                            pwd=pwd,
                                            port=int(port), sslContext=context)
    atexit.register(connect.Disconnect, service_instance)
    content = service_instance.RetrieveContent()

    return content


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


def get_network(network):
    # global pnicmap
    dpnic = {}
    dpg = {}
    for nic in network.pnic:
        # print("pnic key: %s name: %s " %(nic.key, nic.device))
        # pnicmap[nic.key] = nic.device
        dpnic[nic.key] = nic.device
    for pg in network.portgroup:
        # pnicmap[pg.key] = pg.spec.name + ":" + str(pg.spec.vlanId)
        dpg[pg.key] = pg.spec.name + ":" + str(pg.spec.vlanId)
    for nic in network.vnic:
        print("vnic name: %s connected portgroup: %s" % (nic.device, nic.portgroup))
    for sw in network.vswitch:
        #    	print("vSwitch name: %s, numPort: %d pnics: %s" %(sw.name, sw.numPorts, sw.pnic))
        # print("vSwicth name: %s uplink: %s portgroup: %s" % (sw.name, get_uplink(sw.pnic),
        #   get_portgroup(sw.portgroup)))
        print("vSwicth name: %s uplink: %s portgroup: %s" % (sw.name, dpnic, dpg))


def get_host(phosts):
    for host in phosts:
        print("Host Name=%s" % host.name)
        get_network(host.config.network)


def get_cluster(folder):
    for entity in folder.childEntity:
        print("Cluster name = %s" % entity.name)
        get_host(entity.host)


# def get_datacenters(content):
#     print("Getting all Datacenter...")
#     dc_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.Datacenter], True)
#     obj = [ dc for dc in dc_view.view]
#     for dc in obj:
#        print("Datacenter %s" %(dc.name))
#        get_cluster( dc.hostFolder)
#     dc_view.Destroy()
#     return obj


def get_datacenters(content):
    # delete_all()     # delete all data !!!
    print("Getting all Datacenter...")
    dc_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.Datacenter], True)
    obj = [dc for dc in dc_view.view]
    for dc in obj:
        print("Datacenter %s" % dc.name)
        vdc = BiDatacenter()
        vdc.name = dc.name
        vdc.save()
        for entity in dc.hostFolder.childEntity:
            print("Cluster name = %s" % entity.name)
            vcls = BiCluster()
            vcls.name = entity.name
            vcls.save()
            for host in entity.host:
                print("Host Name=%s" % host.name)
                h = BiHost()
                h.datacenter = vdc
                h.cluster = vcls
                h.host = host.name
                h.os = host.config.product.licenseProductName
                h.version = host.config.product.licenseProductVersion
                if len(host.config.network.vnic) > 0:
                    h.ip = host.config.network.vnic[0].spec.ip.ipAddress
                h.status = host.summary.overallStatus
                h.save()

                dpnic = {}
                dpg = {}
                dvlanid = {}
                network = host.config.network
                for nic in network.pnic:
                    # print("pnic key: %s name: %s " %(nic.key, nic.device))
                    # pnicmap[nic.key] = nic.device
                    dpnic[nic.key] = nic.device
                    # pnic = BiPnic()
                    # pnic.device = nic.device
                    # pnic.save()
                for pg in network.portgroup:
                    # pnicmap[pg.key] = pg.spec.name + ":" + str(pg.spec.vlanId)
                    dpg[pg.key] = pg    # .spec.name
                    dvlanid[pg.key] = pg.spec.vlanId
                    # vportgroup = BiPortgroup()
                    # vportgroup.name = pg.spec.name
                    # vportgroup.vlanId = pg.spec.vlanId
                    # vportgroup.save()
                for nic in network.vnic:
                    # print("vnic name: %s connected portgroup: %s" % (nic.device, nic.portgroup))
                    vnic = BiVnic()
                    vnic.device = nic.device
                    vnic.key = nic.key
                    vnic.ipAddress = nic.spec.ip.ipAddress
                    vnic.mac = nic.spec.mac
                    vnic.save()
                    vnic.host.add(h)
                for sw in network.vswitch:
                    #    	print("vSwitch name: %s, numPort: %d pnics: %s" %(sw.name, sw.numPorts, sw.pnic))
                    # print("vSwicth name: %s uplink: %s portgroup: %s" % (sw.name, get_uplink(sw.pnic),
                    #   get_portgroup(sw.portgroup)))
                    # print("vSwicth name: %s uplink: %s portgroup: %s" % (sw.name, dpnic, dpg))

                    if BiVswitch.objects.filter(key=sw.key).__len__() == 0:
                        bsw = BiVswitch()
                        bsw.name = sw.name
                        bsw.key = sw.key
                        bsw.save()
                        bsw.host.add(h)
                    else:
                        bsw = BiVswitch.objects.get(key=sw.key)
                        bsw.host.add(h)

                    for p in sw.pnic:
                        pnic = BiPnic()
                        pnic.device = dpnic[p]
                        pnic.vswitch = bsw
                        pnic.save()
                    for g in sw.portgroup:
                        # only one key
                        if BiPortgroup.objects.filter(key=g).__len__() == 0:
                            vportgroup = BiPortgroup()
                            vportgroup.key = g
                            vportgroup.name = dpg[g].spec.name
                            vportgroup.vlanId = dvlanid[g]
                            vportgroup.vswitch = bsw
                            vportgroup.save()
                for vm in host.vm:
                    vvm = BiVirtualMachine()
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
                    vvm.save()

                for nvm in host.vm:
                    for vmnet in nvm.network:
                        for vnetvm in vmnet.vm:
                            # print(vmnet.name, "<->", vnetvm.config.name)
                            try:
                                lnet = BiPortgroup.objects.get(name=vmnet.name)
                                lvm = BiVirtualMachine.objects.get(name=vnetvm.config.name)
                                if type(lvm) == list :
                                    for vm in lvm:
                                        vm.network.add(lnet)
                                else:
                                    lvm.network.add(lnet)
                            except (MultipleObjectsReturned, ObjectDoesNotExist) as e:
                                #print( "Exception : %s " %e)
                                pass  # print("DoesNotExist")

                for mnt in host.configManager.storageSystem.fileSystemVolumeInfo.mountInfo:
                    if len(mnt.volume.name) > 0:
                        if BiVolume.objects.filter(name=mnt.volume.name).__len__() == 0:
                            vvol = BiVolume()
                            vvol.name = mnt.volume.name
                            vvol.capacity = mnt.volume.capacity
                            vvol.type = mnt.volume.type
                            vvol.save()
                            vvol.host.add(h)
                        else:
                            vvol = BiVolume.objects.get(name=mnt.volume.name)
                            vvol.host.add(h)

    dc_view.Destroy()
    return obj


def delete_all():
    BiVirtualMachine.objects.all().delete()
    BiVolume.objects.all().delete()
    BiPortgroup.objects.all().delete()
    BiPnic.objects.all().delete()
    BiVswitch.objects.all().delete()
    BiVnic.objects.all().delete()
    BiHost.objects.all().delete()
    BiDatacenter.objects.all().delete()

    BiInventory.objects.all().delete()
    BiFaults.objects.all().delete()     # refresh !!

    BiCatalog.objects.all().delete()

    UdCloud.objects.all().delete()
    DashboardAlloc.objects.all().delete()
    DashboardVswitch.objects.all().delete()
    # UdGroup.objects.all().delete()
    UdVDC.objects.all().delete()
    UdVmDisk.objects.all().delete()


def get_catalog():
    clist = catalog_list_all()
    for catalog in clist:
        entity = BiCatalog()
        entity.status = catalog["Status"]
        entity.gruop = catalog["Group"]
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
    vlist = vm_list()
    # print(vlist)
    for vm in vlist:
        try:
            dbvm = BiVirtualMachine.objects.get(name=vm["VM_Name"])
            dbvm.group_name = vm["Group_Name"]
            dbvm.ucsd_vm_id = vm["VM_ID"]
            db_group = UdGroup.objects.get(group_name=vm["Group_Name"])
            dbvm.tenant = db_group
            dbvm.save()
        except:
            print("get_ucsd_vm exception : ", vm["VM_Name"])


def get_ucsd_group_list():
    glist = group_list()
    for group in glist:
        # check in db
        if UdGroup.objects.filter(group_name=unicode(group["groupName"])).count() == 0:

            detail = group_detail_by_id(group["groupId"])
            entity = UdGroup()
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
            entity.save()

def get_ucsd_vdc_list():
    vlist = vdc_list('','')
    for vdc in vlist:

        # get group id
        db_group = UdGroup.objects.get(group_name=vdc["Group"])

        if db_group :

            # check exist data
            if UdVDC.objects.filter(vdc=vdc["vDC"]).count() == 0:
                entity = UdVDC()
                entity.status = vdc["Status"] if vdc.has_key("Status") else None
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
                entity.vdc_description = vdc["vDC_Description"] if vdc.has_key("vDC_Description") else None
                entity.tenant = db_group
                entity.save()
            else:
                print '' + vdc["vDC"] + ' is in DB'


def get_ucsd_vmdisk_list():
    vmlist = BiVirtualMachine.objects.filter(ucsd_vm_id__isnull=False)
    for vm in vmlist:
        # print(vm.ucsd_vm_id)
        # print(ucsd_vm_disk(str(vm.ucsd_vm_id)))
        vmdisklist = ucsd_vm_disk(str(vm.ucsd_vm_id))
        for vmdisk in vmdisklist:
            disk = UdVmDisk()
            disk.vm_name = vmdisk["VM_Name"]
            disk.datacenter_name = vmdisk["Datacenter_Name"]
            disk.unit_number = vmdisk["Unit_Number"]
            disk.disk_id = vmdisk["ID"]
            disk.provision_size_gb = vmdisk["Provision_Size_GB"]
            disk.vm_id = vmdisk["VM_ID"]
            disk.datastore_name = vmdisk["Datastore_Name"]
            disk.disk_name = vmdisk["Disk_Name"]
            disk.save()


def reload_data_t(request):
    patch_data_vcenter_datacenter()
    return HttpResponse(json.dumps({'result': 'OK'}), 'application/json')


def reload_data(request):

    content = get_vcenter_info()  # get all data!!

    delete_all()
    dcs = get_datacenters(content)
    # sync_vcenter_with_ucsd()

    get_ucsm_info()  # get ucsd inventory
    get_catalog()
    get_ucsd_group_list()   # get ucsd group
    get_ucsd_vm_list()  # get ucsd vm id
    get_ucsd_vdc_list()
    get_ucsd_vmdisk_list()

    cloud_list = ucsd_cloud()  # cloud list from ucsd
    for cloud in cloud_list:
        entity = UdCloud()
        entity.tag = cloud["Tag"]
        entity.cloud_type = cloud["Cloud_Type"]
        entity.description = cloud["Description"]
        entity.contact = cloud["Contact"]
        entity.license_status = cloud["License_Status"]
        entity.location = unicode(cloud["Location"])
        entity.user_id = cloud["User_ID"]
        entity.reachable = unicode(cloud["Reachable"])
        entity.message = unicode(cloud["Message"])
        entity.vmware_server = cloud["VMware_Server"]
        entity.cloud = cloud["Cloud"]
        entity.save()

    total_vm = 0
    active_vm = 0
    vdc_list = ucsd_vdcs()
    for vdc in vdc_list:
        total_vm += vdc["Total_VMs"]
        active_vm += vdc["Active_VMs"]

    dash1 = DashboardAlloc()
    dash1.total_vm = int(round(active_vm / total_vm * 100)) if total_vm != 0 else 0
    dash1.save()

    total_cpu = 0.0
    prov_cpu = 0.0
    cpu_alloc = ucsd_cpu()
    for cpu in cpu_alloc:
        if cpu["name"].__contains__("Capacity"):
            total_cpu = float(cpu["value"])
        if cpu["name"].__contains__("Provisioned"):
            prov_cpu = float(cpu["value"])
    dash1.total_cpu = int(round(prov_cpu / total_cpu * 100)) if total_cpu != 0.0 else 0.0
    dash1.save()

    total_mem = 0.0
    prov_mem = 0.0
    mem_alloc = ucsd_memory()
    for mem in mem_alloc:
        if mem["name"].__contains__("Capacity"):
            total_mem = float(mem["value"])
        if mem["name"].__contains__("Provisioned"):
            prov_mem = float(mem["value"])
    dash1.total_mem = int(round(prov_mem / total_mem * 100)) if total_mem != 0.0 else 0.0
    dash1.save()

    total_stg = 0.0
    prov_stg = 0.0
    stg_alloc = ucsd_disk()
    for stg in stg_alloc:
        if stg["name"].__contains__("Capacity"):
            total_stg = float(stg["value"])
        if stg["name"].__contains__("Provisioned"):
            prov_stg = float(stg["value"])
    dash1.total_stg = int(round(prov_stg / total_stg * 100)) if total_stg != 0.0 else 0.0
    dash1.save()
    
    #javaos74 need to fix
    net_list = {} #ucsd_network()
    for net in net_list:
        vswtc = DashboardVswitch()
        vswtc.portgroup = int(net["Num_Port_Groups"])
        vswtc.switch = net["Switch_Name"]
        vswtc.save()

    return HttpResponse(json.dumps({'result': 'OK'}), 'application/json')


def sync_vcenter_with_ucsd(request = None):
    try:
        ucsd_vms = ucsd_get_all_vms()
        for vm in ucsd_vms:
            bivm = BiVirtualMachine.objects.get( vcenter_vm_id=vm['vCenter_VM_Id'])
            if bivm:
                bivm.group_name = vm['Group_Name']
                bivm.ucsd_vm_id = str(vm['VM_ID'])
                bivm.save()
    except KeyError as ke:
        pass
    if request:
        return HttpResponse(json.dumps({'result': 'OK'}), 'application/json')


def ucsd_vm_create(request):
    p_catalog = request.POST.get("catalog")     # catalog_
    p_resource = request.POST.get("resource")   # CPU|MEM|DISK format
    resource = p_resource.split("|")
    p_cpu = resource[0]
    p_mem = resource[1]
    p_disk = ""  # FIXME resource[2]
    p_vdc = request.POST.get("vdc", "Sales Bronze VDC") # FIXME

    vmware_provision(p_catalog, p_vdc, comment="", vmname="", vcpus=p_cpu, vram=p_mem, datastores=p_disk, vnics="")

    return HttpResponse(json.dumps({'result': 'OK'}), 'application/json')


def ucsd_vm_action(request):
    # print(request.GET.get("action"))
    # print(request.GET.get("vmid"))
    action = request.GET.get("action")
    vmid = request.GET.get("vmid").split(",")
    for vm in vmid:
        vm_action(vmid=vm, action=action)
    return HttpResponse(json.dumps({'result': 'OK'}), 'application/json')


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
    while cnt <= int(p_vmcount):
        db_catalog = BiCatalog.objects.filter(catalog_id=p_catalog_id).first()
        # FIXME check catalog type
        l = list()
        l.append(p_vmname)
        l.append("-")
        l.append(str(cnt).zfill(3))
        vmname = ''.join(l)
        order_status = catalog_order(db_catalog.catalog_name, vdc=p_vdc, group=p_group, comment=p_comment, vmname=vmname,
                       vcpus=p_vcpus, vram=p_vram, datastores=p_datastores, vnics=p_vnics)
        cnt += 1
        print (order_status)
    return HttpResponse(json.dumps({'result': 'OK'}), 'application/json')


def users_groups(request):
    if request.method == "POST" :
        group_name = request.POST.get("group_name")
        email = request.POST.get("email")

        # add ucsd group
        ucsd_add_group(group_name=group_name, first_name=group_name, last_name='on cloud ux', contact_email=email)

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

    return render(request, 'test.html', {})


def my_login(request):
    form = AuthenticationForm(request.POST)
    p_username = request.POST.get('username')
    password = request.POST.get('password')
    # tenant_id = request.POST.get("tenant")

    # ucsd verify
    ucsd_user = ucsd_verify_user(user_id=p_username, password=password)
    print ucsd_user
    if ucsd_user == None:
        return HttpResponseRedirect('/login')

    # check user
    if User.objects.filter(username=p_username).count()==0:
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
        addinfo.tenant_id = t_id
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



