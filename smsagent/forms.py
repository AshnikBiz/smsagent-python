from django import forms

from .models import Appsetup, Sshkey, Deploymentsetup


class AppsetupForm(forms.ModelForm):
    class Meta:
        model = Appsetup
        fields = ['account_id', 'application_key', 'application_secret']


class SshkeyForm(forms.ModelForm):
    class Meta:
        model = Sshkey
        fields = ['name', 'content']


class DeploymentsetupForm(forms.ModelForm):
    class Meta:
        model = Deploymentsetup
        fields = ['ipaddress', 'port', 'username', 'ssh_key']
