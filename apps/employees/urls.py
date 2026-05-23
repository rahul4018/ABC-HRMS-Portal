from django.urls import path

from .views import (
    employee_list,
    employee_detail,
    employee_add,
    employee_edit,
    employee_delete,
    my_profile,
)

urlpatterns = [

    # Employee List
    path(
        'employees/',
        employee_list,
        name='employee_list'
    ),

    # Add Employee
    path(
        'employees/add/',
        employee_add,
        name='employee_add'
    ),

    # Employee Detail
    path(
        'employees/<int:pk>/',
        employee_detail,
        name='employee_detail'
    ),

    # Edit Employee
    path(
        'employees/<int:pk>/edit/',
        employee_edit,
        name='employee_edit'
    ),

    # Delete Employee
    path(
        'employees/<int:pk>/delete/',
        employee_delete,
        name='employee_delete'
    ),

    # My Profile
    path(
        'my-profile/',
        my_profile,
        name='my_profile'
    ),
]