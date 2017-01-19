# -*- coding: utf-8 -*-
from ux.models import BiDatacenter, BiCluster, BiHost, ConfigUtil
from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim
import ssl
import atexit


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


def get_datacenters(content):
    dc_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.Datacenter], True)
    obj = [dc for dc in dc_view.view]
    for dc in obj:
        for entity in dc.hostFolder.childEntity:
            for host in entity.host:
                network = host.config.network
                for nic in network.pnic:
                    pass
                for pg in network.portgroup:
                    pass
                for nic in network.vnic:
                    pass
                for sw in network.vswitch:
                    pass
                for vm in host.vm:
                    pass

                for nvm in host.vm:
                    for vmnet in nvm.network:
                        for vnetvm in vmnet.vm:
                            pass

                for mnt in host.configManager.storageSystem.fileSystemVolumeInfo.mountInfo:
                    pass
    dc_view.Destroy()
    return obj


def merge_db_for_dc(content):
    """
    Merge DB (Datacenter Info) from Vcenter
    :param content:
    :return:
    """
    dc_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.Datacenter], True)
    obj = [dc for dc in dc_view.view]

    # 1. delete removed data
    db_list = BiDatacenter.objects.all()
    for db in db_list:
        removed = True
        for dc in obj:
            if db.name == dc.name:
                removed = False
                break
        if removed:
            BiDatacenter.objects.filter(id=db.id).delete()
    # 2. insert new data
    for dc in obj:
        if BiDatacenter.objects.filter(name=dc.name).count() ==0:
            vdc = BiDatacenter()
            vdc.name = dc.name
            vdc.save()
        else:
            # 3. update modified data
            pass
    dc_view.Destroy()


def merge_db_for_cluster(content):
    """
    Merge DB (Cluster Info) from Vcenter
    :param content:
    :return:
    """
    dc_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.Datacenter], True)
    obj = [dc for dc in dc_view.view]

    # 1. delete removed data
    db_list = BiCluster.objects.all()
    for db in db_list:
        removed = True
        for dc in obj:
            for cl in dc.hostFolder.childEntity:
                if db.name == cl.name:
                    removed = False
                    break
        if removed:
            BiCluster.objects.filter(id=db.id).delete()
    # 2. insert new data
    for dc in obj:
        for cl in dc.hostFolder.childEntity:
            if BiCluster.objects.filter(name=cl.name).count() == 0:
                vcls = BiCluster()
                vcls.name = cl.name
                vcls.save()
            else:
                # 3. update modified data
                pass

    dc_view.Destroy()


def merge_db_for_host(content):
    dc_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.Datacenter], True)
    obj = [dc for dc in dc_view.view]

    # 1. delete removed data
    db_list = BiHost.objects.all()
    for db in db_list:
        removed = False
        for dc in obj:
            for cl in dc.hostFolder.childEntity:
                for host in cl.host:
                    if db.name == host.name : # and db.datacenter==host.datacenter
                        # and db.cluster == host.cluster
                        removed = False
                        break
                    pass
        if removed:
            BiHost.objects.filter(id=db.id).delete()
    # 2. insert new data
    for dc in obj:
        for cl in dc.hostFolder.childEntity:
            for host in cl.host:
                if BiHost.objects.filter(host=host.name).count() == 0:
                    h = BiHost()
                    h.datacenter = BiDatacenter.objects.get(name=dc.name)
                    h.cluster = BiCluster.objects.get(name=cl.name)
                    h.host = host.name
                    h.os = host.config.product.licenseProductName
                    h.version = host.config.product.licenseProductVersion
                    if len(host.config.network.vnic) > 0:
                        h.ip = host.config.network.vnic[0].spec.ip.ipAddress
                    h.status = host.summary.overallStatus
                    h.save()
                else:
                    # 3. update modified data
                    pass

    dc_view.Destroy()


def merge_db_for_network(content):
    dc_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.Datacenter], True)
    obj = [dc for dc in dc_view.view]

    # 1. delete removed data
    db_list = BiHost.objects.all()
    for db in db_list:
        removed = False
        for dc in obj:
            for cl in dc.hostFolder.childEntity:
                for host in cl.host:
                    dpnic = {}
                    dpg = {}
                    dvlanid = {}
                    network = host.config.network
                    for nic in network.pnic:
                        pass
                    for pg in network.portgroup:
                        pass
                    for nic in network.vnic:
                        pass
                    for sw in network.vswitch:
                        pass
        if removed:
            BiHost.objects.filter(id=db.id).delete()
    # 2. insert new data
    for dc in obj:
        for cl in dc.hostFolder.childEntity:
            for host in cl.host:
                dpnic = {}
                dpg = {}
                dvlanid = {}
                network = host.config.network
                for nic in network.pnic:
                    if BiHost.objects.filter(host=host.name).count() == 0:
                        pass
                    else:
                        # 3. update modified data
                        pass
                    pass
                for pg in network.portgroup:
                    pass
                for nic in network.vnic:
                    pass
                for sw in network.vswitch:
                    pass
                if BiHost.objects.filter(host=host.name).count() == 0:
                    pass
                else:
                    # 3. update modified data
                    pass

    for dc in obj:
        for entity in dc.hostFolder.childEntity:
            for host in entity.host:
                network = host.config.network
                for nic in network.pnic:
                    pass
                for pg in network.portgroup:
                    pass
                for nic in network.vnic:
                    pass
                for sw in network.vswitch:
                    pass

    dc_view.Destroy()


def patch_data_vcenter_datacenter():
    """
    Merge DB from vcenter API result
    for schedule
    :param request:
    :return: None
    """
    content = get_vcenter_info()
    # merge_db_for_dc(content)
    # merge_db_for_cluster(content)
    # merge_db_for_host(content)
    merge_db_for_network(content)
