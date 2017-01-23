# -*- coding: utf-8 -*-
"""
    Python module of different functions for manipulating UCS Director
    via the API.
"""


# import standard variables and configuration info
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from local_config import ucsdserver, ucsd_key, url, getstring, parameter_lead, headers
from cloud_library import dict_filter, list_search
from models import ConfigUtil

import requests
import json

ucsdserver = ConfigUtil.get_val("UCSD.HOST")
headers["X-Cloupia-Request-Key"] = ConfigUtil.get_val("UCSD.KEY") #ucsd_key

def workflow_inputs(workflow):
    """
    Query UCS Director for the inputs for a workflow
    :param workflow: The workflow name to lookup inputs for
    :return:
    """
    apioperation = "userAPIGetWorkflowInputs"
    u = url % ucsdserver + getstring % apioperation + parameter_lead + "{param0:\"" + workflow + '"' + '}'

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.get(u, headers=headers, verify=False)

    j = json.loads(r.text)

    return j['serviceResult']['details']


def workflow_list(folder="", key_filter=None, result_filter=None):
    """
    Query UCS Director for the workflows for a folder
    :param folder: The UCSD Orchestration Folder to Query - defaults to all
    :param key_filter:
    :param result_filter:
    :return:
    """
    if result_filter is None:
        result_filter = {}
    if key_filter is None:
        key_filter = []
    apioperation = "userAPIGetWorkflows"
    u = url % ucsdserver + getstring % apioperation + parameter_lead + \
        "{param0:\"" + folder + '"' + '}'

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.get(u, headers=headers, verify=False)
    j = json.loads(r.text)

    j['serviceResult'] = list_search(j['serviceResult'], result_filter)

    search_results = [dict_filter(r, key_filter) for r in j['serviceResult']]
    return search_results


def workflow_execute(workflow, inputs):
    """
    Create a Service Request based on the specified Workflow and with Inputs.
    :param workflow:    The workflow name to execute
    :param inputs:      dict of inputs with Input Label as Key
    :return:            JSON of the Service Request Created
    """
    param0 = workflow

    # Get the workflow inputs
    wf_inputs = workflow_inputs(workflow)

    param1 = [{"name": i['label'], "value":inputs[i['label']]} for i in wf_inputs]
    param2 = "-1"

    apioperation = "userAPISubmitWorkflowServiceRequest"
    u = url % ucsdserver + getstring % apioperation + parameter_lead + \
        "{param0:\"" + param0 + '",' + \
        'param1:{"list":' + json.dumps(param1) + '}' + \
        ',param2:' + param2 + '}'

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.get(u, headers=headers, verify=False)

    j = json.loads(r.text)

    return j


def sr_rollback(srnumber):
    """
    Rollback the Service Request Specified
    :param srnumber: The Service Request ID
    :return: JSON status of the request
    """
    apioperation = "userAPIRollbackWorkflow"
    u = url % ucsdserver + getstring % apioperation + parameter_lead + \
        "{param0:\"" + srnumber + '"' + '}'

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.get(u, headers=headers)

    return r.text


def sr_details(srnumber):
    """
    Return the details of the Service Request Specified - Workflow Based Only
    :param srnumber: The Service Request ID
    :return: JSON of the SR Status
    """
    # apioperation = "userAPIGetServiceRequestDetails"
    apioperation = "userAPIGetServiceRequestWorkFlow"
    u = url % ucsdserver + getstring % apioperation + parameter_lead + \
        "{param0:\"" + srnumber + '"' + '}'

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.get(u, headers=headers)

    return r.text


# Need to update notes and things below here
def vdc_list(group="", provider="", key_filter=None, result_filter=None):
    """
    Return a list of all VDCs for a group if provided
    :param group:  The UCSD Group to return VDCs for... default all groups
    :param provider:
    :param key_filter: A sub-list of keys from the returned data to filter for
    :param result_filter: A dictionary of key/value pairs to filter the result list down by (OR logic).
    :return:
    """
    if result_filter is None:
        result_filter = {}
    if key_filter is None:
        key_filter = []
    apioperation = "userAPIGetAllVDCs"
    u = url % ucsdserver + getstring % apioperation

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.get(u, headers=headers, verify=False)
    print(r.text)

    j = json.loads(r.text)

    all_vdcs = j['serviceResult']['rows']
    group_vdcs = []

    for vdc in all_vdcs:
        if vdc['Group'] == group or group == "":
            if vdc['Cloud'] == provider or provider == "":
                group_vdcs.append(vdc)

    group_vdcs = list_search(group_vdcs, result_filter)

    search_results = [dict_filter(r, key_filter) for r in group_vdcs]
    return search_results


