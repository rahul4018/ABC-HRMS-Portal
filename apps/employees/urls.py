from django.urls import path

from .views import (
    employee_list,
    add_employee,
    my_profile,
)

urlpatterns = [

    path(
        'employees/',
        employee_list,
        name='employee_list'
    ),

    path(
        'employees/add/',
        add_employee,
        name='add_employee'
    ),

    path(
        'my-profile/',
        my_profile,
        name='my_profile'
    ),
]