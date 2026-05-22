from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Employee
from .forms import (
    EmployeeCreateForm,
    EmployeeUpdateForm
)

from apps.accounts.decorators import role_required


# =========================
# Employee List
# =========================

@login_required
@role_required(
    allowed_roles=[
        'CEO',
        'HR',
    ]
)
def employee_list(request):

    employees = Employee.objects.select_related(
        'user',
        'department'
    ).all()

    context = {
        'employees': employees
    }

    return render(
        request,
        'employees/list.html',
        context
    )


# =========================
# Employee Detail
# =========================

@login_required
@role_required(
    allowed_roles=[
        'CEO',
        'HR',
    ]
)
def employee_detail(request, pk):

    employee = get_object_or_404(
        Employee,
        pk=pk
    )

    context = {
        'employee': employee
    }

    return render(
        request,
        'employees/detail.html',
        context
    )


# =========================
# Add Employee
# =========================

@login_required
@role_required(
    allowed_roles=[
        'CEO',
        'HR',
    ]
)
def employee_add(request):

    form = EmployeeCreateForm()

    if request.method == 'POST':

        form = EmployeeCreateForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Employee created successfully.'
            )

            return redirect(
                'employee_list'
            )

    context = {
        'form': form
    }

    return render(
        request,
        'employees/add.html',
        context
    )


# =========================
# Edit Employee
# =========================

@login_required
@role_required(
    allowed_roles=[
        'CEO',
        'HR',
    ]
)
def employee_edit(request, pk):

    employee = get_object_or_404(
        Employee,
        pk=pk
    )

    form = EmployeeUpdateForm(
        instance=employee
    )

    if request.method == 'POST':

        form = EmployeeUpdateForm(
            request.POST,
            request.FILES,
            instance=employee
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Employee updated successfully.'
            )

            return redirect(
                'employee_detail',
                pk=employee.pk
            )

    context = {
        'form': form,
        'employee': employee,
    }

    return render(
        request,
        'employees/edit.html',
        context
    )


# =========================
# Delete Employee
# =========================

@login_required
@role_required(
    allowed_roles=[
        'CEO'
    ]
)
def employee_delete(request, pk):

    employee = get_object_or_404(
        Employee,
        pk=pk
    )

    if request.method == 'POST':

        employee.user.delete()

        messages.success(
            request,
            'Employee deleted successfully.'
        )

        return redirect(
            'employee_list'
        )

    context = {
        'employee': employee
    }

    return render(
        request,
        'employees/delete.html',
        context
    )


# =========================
# My Profile
# =========================

@login_required
@role_required(
    allowed_roles=[
        'CEO',
        'HR',
        'EMPLOYEE'
    ]
)
def my_profile(request):

    employee = Employee.objects.filter(
        user=request.user
    ).first()

    context = {
        'employee': employee
    }

    return render(
        request,
        'employees/profile.html',
        context
    )