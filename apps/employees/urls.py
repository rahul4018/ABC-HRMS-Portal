from django.urls import path

from apps.employees.views import (
    employee_list,
    employee_profile,
    add_employee,
    edit_employee,
    delete_employee,
)

urlpatterns = [

    path(
        '',
        employee_list,
        name='employee_list'
    ),

    path(
        'add/',
        add_employee,
        name='add_employee'
    ),

    path(
        'profile/',
        employee_profile,
        name='employee_profile'
    ),

    path(
        'edit/<int:employee_id>/',
        edit_employee,
        name='edit_employee'
    ),

    path(
        'delete/<int:employee_id>/',
        delete_employee,
        name='delete_employee'
    ),

]