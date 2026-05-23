from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from apps.employees.models import (
    Employee,
    Department,
)


@login_required
def dashboard(request):

    total_employees = Employee.objects.count()

    total_departments = Department.objects.count()

    context = {
        'total_employees': total_employees,
        'total_departments': total_departments,
    }

    return render(
        request,
        'dashboard/index.html',
        context
    )