def vm_list(key_filter=None, result_filter=None):
    """
    Return a list of all VMs known by ICF Director
    :param key_filter: A sub-list of keys from the returned data to filter for
    :param result_filter: A dictionary of key/value pairs to filter the result list down by (OR logic).
    :return:
    """
    if result_filter is None:
        result_filter = {}
    if key_filter is None:
        key_filter = []
    apioperation = "userAPIGetAllVMs"
    u = url % ucsdserver + getstring % apioperation

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.get(u, headers=headers, verify=False)

    j = json.loads(r.text)
    j['serviceResult']['rows'] = list_search(j['serviceResult']['rows'], result_filter)

    search_results = [dict_filter(r, key_filter) for r in j['serviceResult']['rows']]
    return search_results


def vm_id(vmname):
    """
    Find the VM ID given a VMname
    :param vmname:
    :return:
    """
    return vm_list(result_filter={"VM_Name": vmname})[0]["VM_ID"]


def vm_details(vmid, key_filter=None, result_filter=None):
    """
    Return the known details of the specified VM
    :param vmid: The ICFD VMID for the Virtual Machine
    :param key_filter: A sub-list of keys from the returned data to filter for
    :param result_filter: A dictionary of key/value pairs to filter the result list down by (OR logic).
    :return:
    """
    if result_filter is None:
        result_filter = {}
    if key_filter is None:
        key_filter = []
    apioperation = "userAPIGetVMSummary"
    u = url % ucsdserver + getstring % apioperation + parameter_lead + \
        "{param0:\"" + vmid + '"' + '}'

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.get(u, headers=headers, verify=False)

    j = json.loads(r.text)
    if j['serviceError']:
        return j['serviceError']
    else:
        j['serviceResult']['rows'] = list_search(j['serviceResult']['rows'], result_filter)
        search_results = [dict_filter(r, key_filter) for r in j['serviceResult']['rows']]
        return search_results


def vm_action(vmid, action, comments=""):
    """
    Power on the specified Cloud Virtual Machine
    :param vmid:  The ICFD VMID for the Cloud VM
    :param action:
    :param comments:
    :return:
    """
    apioperation = "userAPIExecuteVMAction"
    # action = "powerOn"
    generic_actions = ["discardSaveState",
                       "pause",
                       "powerOff",
                       "powerOn",
                       "reboot",
                       "rebuildServer",
                       "repairVM",
                       "reset",
                       "resume",
                       "saveState",
                       "shutdownGuest",
                       "standby",
                       "suspend",
                       "destroyVM"  # for VMware vSphere VMs
                       ]
    if action == "help":
        return generic_actions
    if not any(action == a for a in generic_actions):
        return "Action not valid"

    u = url % ucsdserver + getstring % apioperation + parameter_lead + \
        "{param0:\"" + vmid + '",' + \
        'param1:"' + action + '"' + \
        ',param2:"' + comments + '"}'

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.get(u, headers=headers, verify=False)

    j = json.loads(r.text)

    return j


def vm_getactions(vmid):
    """
    Get Available Actions for a Given VM
    :param vmid:  The ICFD VMID for the Cloud VM
    :return:
    """
    apioperation = "userAPIGetAvailableVMActions"
    u = url % ucsdserver + getstring % apioperation + parameter_lead + \
        "{param0:\"" + vmid + '"' + '}'

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.get(u, headers=headers, verify=False)

    j = json.loads(r.text)

    return j['serviceResult']


