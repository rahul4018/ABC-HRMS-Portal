from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)

from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Resignation
from apps.employees.models import Employee


@login_required
def resignation_list(request):

    resignations = Resignation.objects.select_related(
        "employee",
        "employee__user"
    ).all().order_by(
        "-created_at"
    )

    return render(
        request,
        "resignation/list.html",
        {
            "resignations": resignations
        }
    )


@login_required
def apply_resignation(request):

    if request.method == "POST":

        employee = Employee.objects.filter(
            user=request.user
        ).first()

        if not employee:

            messages.error(
                request,
                "Employee profile not found."
            )

            return redirect(
                "resignation_list"
            )

        Resignation.objects.create(
            employee=employee,
            reason=request.POST.get(
                "reason"
            ),
            status="PENDING"
        )

        messages.success(
            request,
            "Resignation submitted successfully."
        )

        return redirect(
            "resignation_list"
        )

    return render(
        request,
        "resignation/apply.html"
    )


@login_required
def resignation_detail(
    request,
    pk
):

    resignation = get_object_or_404(
        Resignation,
        pk=pk
    )

    return render(
        request,
        "resignation/detail.html",
        {
            "resignation": resignation
        }
    )


@login_required
def approve_resignation(
    request,
    pk
):

    resignation = get_object_or_404(
        Resignation,
        pk=pk
    )

    resignation.status = "APPROVED"

    resignation.save()

    messages.success(
        request,
        "Resignation approved successfully."
    )

    return redirect(
        "resignation_list"
    )


@login_required
def reject_resignation(
    request,
    pk
):

    resignation = get_object_or_404(
        Resignation,
        pk=pk
    )

    resignation.status = "REJECTED"

    resignation.save()

    messages.success(
        request,
        "Resignation rejected successfully."
    )

    return redirect(
        "resignation_list"
    )