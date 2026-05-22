from django.urls import path

from .views import (
    employee_list,
    my_profile,
)

urlpatterns = [

    path(
        'employees/',
        employee_list,
        name='employee_list'
    ),

    path(
        'my-profile/',
        my_profile,
        name='my_profile'
    ),
]