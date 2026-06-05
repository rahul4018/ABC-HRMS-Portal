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
    employee = Employee.objects.filter(user=request.user).first()

    if not employee:
        messages.error(request, "Employee profile not found.")
        return redirect("pmr_list")

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        achievements = request.POST.get("achievements", "").strip()
        goals = request.POST.get("goals", "").strip()

        if not title or not achievements or not goals:
            messages.error(request, "All fields are required.")
            return redirect("pmr_create")

        PMR.objects.create(
            employee=employee,
            title=title,
            achievements=achievements,
            goals=goals,
            status="PENDING"
        )

        # Send automatic notifications to all supervisors
        supervisors = User.objects.filter(role='SUPERVISOR')
        for supervisor in supervisors:
            create_notification(
                supervisor,
                'New PMR Submitted',
                f'{employee.user.email} submitted a PMR.'
            )

        messages.success(request, "PMR submitted successfully.")
        return redirect("pmr_list")

    return render(request, "appraisal/create.html")


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