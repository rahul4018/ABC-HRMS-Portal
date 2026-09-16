from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    list_display = (
        'username',
        'first_name',
        'last_name',
        'access_role',
        'role',
        'is_staff',
        'is_superuser',
        'is_active',
    )

    search_fields = (
        'username',
        'first_name',
        'last_name',
        'email',
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            'HRMS Access',
            {
                'fields': (
                    'access_role',
                    'role',
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            'HRMS Access',
            {
                'fields': (
                    'access_role',
                    'role',
                )
            },
        ),
    )
