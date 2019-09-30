from django.core.management.base import BaseCommand
from django.conf import settings
import requests
import json
import subprocess
from django.core import serializers

from smsagent.models import Appsetup, Sshkey, Deployment, Deploymentsetup, Logging


class Command(BaseCommand):
    help = 'Gather infrastructure logging and forward to sms'

    def handle(self, *args, **kwargs):
        deploymentsetups = Deploymentsetup.objects.all()
        file = open('workdir/log/config/sms_log.txt', 'w')
        file.write('[sms_log]\n')

        for d in deploymentsetups:
            sshkey = Sshkey.objects.get(id=d.ssh_key_id)
            private_key_file_path = 'workdir/log/keys/' + sshkey.name
            file1 = open(private_key_file_path, 'w')
            file1.write(sshkey.content)
            file1.close()
            subprocess.call(['chmod', '0600', private_key_file_path])

            file.write(d.server_id + ' ansible_host=' + d.ipaddress + ' ansible_port=' + str(d.port) + ' ansible_ssh_user=' + d.username + ' ansible_ssh_private_key_file=' + private_key_file_path + ' ansible_user=manager ansible_become=yes\n')

        file.close()
        subprocess.run(['/bin/bash', 'workdir/cmd/ansibleLoggingCmd.sh'], stdout=subprocess.PIPE)

        for d in deploymentsetups:
            with open('workdir/log/out/' + d.server_id) as jsonfile:
                parsed = json.load(jsonfile)
                data = parsed.get('ansible_facts')

            if (data['ansible_devices'].get('xvda', 0) != 0):
                size_disk_gb = (data['ansible_devices']['xvda']['partitions']['xvda1']['size'])[:-6]
            elif (data['ansible_devices'].get('vda', 0) != 0):
                size_disk_gb = (data['ansible_devices']['vda']['partitions']['vda1']['size'])[:-6]
            else:
                size_disk_gb = 0
            deployment = Deployment.objects.get(deployment_id=d.deployment_id)
            Logging.objects.update_or_create(
                deployment_id=d.deployment_id,
                defaults={
                    'deployment_id': d.deployment_id,
                    'deployment_number': deployment.deployment_number,
                    'server_id': d.server_id,
                    'ipaddress': d.ipaddress,
                    'applications': deployment.applications,
                    'tags': deployment.tags,
                    'products': deployment.products,
                    'macaddress': data['ansible_default_ipv4']['macaddress'],
                    'hostname': data['ansible_hostname'],
                    'architecture': data['ansible_architecture'],
                    'num_cpu_processors': data['ansible_processor_vcpus'],
                    'num_cpu_cores': data['ansible_processor_cores'],
                    'num_cpu_logical_cores': data['ansible_processor_vcpus'],
                    'os_name': data['ansible_distribution'],
                    'os_version': data['ansible_distribution_version'],
                    'size_ram_mb': data['ansible_memory_mb']['real']['total'],
                    'size_disk_gb': size_disk_gb,
                },
            )

        subprocess.call('rm -rf workdir/log/keys/*', shell=True)
        subprocess.call('rm -rf workdir/log/out/*', shell=True)
        subprocess.call(['rm', '-f', 'workdir/log/config/sms_log.txt'])

        app = Appsetup.objects.first()
        url = settings.SMS_API + 'logging'
        loggings = serializers.serialize('json', Logging.objects.all())
        headers = {'content-type': 'application/json'}
        # print(json.dumps({'account_id': app.account_id, 'application_key': app.application_key, 'application_secret': app.application_secret, 'loggings': loggings}))
        response = requests.post(url, data=json.dumps({'account_id': app.account_id, 'application_key': app.application_key, 'application_secret': app.application_secret, 'loggings': loggings}), headers=headers, verify=False)
        data = response.json()
        # print(data)
        if data['Message'] == 'Success':
            print('Logging successful')
        else:
            print('Logging error')