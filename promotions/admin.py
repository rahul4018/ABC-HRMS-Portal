from django.contrib import admin

from .models import Promotion


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):

    list_display = (
        'employee',
        'old_designation',
        'new_designation',
        'effective_date',
    )