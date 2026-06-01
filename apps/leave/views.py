from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
from audit.utils import create_audit_log
from .models import Leave
from apps.employees.models import Employee

@login_required
def leave_list(request):
    role = getattr(request.user, 'role', 'EMPLOYEE')

    if role == 'SUPERVISOR':
        leaves = Leave.objects.select_related(
            'employee',
            'employee__user'
        ).order_by('-applied_at')
    else:
        employee = Employee.objects.filter(user=request.user).first()
        if employee:
            leaves = Leave.objects.filter(employee=employee).order_by('-applied_at')
        else:
            leaves = Leave.objects.none()

    return render(
        request,
        'leave/list.html',
        {'leaves': leaves}
    )


@login_required
def apply_leave(request):
    employee = Employee.objects.filter(user=request.user).first()

    if not employee:
        messages.error(request, 'Employee profile not found.')
        return redirect('leave_list')

    if request.method == 'POST':
        leave_type = request.POST.get('leave_type')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = request.POST.get('reason')

        # Safety validation check
        if not all([leave_type, start_date, end_date]):
            messages.error(request, 'Please complete all required fields.')
            return render(request, 'leave/apply.html')

        Leave.objects.create(
            employee=employee,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            status='PENDING'
        )

        create_audit_log(
            request.user,
            'Leave',
            f'Submitted Leave Request ({leave_type}): {start_date} to {end_date}'
        )

        messages.success(request, 'Leave request submitted successfully.')
        return redirect('leave_list')

    return render(request, 'leave/apply.html')


@login_required
def leave_detail(request, pk):
    leave = get_object_or_404(Leave, pk=pk)
    role = getattr(request.user, 'role', 'EMPLOYEE')

    if role != 'SUPERVISOR' and leave.employee.user != request.user:
        raise PermissionDenied('You do not have permission to view this leave request.')

    return render(
        request,
        'leave/detail.html',
        {'leave': leave}
    )


@login_required
@require_POST
def approve_leave(request, pk):
    if getattr(request.user, 'role', 'EMPLOYEE') != 'SUPERVISOR':
        messages.error(request, 'Unauthorized action.')
        return redirect('leave_list')

    leave = get_object_or_404(Leave, pk=pk)
    leave.status = 'APPROVED'
    leave.save()

    create_audit_log(
        request.user,
        'Leave',
        f'Approved Leave Request - {leave.employee.user.email}'
    )

    messages.success(request, 'Leave approved successfully.')
    return redirect('leave_list')


@login_required
@require_POST
def reject_leave(request, pk):
    if getattr(request.user, 'role', 'EMPLOYEE') != 'SUPERVISOR':
        messages.error(request, 'Unauthorized action.')
        return redirect('leave_list')

    leave = get_object_or_404(Leave, pk=pk)
    leave.status = 'REJECTED'
    leave.save()

    create_audit_log(
        request.user,
        'Leave',
        f'Rejected Leave Request - {leave.employee.user.email}'
    )

    messages.success(request, 'Leave rejected successfully.')
    return redirect('leave_list')