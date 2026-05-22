from django.contrib import admin

from .models import (
    Department,
    Employee,
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
    )


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):

    list_display = (
        'employee_id',
        'user',
        'department',
        'designation',
        'status',
    )

    list_filter = (
        'department',
        'status',
    )

    search_fields = (
        'employee_id',
        'user__email',
        'designation',
    )