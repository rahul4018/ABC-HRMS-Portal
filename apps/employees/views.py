from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)

from django.contrib import messages

from django.contrib.auth.decorators import login_required

from django.db.models import Count

from .models import (
    Employee,
    Department,
)

from .forms import (
    EmployeeCreateForm,
    EmployeeUpdateForm,
)

from apps.accounts.decorators import role_required


# ==========================================
# Employee List
# ==========================================

@login_required
@role_required(['CEO', 'HR_ADMIN'])
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


# ==========================================
# Employee Detail
# ==========================================

@login_required
@role_required(['CEO', 'HR_ADMIN'])
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


# ==========================================
# Add Employee
# ==========================================

@login_required
@role_required(['CEO', 'HR_ADMIN'])
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


# ==========================================
# Edit Employee
# ==========================================

@login_required
@role_required(['CEO', 'HR_ADMIN'])
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


# ==========================================
# Delete Employee
# ==========================================

@login_required
@role_required(['CEO'])
def employee_delete(request, pk):

    employee = get_object_or_404(
        Employee,
        pk=pk
    )

    employee.delete()

    messages.success(
        request,
        'Employee deleted successfully.'
    )

    return redirect(
        'employee_list'
    )


# ==========================================
# My Profile
# ==========================================

@login_required
@role_required([
    'CEO',
    'HR_ADMIN',
    'EMPLOYEE'
])
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


# ==========================================
# Department List
# ==========================================

@login_required
@role_required(['CEO', 'HR_ADMIN'])
def department_list(request):

    departments = Department.objects.annotate(
        employee_count=Count('employee')
    )

    context = {
        'departments': departments
    }

    return render(
        request,
        'departments/list.html',
        context
    )


# ==========================================
# Add Department
# ==========================================

@login_required
@role_required(['CEO', 'HR_ADMIN'])
def add_department(request):

    if request.method == 'POST':

        name = request.POST.get('name')

        Department.objects.create(
            name=name
        )

        messages.success(
            request,
            'Department added successfully.'
        )

        return redirect(
            'department_list'
        )

    return render(
        request,
        'departments/add.html'
    )


# ==========================================
# Edit Department
# ==========================================

@login_required
@role_required(['CEO', 'HR_ADMIN'])
def edit_department(request, department_id):

    department = get_object_or_404(
        Department,
        id=department_id
    )

    if request.method == 'POST':

        department.name = request.POST.get('name')

        department.save()

        messages.success(
            request,
            'Department updated successfully.'
        )

        return redirect(
            'department_list'
        )

    context = {
        'department': department
    }

    return render(
        request,
        'departments/edit.html',
        context
    )


# ==========================================
# Delete Department
# ==========================================

@login_required
@role_required(['CEO'])
def delete_department(request, department_id):

    department = get_object_or_404(
        Department,
        id=department_id
    )

    if request.method == 'POST':

        department.delete()

        messages.success(
            request,
            'Department deleted successfully.'
        )

        return redirect(
            'department_list'
        )

    context = {
        'department': department
    }

    return render(
        request,
        'departments/delete.html',
        context
    )