def vm_terminate(vmid, comments=""):
    """
    Power on the specified Cloud Virtual Machine
    :param vmid:  The UCSD VMID for the Cloud VM
    :param comments:
    :return:
    """
    apioperation = "userAPIExecuteVMAction"
    action = "destroyVM"

    u = url % ucsdserver + getstring % apioperation + parameter_lead + \
        "{param0:\"" + vmid + '",' + \
        'param1:"' + action + '"' + \
        ',param2:"' + comments + '"}'

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.get(u, headers=headers, verify=False)

    j = json.loads(r.text)

    return j


def vm_poweron(vmid, comments=""):
    """
    Power on the specified Cloud Virtual Machine
    :param vmid:  The UCSD VMID for the Cloud VM
    :param comments:
    :return:
    """

    return vm_action(vmid, "powerOn", comments)


def vm_poweroff(vmid, comments=""):
    """
    Power on the specified Cloud Virtual Machine
    :param vmid:  The UCSD VMID for the Cloud VM
    :param comments:
    :return:
    """

    return vm_action(vmid, "shutdownGuest", comments)


def vm_reboot(vmid, comments=""):
    """
    Reboot the specified Cloud Virtual Machine
    :param vmid:  The UCSD VMID for the Cloud VM
    :param comments:
    :return:
    """

    return vm_action(vmid, "reboot", comments)


def catalog_list(group="", key_filter=None, result_filter=None):
    """
    Get a list of Catalog Options for a Group
    :param group:  The UCSD Group to Query on behalf of
    :param key_filter: A sub-list of keys from the returned data to filter for
    :param result_filter: A dictionary of key/value pairs to filter the result list down by (OR logic).
    :return:
    """
    if result_filter is None:
        result_filter = {}
    if key_filter is None:
        key_filter = []
    apioperation = "userAPIGetCatalogsPerGroup"
    u = url % ucsdserver + getstring % apioperation + parameter_lead + \
        "{param0:\"" + group + '"' + '}'

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.get(u, headers=headers, verify=False)

    j = json.loads(r.text)
    print(j)

    j['serviceResult']['rows'] = list_search(j['serviceResult']['rows'], result_filter)

    search_results = [dict_filter(r, key_filter) for r in j['serviceResult']['rows']]
    return search_results


def catalog_list_all(key_filter=None, result_filter=None):
    """
    Get a list of Catalog Options for a Group
    :param key_filter: A sub-list of keys from the returned data to filter for
    :param result_filter: A dictionary of key/value pairs to filter the result list down by (OR logic).
    :return:
    """
    if result_filter is None:
        result_filter = {}
    if key_filter is None:
        key_filter = []
    apioperation = "userAPIGetAllCatalogs"
    u = url % ucsdserver + getstring % apioperation + parameter_lead + \
        "{}"

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.get(u, headers=headers, verify=False)

    j = json.loads(r.text)
    # print(j)

    j['serviceResult']['rows'] = list_search(j['serviceResult']['rows'], result_filter)

    search_results = [dict_filter(r, key_filter) for r in j['serviceResult']['rows']]
    return search_results


def cloud_list(key_filter=None, result_filter=None):
    """
    Return a list of all clouds known by UCSD Director
    :param key_filter: A sub-list of keys from the returned data to filter for
    :param result_filter: A dictionary of key/value pairs to filter the result list down by (OR logic).
    :return:
    """
    if result_filter is None:
        result_filter = {}
    if key_filter is None:
        key_filter = []
    apioperation = "userAPIGetCloudsListReport"
    u = url % ucsdserver + getstring % apioperation

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.get(u, headers=headers, verify=False)

    j = json.loads(r.text)
    j['serviceResult']['rows'] = list_search(j['serviceResult']['rows'], result_filter)

    search_results = [dict_filter(r, key_filter) for r in j['serviceResult']['rows']]
    return search_results


def cloud_type(cloud):
    """
    Returns the cloud type for the given cloud
    :param cloud:
    :return:
    """
    cloud = cloud_list(result_filter={"Cloud": cloud})
    return cloud[0]["Cloud_Type"]


def catalog_cloud(catalog, group):
    """
    Returns the cloud for the given catalog
    :param catalog:
    :param group:
    :return:
    """
    c = catalog_list(group, result_filter={"Catalog_Name": catalog})
    return c[0]["Cloud"]


