from django.shortcuts import (
    render,
    redirect,
)

from .models import Employee

from .forms import EmployeeCreateForm

from apps.accounts.decorators import role_required


@role_required(
    allowed_roles=['CEO', 'HR_ADMIN']
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


@role_required(
    allowed_roles=['CEO', 'HR_ADMIN']
)
def add_employee(request):

    form = EmployeeCreateForm()

    if request.method == 'POST':

        form = EmployeeCreateForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            form.save()

            return redirect('employee_list')

    context = {
        'form': form
    }

    return render(
        request,
        'employees/add.html',
        context
    )


@role_required(
    allowed_roles=[
        'CEO',
        'HR_ADMIN',
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