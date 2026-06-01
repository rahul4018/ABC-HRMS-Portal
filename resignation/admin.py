from django.contrib import admin

from .models import Resignation


@admin.register(Resignation)
class ResignationAdmin(admin.ModelAdmin):

    list_display = (
        'employee',
        'status',
        'last_working_day',
        'created_at',
    )

    list_filter = (
        'status',
    )

    search_fields = (
        'employee__employee_id',
    )