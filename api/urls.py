from django.urls import path

from .views import employee_api


urlpatterns = [

    path(
        'employees/',
        employee_api,
        name='employee_api'
    ),

]