from django.contrib import admin
from .models import Attendance

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
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):

    list_display = (
        'employee',
        'date',
        'status',
        'check_in',
        'check_out',
    )

    list_filter = (
        'status',
        'date',
    )

    search_fields = (
        'employee__employee_id',
        'employee__user__email',
    )