def catalog_type(catalog, group):
    """
    Returns the catalog type for the given catalog
    :param catalog:
    :param group:
    :return:
    """
    c = catalog_list(group, result_filter={"Catalog_Name": catalog})
    return c[0]["Catalog_Type"]


def catalog_order(catalog, vdc, group, comment="", vmname="", vcpus="0", vram="0", datastores="", vnics="", username=""):
    """
    Order a Standard Catalog Item
    :param catalog:
    :param vdc:
    :param group:
    :param comment:
    :param vmname:
    :param vcpus:
    :param vram:
    :param datastores:
    :param vnics:
    :return:
    """
    # Get the catalog type, only STandard supported
    if catalog_type(catalog, group) not in [ "Standard", u'표준', '표준'] :
        return "Error: Only Standard Catalogs Supported.  " \
                "Use 'workflow_execute' for Advanced Catalogs "

    # Get the type of cloud that the catalog is for
    catalog_cloud_type = cloud_type(catalog_cloud(catalog, group))
    # print catalog_cloud_type

    # Only support vCenter so far
    if catalog_cloud_type == "VMware":
        order = vmware_provision(catalog, vdc, comment, vmname, vcpus, vram, datastores, vnics, username)
        return order

    return "Invalid Request Provided"


def vmware_provision(catalog, vdc, comment="", vmname="", vcpus="0", vram="0", datastores="", vnics="0", username=""):
    """
    Order a VMware based standard catalog
    :param catalog: Name of the catalog
    :param vdc: Name of the vDC
    :param comment: Comment that is set as the VM label
    :param vmname: Name of the VM to be provisioned
    :param vcpus: Number of CPUs
    :param vram: Size of memory in GB
    :param datastores: Number of VM Disks
    :param vnics: VM networks
    :return:
    """
    param0 = catalog
    param1 = vdc
    param2 = vmname
    param3 = comment if comment else ""
    param4 = vcpus if vcpus else "0"
    param5 = vram if vram else "0"
    param6 = datastores if datastores else ""
    param7 = vnics if vnics else ""

    apioperation = "userAPIVMWareProvisionRequest"
    u = url % ucsdserver + getstring % apioperation + parameter_lead + \
        "{param0:\"" + param0 + '",' + \
        "param1:\"" + param1 + '",' + \
        "param2:\"" + param2 + '",' + \
        "param3:\"" + param3 + '",' + \
        "param4:" + param4 + ',' + \
        "param5:" + param5 + ',' + \
        "param6:\"" + param6 + '",' + \
        "param7:\"" + param7 + '"}'

    print u

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    if username != "":
        myheaders = {"X-Cloupia-Request-Key": ucsd_get_restaccesskey(username)}
        r = requests.get(u, headers=myheaders, verify=False)
    else :
        r = requests.get(u, headers=headers, verify=False)
    #print r.text
    j = json.loads(r.text)
    print j
    # vms = sr_vms()

    return j


def sr_vms(srnumber):
    """
    Return the VMs of the Service Request Specified
    :param srnumber: The Service Request ID
    :return: JSON of the SR Status
    """
    apioperation = "userAPIGetVMsForServiceRequest"
    u = url % ucsdserver + getstring % apioperation + parameter_lead + \
        "{param0:\"" + srnumber + '"' + '}'

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.get(u, headers=headers)
    j = json.loads(r.text)

    return j['serviceResult']['vms']


def ucsd_cloud():
    apioperation = "userAPIGetTabularReport"
    u = url % ucsdserver + getstring % apioperation + parameter_lead + \
        "{param0:\"" + '0' + '"' \
        + ',param1:\"' + 'All%20Clouds' + '"' \
        + ',param2:\"' + 'CLOUDS-T0' + '"' \
        + '}'

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.get(u, headers=headers, verify=False)
    j = json.loads(r.text)

    return j['serviceResult']['rows']



def ucsd_vdcs():
    # /api/rest?formatType=json&opName=userAPIGetTabularReport&opData={param0:"0",param1:"All%20Clouds",param2:"VDCS-T0"}
    apioperation = "userAPIGetTabularReport"
    u = url % ucsdserver + getstring % apioperation + parameter_lead + \
        "{param0:\"" + '0' + '"' \
        + ',param1:\"' + 'All%20Clouds' + '"' \
        + ',param2:\"' + 'VDCS-T0' + '"' \
        + '}'

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.get(u, headers=headers, verify=False)
    j = json.loads(r.text)

    return j['serviceResult']['rows']


