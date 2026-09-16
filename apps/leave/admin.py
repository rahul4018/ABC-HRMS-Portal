from django.contrib import admin

from .models import (
    Leave,
    LeaveBalance,
    Holiday
)

admin.site.register(Leave)
admin.site.register(LeaveBalance)
admin.site.register(Holiday)