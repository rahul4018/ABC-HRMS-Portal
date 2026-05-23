from django.contrib import admin

from django.urls import (
    path,
    include,
)

from django.conf import settings

from django.conf.urls.static import static

from apps.dashboard.views import dashboard

from apps.accounts.views import (
    login_view,
    logout_view,
)

from apps.employees.views import (
    my_profile,
)

urlpatterns = [

    # ==========================================
    # ADMIN
    # ==========================================

    path(
        'admin/',
        admin.site.urls
    ),

    # ==========================================
    # AUTHENTICATION
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
    # DASHBOARD
    # ==========================================

    path(
        '',
        dashboard,
        name='dashboard'
    ),

    # ==========================================
    # EMPLOYEES
    # ==========================================

    path(
        'employees/',
        include(
            'apps.employees.urls'
        )
    ),

    # ==========================================
    # DEPARTMENTS
    # ==========================================

    path(
        'departments/',
        include(
            'apps.employees.department_urls'
        )
    ),

    # ==========================================
    # ATTENDANCE
    # ==========================================

    path(
        'attendance/',
        include(
            'apps.employees.attendance_urls'
        )
    ),

    # ==========================================
    # PAYSLIPS
    # ==========================================

    path(
        'payslips/',
        include(
            'apps.employees.payslip_urls'
        )
    ),

    # ==========================================
    # ANNOUNCEMENTS
    # ==========================================

    path(
        'announcements/',
        include(
            'apps.employees.announcement_urls'
        )
    ),

    # ==========================================
    # REPORTS & ANALYTICS
    # ==========================================

    path(
        'reports/',
        include(
            'apps.employees.report_urls'
        )
    ),

    # ==========================================
    # MY PROFILE
    # ==========================================

    path(
        'my-profile/',
        my_profile,
        name='my_profile'
    ),

    # ==========================================
    # LEAVE MANAGEMENT
    # ==========================================

    path(
        'leave/',
        include(
            'apps.leave.urls'
        )
    ),

]

# ==========================================
# MEDIA FILES
# ==========================================

if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )