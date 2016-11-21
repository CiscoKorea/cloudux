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
        except:
            pass

        return data.val

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

    def __unicode__(self):
        return self.name


class UserAddInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contact = models.CharField(max_length=50, blank=True, null=True)


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
