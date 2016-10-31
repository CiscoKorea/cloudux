from django.shortcuts import render
from django.http import HttpResponse
import json
import atexit

from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim

from models import GlobalConfig, BiHost, BiVnic, BiVolume, BiVswitch, BiVirtualMachine

import tools.cli as cli

import ssl

# Create your views here.


def dashboard(request):
    return render(request, 'dashboard.html', {})


def hosts(request):
    try:

        config = GlobalConfig.objects.all()
        context = ssl._create_unverified_context()
        service_instance = connect.SmartConnect(host=config[0].vc_host,
                                                user=config[0].vc_user,
                                                pwd=config[0].vc_pass,
                                                port=int(config[0].vc_port), sslContext=context)

        atexit.register(connect.Disconnect, service_instance)

        content = service_instance.RetrieveContent()

        container = content.rootFolder  # starting point to look into
        viewType = [vim.HostSystem]  # object types to look for
        recursive = True  # whether we should look into it recursively
        containerView = content.viewManager.CreateContainerView(
            container, viewType, recursive)

        children = containerView.view
        results = []
        for child in children:
            print("summary :", child.summary)
            h = BiHost()
            h.host = child.summary.host
            h.os = child.summary.config.product.osType
            h.version = child.summary.config.product.version
            h.ip = child.summary.managementServerIp
            h.status = child.summary.overallStatus
            h.save()

            for vnic in child.summary.host.configManager.networkSystem.networkConfig.vnic:
                n = BiVnic()
                n.device = vnic.device
                n.ipAddress = vnic.spec.ip.ipAddress
                n.save()
                n.host.add(h)

            for vswitch in child.summary.host.configManager.networkSystem.networkConfig.vswitch:
                s = BiVswitch()
                s.name = vswitch.name
                s.save()
                s.host.add(h)

            for vol in child.summary.host.configManager.storageSystem.fileSystemVolumeInfo.mountInfo:
                v = BiVolume()
                v.name = vol.volume.name
                v.save()
                v.host.add(h)
        # print_vm_info(child)
        #     jsonObject = {}
        #     jsonObject['Name'] = child.summary.config.name
        #     jsonObject['IP'] = child.summary.guest.ipAddress
        #     results.append(jsonObject)

    except vmodl.MethodFault as error:
        print("Caught vmodl fault : " + error.msg)

    if request.is_ajax():
        return HttpResponse(json.dumps(results), 'application/json')
    return render(request, 'hostList.html', {'list': children})


def vms(request):

    try:

        config = GlobalConfig.objects.all()
        context = ssl._create_unverified_context()
        service_instance = connect.SmartConnect(host=config[0].vc_host,
                                                user=config[0].vc_user,
                                                pwd=config[0].vc_pass,
                                                port=int(config[0].vc_port), sslContext=context)

        atexit.register(connect.Disconnect, service_instance)

        content = service_instance.RetrieveContent()

        container = content.rootFolder  # starting point to look into
        viewType = [vim.VirtualMachine]  # object types to look for
        recursive = True  # whether we should look into it recursively
        containerView = content.viewManager.CreateContainerView(
            container, viewType, recursive)

        children = containerView.view
        results = []
        for child in children:
            #print_vm_info(child)
            jsonObject = {}
            jsonObject['Name'] = child.summary.config.name
            jsonObject['IP'] = child.summary.guest.ipAddress
            results.append(jsonObject)

            vm = BiVirtualMachine()
            vm.name = child.summary.config.name
            vm.ipAddress = child.summary.guest.ipAddress
            vm.macAddress = None
            vm.cpuUsage = child.summary.quickStats.overallCpuUsage
            vm.memUsage = child.summary.quickStats.guestMemoryUsage
            vm.netUsage = None
            vm.stgUsage = child.summary.storage.committed
            vm.status = None
            vm.save()

    except vmodl.MethodFault as error:
        print("Caught vmodl fault : " + error.msg)

    if request.is_ajax():
        return HttpResponse(json.dumps(results), 'application/json')
    return render(request, 'vmList.html', {'list': children})  # {'list': children}


def vmsAjax(request):

    try:
        context = ssl._create_unverified_context()

        service_instance = connect.SmartConnect(host="198.18.133.30",
                                                user="root",
                                                pwd="C1sco12345!",
                                                port=int("443"), sslContext = context)

        atexit.register(connect.Disconnect, service_instance)

        content = service_instance.RetrieveContent()

        container = content.rootFolder  # starting point to look into
        viewType = [vim.VirtualMachine]  # object types to look for
        recursive = True  # whether we should look into it recursively
        containerView = content.viewManager.CreateContainerView(
            container, viewType, recursive)

        children = containerView.view

    except vmodl.MethodFault as error:
        print("Caught vmodl fault : " + error.msg)

    return HttpResponse( json.dumps({'list': children}), 'application/json')


def vnets(request):
    return render(request, 'virtualNetworkList.html', {})


def volumes(request):
    try:

        config = GlobalConfig.objects.all()
        context = ssl._create_unverified_context()
        service_instance = connect.SmartConnect(host=config[0].vc_host,
                                                user=config[0].vc_user,
                                                pwd=config[0].vc_pass,
                                                port=int(config[0].vc_port), sslContext=context)

        atexit.register(connect.Disconnect, service_instance)

        content = service_instance.RetrieveContent()

        container = content.rootFolder  # starting point to look into
        viewType = [vim.HostSystem]  # object types to look for
        recursive = True  # whether we should look into it recursively
        containerView = content.viewManager.CreateContainerView(
            container, viewType, recursive)

        children = containerView.view
        results = []
        for child in children:
            print("mountInfo :", child.configManager.storageSystem.fileSystemVolumeInfo.mountInfo)
            # print_vm_info(child)
        #     jsonObject = {}
        #     jsonObject['Name'] = child.summary.config.name
        #     jsonObject['IP'] = child.summary.guest.ipAddress
        #     results.append(jsonObject)

    except vmodl.MethodFault as error:
        print("Caught vmodl fault : " + error.msg)

    if request.is_ajax():
        return HttpResponse(json.dumps(results), 'application/json')
    return render(request, 'volumeList.html', {'list': children})


def disks(request):
    return render(request, 'vmDiskList.html', {})


def monitoring(request):
    return render(request, 'Mmonitoring.html', {})


def users(request):
    return render(request, 'userList.html', {})


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
