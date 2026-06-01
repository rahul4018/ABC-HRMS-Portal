from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib.auth.decorators import login_required

from django.contrib import messages

from apps.employees.models import Employee

from .models import PMR


@login_required
def pmr_list(request):

    if request.user.role == "SUPERVISOR":

        pmrs = PMR.objects.all().order_by(
    '-submitted_date'
    )

    else:

        employee = Employee.objects.filter(
            user=request.user
        ).first()

        pmrs = PMR.objects.filter(
            employee=employee
        ).order_by(
            "-created_at"
        )

    return render(
        request,
        "appraisal/list.html",
        {
            "pmrs": pmrs
        }
    )


@login_required
def pmr_create(request):

    employee = Employee.objects.filter(
        user=request.user
    ).first()

    if not employee:

        messages.error(
            request,
            "Employee profile not found."
        )

        return redirect(
            "pmr_list"
        )

    if request.method == "POST":

        PMR.objects.create(

            employee=employee,

            title=request.POST.get(
                "title"
            ),

            achievements=request.POST.get(
                "achievements"
            ),

            goals=request.POST.get(
                "goals"
            ),

            status="PENDING"
        )

        messages.success(
            request,
            "PMR submitted successfully."
        )

        return redirect(
            "pmr_list"
        )

    return render(
        request,
        "appraisal/create.html"
    )


@login_required
def pmr_detail(request, pk):

    pmr = get_object_or_404(
        PMR,
        pk=pk
    )

    return render(
        request,
        "appraisal/detail.html",
        {
            "pmr": pmr
        }
    )


@login_required
def pmr_approve(request, pk):

    if request.user.role != "SUPERVISOR":

        return redirect(
            "pmr_list"
        )

    pmr = get_object_or_404(
        PMR,
        pk=pk
    )

    pmr.status = "APPROVED"

    pmr.save()

    messages.success(
        request,
        "PMR approved successfully."
    )

    return redirect(
        "pmr_list"
    )


@login_required
def pmr_reject(request, pk):

    if request.user.role != "SUPERVISOR":

        return redirect(
            "pmr_list"
        )

    pmr = get_object_or_404(
        PMR,
        pk=pk
    )

    pmr.status = "REJECTED"

    pmr.save()

    messages.success(
        request,
        "PMR rejected successfully."
    )

    return redirect(
        "pmr_list"
    )


@login_required
def pmr_send_back(request, pk):

    if request.user.role != "SUPERVISOR":

        return redirect(
            "pmr_list"
        )

    pmr = get_object_or_404(
        PMR,
        pk=pk
    )

    pmr.status = "RESUBMIT"

    pmr.save()

    messages.success(
        request,
        "PMR sent back for resubmission."
    )

    return redirect(
        "pmr_list"
    )