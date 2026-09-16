from calendar import monthrange
from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Resignation
from apps.employees.models import Employee

try:
    from notifications.utils import create_notification
except Exception:
    create_notification = None

try:
    from audit.utils import create_audit_log
except Exception:
    create_audit_log = None


DEFAULT_NOTICE_PERIOD_DAYS = 15
DEFAULT_NOTICE_PERIOD_UNIT = 'CALENDAR'


def _is_manager(user):
    role = getattr(user, 'role', None)
    portal_role = getattr(user, 'portal_role', None)
    return (
        role == 'SUPERVISOR'
        or portal_role in {'ADMIN', 'FOUNDER', 'CEO', 'CTO', 'CFO', 'HR'}
    )


def _calculate_lwd(start_date, notice_days=DEFAULT_NOTICE_PERIOD_DAYS,
                   unit=DEFAULT_NOTICE_PERIOD_UNIT):
    """Calculate the expected LWD, excluding the resignation date itself."""
    if unit == 'WORKING':
        current = start_date
        remaining = int(notice_days)
        while remaining > 0:
            current += timedelta(days=1)
            # Monday-Friday. Company holidays can be incorporated later via policy.
            if current.weekday() < 5:
                remaining -= 1
        return current
    return start_date + timedelta(days=int(notice_days))


def _notify_supervisors(title, message, exclude_user=None):
    if not create_notification:
        return
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        supervisors = User.objects.filter(role='SUPERVISOR', is_active=True)
        if exclude_user is not None:
            supervisors = supervisors.exclude(pk=exclude_user.pk)
        for user in supervisors:
            create_notification(user, title, message)
    except Exception:
        pass


def _audit(user, action):
    if create_audit_log:
        try:
            create_audit_log(user, 'Resignation', action)
        except Exception:
            pass


@login_required
def resignation_list(request):
    manager = _is_manager(request.user)

    if manager:
        resignations = Resignation.objects.select_related(
            'employee', 'employee__user', 'employee__department'
        ).all()
    else:
        employee = Employee.objects.filter(user=request.user).first()
        resignations = (
            Resignation.objects.select_related(
                'employee', 'employee__user', 'employee__department'
            ).filter(employee=employee)
            if employee else Resignation.objects.none()
        )

    # Optional filters for HR.
    status = request.GET.get('status', '').strip()
    query = request.GET.get('q', '').strip()

    if status:
        resignations = resignations.filter(status=status)

    if query:
        resignations = resignations.filter(
            employee__employee_id__icontains=query
        ) | resignations.filter(
            employee__user__first_name__icontains=query
        ) | resignations.filter(
            employee__user__last_name__icontains=query
        )

    today = timezone.localdate()

    context = {
        'resignations': resignations.order_by('-created_at'),
        'is_manager': manager,
        'today': today,
        'total_requests': resignations.count(),
        'pending_count': resignations.filter(status='PENDING').count(),
        'notice_count': resignations.filter(status='NOTICE_PERIOD').count(),
        'early_release_count': resignations.filter(status='EARLY_RELEASE_REQUESTED').count(),
        'exit_process_count': resignations.filter(status='EXIT_PROCESS').count(),
        'completed_count': resignations.filter(status='COMPLETED').count(),
        'status_filter': status,
        'query': query,
        'status_choices': Resignation.STATUS_CHOICES,
    }

    return render(request, 'resignation/list.html', context)


