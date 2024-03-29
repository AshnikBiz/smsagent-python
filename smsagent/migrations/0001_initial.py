# Generated by Django 2.2.5 on 2019-09-30 03:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Appsetup',
            fields=[
                ('account_id', models.CharField(max_length=64, primary_key=True, serialize=False)),
                ('application_key', models.CharField(max_length=64)),
                ('application_secret', models.CharField(max_length=64)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Deployment',
            fields=[
                ('deployment_id', models.CharField(max_length=64, primary_key=True, serialize=False)),
                ('deployment_number', models.CharField(max_length=20)),
                ('deployment_text', models.TextField()),
                ('applications', models.CharField(max_length=255)),
                ('tags', models.CharField(max_length=255)),
                ('products', models.CharField(max_length=255)),
                ('server_id', models.CharField(max_length=255)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Logging',
            fields=[
                ('deployment_id', models.CharField(max_length=64, primary_key=True, serialize=False)),
                ('deployment_number', models.CharField(max_length=20)),
                ('server_id', models.CharField(max_length=255)),
                ('ipaddress', models.CharField(max_length=16)),
                ('applications', models.CharField(max_length=255)),
                ('tags', models.CharField(max_length=255)),
                ('products', models.CharField(max_length=255)),
                ('macaddress', models.CharField(max_length=255)),
                ('hostname', models.CharField(max_length=255)),
                ('architecture', models.CharField(max_length=255)),
                ('num_cpu_processors', models.PositiveIntegerField()),
                ('num_cpu_cores', models.PositiveIntegerField()),
                ('num_cpu_logical_cores', models.PositiveIntegerField()),
                ('os_name', models.CharField(max_length=255)),
                ('os_version', models.CharField(max_length=255)),
                ('size_ram_mb', models.PositiveIntegerField()),
                ('size_disk_gb', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Sshkey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('content', models.TextField()),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Deploymentsetup',
            fields=[
                ('deployment_id', models.CharField(max_length=64, primary_key=True, serialize=False)),
                ('server_id', models.CharField(max_length=255)),
                ('ipaddress', models.CharField(max_length=16)),
                ('port', models.PositiveIntegerField(default=22)),
                ('username', models.CharField(max_length=255)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('ssh_key', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='smsagent.Sshkey')),
            ],
        ),
    ]
