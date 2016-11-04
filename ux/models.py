from django.db import models

# Create your models here.


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

