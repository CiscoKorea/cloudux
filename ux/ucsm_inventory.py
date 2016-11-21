# -*- coding: utf-8 -*-

import logging
import time
from ucsmsdk.ucseventhandler import UcsEventHandle
from ucsmsdk.mometa.ls.LsServer import LsServerConsts
#from connection.info import ucs_login, ucs_logout

from models import BiInventory, BiFaults
import datetime
import pytz

handle = None
log = logging.getLogger('ucs')
log.setLevel(logging.DEBUG)


def ucs_login():
    import ConfigParser
    import os
    from ucsmsdk.ucshandle import UcsHandle

    config = ConfigParser.RawConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), 'connection.cfg'))

    hostname = config.get('ucs', "hostname")
    username = config.get('ucs', "username")
    password = config.get('ucs', "password")
    port = config.get('ucs', "port")
    handle = UcsHandle(hostname, username, password, port)
    handle.login()
    return handle


def ucs_logout(phandle):
    phandle.logout()


def _convert_name( name):
    if name.startswith('sys/'):
        return name[4:]
    else:
        return name


def _fault_target( name):
    if name.startswith('sys/'):
        return name.split('/')[1]
    elif name.startswith('fabric/lan/'):
        items = name.split('/')
        return items[ len(items)-2]
    else:
        return '/'.join(name.split('/')[0:-1])


def _get_inventory(phandle, subject=None):
    inventories = []
    chassises = phandle.query_classid(class_id='EquipmentChassis')
    if len(chassises) == 0:
        return []
    for chassis in chassises:
        blades = phandle.query_children(in_mo=chassis, class_id="ComputeBlade")
        for blade in blades:
            firmware = None
            mgmts = phandle.query_children(in_mo=blade, class_id="MgmtController")
            for mgmt in mgmts:
                fws = phandle.query_children(in_mo=mgmt, class_id="FirmwareRunning")
                for fw in fws:
                    if fw.deployment == 'system': firmware = fw.version
            print (blade.model, blade.serial, _convert_name(blade.dn), firmware, blade.mfg_time)
            entity = BiInventory()
            entity.model = blade.model
            entity.hwtype = 'Blade'
            entity.serial = blade.serial
            entity.name = _convert_name(blade.dn)
            entity.firmwareVersion = firmware
            entity.mfgtime = blade.mfg_time
            entity.ipAddress = ''
            # entity.lastModified
            # entity.desc
            entity.save()
    racks = phandle.query_classid(class_id='ComputeRackUnit')
    if len(racks) == 0:
        return []
    for rack in racks:
        firmware = None
        mgmts = phandle.query_children(in_mo=rack, class_id="MgmtController")
        for mgmt in mgmts:
            fws = phandle.query_children(in_mo=mgmt, class_id="FirmwareRunning")
            for fw in fws:
                if fw.deployment == 'system': firmware = fw.version
        print(rack.model, rack.serial, _convert_name(rack.dn), firmware, rack.mfg_time)
        entity = BiInventory()
        entity.model = rack.model
        entity.hwtype = 'Rack'
        entity.serial = rack.serial
        entity.name = _convert_name(rack.dn)
        entity.firmwareVersion = firmware
        entity.mfgtime = rack.mfg_time
        entity.ipAddress = ''
        # entity.lastModified
        # entity.desc
        entity.save()

    networks = phandle.query_classid( class_id='NetworkElement')
    for network in networks:
        firmware = None
        mgmts = phandle.query_children(in_mo=network, class_id="MgmtController")
        for mgmt in mgmts:
            fws = phandle.query_children(in_mo=mgmt, class_id="FirmwareRunning")
            for fw in fws:
                if fw.deployment == 'system': firmware = fw.version
        print (network.model, network.serial, network.oob_if_ip, _convert_name(network.dn), firmware)
        entity = BiInventory()
        entity.model = network.model
        entity.hwtype = 'Network'
        entity.serial = network.serial
        entity.name = _convert_name(network.dn)
        entity.firmwareVersion = firmware
        # entity.mfgtime =
        entity.ipAddress = network.oob_if_ip
        # entity.lastModified
        # entity.desc
        entity.save()


def _print_fault_info(faults):
    for fault in faults:
        print(fault.severity, fault.code, _fault_target(fault.dn), fault.created, fault.descr, fault.occur)
        entity = BiFaults()
        entity.severity = fault.severity
        entity.target = _fault_target(fault.dn)
        entity.faultType = fault.code
        entity.code = fault.code
        entity.created = fault.created  # FIXME timezone
        entity.desc = fault.descr
        entity.occur = fault.occur
        entity.save()


def _get_faults(phandle):
    # severity=critial
    faults = phandle.query_classid(class_id='FaultInst', filter_str='(severity,"critical",type="eq")')
    if faults:
        _print_fault_info(faults)
    # severity=major
    faults = phandle.query_classid(class_id='FaultInst', filter_str='(severity,"major",type="eq")')
    if faults:
        _print_fault_info(faults)
    # severity=warning
    faults = phandle.query_classid(class_id='FaultInst', filter_str='(severity,"warning",type="eq")')
    if faults:
        _print_fault_info(faults)


def get_ucsm_info():
    try:
        global handle
        handle = ucs_login()
        #get faults
        _get_faults(handle)
        # get inventory
        _get_inventory(handle)
        ucs_logout(handle)
    except:
        # ucs_logout(handle)
        raise

#main()
