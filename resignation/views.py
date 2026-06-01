from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Resignation
from apps.employees.models import Employee

@login_required
def resignation_list(request):
    # Safely check for role attribute to avoid AttributeError
    user_role = getattr(request.user, "role", None)
    
    if user_role == "SUPERVISOR":
        resignations = Resignation.objects.select_related(
            "employee", 
            "employee__user"
        ).all().order_by("-created_at")
    else:
        employee = Employee.objects.filter(user=request.user).first()
        resignations = Resignation.objects.filter(employee=employee).order_by("-created_at")

    return render(
        request,
        "resignation/list.html",
        {"resignations": resignations}
    )


@login_required
def apply_resignation(request):
    if request.method == "POST":
        employee = Employee.objects.filter(user=request.user).first()

        if not employee:
            messages.error(request, "Employee profile not found.")
            return redirect("resignation_list")

        # Basic validation to ensure fields aren't empty
        reason = request.POST.get("reason")
        last_working_day = request.POST.get("last_working_day")
        
        if not reason or not last_working_day:
            messages.error(request, "Please fill out all required fields.")
            return render(request, "resignation/apply.html")

        Resignation.objects.create(
            employee=employee,
            reason=reason,
            last_working_day=last_working_day,
            status="PENDING"
        )

        messages.success(request, "Resignation submitted successfully.")
        return redirect("resignation_list")

    return render(request, "resignation/apply.html")


@login_required
def resignation_detail(request, pk):
    resignation = get_object_or_404(Resignation, pk=pk)
    
    # Security Check: Ensure employees can only view their own resignation
    user_role = getattr(request.user, "role", None)
    if user_role != "SUPERVISOR" and resignation.employee.user != request.user:
        messages.error(request, "You do not have permission to view this resignation.")
        return redirect("resignation_list")

    return render(
        request,
        "resignation/detail.html",
        {"resignation": resignation}
    )


@login_required
@require_POST  # State-changing actions should ideally use POST
def approve_resignation(request, pk):
    user_role = getattr(request.user, "role", None)
    if user_role != "SUPERVISOR":
        messages.error(request, "Unauthorized action.")
        return redirect("resignation_list")

    resignation = get_object_or_404(Resignation, pk=pk)
    resignation.status = "APPROVED"
    resignation.save()

    messages.success(request, "Resignation approved successfully.")
    return redirect("resignation_list")


@login_required
@require_POST
def reject_resignation(request, pk):
    user_role = getattr(request.user, "role", None)
    if user_role != "SUPERVISOR":
        messages.error(request, "Unauthorized action.")
        return redirect("resignation_list")

    resignation = get_object_or_404(Resignation, pk=pk)
    resignation.status = "REJECTED"
    resignation.save()

    messages.success(request, "Resignation rejected successfully.")
    return redirect("resignation_list")


@login_required
@require_POST
def send_back_resignation(request, pk):
    user_role = getattr(request.user, "role", None)
    if user_role != "SUPERVISOR":
        messages.error(request, "Unauthorized action.")
        return redirect("resignation_list")

    resignation = get_object_or_404(Resignation, pk=pk)
    resignation.status = "SENT_BACK"
    resignation.save()

    messages.success(request, "Resignation sent back for correction.")
    return redirect("resignation_list")