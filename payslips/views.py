from decimal import Decimal

from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib.auth.decorators import login_required
from django.contrib import messages

from apps.employees.models import Employee
from .models import Payslip


@login_required
def payslip_list(request):

    role = getattr(request.user, "role", "EMPLOYEE")

    if role == "SUPERVISOR":

        payslips = Payslip.objects.select_related(
            "employee",
            "employee__user"
        ).order_by("-generated_at")

    else:

        employee = Employee.objects.filter(
            user=request.user
        ).first()

        if employee:

            payslips = Payslip.objects.filter(
                employee=employee
            ).order_by("-generated_at")

        else:

            payslips = Payslip.objects.none()

    return render(
        request,
        "payslips/list.html",
        {
            "payslips": payslips
        }
    )


@login_required
def create_payslip(request):

    if getattr(request.user, "role", "") != "SUPERVISOR":

        messages.error(
            request,
            "Only supervisors can generate payslips."
        )

        return redirect("payslip_list")

    employees = Employee.objects.select_related(
        "user"
    ).all()

    if request.method == "POST":

        employee_id = request.POST.get("employee")

        employee = get_object_or_404(
            Employee,
            pk=employee_id
        )

        month = request.POST.get("month")
        year = request.POST.get("year")

        basic_salary = Decimal(
            request.POST.get("basic_salary", 0)
        )

        hra = Decimal(
            request.POST.get("hra", 0)
        )

        allowance = Decimal(
            request.POST.get("allowance", 0)
        )

        bonus = Decimal(
            request.POST.get("bonus", 0)
        )

        pf = Decimal(
            request.POST.get("pf", 0)
        )

        professional_tax = Decimal(
            request.POST.get("professional_tax", 0)
        )

        other_deduction = Decimal(
            request.POST.get("other_deduction", 0)
        )

        gross_salary = (
            basic_salary +
            hra +
            allowance +
            bonus
        )

        total_deduction = (
            pf +
            professional_tax +
            other_deduction
        )

        net_salary = (
            gross_salary -
            total_deduction
        )

        Payslip.objects.create(
            employee=employee,
            month=month,
            year=year,
            basic_salary=basic_salary,
            hra=hra,
            allowance=allowance,
            bonus=bonus,
            pf=pf,
            professional_tax=professional_tax,
            other_deduction=other_deduction,
            net_salary=net_salary
        )

        messages.success(
            request,
            "Payslip generated successfully."
        )

        return redirect(
            "payslip_list"
        )

    return render(
        request,
        "payslips/create.html",
        {
            "employees": employees
        }
    )


@login_required
def payslip_detail(request, pk):

    payslip = get_object_or_404(
        Payslip,
        pk=pk
    )

    if (
        getattr(request.user, "role", "") != "SUPERVISOR"
        and payslip.employee.user != request.user
    ):
        messages.error(
            request,
            "Unauthorized access."
        )

        return redirect(
            "payslip_list"
        )

    return render(
        request,
        "payslips/detail.html",
        {
            "payslip": payslip
        }
    )