def ucsd_cpu():
    apioperation = "userAPIGetInstantDataReport"
    u = url % ucsdserver + getstring % apioperation + parameter_lead + \
        "{param0:\"" + '0' + '"' \
        + ',param1:\"' + 'All%20Clouds' + '"' \
        + ',param2:\"' + 'CPU-S0' + '"' \
        + '}'

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.get(u, headers=headers, verify=False)
    j = json.loads(r.text)

    return j['serviceResult']['categories'][0]['nameValuePairs']


def ucsd_memory():
    apioperation = "userAPIGetInstantDataReport"
    u = url % ucsdserver + getstring % apioperation + parameter_lead + \
        "{param0:\"" + '0' + '"' \
        + ',param1:\"' + 'All%20Clouds' + '"' \
        + ',param2:\"' + 'MEMORY-S0' + '"' \
        + '}'

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.get(u, headers=headers, verify=False)
    j = json.loads(r.text)

    return j['serviceResult']['categories'][0]['nameValuePairs']


def ucsd_disk():
    apioperation = "userAPIGetInstantDataReport"
    u = url % ucsdserver + getstring % apioperation + parameter_lead + \
        "{param0:\"" + '0' + '"' \
        + ',param1:\"' + 'All%20Clouds' + '"' \
        + ',param2:\"' + 'DISK-S0' + '"' \
        + '}'

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.get(u, headers=headers, verify=False)
    j = json.loads(r.text)

    return j['serviceResult']['categories'][0]['nameValuePairs']

#javaos74 need to fix 
def ucsd_network():
    # opName=userAPIGetTabularReport&opData={param0:"1",param1:"dCloud-Cluster",param2:"VSWITCHES-T2"}
    apioperation = "userAPIGetTabularReport"
    u = url % ucsdserver + getstring % apioperation + parameter_lead + \
        "{param0:\"" + '1' + '"' \
        + ',param1:\"' + 'dCloud-Cluster' + '"' \
        + ',param2:\"' + 'VSWITCHES-T2' + '"' \
        + '}'

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.get(u, headers=headers, verify=False)
    j = json.loads(r.text)
   
    return j['serviceResult']['rows'] if 'rows' in j['serviceResult'] else {}


def group_list():
    """
    Get a list of Group
    :return:
    """
    apioperation = "userAPIGetGroups"
    u = url % ucsdserver + getstring % apioperation + parameter_lead + \
        "{param0:\"" + "" + '"' + '}'

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.get(u, headers=headers, verify=False)
    # print r.text
    j = json.loads(r.text)
    return j['serviceResult']


def group_detail_by_id(group_id):
    """
    Get a list of Group
    :return:
    """
    apioperation = "userAPIGetGroupById"
    u = url % ucsdserver + getstring % apioperation + parameter_lead + \
        "{param0:\"" + str(group_id) + '"' + '}'

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.get(u, headers=headers, verify=False)
    # print r.text
    j = json.loads(r.text)
    # print j
    return j['serviceResult'][0]


def vdc_list_all():
    """
    Get a list of Group
    :return:
    """
    apioperation = "userAPIGetAllVDCs"
    u = url % ucsdserver + getstring % apioperation + parameter_lead + \
        "{param0:\"" + "" + '"' + '}'

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.get(u, headers=headers, verify=False)
    # print r.text
    j = json.loads(r.text)
    # print j
    return j['serviceResult']['rows']


def global_vms():
    apioperation = "userAPIGetTabularReport"
    u = url % ucsdserver + getstring % apioperation + parameter_lead + \
        "{param0:\"" + '0' + '"' \
        + ',param1:\"' + 'All%20Clouds' + '"' \
        + ',param2:\"' + 'VMS-T0' + '"' \
        + '}'

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.get(u, headers=headers, verify=False)
    #print r
    j = json.loads(r.text)
    #print j

    return j    # ['serviceResult']['rows']


