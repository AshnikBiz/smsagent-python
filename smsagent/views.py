from django.shortcuts import get_object_or_404, redirect, render
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
import requests
import json
import subprocess
from .forms import AppsetupForm, DeploymentsetupForm
from .models import Appsetup, Sshkey, Deployment, Deploymentsetup, Logging
from django.forms import ModelForm


class SshkeyForm(ModelForm):
    class Meta:
        model = Sshkey
        fields = ['name', 'content']


# Create your views here.
def home(request):
    return render(request, "home.html", {})


@login_required
def appsetup(request):
    app = Appsetup.objects.first()
    if request.method == 'POST':
        form = AppsetupForm(request.POST, instance=app)
        if form.is_valid():
            app = form.save()
            url = settings.SMS_API + 'validateapp'
            headers = {'content-type': 'application/json'}
            payload = {'account_id': app.account_id, 'application_key': app.application_key, 'application_secret': app.application_secret}
            response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
            data = response.json()
            if data['Message'] == 'Success':
                return render(request, 'appsetupform.html', {'form': form, 'status': 'success', 'message': 'Application setup successful'})
            else:
                return render(request, 'appsetupform.html', {'form': form, 'status': 'error', 'message': 'Application setup credentials do not match'})
        else:
            return render(request, 'appsetupform.html', {'form': form, 'status': 'error', 'message': 'There was an error'})
    else:
        form = AppsetupForm(instance=app)
        return render(request, 'appsetupform.html', {'form': form})


@login_required
def sshkeys(request, template_name='sshkeys.html'):
    sshkeys = Sshkey.objects.all()
    data = {}
    data['object_list'] = sshkeys
    return render(request, template_name, data)


@login_required
def sshkey_view(request, pk, template_name='sshkeysetupform.html'):
    sshkey = get_object_or_404(Sshkey, pk=pk)
    return render(request, template_name, {'object': sshkey})


@login_required
def sshkey_create(request, template_name='sshkeysetupform.html'):
    form = SshkeyForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('sshkeys')
    return render(request, template_name, {'form': form})


@login_required
def sshkey_update(request, pk, template_name='sshkeysetupform.html'):
    sshkey = get_object_or_404(Sshkey, pk=pk)
    form = SshkeyForm(request.POST or None, instance=sshkey)
    if form.is_valid():
        form.save()
        return redirect('sshkeys')
    return render(request, template_name, {'form': form})


@login_required
def sshkey_delete(request, pk, template_name='sshkeydeleteform.html'):
    sshkey = get_object_or_404(Sshkey, pk=pk)
    if request.method == 'POST':
        sshkey.delete()
        return redirect('sshkeys')
    return render(request, template_name, {'object':sshkey})


@login_required
def deployments(request):
    app = Appsetup.objects.first()
    if app:
        url = settings.SMS_API + 'deployments'
        headers = {'content-type': 'application/json'}
        payload = {'account_id': app.account_id, 'application_key': app.application_key, 'application_secret': app.application_secret}
        response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
        data = response.json()
        if data['Message'] == 'Success':
            deployments = data['Data']
            for deployment in deployments:
                Deployment.objects.update_or_create(
                    deployment_id=deployment['slug'],
                    defaults={
                        'deployment_id': deployment['slug'],
                        'deployment_number': deployment['deployment_number'],
                        'deployment_text': deployment,
                        'applications': deployment['applications'],
                        'tags': deployment['tags'],
                        'products': deployment['fulfillments']['productsubscriptions']['products']['name'],
                        'server_id': deployment['server_id'],
                    },
                )

            return render(request, 'deployments.html', {'deployments': Deployment.objects.all(), 'deploymentsetups': Deploymentsetup.objects.values_list('deployment_id', flat=True)})
        else:
            return redirect('/appsetup/')

    else:
        return redirect('/appsetup/')


@login_required
def deploymentsetup(request, deployment_id):
    deployment = get_object_or_404(Deployment, deployment_id=deployment_id)
    if request.method == 'POST':
        form = DeploymentsetupForm(request.POST)
        if form.is_valid():
            try:
                deploymentsetup = Deploymentsetup.objects.get(deployment_id=deployment.deployment_id)
                deploymentsetup = form.save(commit=False)
                deploymentsetup.deployment_id = deployment.deployment_id
                deploymentsetup.server_id = deployment.server_id
                deploymentsetup.save()
                return render(request, 'deploymentsetupform.html', {'deployment': deployment, 'deploymentsetup_id': deploymentsetup.deployment_id, 'form': form, 'status': 'success', 'message': 'Deployment setup saved'})
            except ObjectDoesNotExist:
                deploymentsetup = form.save(commit=False)
                deploymentsetup.deployment_id = deployment.deployment_id
                deploymentsetup.server_id = deployment.server_id
                deploymentsetup.save()
                return render(request, 'deploymentsetupform.html', {'deployment': deployment, 'deploymentsetup_id': deploymentsetup.deployment_id, 'form': form, 'status': 'success', 'message': 'Deployment setup saved'})
        else:
            return render(request, 'deploymentsetupform.html', {'deployment': deployment, 'deploymentsetup_id': '', 'form': form, 'status': 'error', 'message': 'There was an error'})
    else:
        try:
            deploymentsetup = Deploymentsetup.objects.get(deployment_id=deployment.deployment_id)
            form = DeploymentsetupForm(instance=deploymentsetup)
            return render(request, 'deploymentsetupform.html', {'deployment': deployment, 'deploymentsetup_id': deploymentsetup.deployment_id, 'form': form})
        except ObjectDoesNotExist:
            form = DeploymentsetupForm()
            return render(request, 'deploymentsetupform.html', {'deployment': deployment, 'deploymentsetup_id': '', 'form': form})


@login_required
def connect(request):
    deployment_id = request.GET['deployment_id']
    d = Deploymentsetup.objects.get(deployment_id=deployment_id)

    sshkey = Sshkey.objects.get(id=d.ssh_key_id)
    private_key_file_path = 'workdir/test/keys/' + sshkey.name
    file = open(private_key_file_path, 'w')
    file.write(sshkey.content)
    file.close()
    subprocess.call(['chmod', '0600', private_key_file_path])

    file = open('workdir/test/config/sms_connection_test.txt', 'w')
    file.write('[sms_connection_test]\n') 
    file.write(d.server_id + ' ansible_host=' + d.ipaddress + ' ansible_port=' + str(d.port) + ' ansible_ssh_user=' + d.username + ' ansible_ssh_private_key_file=' + private_key_file_path + ' ansible_user=manager ansible_become=yes')
    file.close()

    subprocess.run(['/bin/bash', 'workdir/cmd/ansibleConnectionTestCmd.sh'], stdout=subprocess.PIPE)
    with open('workdir/test/out/' + d.server_id) as jsonfile:
        parsed = json.load(jsonfile)

    subprocess.call(['rm', '-f', private_key_file_path])
    subprocess.call('rm -rf workdir/test/out/*', shell=True)
    subprocess.call(['rm', '-f', 'workdir/test/config/sms_connection_test.txt'])

    status = parsed.get('ping', 'unreachable')
    if (status == 'unreachable'):
        return HttpResponse(json.dumps({'status': 'error', 'message': 'Could not connect to host'}))
    else:
        return HttpResponse(json.dumps({'status': 'success', 'message': 'Host connection successful'}))


@login_required
def initiatelogging(request):
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

    return redirect('/logging/')


@login_required
def logging(request):
    loggings = Logging.objects.all()
    return render(request, 'loggings.html', {'loggings': loggings})
