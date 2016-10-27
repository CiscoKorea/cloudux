from django.db import models

# Create your models here.


class GlobalConfig(models.Model):
    vc_host = models.CharField(max_length=50, blank=True, null=True)
    vc_user = models.CharField(max_length=30, blank=True, null=True)
    vc_pass = models.CharField(max_length=30, blank=True, null=True)
    vc_port = models.CharField(max_length=10, blank=True, null=True)

    def __unicode__(self):
        return self.vc_host


class BiHost(models.Model):
    datacenter = models.CharField(max_length=100, blank=True, null=True)
    cluster = models.CharField(max_length=100, blank=True, null=True)
    host = models.CharField(max_length=100, blank=True, null=True)
    os = models.CharField(max_length=50, blank=True, null=True)
    version = models.CharField(max_length=20, blank=True, null=True)
    ip = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)

    def __unicode__(self):
        return self.host

    class Meta:
        ordering = ('datacenter', 'cluster', 'host',)


class BiVnic(models.Model):
    device = models.CharField(max_length=100, blank=True, null=True)
    ipAddress = models.CharField(max_length=20, blank=True, null=True)
    host = models.ManyToManyField(BiHost)

    def __unicode__(self):
        return self.device

    class Meta:
        ordering = ('ipAddress',)


class BiVswitch(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    host = models.ManyToManyField(BiHost)

    def __unicode__(self):
        return self.name


class BiVolume(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    host = models.ManyToManyField(BiHost)

    def __unicode__(self):
        return self.name


class BiVirtualMachine(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    ipAddress = models.CharField(max_length=20, blank=True, null=True)
    macAddress = models.CharField(max_length=20, blank=True, null=True)
    cpuUsage = models.CharField(max_length=5, blank=True, null=True)
    memUsage = models.CharField(max_length=5, blank=True, null=True)
    netUsage = models.CharField(max_length=5, blank=True, null=True)
    stgUsage = models.CharField(max_length=30, blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)

    def __unicode__(self):
        return self.name