def group_vms(group_id):
    apioperation = "userAPIGetTabularReport"
    u = url % ucsdserver + getstring % apioperation + parameter_lead + \
        "{param0:\"" + 'group' + '"' \
        + ',param1:\"' + group_id + '"' \
        + ',param2:\"' + 'VMS-T14' + '"' \
        + '}'

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.get(u, headers=headers, verify=False)
    # print r.text
    j = json.loads(r.text)
    # print j

    return j['serviceResult']['rows']


def available_reports(group_name):
    apioperation = "userAPIGetAvailableReports"
    u = url % ucsdserver + getstring % apioperation + parameter_lead + \
        "{param0:\"" + 'group' + '"' \
        + ',param1:\"' + group_name + '"' \
        + '}'

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.get(u, headers=headers, verify=False)
    # print r.text
    j = json.loads(r.text)
    # print j

    return j['serviceResult']


def tabular_report(context_name, context_value, report_id):
    apioperation = "userAPIGetTabularReport"
    u = url % ucsdserver + getstring % apioperation + parameter_lead + \
        "{param0:\"" + context_name + '"' \
        + ',param1:\"' + context_value + '"' \
        + ',param2:\"' + report_id + '"' \
        + '}'

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.get(u, headers=headers, verify=False)
    j = json.loads(r.text)

    return j['serviceResult']['rows']


def ucsd_vm_disk(p_vm_id):
    # /userAPIGetTabularReport&opData={param0:"3",param1:"70",param2:"DISKS-T0"}
    assert isinstance(p_vm_id, str)
    return tabular_report('3', p_vm_id, 'DISKS-T0')


def ucsd_get_restaccesskey( p_user_id):
    #userAPIGetRESTAccessKey&opData={param0:"sample"}
    assert isinstance(p_user_id, str)
    apioperation = "userAPIGetRESTAccessKey"
    u = url % ucsdserver + getstring % apioperation + parameter_lead + \
        "{param0:\"" + p_user_id + '"' \
        + '}'
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.get(u, headers=headers, verify=False)
    j = json.loads(r.text)
    print(j)
    return j['serviceResult']

def ucsd_get_userprofile( p_user_id):
    # userAPIGetUserLoginProfile& opData={param0:"sample"}
    assert isinstance(p_user_id, str)
    apioperation = "userAPIGetUserLoginProfile"
    u = url % ucsdserver + getstring % apioperation + parameter_lead + \
        "{param0:\"" + p_user_id + '"' \
        + '}'
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.get(u, headers=headers, verify=False)
    j = json.loads(r.text)
    return j['serviceResult']

def ucsd_get_all_vms():
    #/app/api/rest?formatType=json&opName=userAPIGetAllVMs& ;opData={}
    apioperation = "userAPIGetAllVMs"
    u = url % ucsdserver + getstring % apioperation + parameter_lead + \
        "{}"
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.get(u, headers=headers, verify=False)
    j = json.loads(r.text)
    rows = []
    try :
        rows = j['serviceResult']['rows']
    except KeyError as ke:
        pass
    return rows

def ucsd_get_groups():
    #/app/api/rest?formatType=json&opName=userAPIGetAllGroups& amp;opData={}

    apioperation = "userAPIGetAllGroups"
    u = url % ucsdserver + getstring % apioperation + parameter_lead + \
        "{}"
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.get(u, headers=headers, verify=False)
    j = json.loads(r.text)

    rows = []
    try:
        rows = j['serviceResult']['rows']
    except KeyError as ke:
        pass
    return rows

def ucsd_get_groupbyname( grp_name):
    #userAPIGetGroupByName&opData={param0:"grp1"}
    apioperation = "userAPIGetGroupByName"
    u = url % ucsdserver + getstring % apioperation + parameter_lead + \
        "{param0:\"" + grp_name + '"' \
        + '}'
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.get(u, headers=headers, verify=False)
    j = json.loads(r.text)

    return j['serviceResult']


