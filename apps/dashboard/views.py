from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from apps.employees.models import Employee, Department


@login_required
def dashboard(request):

    total_employees = Employee.objects.count()

    total_departments = Department.objects.count()

    context = {
        "total_employees": total_employees,
        "total_departments": total_departments,
        "pending_leave": 0,
        "pending_pmr": 0,
        "pending_resignation": 0,
        "total_documents": 0,
    }

    return render(
        request,
        "dashboard/dashboard.html",
        context
    )