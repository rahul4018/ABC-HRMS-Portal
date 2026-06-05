from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
from django.utils.dateparse import parse_date
from datetime import date
from audit.utils import create_audit_log
from .models import Leave
from apps.employees.models import Employee
from notifications.utils import create_notification
from apps.accounts.models import User

@login_required
def leave_list(request):
    role = getattr(request.user, 'role', 'EMPLOYEE')

    if role == 'SUPERVISOR':
        leaves = Leave.objects.select_related('employee', 'employee__user').order_by('-applied_at')
    else:
        employee = Employee.objects.filter(user=request.user).first()
        if employee:
            leaves = Leave.objects.filter(employee=employee).order_by('-applied_at')
        else:
            leaves = Leave.objects.none()

    return render(request, 'leave/list.html', {'leaves': leaves})


@login_required
def apply_leave(request):
    employee = Employee.objects.filter(user=request.user).first()

    if not employee:
        messages.error(request, 'Employee profile not found.')
        return redirect('leave_list')

    if request.method == 'POST':
        leave_type = request.POST.get('leave_type')
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
        reason = request.POST.get('reason', '').strip()

        # Capture payload for form-repopulation upon error validation
        context_payload = {
            'leave_type': leave_type,
            'start_date': start_date_str,
            'end_date': end_date_str,
            'reason': reason
        }

        if not all([leave_type, start_date_str, end_date_str]):
            messages.error(request, 'Please complete all required fields.')
            return render(request, 'leave/apply.html', context_payload)

        # Parse and cross-validate dates
        start_date = parse_date(start_date_str)
        end_date = parse_date(end_date_str)

        if not start_date or not end_date:
            messages.error(request, 'Invalid date formats provided.')
            return render(request, 'leave/apply.html', context_payload)

        if start_date < date.today():
            messages.error(request, 'Start date cannot be in the past.')
            return render(request, 'leave/apply.html', context_payload)

        if end_date < start_date:
            messages.error(request, 'End date cannot occur before the start date.')
            return render(request, 'leave/apply.html', context_payload)

        # Everything is verified safe, proceed to create
        Leave.objects.create(
            employee=employee,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            status='PENDING'
        )

        # Send automatic notifications to all supervisors
        supervisors = User.objects.filter(role='SUPERVISOR')
        for supervisor in supervisors:
            create_notification(
                supervisor,
                'New Leave Request',
                f'{employee.user.email} applied for leave.'
            )

        create_audit_log(request.user, 'Leave', f'Submitted Leave Request ({leave_type})')
        messages.success(request, 'Leave request submitted successfully.')
        return redirect('leave_list')

    return render(request, 'leave/apply.html')


@login_required
def leave_detail(request, pk):
    leave = get_object_or_404(Leave, pk=pk)
    role = getattr(request.user, 'role', 'EMPLOYEE')

    if role != 'SUPERVISOR' and leave.employee.user != request.user:
        raise PermissionDenied('You do not have permission to view this leave request.')

    if request.method == 'POST' and role == 'SUPERVISOR':
        status = request.POST.get('status')

        if status in ['PENDING', 'APPROVED', 'REJECTED']:
            leave.status = status
            leave.save()

            create_audit_log(request.user, 'Leave', f'Updated Leave Status to {status}')
            messages.success(request, f'Leave status updated to {status}.')
            return redirect('leave_detail', pk=leave.pk)

    return render(request, 'leave/detail.html', {'leave': leave})


@login_required
@require_POST
def approve_leave(request, pk):
    if getattr(request.user, 'role', 'EMPLOYEE') != 'SUPERVISOR':
        messages.error(request, 'Unauthorized action.')
        return redirect('leave_list')

    leave = get_object_or_404(Leave, pk=pk)
    leave.status = 'APPROVED'
    leave.save()

    create_audit_log(request.user, 'Leave', f'Approved Leave Request - {leave.employee.user.email}')
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

    create_audit_log(request.user, 'Leave', f'Rejected Leave Request - {leave.employee.user.email}')
    messages.success(request, 'Leave rejected successfully.')
    return redirect('leave_list')