def ucsd_add_user(user_id="", password="", first_name="", last_name="", email="", role="", group_name=""):

    apioperation = "userAPIAddUser"
    u = url % ucsdserver + getstring % apioperation + parameter_lead + \
        '{' + \
        'param0:"' + user_id + '"' + \
        ',' + 'param1:"' + password + '"' + \
        ',' + 'param2:"' + first_name + '"' + \
        ',' + 'param3:"' + last_name + '"' + \
        ',' + 'param4:"' + email + '"' + \
        ',' + 'param5:"' + role + '"' + \
        ',' + 'param6:"' + group_name + '"' + \
        '}'

    # print(u)
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.get(u, headers=headers, verify=False)
    # print('end')

    j = json.loads(r.text)
    print(j)

    if j['serviceError']:
        print(j['serviceError'])
        return None

    return j['serviceResult']


def ucsd_add_group(group_name="", first_name="", last_name="", contact_email=""):
    apioperation = "userAPIAddGroup"
    u = url % ucsdserver + getstring % apioperation + parameter_lead + \
        '{' + \
        'param0:"' + group_name + '"' + \
        ',' + 'param1:"' + '' + '"' + \
        ',' + 'param2:"' + first_name + '"' + \
        ',' + 'param3:"' + last_name + '"' + \
        ',' + 'param4:"' + contact_email + '"' + \
        '}'

    # print(u)
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.get(u, headers=headers, verify=False)
    # print('end')

    j = json.loads(r.text)
    print(j)

    if j['serviceError']:
        print(j['serviceError'])
        return None

    return j['serviceResult']


def ucsd_verify_user(user_id="", password=""):
    apioperation = "userAPIVerifyUser"
    u = url % ucsdserver + getstring % apioperation + parameter_lead + \
        '{' + \
        'param0:"' + user_id + '"' + \
        ',' + 'param1:"' + password + '"' + \
        '}'

    print(u)
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.get(u, headers=headers, verify=False)
    print r
    # print('end')

    j = json.loads(r.text)
    print(j)

    if j['serviceError']:
        print(j['serviceError'])
        return None

    return j['serviceResult']


# def change_header_rest_key(p_user_id):
#     key = ucsd_get_restaccesskey(p_user_id=p_user_id)
#     headers["X-Cloupia-Request-Key"] = key
#     return key
#
#
# def get_header_rest_key():
#     return headers["X-Cloupia-Request-Key"]
#
#
# def set_header_rest_key(key):
#     headers["X-Cloupia-Request-Key"] = key


def ucsd_provision_request(catalog, vdc, comment="", vmname="", vcpus="0", vram="0", datastores="", vnics="0", username=""):
    """
    Order a VMware based standard catalog
    :param catalog: Name of the catalog
    :param vdc: Name of the vDC
    :param comment: Comment that is set as the VM label
    :param vmname: Name of the VM to be provisioned
    :param vcpus: Number of CPUs
    :param vram: Size of memory in GB
    :param datastores: Number of VM Disks
    :param vnics: VM networks
    :return:
    """
    # param0 = catalog
    # param1 = vdc
    # param2 = vmname
    # param3 = comment if comment else ""
    # param4 = vcpus if vcpus else "0"
    # param5 = vram if vram else "0"
    # param6 = datastores if datastores else ""
    # param7 = vnics if vnics else "0"
    param0 = {"catalogName": catalog, "vdcName": vdc, "userID": 'test3'}

    if username == "":
        username = 'admin'

    apioperation = "userAPIProvisionRequest"
    u = url % ucsdserver + getstring % apioperation + parameter_lead + \
        '{param0:{"catalogName":"' + catalog + '"' \
                  + ',"vdcName":"' + vdc + '"' \
                  + ',"userID":"'+username + '"' \
                  + ',"vmName":"'+vmname + '"' \
                  + ',"resourceAllocated":'+'true' + '' \
                  + ',"cores":'+vcpus + '' \
                  + ',"memoryMB":'+vram + '' \
                  + ',"diskGB":'+'15' + '' \
                  + ',"comments":"'+'abc' + '"' \
        '}}'
    print u

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    if username != "":
        myheaders = {"X-Cloupia-Request-Key": ucsd_get_restaccesskey(username)}
        r = requests.get(u, headers=myheaders, verify=False)
    else :
        r = requests.get(u, headers=headers, verify=False)
    print r.text
    j = json.loads(r.text)
    print j
    # vms = sr_vms()

    return j


