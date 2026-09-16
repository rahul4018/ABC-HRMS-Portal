from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from apps.accounts.views import (
    change_password,
    login_view,
    logout_view,
    forgot_password,
    company_settings,
)

from apps.dashboard.views import dashboard

from apps.employees.views import (
    my_profile,
    global_search,
)


urlpatterns = [

    # =====================================================
    # PASSWORD MANAGEMENT
    # =====================================================

    path(
        'change-password/',
        change_password,
        name='change_password',
    ),

    # =====================================================
    # DJANGO ADMIN
    # =====================================================

    path(
        'admin/',
        admin.site.urls,
    ),

    # =====================================================
    # AUTHENTICATION
    # =====================================================

    path(
        'login/',
        login_view,
        name='login',
    ),

    path(
        'logout/',
        logout_view,
        name='logout',
    ),

    path(
        'forgot-password/',
        forgot_password,
        name='forgot_password',
    ),

    # =====================================================
    # ROOT
    # =====================================================
    #
    # No corporate landing page.
    #
    # Opening:
    #   http://127.0.0.1:8000/
    #
    # opens the same login screen as /login/.
    # =====================================================

    path(
        '',
        login_view,
        name='root_login',
    ),

    # =====================================================
    # AUTHENTICATED DASHBOARD
    # =====================================================

    path(
        'dashboard/',
        dashboard,
        name='dashboard',
    ),

    # =====================================================
    # JWT AUTHENTICATION
    # =====================================================

    path(
        'api/token/',
        TokenObtainPairView.as_view(),
        name='token_obtain_pair',
    ),

    path(
        'api/token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh',
    ),

    # =====================================================
    # REST API
    # =====================================================

    path(
        'api/',
        include('api.urls'),
    ),

    # =====================================================
    # EMPLOYEE MANAGEMENT
    # =====================================================

    path(
        'employees/',
        include('apps.employees.urls'),
    ),

    # =====================================================
    # DEPARTMENTS
    # =====================================================

    path(
        'departments/',
        include('apps.employees.department_urls'),
    ),

    # =====================================================
    # ATTENDANCE
    # =====================================================

    path(
        'attendance/',
        include('apps.employees.attendance_urls'),
    ),

    # =====================================================
    # PAYSLIPS
    # =====================================================

    path(
        'payslips/',
        include('apps.employees.payslip_urls'),
    ),

    # =====================================================
    # REPORTS
    # =====================================================

    path(
        'reports/',
        include('apps.employees.report_urls'),
    ),

    # =====================================================
    # DOCUMENTS
    # =====================================================

    path(
        'documents/',
        include('apps.employees.document_urls'),
    ),

    # =====================================================
    # MY PROFILE
    # =====================================================

    path(
        'my-profile/',
        my_profile,
        name='my_profile',
    ),

    # =====================================================
    # LEAVE
    # =====================================================

    path(
        'leave/',
        include('apps.leave.urls'),
    ),

    # =====================================================
    # RESIGNATION
    # =====================================================

    path(
        'resignation/',
        include('resignation.urls'),
    ),

    # =====================================================
    # APPRAISAL / PMR
    # =====================================================

    path(
        'appraisal/',
        include('appraisal.urls'),
    ),

    # =====================================================
    # PROMOTIONS
    # =====================================================

    path(
        'promotions/',
        include('promotions.urls'),
    ),

    # =====================================================
    # COMPANY SETTINGS
    # =====================================================

    path(
        'settings/',
        company_settings,
        name='company_settings',
    ),

    # =====================================================
    # NOTIFICATIONS
    # =====================================================

    path(
        'notifications/',
        include('notifications.urls'),
    ),

    # =====================================================
    # RECRUITMENT
    # =====================================================

    path(
        'recruitment/',
        include('recruitment.urls'),
    ),

    # =====================================================
    # AUDIT
    # =====================================================

    path(
        'audit/',
        include('audit.urls'),
    ),

    # =====================================================
    # GLOBAL SEARCH
    # =====================================================

    path(
        'search/',
        global_search,
        name='global_search',
    ),
    path('workforce/', include('apps.workforce.urls')),
]


# =========================================================
# MEDIA FILES - DEVELOPMENT
# =========================================================

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )