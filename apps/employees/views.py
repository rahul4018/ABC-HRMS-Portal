from datetime import date
from datetime import datetime

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
    Payslip,
    Attendance,
)

from .forms import (
    EmployeeCreateForm,
    EmployeeUpdateForm,
)

from apps.accounts.decorators import role_required


# ==========================================
# Dashboard
# ==========================================

@login_required
def dashboard(request):

    total_employees = Employee.objects.count()

    total_departments = Department.objects.count()

    total_attendance = Attendance.objects.count()

    context = {
        'total_employees': total_employees,
        'total_departments': total_departments,
        'total_attendance': total_attendance,
    }

    return render(
        request,
        'dashboard/index.html',
        context
    )


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
    ).order_by('name')

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
def department_add(request):

    if request.method == 'POST':

        Department.objects.create(

            name=request.POST.get('name'),

            description=request.POST.get(
                'description'
            ),

            department_head=request.POST.get(
                'department_head'
            )

        )

        messages.success(
            request,
            'Department created successfully.'
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
def department_edit(request, pk):

    department = get_object_or_404(
        Department,
        pk=pk
    )

    if request.method == 'POST':

        department.name = request.POST.get(
            'name'
        )

        department.description = request.POST.get(
            'description'
        )

        department.department_head = request.POST.get(
            'department_head'
        )

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
def department_delete(request, pk):

    department = get_object_or_404(
        Department,
        pk=pk
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


# ==========================================
# PAYSLIP MANAGEMENT
# ==========================================

@login_required
def payslip_list(request):

    if request.user.role in ['CEO', 'HR_ADMIN']:

        payslips = Payslip.objects.all().order_by(
            '-generated_at'
        )

    else:

        payslips = Payslip.objects.filter(
            employee__user=request.user
        ).order_by(
            '-generated_at'
        )

    context = {
        'payslips': payslips
    }

    return render(
        request,
        'payslips/list.html',
        context
    )


@login_required
def payslip_detail(request, pk):

    payslip = get_object_or_404(
        Payslip,
        pk=pk
    )

    if (
        request.user.role == 'EMPLOYEE'
        and payslip.employee.user != request.user
    ):

        messages.error(
            request,
            'Access denied.'
        )

        return redirect(
            'payslip_list'
        )

    context = {
        'payslip': payslip
    }

    return render(
        request,
        'payslips/detail.html',
        context
    )


# ==========================================
# ATTENDANCE MANAGEMENT
# ==========================================

@login_required
def attendance_list(request):

    if request.user.role in ['CEO', 'HR_ADMIN']:

        attendances = Attendance.objects.select_related(
            'employee',
            'employee__user'
        ).all()

    else:

        employee = Employee.objects.filter(
            user=request.user
        ).first()

        attendances = Attendance.objects.filter(
            employee=employee
        )

    context = {
        'attendances': attendances
    }

    return render(
        request,
        'attendance/list.html',
        context
    )


@login_required
def mark_attendance(request):

    employee = Employee.objects.filter(
        user=request.user
    ).first()

    if not employee:

        messages.error(
            request,
            'Employee profile not found.'
        )

        return redirect(
            'attendance_list'
        )

    today = date.today()

    attendance = Attendance.objects.filter(
        employee=employee,
        date=today
    ).first()

    if request.method == 'POST':

        current_time = datetime.now().time()

        if not attendance:

            Attendance.objects.create(
                employee=employee,
                date=today,
                check_in=current_time,
                status='PRESENT'
            )

            messages.success(
                request,
                'Check-in successful.'
            )

        elif not attendance.check_out:

            attendance.check_out = current_time

            attendance.save()

            messages.success(
                request,
                'Check-out successful.'
            )

        else:

            messages.warning(
                request,
                'Attendance already completed today.'
            )

        return redirect(
            'attendance_list'
        )

    context = {
        'attendance': attendance
    }

    return render(
        request,
        'attendance/mark.html',
        context
    )


@login_required
def attendance_detail(request, pk):

    attendance = get_object_or_404(
        Attendance,
        pk=pk
    )

    if (
        request.user.role == 'EMPLOYEE'
        and attendance.employee.user != request.user
    ):

        messages.error(
            request,
            'Access denied.'
        )

        return redirect(
            'attendance_list'
        )

    context = {
        'attendance': attendance
    }

    return render(
        request,
        'attendance/detail.html',
        context
    )