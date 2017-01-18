from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Config(models.Model):
    key = models.CharField(max_length=50, blank=False, null=False)
    val = models.CharField(max_length=50, blank=True, null=True)
    type = models.CharField(max_length=5, blank=True, null=True)
    is_used = models.CharField(max_length=1, blank=True, null=True)


class ConfigUtil:
    @staticmethod
    def get_val(key_str):
        try:
            data = Config.objects.get(key=key_str, type=1, is_used='Y')
            data2 = data.val
        except:
            data2 = ''
            pass

        return data2

    def __init__(self):
        pass

    def __unicode__(self):
        return ""


class GlobalConfig(models.Model):
    vc_host = models.CharField(max_length=50, blank=True, null=True)
    vc_user = models.CharField(max_length=30, blank=True, null=True)
    vc_pass = models.CharField(max_length=30, blank=True, null=True)
    vc_port = models.CharField(max_length=10, blank=True, null=True)

    def __unicode__(self):
        return self.vc_host


class Audited(models.Model):
    created = models.DateTimeField(blank=True, null=True)
    modified = models.DateTimeField(auto_now=True)
    dbstatus = models.CharField(max_length=1, default='A')

    class Meta:
        abstract = True


class BiDatacenter(Audited):
    name = models.CharField(max_length=100, blank=True, null=True)

    def __unicode__(self):
        return self.name


class BiCluster(Audited):
    name = models.CharField(max_length=100, blank=True, null=True)

    def __unicode__(self):
        return self.name


class BiHost(Audited):
    datacenter = models.ForeignKey(BiDatacenter, blank=True, null=True, on_delete=models.CASCADE)
    cluster = models.ForeignKey(BiCluster, blank=True, null=True, on_delete=models.CASCADE)
    host = models.CharField(max_length=100, blank=True, null=True)
    os = models.CharField(max_length=50, blank=True, null=True)
    version = models.CharField(max_length=20, blank=True, null=True)
    ip = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)

    def __unicode__(self):
        return self.host

    class Meta:
        ordering = ('datacenter', 'cluster', 'host',)


class BiVnic(Audited):
    device = models.CharField(max_length=100, blank=True, null=True)
    key = models.CharField(max_length=100, blank=True, null=True)
    ipAddress = models.CharField(max_length=20, blank=True, null=True)
    mac = models.CharField(max_length=30, blank=True, null=True)
    host = models.ManyToManyField(BiHost)
    portgroup = models.CharField(max_length=100, blank=True, null=True) #FIXME

    def __unicode__(self):
        return self.device

    class Meta:
        ordering = ('ipAddress',)


class BiVswitch(Audited):
    name = models.CharField(max_length=100, blank=True, null=True)
    key = models.CharField(max_length=100, blank=True, null=True)
    numPorts = models.IntegerField(default=0)
    numPortsAvailable = models.IntegerField(default=0)
    host = models.ManyToManyField(BiHost)

    def __unicode__(self):
        return self.name


class BiPnic(Audited):
    device = models.CharField(max_length=100, blank=True, null=True)
    key = models.CharField(max_length=100, blank=True, null=True)
    vswitch = models.ForeignKey(BiVswitch, blank=True, null=True, on_delete=models.CASCADE)

    def __unicode__(self):
        return self.device


class BiPortgroup(Audited):
    name = models.CharField(max_length=100, blank=True, null=True)
    key = models.CharField(max_length=100, blank=True, null=True)
    vlanId = models.CharField(max_length=100, blank=True, null=True)
    vswitch = models.ForeignKey(BiVswitch, blank=True, null=True, on_delete=models.CASCADE)

    def __unicode__(self):
        return self.name


