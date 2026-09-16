from calendar import monthrange
from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_POST

from audit.utils import create_audit_log
from notifications.utils import create_notification
from apps.accounts.decorators import role_required
from apps.accounts.models import User
from apps.employees.models import Employee, Department

from .models import Leave, LeaveBalance, LeavePolicy, Holiday


def _is_hr(request):
    return getattr(request.user, 'role', None) == 'SUPERVISOR' or getattr(
        request.user, 'portal_role', None
    ) in {'ADMIN', 'HR', 'CEO', 'FOUNDER'}


def _is_admin(request):
    return getattr(request.user, 'role', None) == 'SUPERVISOR' or getattr(
        request.user, 'portal_role', None
    ) == 'ADMIN'


@login_required
def leave_list(request):
    role = getattr(request.user, 'portal_role', None) or getattr(request.user, 'role', 'EMPLOYEE')

    if _is_hr(request):
        leaves = Leave.objects.select_related(
            'employee', 'employee__user', 'employee__department'
        ).all()
    else:
        employee = Employee.objects.filter(user=request.user).first()
        leaves = Leave.objects.filter(employee=employee) if employee else Leave.objects.none()

    # Filters
    search = request.GET.get('search', '').strip()
    department = request.GET.get('department', '').strip()
    leave_type = request.GET.get('leave_type', '').strip()
    status = request.GET.get('status', '').strip()
    start_date = parse_date(request.GET.get('start_date', '').strip()) if request.GET.get('start_date') else None
    end_date = parse_date(request.GET.get('end_date', '').strip()) if request.GET.get('end_date') else None

    if search:
        leaves = leaves.filter(
            Q(employee__user__first_name__icontains=search) |
            Q(employee__user__last_name__icontains=search) |
            Q(employee__user__email__icontains=search) |
            Q(employee__employee_id__icontains=search)
        )
    if department:
        leaves = leaves.filter(employee__department_id=department)
    if leave_type:
        leaves = leaves.filter(leave_type=leave_type)
    if status:
        leaves = leaves.filter(status=status)
    if start_date:
        leaves = leaves.filter(end_date__gte=start_date)
    if end_date:
        leaves = leaves.filter(start_date__lte=end_date)

    total_requests = leaves.count()
    pending_requests = leaves.filter(status='PENDING').count()
    approved_requests = leaves.filter(status='APPROVED').count()
    rejected_requests = leaves.filter(status='REJECTED').count()

    today = timezone.localdate()
    on_leave_today = Leave.objects.filter(
        status='APPROVED',
        start_date__lte=today,
        end_date__gte=today,
    ).count()

    month_start = today.replace(day=1)
    month_end = today.replace(day=monthrange(today.year, today.month)[1])
    approved_this_month = Leave.objects.filter(
        status='APPROVED',
        start_date__lte=month_end,
        end_date__gte=month_start,
    ).count()

    paginator = Paginator(leaves.order_by('-applied_at'), 10)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    context = {
        'leaves': page_obj.object_list,
        'page_obj': page_obj,
        'paginator': paginator,
        'departments': Department.objects.order_by('name'),
        'leave_types': Leave.LEAVE_TYPES,
        'status_choices': Leave.STATUS_CHOICES,
        'search': search,
        'selected_department': department,
        'selected_leave_type': leave_type,
        'selected_status': status,
        'selected_start_date': request.GET.get('start_date', ''),
        'selected_end_date': request.GET.get('end_date', ''),
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        'rejected_requests': rejected_requests,
        'on_leave_today': on_leave_today,
        'approved_this_month': approved_this_month,
        'is_hr': _is_hr(request),
        'portal_role': role,
    }
    return render(request, 'leave/list.html', context)


