from django.db import models
from django.urls import reverse


# Create your models here.
class Appsetup(models.Model):
    account_id = models.CharField(max_length=64, primary_key=True)
    application_key = models.CharField(max_length=64)
    application_secret = models.CharField(max_length=64)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.account_id


class Sshkey(models.Model):
    name = models.CharField(max_length=255, unique=True)
    content = models.TextField()
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('sshkey_edit', kwargs={'pk': self.pk})


class Deployment(models.Model):
    deployment_id = models.CharField(max_length=64, primary_key=True)
    deployment_number = models.CharField(max_length=20)
    deployment_text = models.TextField()
    applications = models.CharField(max_length=255)
    tags = models.CharField(max_length=255)
    products = models.CharField(max_length=255)
    server_id = models.CharField(max_length=255)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.deployment_id


class Deploymentsetup(models.Model):
    deployment_id = models.CharField(max_length=64, primary_key=True)
    server_id = models.CharField(max_length=255)
    ipaddress = models.CharField(max_length=16)
    port = models.PositiveIntegerField(default=22)
    username = models.CharField(max_length=255)
    ssh_key = models.ForeignKey(Sshkey, on_delete=models.SET_NULL, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.deployment_id


class Logging(models.Model):
    deployment_id = models.CharField(max_length=64, primary_key=True)
    deployment_number = models.CharField(max_length=20)
    server_id = models.CharField(max_length=255)
    ipaddress = models.CharField(max_length=16)
    applications = models.CharField(max_length=255)
    tags = models.CharField(max_length=255)
    products = models.CharField(max_length=255)
    macaddress = models.CharField(max_length=255)
    hostname = models.CharField(max_length=255)
    architecture = models.CharField(max_length=255)
    num_cpu_processors = models.PositiveIntegerField()
    num_cpu_cores = models.PositiveIntegerField()
    num_cpu_logical_cores = models.PositiveIntegerField()
    os_name = models.CharField(max_length=255)
    os_version = models.CharField(max_length=255)
    size_ram_mb = models.PositiveIntegerField()
    size_disk_gb = models.PositiveIntegerField()

    def __str__(self):
        return self.deployment_id
