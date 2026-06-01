from django.contrib import admin

from .models import PMR


@admin.register(PMR)
class PMRAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'employee',
        'status',
        'submitted_date',
    )

    list_filter = (
        'status',
    )