@login_required
def apply_leave(request):
    employee = Employee.objects.filter(user=request.user).first()
    if not employee:
        messages.error(request, 'Employee profile not found.')
        return redirect('leave_list')

    balance, _ = LeaveBalance.objects.get_or_create(employee=employee)

    if request.method == 'POST':
        leave_type = request.POST.get('leave_type')
        duration_type = request.POST.get('duration_type', 'FULL_DAY')
        half_day_period = request.POST.get('half_day_period') or None
        start_date = parse_date(request.POST.get('start_date', ''))
        end_date = parse_date(request.POST.get('end_date', ''))
        reason = request.POST.get('reason', '').strip()

        payload = {
            'leave_type': leave_type,
            'duration_type': duration_type,
            'half_day_period': half_day_period,
            'start_date': request.POST.get('start_date', ''),
            'end_date': request.POST.get('end_date', ''),
            'reason': reason,
        }

        if not all([leave_type, start_date, end_date, reason]):
            messages.error(request, 'Please complete all required fields.')
            return render(request, 'leave/apply.html', {**payload, 'balance': balance})

        if start_date < timezone.localdate():
            messages.error(request, 'Start date cannot be in the past.')
            return render(request, 'leave/apply.html', {**payload, 'balance': balance})

        if end_date < start_date:
            messages.error(request, 'End date cannot occur before start date.')
            return render(request, 'leave/apply.html', {**payload, 'balance': balance})

        leave = Leave(
            employee=employee,
            leave_type=leave_type,
            duration_type=duration_type,
            half_day_period=half_day_period,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            status='PENDING',
        )

        try:
            leave.full_clean()
            leave.save()
        except ValidationError as exc:
            messages.error(request, '; '.join(
                str(v) for values in exc.message_dict.values() for v in values
            ) if hasattr(exc, 'message_dict') else '; '.join(exc.messages))
            return render(request, 'leave/apply.html', {**payload, 'balance': balance})

        for supervisor in User.objects.filter(role='SUPERVISOR', is_active=True):
            create_notification(
                supervisor,
                'New Leave Request',
                f'{employee.user.get_full_name() or employee.user.email} submitted a leave request.',
            )

        create_audit_log(request.user, 'Leave', f'Submitted Leave Request ({leave_type})')
        messages.success(request, 'Leave request submitted successfully.')
        return redirect('leave_list')

    return render(request, 'leave/apply.html', {
        'balance': balance,
        'leave_types': Leave.LEAVE_TYPES,
        'leave_policies': LeavePolicy.objects.filter(is_active=True),
    })


@login_required
def leave_detail(request, pk):
    leave = get_object_or_404(
        Leave.objects.select_related('employee', 'employee__user', 'employee__department'),
        pk=pk,
    )

    if not _is_hr(request) and leave.employee.user != request.user:
        raise PermissionDenied('You do not have permission to view this leave request.')

    return render(request, 'leave/detail.html', {
        'leave': leave,
        'is_hr': _is_hr(request),
    })


@login_required
@require_POST
def approve_leave(request, pk):
    if not _is_hr(request):
        messages.error(request, 'Unauthorized action.')
        return redirect('leave_list')

    leave = get_object_or_404(Leave, pk=pk)
    leave.approved_by = request.user
    leave.status = 'APPROVED'
    leave.review_comment = request.POST.get('review_comment', '').strip()
    leave.save()

    create_audit_log(
        request.user,
        'Leave',
        f'Approved Leave Request - {leave.employee.user.email}'
    )
    create_notification(
        leave.employee.user,
        'Leave Approved',
        f'Your {leave.get_leave_type_display()} request has been approved.'
    )
    messages.success(request, 'Leave approved successfully.')
    return redirect('leave_list')


@login_required
@require_POST
def reject_leave(request, pk):
    if not _is_hr(request):
        messages.error(request, 'Unauthorized action.')
        return redirect('leave_list')

    leave = get_object_or_404(Leave, pk=pk)
    leave.approved_by = request.user
    leave.status = 'REJECTED'
    leave.review_comment = request.POST.get('review_comment', '').strip()
    leave.save()

    create_audit_log(
        request.user,
        'Leave',
        f'Rejected Leave Request - {leave.employee.user.email}'
    )
    create_notification(
        leave.employee.user,
        'Leave Rejected',
        f'Your {leave.get_leave_type_display()} request has been rejected.'
    )
    messages.success(request, 'Leave rejected successfully.')
    return redirect('leave_list')


@login_required
@require_POST
def request_leave_changes(request, pk):
    if not _is_hr(request):
        messages.error(request, 'Unauthorized action.')
        return redirect('leave_list')

    leave = get_object_or_404(Leave, pk=pk)
    leave.status = 'PENDING'
    leave.review_comment = request.POST.get('review_comment', '').strip()
    leave.save()

    create_notification(
        leave.employee.user,
        'Leave Changes Requested',
        f'HR requested changes to your {leave.get_leave_type_display()} request.'
    )
    messages.info(request, 'The leave request was returned to the employee for changes.')
    return redirect('leave_detail', pk=pk)


@login_required
@require_POST
def cancel_leave(request, pk):
    leave = get_object_or_404(Leave, pk=pk)

    if leave.employee.user != request.user:
        raise PermissionDenied('Only the employee who submitted the request can cancel it.')

    if leave.status != 'PENDING':
        messages.error(request, 'Only pending leave requests can be cancelled.')
        return redirect('leave_detail', pk=pk)

    leave.status = 'CANCELLED'
    leave.save()
    create_audit_log(request.user, 'Leave', f'Cancelled Leave Request ({leave.pk})')
    messages.success(request, 'Leave request cancelled.')
    return redirect('leave_list')


@login_required
def leave_balance(request, employee_id=None):
    if employee_id and not _is_hr(request):
        raise PermissionDenied('You do not have permission to view another employee balance.')

    if employee_id:
        employee = get_object_or_404(Employee, pk=employee_id)
    else:
        employee = Employee.objects.filter(user=request.user).first()

    if not employee:
        messages.error(request, 'Employee profile not found.')
        return redirect('leave_list')

    balance, _ = LeaveBalance.objects.get_or_create(employee=employee)

    history = Leave.objects.filter(
        employee=employee
    ).order_by('-applied_at')[:20]

    return render(request, 'leave/balance.html', {
        'employee': employee,
        'balance': balance,
        'history': history,
        'is_hr': _is_hr(request),
    })


@login_required
def leave_calendar(request):
    if _is_hr(request):
        employee = None
        leaves = Leave.objects.filter(status__in=['PENDING', 'APPROVED'])
    else:
        employee = Employee.objects.filter(user=request.user).first()
        leaves = Leave.objects.filter(
            employee=employee,
            status__in=['PENDING', 'APPROVED'],
        ) if employee else Leave.objects.none()

    try:
        year = int(request.GET.get('year', timezone.localdate().year))
    except (TypeError, ValueError):
        year = timezone.localdate().year

    try:
        month = int(request.GET.get('month', timezone.localdate().month))
    except (TypeError, ValueError):
        month = timezone.localdate().month

    if month < 1 or month > 12:
        month = 1

    first_day = date(year, month, 1)
    days = []
    last_day = monthrange(year, month)[1]

    holidays = set(
        Holiday.objects.filter(
            is_active=True,
            holiday_date__year=year,
            holiday_date__month=month,
        ).values_list('holiday_date', flat=True)
    )

    for day_num in range(1, last_day + 1):
        day = date(year, month, day_num)
        day_leaves = leaves.filter(start_date__lte=day, end_date__gte=day)
        days.append({
            'date': day,
            'is_weekend': day.weekday() >= 5,
            'is_holiday': day in holidays,
            'leaves': day_leaves,
        })

    return render(request, 'leave/calendar.html', {
        'year': year,
        'month': month,
        'days': days,
        'holidays': holidays,
        'month_name': first_day.strftime('%B'),
        'is_hr': _is_hr(request),
        'employee': employee,
    })


@login_required
@role_required(['SUPERVISOR'])
def holiday_list(request):
    holidays = Holiday.objects.all()
    return render(request, 'leave/holiday_list.html', {'holidays': holidays})


@login_required
@role_required(['SUPERVISOR'])
def holiday_add(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        holiday_date = parse_date(request.POST.get('holiday_date', ''))
        holiday_type = request.POST.get('holiday_type', 'NATIONAL')
        description = request.POST.get('description', '').strip()

        if not name or not holiday_date:
            messages.error(request, 'Holiday name and date are required.')
        else:
            Holiday.objects.update_or_create(
                holiday_date=holiday_date,
                defaults={
                    'name': name,
                    'holiday_type': holiday_type,
                    'description': description,
                    'is_active': True,
                }
            )
            messages.success(request, 'Holiday created successfully.')
            return redirect('holiday_list')

    return render(request, 'leave/holiday_add.html', {
        'holiday_types': Holiday.HOLIDAY_TYPES,
    })


@login_required
def leave_policy_list(request):
    if not _is_hr(request):
        raise PermissionDenied('Only HR/Admin can manage leave policies.')

    for leave_type, label in Leave.LEAVE_TYPES:
        LeavePolicy.objects.get_or_create(
            leave_type=leave_type,
            defaults={'annual_allocation': {
                'CASUAL': 12, 'SICK': 12, 'EARNED': 18
            }.get(leave_type, 0)}
        )

    policies = LeavePolicy.objects.all()
    return render(request, 'leave/policies.html', {'policies': policies})


@login_required
@require_POST
def leave_policy_update(request, pk):
    if not _is_hr(request):
        raise PermissionDenied('Only HR/Admin can manage leave policies.')

    policy = get_object_or_404(LeavePolicy, pk=pk)
    try:
        policy.annual_allocation = int(request.POST.get('annual_allocation', policy.annual_allocation))
        policy.max_carry_forward = int(request.POST.get('max_carry_forward', policy.max_carry_forward))
    except (TypeError, ValueError):
        messages.error(request, 'Allocation values must be whole numbers.')
        return redirect('leave_policy_list')

    policy.is_paid = request.POST.get('is_paid') == 'on'
    policy.carry_forward = request.POST.get('carry_forward') == 'on'
    policy.is_active = request.POST.get('is_active') == 'on'
    policy.save()

    messages.success(request, 'Leave policy updated.')
    return redirect('leave_policy_list')
