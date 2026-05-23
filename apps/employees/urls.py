from django.urls import path

from .views import (
    employee_list,
    employee_detail,
    employee_add,
    employee_edit,
    employee_delete,
    my_profile,

    department_list,
    department_add,
    department_edit,
    department_delete,

    payslip_list,
    payslip_detail,
)

urlpatterns = [

    # ==========================================
    # EMPLOYEE URLS
    # ==========================================

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

    # ==========================================
    # PROFILE
    # ==========================================

    path(
        'my-profile/',
        my_profile,
        name='my_profile'
    ),

    # ==========================================
    # DEPARTMENT URLS
    # ==========================================

    path(
        'departments/',
        department_list,
        name='department_list'
    ),

    path(
        'departments/add/',
        department_add,
        name='add_department'
    ),

    path(
        'departments/<int:pk>/edit/',
        department_edit,
        name='edit_department'
    ),

    path(
        'departments/<int:pk>/delete/',
        department_delete,
        name='delete_department'
    ),

    # ==========================================
    # PAYSLIP URLS
    # ==========================================

    path(
        'payslips/',
        payslip_list,
        name='payslip_list'
    ),

    path(
        'payslips/<int:pk>/',
        payslip_detail,
        name='payslip_detail'
    ),

]