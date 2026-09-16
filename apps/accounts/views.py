from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    login,
    logout,
    get_user_model,
)
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect

from .models import CompanySettings
from apps.employees.models import (
    Employee,
    Department,
    Announcement,
)
from apps.leave.models import Leave


User = get_user_model()


def _submitted_user_id(request):
    return (
        request.POST.get("username")
        or request.POST.get("user_id")
        or request.POST.get("email")
        or ""
    ).strip()


def _profile_status(employee):
    """
    Return the employee onboarding status.

    Older Employee rows created before the onboarding fields existed are
    treated as PROFILE_PENDING so they go through the same setup flow.
    """
    if not employee:
        return None

    return getattr(
        employee,
        "profile_status",
        "PROFILE_PENDING",
    ) or "PROFILE_PENDING"


def _redirect_after_login(user):
    """
    Centralize the post-login onboarding flow.

    Master Admin has no Employee record and therefore goes directly
    to the dashboard.

    Employees/Founders/HR with a pending employee profile are sent
    through the mandatory profile setup before normal dashboard access.
    """
    if getattr(user, "must_change_password", False):
        return redirect("change_password")

    employee = Employee.objects.filter(
        user=user
    ).first()

    if employee:
        profile_status = _profile_status(employee)

        if profile_status == "PROFILE_PENDING":
            return redirect("my_profile_edit")

        if profile_status in {
            "PROFILE_SUBMITTED",
            "HR_REVIEW",
        }:
            messages.info(
                None,
                "Your profile has been submitted and is waiting for HR approval.",
            )
            return redirect("my_profile")

    return redirect("dashboard")


def login_view(request):
    if request.user.is_authenticated:
        if getattr(
            request.user,
            "must_change_password",
            False,
        ):
            return redirect("change_password")

        employee = Employee.objects.filter(
            user=request.user
        ).first()

        if employee:
            profile_status = _profile_status(employee)

            if profile_status == "PROFILE_PENDING":
                return redirect("my_profile_edit")

            if profile_status in {
                "PROFILE_SUBMITTED",
                "HR_REVIEW",
            }:
                return redirect("my_profile")

        return redirect("dashboard")

    if request.method == "POST":
        username = _submitted_user_id(request)
        password = request.POST.get("password", "")

        if not username:
            messages.error(
                request,
                "Please enter your User ID.",
            )
            return render(
                request,
                "accounts/login.html",
            )

        if not password:
            messages.error(
                request,
                "Please enter your password.",
            )
            return render(
                request,
                "accounts/login.html",
            )

        # Resolve case-insensitively, then authenticate with the real
        # stored username so ABC19 / ABC19 both work.
        account = User.objects.filter(
            username__iexact=username
        ).first()

        if account is None:
            messages.error(
                request,
                "Invalid User ID or password.",
            )
            return render(
                request,
                "accounts/login.html",
            )

        user = authenticate(
            request,
            username=account.username,
            password=password,
        )

        if user is None:
            messages.error(
                request,
                "Invalid User ID or password.",
            )
            return render(
                request,
                "accounts/login.html",
            )

        if not user.is_active:
            messages.error(
                request,
                "This account is inactive. Please contact HR or the administrator.",
            )
            return render(
                request,
                "accounts/login.html",
            )

        login(request, user)

        # Temporary/first-login password flow.
        if getattr(
            user,
            "must_change_password",
            False,
        ):
            return redirect("change_password")

        employee = Employee.objects.filter(
            user=user
        ).first()

        if employee:
            profile_status = _profile_status(employee)

            if profile_status == "PROFILE_PENDING":
                messages.info(
                    request,
                    "Please complete your employee profile before continuing.",
                )
                return redirect("my_profile_edit")

            if profile_status in {
                "PROFILE_SUBMITTED",
                "HR_REVIEW",
            }:
                messages.info(
                    request,
                    "Your profile is waiting for HR approval.",
                )
                return redirect("my_profile")

        return redirect("dashboard")

    return render(
        request,
        "accounts/login.html",
    )


@login_required
def change_password(request):
    """
    Change password and force a fresh login after success.

    Required fields:
        old_password
        new_password
        confirm_password
    """

    if request.method == "POST":
        old_password = request.POST.get(
            "old_password",
            "",
        )
        new_password = request.POST.get(
            "new_password",
            "",
        )
        confirm_password = request.POST.get(
            "confirm_password",
            "",
        )

        if not old_password:
            messages.error(
                request,
                "Please enter your old password.",
            )
            return render(
                request,
                "accounts/change_password.html",
            )

        if not request.user.check_password(old_password):
            messages.error(
                request,
                "Old password is incorrect.",
            )
            return render(
                request,
                "accounts/change_password.html",
            )

        if not new_password:
            messages.error(
                request,
                "Please enter a new password.",
            )
            return render(
                request,
                "accounts/change_password.html",
            )

        if len(new_password) < 8:
            messages.error(
                request,
                "New password must contain at least 8 characters.",
            )
            return render(
                request,
                "accounts/change_password.html",
            )

        if new_password != confirm_password:
            messages.error(
                request,
                "New password and confirm password do not match.",
            )
            return render(
                request,
                "accounts/change_password.html",
            )

        if new_password == old_password:
            messages.error(
                request,
                "New password must be different from old password.",
            )
            return render(
                request,
                "accounts/change_password.html",
            )

        request.user.set_password(new_password)
        request.user.must_change_password = False
        request.user.save(
            update_fields=[
                "password",
                "must_change_password",
            ]
        )

        # Force a fresh authentication with the new password.
        logout(request)

        messages.success(
            request,
            "Password changed successfully. Please login with your new password.",
        )

        return redirect("login")

    return render(
        request,
        "accounts/change_password.html",
    )