@login_required
def apply_resignation(request):
    employee = Employee.objects.filter(user=request.user).first()

    if not employee:
        messages.error(request, 'Employee profile not found.')
        return redirect('resignation_list')

    active_statuses = {
        'PENDING', 'APPROVED', 'NOTICE_PERIOD',
        'EARLY_RELEASE_REQUESTED', 'SENT_BACK', 'EXIT_PROCESS'
    }
    existing_active = Resignation.objects.filter(
        employee=employee,
        status__in=active_statuses
    ).first()

    resignation_date = timezone.localdate()
    expected_lwd = _calculate_lwd(
        resignation_date,
        DEFAULT_NOTICE_PERIOD_DAYS,
        DEFAULT_NOTICE_PERIOD_UNIT
    )

    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        additional_comments = request.POST.get('additional_comments', '').strip()
        early_release_date_raw = request.POST.get('requested_early_release_date', '').strip()
        early_release_reason = request.POST.get('early_release_reason', '').strip()
        early_release_requested = request.POST.get('early_release_requested') == 'on'

        if existing_active:
            messages.warning(
                request,
                'You already have an active resignation request. '
                'Please track or withdraw the existing request before submitting another.'
            )
            return redirect('resignation_detail', pk=existing_active.pk)

        if not reason:
            messages.error(request, 'Reason for resignation is required.')
            return render(request, 'resignation/apply.html', {
                'employee': employee,
                'resignation_date': resignation_date,
                'notice_period_days': DEFAULT_NOTICE_PERIOD_DAYS,
                'notice_period_unit': DEFAULT_NOTICE_PERIOD_UNIT,
                'expected_lwd': expected_lwd,
            })

        requested_early_release_date = None
        if early_release_requested:
            from django.utils.dateparse import parse_date
            requested_early_release_date = parse_date(early_release_date_raw)
            if not requested_early_release_date:
                messages.error(request, 'Please provide a valid early release date.')
                return render(request, 'resignation/apply.html', {
                    'employee': employee,
                    'resignation_date': resignation_date,
                    'notice_period_days': DEFAULT_NOTICE_PERIOD_DAYS,
                    'notice_period_unit': DEFAULT_NOTICE_PERIOD_UNIT,
                    'expected_lwd': expected_lwd,
                })
            if requested_early_release_date >= expected_lwd:
                messages.error(
                    request,
                    'The early release date must be before the expected last working day.'
                )
                return render(request, 'resignation/apply.html', {
                    'employee': employee,
                    'resignation_date': resignation_date,
                    'notice_period_days': DEFAULT_NOTICE_PERIOD_DAYS,
                    'notice_period_unit': DEFAULT_NOTICE_PERIOD_UNIT,
                    'expected_lwd': expected_lwd,
                })
            if not early_release_reason:
                messages.error(request, 'Please provide a reason for requesting early release.')
                return render(request, 'resignation/apply.html', {
                    'employee': employee,
                    'resignation_date': resignation_date,
                    'notice_period_days': DEFAULT_NOTICE_PERIOD_DAYS,
                    'notice_period_unit': DEFAULT_NOTICE_PERIOD_UNIT,
                    'expected_lwd': expected_lwd,
                })

        resignation = Resignation.objects.create(
            employee=employee,
            resignation_date=resignation_date,
            notice_period_days=DEFAULT_NOTICE_PERIOD_DAYS,
            notice_period_unit=DEFAULT_NOTICE_PERIOD_UNIT,
            expected_last_working_day=expected_lwd,
            last_working_day=(requested_early_release_date if early_release_requested else expected_lwd),
            requested_early_release_date=requested_early_release_date,
            early_release_reason=early_release_reason or None,
            reason=reason,
            additional_comments=additional_comments or None,
            status='EARLY_RELEASE_REQUESTED' if early_release_requested else 'PENDING',
        )

        _notify_supervisors(
            'New Resignation Submitted',
            f'{employee.user.get_full_name() or employee.user.email} submitted a resignation request.'
        )
        _audit(request.user, f'Submitted resignation - {employee.employee_id}')

        messages.success(request, 'Resignation submitted successfully.')
        return redirect('resignation_detail', pk=resignation.pk)

    return render(request, 'resignation/apply.html', {
        'employee': employee,
        'resignation_date': resignation_date,
        'notice_period_days': DEFAULT_NOTICE_PERIOD_DAYS,
        'notice_period_unit': DEFAULT_NOTICE_PERIOD_UNIT,
        'expected_lwd': expected_lwd,
    })


@login_required
def resignation_detail(request, pk):
    resignation = get_object_or_404(
        Resignation.objects.select_related(
            'employee', 'employee__user', 'employee__department'
        ),
        pk=pk
    )

    manager = _is_manager(request.user)
    if not manager and resignation.employee.user != request.user:
        messages.error(request, 'You do not have permission to view this resignation.')
        return redirect('resignation_list')

    return render(request, 'resignation/detail.html', {
        'resignation': resignation,
        'is_manager': manager,
        'today': timezone.localdate(),
    })


@login_required
@require_POST
def approve_resignation(request, pk):
    if not _is_manager(request.user):
        messages.error(request, 'Unauthorized action.')
        return redirect('resignation_list')

    resignation = get_object_or_404(Resignation, pk=pk)
    if resignation.status not in {'PENDING', 'EARLY_RELEASE_REQUESTED', 'SENT_BACK'}:
        messages.warning(request, 'This resignation cannot be approved in its current state.')
        return redirect('resignation_detail', pk=pk)

    early_release_approved = (
        resignation.status == 'EARLY_RELEASE_REQUESTED'
        and resignation.requested_early_release_date
    )

    resignation.status = 'NOTICE_PERIOD'
    if early_release_approved:
        # Keep the policy-computed LWD visible while recording the approved
        # early release date as the operational last working day.
        resignation.last_working_day = resignation.requested_early_release_date
    else:
        resignation.last_working_day = resignation.expected_last_working_day
    resignation.supervisor_remark = request.POST.get('remark', '').strip() or resignation.supervisor_remark
    resignation.save()

    _audit(request.user, f'Approved resignation - {resignation.employee.employee_id}')
    messages.success(request, 'Resignation approved and moved to notice period.')
    return redirect('resignation_detail', pk=pk)


@login_required
@require_POST
def reject_resignation(request, pk):
    if not _is_manager(request.user):
        messages.error(request, 'Unauthorized action.')
        return redirect('resignation_list')

    resignation = get_object_or_404(Resignation, pk=pk)
    resignation.status = 'REJECTED'
    resignation.supervisor_remark = request.POST.get('remark', '').strip() or resignation.supervisor_remark
    resignation.save()

    _audit(request.user, f'Rejected resignation - {resignation.employee.employee_id}')
    messages.success(request, 'Resignation rejected.')
    return redirect('resignation_detail', pk=pk)


@login_required
@require_POST
def send_back_resignation(request, pk):
    if not _is_manager(request.user):
        messages.error(request, 'Unauthorized action.')
        return redirect('resignation_list')

    resignation = get_object_or_404(Resignation, pk=pk)
    resignation.status = 'SENT_BACK'
    resignation.supervisor_remark = request.POST.get('remark', '').strip() or resignation.supervisor_remark
    resignation.save()

    _audit(request.user, f'Sent back resignation - {resignation.employee.employee_id}')
    messages.info(request, 'Resignation sent back for clarification/correction.')
    return redirect('resignation_detail', pk=pk)


@login_required
@require_POST
def withdraw_resignation(request, pk):
    resignation = get_object_or_404(Resignation, pk=pk)
    if resignation.employee.user != request.user:
        messages.error(request, 'Unauthorized action.')
        return redirect('resignation_list')

    if resignation.status not in {'PENDING', 'SENT_BACK', 'EARLY_RELEASE_REQUESTED'}:
        messages.warning(request, 'This resignation cannot be withdrawn now.')
        return redirect('resignation_detail', pk=pk)

    resignation.status = 'WITHDRAWN'
    resignation.save(update_fields=['status', 'updated_at'])

    _audit(request.user, f'Withdrawn resignation - {resignation.employee.employee_id}')
    messages.success(request, 'Resignation withdrawn successfully.')
    return redirect('resignation_list')


@login_required
@require_POST
def update_offboarding(request, pk):
    if not _is_manager(request.user):
        messages.error(request, 'Unauthorized action.')
        return redirect('resignation_list')

    resignation = get_object_or_404(Resignation, pk=pk)

    resignation.handover_status = request.POST.get('handover_status', resignation.handover_status)
    resignation.handover_notes = request.POST.get('handover_notes', '').strip() or None

    for field in [
        'exit_interview_completed',
        'assets_cleared',
        'documents_cleared',
        'payroll_cleared',
        'full_final_settlement_completed',
        'experience_letter_issued',
        'relieving_letter_issued',
        'account_deactivated',
    ]:
        setattr(resignation, field, request.POST.get(field) == 'on')

    if resignation.status == 'NOTICE_PERIOD':
        resignation.status = 'EXIT_PROCESS'

    if all([
        resignation.handover_status == 'COMPLETED',
        resignation.exit_interview_completed,
        resignation.assets_cleared,
        resignation.documents_cleared,
        resignation.payroll_cleared,
        resignation.full_final_settlement_completed,
        resignation.experience_letter_issued,
        resignation.relieving_letter_issued,
        resignation.account_deactivated,
    ]):
        resignation.status = 'COMPLETED'
        resignation.exit_date = resignation.exit_date or timezone.localdate()

    resignation.save()

    _audit(request.user, f'Updated offboarding - {resignation.employee.employee_id}')
    messages.success(request, 'Offboarding checklist updated successfully.')
    return redirect('resignation_detail', pk=pk)
