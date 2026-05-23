from django.urls import path

from apps.employees.views import (
    reports_dashboard,
)

urlpatterns = [

    path(
        '',
        reports_dashboard,
        name='reports_dashboard'
    ),

]