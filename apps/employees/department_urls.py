from django.urls import path

from apps.employees.views import (
    department_list,
    department_add,
    department_edit,
    department_delete,
)

urlpatterns = [

    # ==========================================
    # Department List
    # ==========================================

    path(
        '',
        department_list,
        name='department_list'
    ),

    # ==========================================
    # Add Department
    # ==========================================

    path(
        'add/',
        department_add,
        name='department_add'
    ),

    # ==========================================
    # Edit Department
    # ==========================================

    path(
        '<int:pk>/edit/',
        department_edit,
        name='department_edit'
    ),

    # ==========================================
    # Delete Department
    # ==========================================

    path(
        '<int:pk>/delete/',
        department_delete,
        name='department_delete'
    ),

]