def ucsd_create_vdc(vdcName,  group_id,  cloudName, systemPolicy, computingPolicy, storagePolicy, networkPolicy):
    apioperation = "userAPICreateVDC"
    u = url % ucsdserver + getstring % apioperation + parameter_lead + \
        '{param0:{"vdcName":"' + vdcName + '"' \
        + ',"vdcDescription":"' + 'vdcDescription' + '"' \
        + ',"cloudName":"' + cloudName + '"' \
        + ',"groupName":' + str(group_id) + '' \
        + ',"approver1":"' + '' + '"' \
        + ',"approver1":"' + '' + '"' \
        + ',"vdcSupportEmail":"' + '' + '"' \
        + ',"vdcCustomerNoticationEmail":"' + '' + '"' \
        + ',"systemPolicy":"' + systemPolicy + '"' \
        + ',"deploymentPolicy":"' + '' + '"' \
        + ',"slaPolicy":"' + '' + '"' \
        + ',"computingPolicy":"' + computingPolicy + '"' \
        + ',"storagePolicy":"' + storagePolicy + '"' \
        + ',"networkPolicy":"' + networkPolicy + '"' \
        + ',"costModel":"' + '' + '"' \
        + ',"isLocked":' + 'false' + '' \
        + ',"isDeletable":' + 'true' + '' \
        + ',"inactivityPeriodForDeletion":' + '-1' + '' \
        + ',"selfServiceEndUserPolicy":"' + '' + '"' \
                                                 '}}'

    print(u)
    print(headers)
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.get(u, headers=headers, verify=False)
    print r
    print r.text
    # print('end')

    j = json.loads(r.text)
    print(j)

    if j['serviceError']:
        print(j['serviceError'])
        return None

    return j['serviceResult']


def ucsd_vmware_system_policy():
    apioperation = "userAPIGetTabularReport"
    u = url % ucsdserver + getstring % apioperation + parameter_lead + \
        "{param0:\"" + '10' + '"' \
        + ',param1:\"' + '' + '"' \
        + ',param2:\"' + 'VMWARE-SYSTEM-POLICY-T41' + '"' \
        + '}'

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.get(u, headers=headers, verify=False)
    print r.text
    j = json.loads(r.text)
    #print j

    return j['serviceResult']['rows']


def ucsd_vmware_computing_policy():
    apioperation = "userAPIGetTabularReport"
    u = url % ucsdserver + getstring % apioperation + parameter_lead + \
        "{param0:\"" + '10' + '"' \
        + ',param1:\"' + '' + '"' \
        + ',param2:\"' + 'VMWARE-COMPUTING-POLICY-T42' + '"' \
        + '}'

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.get(u, headers=headers, verify=False)
    print r.text
    j = json.loads(r.text)
    #print j

    return j['serviceResult']['rows']


def ucsd_vmware_storage_policy():
    apioperation = "userAPIGetTabularReport"
    u = url % ucsdserver + getstring % apioperation + parameter_lead + \
        "{param0:\"" + '10' + '"' \
        + ',param1:\"' + '' + '"' \
        + ',param2:\"' + 'VMWARE-STORAGE-POLICY-T43' + '"' \
        + '}'

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.get(u, headers=headers, verify=False)
    print r.text
    j = json.loads(r.text)
    #print j

    return j['serviceResult']['rows']


def ucsd_vmware_network_policy():
    apioperation = "userAPIGetTabularReport"
    u = url % ucsdserver + getstring % apioperation + parameter_lead + \
        "{param0:\"" + '10' + '"' \
        + ',param1:\"' + '' + '"' \
        + ',param2:\"' + 'VMWARE-NETWORK-POLICY-T44' + '"' \
        + '}'

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.get(u, headers=headers, verify=False)
    print r.text
    j = json.loads(r.text)
    #print j

    return j['serviceResult']['rows']


if __name__ == '__main__':
    print('test code')
    #print (ucsd_user_profile('hyungsok'))
    #print (ucsd_get_all_vms())
    #ret = ucsd_get_userprofile('hyungsok')
    #print( ret )
    #print( ucsd_get_groupbyname(ret['groupName']))
    #print(ucsd_get_restaccesskey('hyungsok'))

