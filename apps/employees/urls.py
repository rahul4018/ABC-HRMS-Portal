from django.urls import path

from .views import (
    employee_list,
    employee_detail,
    employee_add,
    employee_edit,
    employee_delete,
)

urlpatterns = [

    path(
        '',
        employee_list,
        name='employee_list'
    ),

    path(
        'add/',
        employee_add,
        name='employee_add'
    ),

    path(
        '<int:pk>/',
        employee_detail,
        name='employee_detail'
    ),

    path(
        '<int:pk>/edit/',
        employee_edit,
        name='employee_edit'
    ),

    path(
        '<int:pk>/delete/',
        employee_delete,
        name='employee_delete'
    ),
]