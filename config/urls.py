from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.accounts.views import company_settings

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.urls import path, include
from apps.dashboard.views import dashboard
from apps.accounts.views import login_view, logout_view
from apps.employees.views import my_profile


urlpatterns = [

    # Admin
    path("admin/", admin.site.urls),

    # Authentication
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),

    # JWT Authentication
    path(
        "api/token/",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair"
    ),

    path(
        "api/token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh"
    ),

    # API
    path("api/", include("api.urls")),

    # Dashboard
    path("", dashboard, name="dashboard"),

    # Employees
    path(
        "employees/",
        include("apps.employees.urls")
    ),

    # Departments
    path(
        "departments/",
        include("apps.employees.department_urls")
    ),

    # Attendance
    path(
        "attendance/",
        include("apps.employees.attendance_urls")
    ),

    # Payslips
    path(
        "payslips/",
        include("apps.employees.payslip_urls")
    ),

    # Reports
    path(
        "reports/",
        include("apps.employees.report_urls")
    ),

    # Profile
    path(
        "my-profile/",
        my_profile,
        name="my_profile"
    ),

    # Leave Management System
    path(
        "leave/",
        include("apps.leave.urls")
    ),

    # Document Management System
    path(
        "documents/",
        include("apps.employees.document_urls")
    ),

    # Resignation
    path(
        "resignation/",
        include("resignation.urls")
    ),

    # PMR / Appraisal
    path(
        "appraisal/",
        include("appraisal.urls")
    ),
    path(
    "promotions/",
    include("promotions.urls")
),
path(
    "settings/",
    company_settings,
    name="company_settings"
),
path(
    'notifications/',
    include('notifications.urls')
),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )