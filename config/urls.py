from django.contrib import admin

from django.urls import (
    path,
    include,
)

from django.conf import settings

from django.conf.urls.static import static

from apps.dashboard.views import (
    dashboard_view,
)

from apps.accounts.views import (
    login_view,
    logout_view,
)

urlpatterns = [

    # ==========================================
    # Admin Panel
    # ==========================================

    path(
        'admin/',
        admin.site.urls
    ),

    # ==========================================
    # Authentication
    # ==========================================

    path(
        'login/',
        login_view,
        name='login'
    ),

    path(
        'logout/',
        logout_view,
        name='logout'
    ),

    # ==========================================
    # Dashboard
    # ==========================================

    path(
        '',
        dashboard_view,
        name='dashboard'
    ),

    # ==========================================
    # Employee + Department Module
    # ==========================================

    path(
        '',
        include(
            'apps.employees.urls'
        )
    ),

    # ==========================================
    # Leave Management Module
    # ==========================================

    path(
        'leave/',
        include(
            'apps.leave.urls'
        )
    ),

]

# ==========================================
# Media Files
# ==========================================

if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )