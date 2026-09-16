from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from apps.employees.models import Employee
from .models import PMR
from notifications.utils import create_notification
from apps.accounts.models import User

@login_required
def pmr_list(request):
    # NOTE: Ensure your Custom User Model actually contains the 'role' field.
    # If role lives on the Employee profile, fetch the employee profile first.
    if hasattr(request.user, 'role') and request.user.role == "SUPERVISOR":
        pmrs = PMR.objects.select_related("employee", "employee__user").all().order_by("-created_at")
    else:
        employee = Employee.objects.filter(user=request.user).first()
        pmrs = PMR.objects.filter(employee=employee).order_by("-created_at") if employee else PMR.objects.none()

    return render(request, "appraisal/list.html", {"pmrs": pmrs})


@login_required
def pmr_create(request):
    """
    HR/Supervisor can create a PMR for any employee.
    Employees can create a PMR only for themselves.
    """

    is_manager = (
        getattr(request.user, "role", None) == "SUPERVISOR"
        or getattr(request.user, "portal_role", None) in {
            "ADMIN",
            "HR",
            "CEO",
            "FOUNDER",
        }
    )

    # -----------------------------------------
    # HR / Management: choose the employee
    # -----------------------------------------
    if is_manager:

        employees = Employee.objects.select_related(
            "user",
            "department"
        ).filter(
            status="ACTIVE"
        ).order_by(
            "employee_id"
        )

    else:

        employee = Employee.objects.filter(
            user=request.user
        ).first()

        if not employee:
            messages.error(
                request,
                "Employee profile not found."
            )

            return redirect("pmr_list")

        employees = Employee.objects.filter(
            pk=employee.pk
        )

    # -----------------------------------------
    # CREATE PMR
    # -----------------------------------------
    if request.method == "POST":

        title = request.POST.get(
            "title",
            ""
        ).strip()

        achievements = request.POST.get(
            "achievements",
            ""
        ).strip()

        goals = request.POST.get(
            "goals",
            ""
        ).strip()

        # HR chooses employee
        if is_manager:

            employee_id = request.POST.get(
                "employee"
            )

            employee = Employee.objects.filter(
                pk=employee_id,
                status="ACTIVE"
            ).first()

        else:

            employee = Employee.objects.filter(
                user=request.user
            ).first()

        # -----------------------------------------
        # Validation
        # -----------------------------------------
        if not employee:

            messages.error(
                request,
                "Please select a valid employee."
            )

            return render(
                request,
                "appraisal/create.html",
                {
                    "employees": employees,
                    "is_manager": is_manager,
                    "title": title,
                    "achievements": achievements,
                    "goals": goals,
                }
            )

        if not title or not achievements or not goals:

            messages.error(
                request,
                "Title, achievements and goals are required."
            )

            return render(
                request,
                "appraisal/create.html",
                {
                    "employees": employees,
                    "is_manager": is_manager,
                    "selected_employee": employee.id,
                    "title": title,
                    "achievements": achievements,
                    "goals": goals,
                }
            )

        # -----------------------------------------
        # Create PMR
        # -----------------------------------------
        PMR.objects.create(
            employee=employee,
            title=title,
            achievements=achievements,
            goals=goals,
            status="PENDING"
        )

        # -----------------------------------------
        # Notify supervisors
        # -----------------------------------------
        supervisors = User.objects.filter(
            role="SUPERVISOR",
            is_active=True
        )

        for supervisor in supervisors:

            create_notification(
                supervisor,
                "New PMR Submitted",
                (
                    f"{employee.user.get_full_name() or employee.user.email} "
                    f"has a new performance review."
                )
            )

        # -----------------------------------------
        # Audit
        # -----------------------------------------
        try:

            create_audit_log(
                request.user,
                "PMR",
                (
                    f"Created performance review for "
                    f"{employee.user.email}"
                )
            )

        except Exception:
            pass

        messages.success(
            request,
            "PMR created successfully."
        )

        return redirect("pmr_list")

    # -----------------------------------------
    # GET
    # -----------------------------------------
    return render(
        request,
        "appraisal/create.html",
        {
            "employees": employees,
            "is_manager": is_manager,
        }
    )

@login_required
def pmr_detail(request, pk):
    pmr = get_object_or_404(PMR, pk=pk)

    # Validate ownership or leadership permissions
    is_supervisor = hasattr(request.user, 'role') and request.user.role == "SUPERVISOR"
    is_owner = pmr.employee.user == request.user

    if not (is_supervisor or is_owner):
        messages.error(request, "Access denied.")
        return redirect("pmr_list")

    return render(request, "appraisal/detail.html", {"pmr": pmr})


@login_required
@require_POST
def pmr_approve(request, pk):
    if not (hasattr(request.user, 'role') and request.user.role == "SUPERVISOR"):
        messages.error(request, "Access denied.")
        return redirect("pmr_list")

    pmr = get_object_or_404(PMR, pk=pk)
    pmr.status = "APPROVED"
    pmr.save()
    
    messages.success(request, "PMR approved successfully.")
    return redirect("pmr_list")


@login_required
@require_POST
def pmr_reject(request, pk):
    if not (hasattr(request.user, 'role') and request.user.role == "SUPERVISOR"):
        messages.error(request, "Access denied.")
        return redirect("pmr_list")

    pmr = get_object_or_404(PMR, pk=pk)
    pmr.status = "REJECTED"
    pmr.save()

    messages.success(request, "PMR rejected successfully.")
    return redirect("pmr_list")


@login_required
@require_POST
def pmr_send_back(request, pk):
    if not (hasattr(request.user, 'role') and request.user.role == "SUPERVISOR"):
        messages.error(request, "Access denied.")
        return redirect("pmr_list")

    pmr = get_object_or_404(PMR, pk=pk)
    pmr.status = "RESUBMIT"
    pmr.save()

    messages.success(request, "PMR sent back successfully.")
    return redirect("pmr_list")