class BiVolume(Audited):
    name = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=100, blank=True, null=True)
    capacity = models.BigIntegerField(default=0)
    host = models.ManyToManyField(BiHost)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class BiVirtualMachine(Audited):
    name = models.CharField(max_length=100, blank=True, null=True)
    ipAddress = models.CharField(max_length=20, blank=True, null=True)
    macAddress = models.CharField(max_length=20, blank=True, null=True)
    cpuUsage = models.CharField(max_length=5, blank=True, null=True)
    memUsage = models.CharField(max_length=5, blank=True, null=True)
    netUsage = models.CharField(max_length=5, blank=True, null=True)
    stgUsage = models.CharField(max_length=30, blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    host = models.ForeignKey(BiHost, blank=True, null=True, on_delete=models.CASCADE)
    network = models.ManyToManyField(BiPortgroup)
    ucsd_vm_id = models.CharField(max_length=20, blank=True, null=True)
    #added items for link vcenter and ucsd
    vcenter_vm_id = models.CharField(max_length=20,blank=True, null=True)
    assigned_to_user = models.CharField(max_length=30,blank=True, null=True)
    group_name = models.CharField(max_length=30, blank=True, null=True)

    def __unicode__(self):
        return self.name


class BiInventory(Audited):
    model = models.CharField(max_length=100, blank=True, null=True)
    hwtype = models.CharField(max_length=100, blank=True, null=True)
    serial = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    firmwareVersion = models.CharField(max_length=100, blank=True, null=True)
    mfgtime = models.CharField(max_length=100, blank=True, null=True)
    ipAddress = models.CharField(max_length=20, blank=True, null=True)
    lastModified = models.DateTimeField(blank=True, null=True)
    desc = models.CharField(max_length=100, blank=True, null=True)


class BiFaults(models.Model):
    severity = models.CharField(max_length=100, blank=True, null=True)
    target = models.CharField(max_length=100, blank=True, null=True)
    faultType = models.CharField(max_length=100, blank=True, null=True)
    code = models.CharField(max_length=100, blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True)
    desc = models.CharField(max_length=100, blank=True, null=True)
    occur = models.CharField(max_length=100, blank=True, null=True)

    def to_dict(self):
        dc = dict()
        dc["severity"] = self.severity
        dc["target"] = self.target
        dc["faultType"] = self.faultType
        dc["code"] = self.code
        dc["created"] = self.created.strftime("%Y-%m-%d %H:%M:%S")
        dc["desc"] = self.desc
        dc["occur"] = self.occur
        return dc


class BiCatalog(Audited):
    status = models.CharField(max_length=100, blank=True, null=True)
    group = models.CharField(max_length=100, blank=True, null=True)
    template_name = models.CharField(max_length=100, blank=True, null=True)
    image = models.CharField(max_length=100, blank=True, null=True)
    catalog_name = models.CharField(max_length=100, blank=True, null=True)
    applications = models.CharField(max_length=100, blank=True, null=True)
    catalog_type = models.CharField(max_length=100, blank=True, null=True)
    catalog_id = models.CharField(max_length=100, blank=True, null=True)
    folder = models.CharField(max_length=100, blank=True, null=True)
    os = models.CharField(max_length=100, blank=True, null=True)
    catalog_description = models.TextField(blank=True, null=True)
    cloud = models.CharField(max_length=100, blank=True, null=True)
    icon = models.CharField(max_length=100, blank=True, null=True)


class UdCloud(Audited):
    tag = models.CharField(max_length=100, blank=True, null=True)
    cloud_type = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    contact = models.CharField(max_length=100, blank=True, null=True)
    license_status = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    user_id = models.CharField(max_length=100, blank=True, null=True)
    reachable = models.CharField(max_length=100, blank=True, null=True)
    message = models.CharField(max_length=100, blank=True, null=True)
    vmware_server = models.CharField(max_length=100, blank=True, null=True)
    cloud = models.CharField(max_length=100, blank=True, null=True)


class DashboardAlloc(Audited):
    total_vm = models.IntegerField(default=0)
    total_cpu = models.IntegerField(default=0)
    total_mem = models.IntegerField(default=0)
    total_stg = models.IntegerField(default=0)


class DashboardVswitch(Audited):
    switch = models.CharField(max_length=100, blank=True, null=True)
    portgroup = models.IntegerField(default=0)


class UdGroup(Audited):
    group_id = models.IntegerField(default=0)
    group_name = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    parent_group_id = models.IntegerField(default=0)
    parent_group_name = models.CharField(max_length=100, blank=True, null=True)
    email_address = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    group_type = models.IntegerField(default=0)
    enable_budget = models.BooleanField(default=False)


class UdVDC(Audited):
    status = models.CharField(max_length=100, blank=True, null=True)
    tag = models.CharField(max_length=100, blank=True, null=True)
    vdc_id = models.IntegerField(default=0)
    custom_categories = models.IntegerField(default=0)
    total_vms = models.IntegerField(default=0)
    active_vms = models.IntegerField(default=0)
    dcloud = models.CharField(max_length=100, blank=True, null=True)
    vdc = models.CharField(max_length=100, blank=True, null=True)
    approvers = models.CharField(max_length=100, blank=True, null=True)
    lock_state = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=100, blank=True, null=True)
    cloud = models.CharField(max_length=100, blank=True, null=True)
    vdc_description = models.CharField(max_length=255, blank=True, null=True)


class UdVmDisk(Audited):
    vm_name = models.CharField(max_length=100, blank=True, null=True)
    datacenter_name = models.CharField(max_length=100, blank=True, null=True)
    unit_number = models.IntegerField(default=0)
    disk_id = models.CharField(max_length=200, blank=True, null=True)
    provision_size_gb = models.CharField(max_length=10, blank=True, null=True)
    vm_id = models.CharField(max_length=100, blank=True, null=True)
    datastore_name = models.CharField(max_length=100, blank=True, null=True)
    disk_name = models.CharField(max_length=100, blank=True, null=True)


class UserAddInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contact = models.CharField(max_length=50, blank=True, null=True)
    role = models.CharField(max_length=20, blank=True, null=True)
    tenant = models.ForeignKey(UdGroup, default=1)
