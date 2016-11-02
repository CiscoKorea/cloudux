from django.shortcuts import render
from django.http import HttpResponse
import json
import atexit

from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim

from models import GlobalConfig, BiHost, BiVnic, BiVolume, BiVswitch, BiVirtualMachine, BiPnic, BiPortgroup, BiCluster, BiDatacenter

import tools.cli as cli

import ssl

# Create your views here.


def dashboard(request):
    dcs = getVcenterInfo()  # get all data!!
    return render(request, 'dashboard.html', {})


def hosts(request):

    hlist = BiHost.objects.all()
    return render(request, 'hostList.html', {'list': hlist})


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


def vms(request):
    vlist = BiVirtualMachine.objects.all()
    return render(request, 'vmList.html', {'list': vlist})

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
    slist = BiVswitch.objects.all()
    return render(request, 'virtualNetworkList.html', {'list':slist})


def volumes(request):
    dcs = getVcenterInfo()
    slist = BiVolume.objects.all()
    return render(request, 'volumeList.html', {'list':slist})


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



def getVcenterInfo():
    # global content, hosts, hostPgDict#
    config = GlobalConfig.objects.all()
    # host, user, password = GetArgs()
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    context.verify_mode = ssl.CERT_NONE
    service_instance = connect.SmartConnect(host=config[0].vc_host,
                                            user=config[0].vc_user,
                                            pwd=config[0].vc_pass,
                                            port=int(config[0].vc_port), sslContext=context)
    atexit.register(connect.Disconnect, service_instance)
    content = service_instance.RetrieveContent()
    dcs = GetDatacenters(content)

    return dcs


def GetUplink(uplinks):
    vals = []
    for nic in uplinks:
        # vals.append(pnicmap.get(nic))
        vals.append('')
    return "[" + ",".join(vals) + "]"


def GetPortgroup(portgroups):
    vals = []
    for pg in portgroups:
        # vals.append(pnicmap.get(pg))
        vals.append('')
    return "[" + ",".join(vals) + "]"


def GetNetwork(network):
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
        print("vnic name: %s connected portgroup: %s" %(nic.device, nic.portgroup))
    for sw in network.vswitch:
        #    	print("vSwitch name: %s, numPort: %d pnics: %s" %(sw.name, sw.numPorts, sw.pnic))
        #print("vSwicth name: %s uplink: %s portgroup: %s" % (sw.name, GetUplink(sw.pnic), GetPortgroup(sw.portgroup)))
        print("vSwicth name: %s uplink: %s portgroup: %s" % (sw.name, dpnic, dpg))


def GetHost(hosts):
    for host in hosts:
        print("Host Name=%s" % (host.name))
        GetNetwork(host.config.network)


def GetCluster(folder):
    for entity in folder.childEntity:
        print("Cluster name = %s" % (entity.name))
        GetHost(entity.host)


# def GetDatacenters(content):
#     print("Getting all Datacenter...")
#     dc_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.Datacenter], True)
#     obj = [ dc for dc in dc_view.view]
#     for dc in obj:
#        print("Datacenter %s" %(dc.name))
#        GetCluster( dc.hostFolder)
#     dc_view.Destroy()
#     return obj


def GetDatacenters(content):
    deleteAll()
    print("Getting all Datacenter...")
    dc_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.Datacenter], True)
    obj = [ dc for dc in dc_view.view]
    for dc in obj:
        print("Datacenter %s" % (dc.name))
        vdc = BiDatacenter()
        vdc.name = dc.name
        vdc.save()
        for entity in dc.hostFolder.childEntity:
            print("Cluster name = %s" % (entity.name))
            vcls = BiCluster()
            vcls.name = entity.name
            vcls.save()
            for host in entity.host:
                print("Host Name=%s" % (host.name))
                h = BiHost()
                h.datacenter = vdc
                h.cluster = vcls
                h.host = host.name
                h.os = host.summary.config.product.osType
                h.version = host.summary.config.product.version
                h.ip = host.summary.managementServerIp
                h.status = host.summary.overallStatus
                h.save()

                dpnic = {}
                dpg = {}
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
                    dpg[pg.key] = pg.spec.name + ":" + str(pg.spec.vlanId)
                    # vportgroup = BiPortgroup()
                    # vportgroup.name = pg.spec.name
                    # vportgroup.vlanId = pg.spec.vlanId
                    # vportgroup.save()
                for nic in network.vnic:
                    print("vnic name: %s connected portgroup: %s" % (nic.device, nic.portgroup))
                for sw in network.vswitch:
                    #    	print("vSwitch name: %s, numPort: %d pnics: %s" %(sw.name, sw.numPorts, sw.pnic))
                    # print("vSwicth name: %s uplink: %s portgroup: %s" % (sw.name, GetUplink(sw.pnic), GetPortgroup(sw.portgroup)))
                    # print("vSwicth name: %s uplink: %s portgroup: %s" % (sw.name, dpnic, dpg))
                    bsw = BiVswitch()
                    bsw.name = sw.name
                    bsw.host = h
                    bsw.save()

                    for p in sw.pnic:
                        pnic = BiPnic()
                        pnic.device = dpnic[p]
                        pnic.vswitch = bsw
                        pnic.save()
                    for g in sw.portgroup:
                        vportgroup = BiPortgroup()
                        vportgroup.name = dpg[g]
                        vportgroup.vlanId = dpg[g]
                        vportgroup.vswitch = bsw
                        vportgroup.save()
                for vm in host.vm:
                    vvm = BiVirtualMachine()
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
                for mnt in host.configManager.storageSystem.fileSystemVolumeInfo.mountInfo:
                    vvol = BiVolume()
                    vvol.name = mnt.volume.name
                    vvol.capacity = mnt.volume.capacity
                    vvol.type = mnt.volume.type
                    vvol.host = h
                    vvol.save()


    dc_view.Destroy()
    return obj


def deleteAll():
    BiVirtualMachine.objects.all().delete()
    BiVolume.objects.all().delete()
    BiPortgroup.objects.all().delete()
    BiPnic.objects.all().delete()
    BiVswitch.objects.all().delete()
    BiVnic.objects.all().delete()
    BiHost.objects.all().delete()