def forgot_password(request):
    """
    No-email recovery flow.

    A public reset must not reveal or generate credentials.
    The user is directed to HR / Master Admin for an authorised reset.
    """

    if request.method == "POST":
        username = _submitted_user_id(request)

        if not username:
            messages.error(
                request,
                "Please enter your User ID.",
            )
            return render(
                request,
                "accounts/forgot_password.html",
            )

        account = User.objects.filter(
            username__iexact=username
        ).first()

        if account is None:
            messages.error(
                request,
                "No account was found with that User ID.",
            )
            return render(
                request,
                "accounts/forgot_password.html",
            )

        messages.success(
            request,
            "Your account was found. Please contact HR or the Master Admin for a password reset.",
        )

        return render(
            request,
            "accounts/forgot_password.html",
        )

    return render(
        request,
        "accounts/forgot_password.html",
    )


@login_required
def dashboard_view(request):
    """
    Application dashboard entry point.

    Employees must complete/submit their profile before they can
    access their normal dashboard. HR review states are also held
    on the profile page until approval.
    """
    access_role = getattr(
        request.user,
        "access_role",
        "EMPLOYEE",
    )

    employee = Employee.objects.filter(
        user=request.user
    ).first()

    if employee:
        profile_status = _profile_status(employee)

        if profile_status == "PROFILE_PENDING":
            messages.info(
                request,
                "Please complete your employee profile before accessing the dashboard.",
            )
            return redirect("my_profile_edit")

        if profile_status in {
            "PROFILE_SUBMITTED",
            "HR_REVIEW",
        }:
            messages.info(
                request,
                "Your employee profile is waiting for HR approval.",
            )
            return redirect("my_profile")

    if access_role in {
        "MASTER_ADMIN",
        "FOUNDER",
        "HR",
    }:
        context = {
            "total_employees": Employee.objects.count(),
            "pending_leaves": Leave.objects.filter(
                status="PENDING"
            ).count(),
            "total_departments": Department.objects.count(),
            "total_announcements": Announcement.objects.count(),
            "access_role": access_role,
        }

        return render(
            request,
            "dashboard/supervisor.html",
            context,
        )

    employee_leaves = 0

    if employee:
        employee_leaves = Leave.objects.filter(
            employee=employee
        ).count()

    return render(
        request,
        "dashboard/employee.html",
        {
            "employee": employee,
            "employee_leaves": employee_leaves,
            "access_role": access_role,
        },
    )


@login_required
def company_settings(request):
    access_role = getattr(
        request.user,
        "access_role",
        "EMPLOYEE",
    )

    if access_role not in {
        "MASTER_ADMIN",
        "FOUNDER",
        "HR",
    }:
        raise PermissionDenied(
            "You do not have permission to access company settings."
        )

    settings_obj = CompanySettings.objects.first()

    if not settings_obj:
        settings_obj = CompanySettings.objects.create(
            company_name="ABC HRMS Portal",
            company_address=(
                "Demo Corporate Office, India"
            ),
            company_email="hr@ABC HRMS Portal.com",
            company_phone="+91 1234567890",
        )

    if request.method == "POST":
        settings_obj.company_name = (
            request.POST.get("company_name") or ""
        ).strip()

        settings_obj.company_address = (
            request.POST.get("company_address") or ""
        ).strip()

        settings_obj.company_email = (
            request.POST.get("company_email") or ""
        ).strip()

        settings_obj.company_phone = (
            request.POST.get("company_phone") or ""
        ).strip()

        if request.FILES.get("company_logo"):
            settings_obj.company_logo = request.FILES[
                "company_logo"
            ]

        settings_obj.save()

        messages.success(
            request,
            "Company settings updated successfully.",
        )

        return redirect("company_settings")

    return render(
        request,
        "settings/company.html",
        {
            "settings_obj": settings_obj,
            "access_role": access_role,
        },
    )


def terms_view(request):
    return render(
        request,
        "legal/terms.html",
    )


def privacy_view(request):
    return render(
        request,
        "legal/privacy.html",
    )


def logout_view(request):
    logout(request)
    return redirect("login")
