from django.contrib import admin
from django.urls import path, include

from apps.dashboard.views import dashboard_view
from apps.accounts.views import (
    login_view,
    logout_view,
)

urlpatterns = [

    # Admin
    path(
        'admin/',
        admin.site.urls
    ),

    # Authentication
    path(
        'login/',
        login_view,
        name='login'
    ),

    path(
        'logout/',
        logout_view,
        name='logout'
    ),

    # Dashboard
    path(
        '',
        dashboard_view,
        name='dashboard'
    ),

    # Employee Module
    path(
        '',
        include('apps.employees.urls')
    ),
]