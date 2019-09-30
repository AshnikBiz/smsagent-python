"""sms URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from smsagent import views


urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^login/$', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(), {'next_page': '/'}, name='logout'),

    url(r'^reset/$',
        auth_views.PasswordResetView.as_view(
            template_name='password_reset.html',
            email_template_name='password_reset_email.html',
            subject_template_name='password_reset_subject.txt'
        ),
        name='password_reset'),
    url(r'^reset/done/$',
        auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'),
        name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
        name='password_reset_confirm'),
    url(r'^reset/complete/$',
        auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
        name='password_reset_complete'),

    url(r'^settings/password/$', auth_views.PasswordChangeView.as_view(template_name='password_change.html'),
        name='password_change'),
    url(r'^settings/password/done/$', auth_views.PasswordChangeDoneView.as_view(template_name='password_change_done.html'),
        name='password_change_done'),

    url(r'^admin/', admin.site.urls),

    path('appsetup/', views.appsetup, name='appsetup'),
    
    path('sshkeys/', views.sshkeys, name='sshkeys'),
    path('sshkeys/view/<int:pk>/', views.sshkey_view, name='sshkey_view'),
    path('sshkeys/new/', views.sshkey_create, name='sshkey_new'),
    path('sshkeys/edit/<int:pk>/', views.sshkey_update, name='sshkey_edit'),
    path('sshkeys/delete/<int:pk>/', views.sshkey_delete, name='sshkey_delete'),
    
    path('deployments/', views.deployments, name='deployments'),
    path('deployment/<uuid:deployment_id>/setup/', views.deploymentsetup, name='deploymentsetup'),
    
    url(r'^deploymentsetup/connect/$', views.connect, name='connect'),
    
    path('logging/initiate/', views.initiatelogging, name='initiatelogging'),
    path('logging/', views.logging, name='logging'),
]
