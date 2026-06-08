from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.accounts.views import login_view, logout_view, forgot_password, company_settings
from apps.dashboard.views import dashboard
from apps.employees.views import my_profile
from apps.employees.views import global_search

urlpatterns = [
    # Admin Interface
    path("admin/", admin.site.urls),

    # Authentication & Session Management
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("forgot-password/", forgot_password, name="forgot_password"),

    # Application Dashboard
    path("", dashboard, name="dashboard"),

    # SimpleJWT API Authentication Endpoints
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # REST Framework Modular API Inclusion
    path("api/", include("api.urls")),

    # HR Core Module Routers (Employees, Departments, Attendance, Payslips, Reports, Documents)
    path("employees/", include("apps.employees.urls")),
    path("departments/", include("apps.employees.department_urls")),
    path("attendance/", include("apps.employees.attendance_urls")),
    path("payslips/", include("apps.employees.payslip_urls")),
    path("reports/", include("apps.employees.report_urls")),
    path("documents/", include("apps.employees.document_urls")),
    
    # User Profile Settings Shortcut
    path("my-profile/", my_profile, name="my_profile"),

    # Operational Sub-Modules (Leave, Resignation, Performance, Promotions, Recruitment, Alerts)
    path("leave/", include("apps.leave.urls")),
    path("resignation/", include("resignation.urls")),
    path("appraisal/", include("appraisal.urls")),
    path("promotions/", include("promotions.urls")),
    path("settings/", company_settings, name="company_settings"),
    path("notifications/", include("notifications.urls")),
    path("recruitment/", include("recruitment.urls")),
    path('audit/',include('audit.urls')),
    path("search/", global_search, name="global_search"),
]

# Serve User-Uploaded Media Files During Local Sandbox Development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)