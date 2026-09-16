from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.employees.models import Employee

from .forms import ExitCaseForm, ExitClearanceForm, ExitInterviewForm, FinalSettlementForm, HRRequestForm
from .models import (
    Designation, EmploymentHistory, ExitCase, ExitClearance, ExitDocument, ExitInterview,
    FinalSettlement, HRRequest, JobGrade, Location, RehireRecord, Team,
)


MANAGE_ROLES = {'MASTER_ADMIN', 'FOUNDER', 'HR', 'CEO', 'ADMIN', 'SUPERVISOR', 'HR_ADMIN'}


def _role(user):
    return getattr(user, 'access_role', None) or getattr(user, 'portal_role', None) or getattr(user, 'role', None)


def _can_manage(user):
    if not user.is_authenticated:
        return False
    return bool(user.is_superuser or _role(user) in MANAGE_ROLES)


def _require_manager(request):
    if not _can_manage(request.user):
        messages.error(request, 'You do not have permission to manage workforce operations.')
        return redirect('dashboard')
    return None


@login_required
def workforce_home(request):
    blocker = _require_manager(request)
    if blocker:
        return blocker
    context = {
        'total_employees': Employee.objects.count(),
        'active_employees': Employee.objects.filter(status='ACTIVE').count(),
        'exit_in_progress': ExitCase.objects.filter(status__in=['PENDING_APPROVAL', 'APPROVED', 'IN_PROGRESS']).count(),
        'pending_clearance': ExitClearance.objects.filter(status='PENDING').count(),
        'open_hr_requests': HRRequest.objects.filter(status__in=['OPEN', 'IN_PROGRESS', 'WAITING']).count(),
        'departments': Employee.objects.values('department__name').annotate(total=Count('id')).order_by('-total')[:6],
        'recent_history': EmploymentHistory.objects.select_related('employee', 'employee__user')[:8],
        'recent_exits': ExitCase.objects.select_related('employee', 'employee__user').order_by('-created_at')[:8],
    }
    return render(request, 'workforce/home.html', context)


@login_required
def employee_360(request, pk):
    employee = get_object_or_404(
        Employee.objects.select_related('user', 'department', 'reporting_manager'), pk=pk
    )
    role = _role(request.user)
    is_self = hasattr(request.user, 'employee') and getattr(request.user.employee, 'pk', None) == employee.pk
    if not (_can_manage(request.user) or is_self or role in {'CEO', 'FOUNDER'}):
        messages.error(request, 'You do not have permission to view this employee.')
        return redirect('dashboard')
    context = {
        'employee': employee,
        'history': EmploymentHistory.objects.filter(employee=employee),
        'exit_cases': ExitCase.objects.filter(employee=employee),
        'requests': HRRequest.objects.filter(employee=employee)[:10],
        'rehire_records': RehireRecord.objects.filter(employee=employee),
    }
    return render(request, 'workforce/employee_360.html', context)


@login_required
def exit_list(request):
    blocker = _require_manager(request)
    if blocker:
        return blocker
    exits = ExitCase.objects.select_related('employee', 'employee__user').all()
    q = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    exit_type = request.GET.get('exit_type', '').strip()
    if q:
        exits = exits.filter(Q(employee__employee_id__icontains=q) | Q(employee__user__first_name__icontains=q) | Q(employee__user__last_name__icontains=q))
    if status:
        exits = exits.filter(status=status)
    if exit_type:
        exits = exits.filter(exit_type=exit_type)
    return render(request, 'workforce/exit_list.html', {'exits': exits, 'status': status, 'exit_type': exit_type, 'q': q, 'statuses': ExitCase.STATUSES, 'types': ExitCase.TYPES})


@login_required
def exit_create(request):
    blocker = _require_manager(request)
    if blocker:
        return blocker
    if request.method == 'POST':
        form = ExitCaseForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.created_by = request.user
            obj.status = 'PENDING_APPROVAL'
            obj.save()
            for name in ['Manager', 'HR', 'Finance', 'IT', 'Admin', 'Asset Management']:
                ExitClearance.objects.get_or_create(exit_case=obj, department_name=name)
            messages.success(request, 'Exit case created and sent for approval.')
            return redirect('workforce:exit_detail', obj.pk)
    else:
        form = ExitCaseForm()
    return render(request, 'workforce/exit_form.html', {'form': form, 'title': 'Create Exit Case'})


@login_required
def exit_detail(request, pk):
    blocker = _require_manager(request)
    if blocker:
        return blocker
    exit_case = get_object_or_404(ExitCase.objects.select_related('employee', 'employee__user'), pk=pk)
    settlement, _ = FinalSettlement.objects.get_or_create(exit_case=exit_case)
    interview, _ = ExitInterview.objects.get_or_create(exit_case=exit_case)
    return render(request, 'workforce/exit_detail.html', {'exit_case': exit_case, 'settlement': settlement, 'interview': interview, 'service_text': exit_case.service_text})


@login_required
def exit_action(request, pk, action):
    blocker = _require_manager(request)
    if blocker:
        return blocker
    obj = get_object_or_404(ExitCase, pk=pk)
    if action == 'approve':
        obj.status = 'APPROVED'; obj.approved_by = request.user; obj.approved_at = timezone.now()
        obj.save(update_fields=['status', 'approved_by', 'approved_at', 'updated_at'])
        messages.success(request, 'Exit case approved.')
    elif action == 'start':
        obj.status = 'IN_PROGRESS'; obj.save(update_fields=['status', 'updated_at']); messages.success(request, 'Exit process started.')
    elif action == 'complete':
        obj.status = 'COMPLETED';
        if obj.actual_last_working_day:
            obj.employee.exit_date = obj.actual_last_working_day
            obj.employee.status = 'INACTIVE'
            obj.employee.save(update_fields=['exit_date', 'status'])
        messages.success(request, 'Exit completed and employee marked inactive.')
    elif action == 'reject':
        obj.status = 'REJECTED'; obj.save(update_fields=['status', 'updated_at']); messages.warning(request, 'Exit case rejected.')
    elif action == 'cancel':
        obj.status = 'CANCELLED'; obj.save(update_fields=['status', 'updated_at']); messages.info(request, 'Exit case cancelled.')
    return redirect('workforce:exit_detail', obj.pk)


@login_required
def clearance_update(request, pk):
    blocker = _require_manager(request)
    if blocker:
        return blocker
    obj = get_object_or_404(ExitClearance, pk=pk)
    if request.method == 'POST':
        form = ExitClearanceForm(request.POST, instance=obj)
        if form.is_valid():
            obj = form.save(commit=False)
            if obj.status in {'CLEARED', 'NA'}:
                obj.cleared_by = request.user; obj.cleared_at = timezone.now()
            obj.save()
            messages.success(request, 'Clearance updated.')
            return redirect('workforce:exit_detail', obj.exit_case_id)
    else:
        form = ExitClearanceForm(instance=obj)
    return render(request, 'workforce/form.html', {'form': form, 'title': f'{obj.department_name} Clearance'})


@login_required
def interview_update(request, pk):
    blocker = _require_manager(request)
    if blocker:
        return blocker
    obj = get_object_or_404(ExitInterview, pk=pk)
    if request.method == 'POST':
        form = ExitInterviewForm(request.POST, instance=obj)
        if form.is_valid():
            obj = form.save(commit=False); obj.completed_at = timezone.now(); obj.save()
            messages.success(request, 'Exit interview saved.')
            return redirect('workforce:exit_detail', obj.exit_case_id)
    else:
        form = ExitInterviewForm(instance=obj)
    return render(request, 'workforce/form.html', {'form': form, 'title': 'Exit Interview'})


@login_required
def settlement_update(request, pk):
    blocker = _require_manager(request)
    if blocker:
        return blocker
    obj = get_object_or_404(FinalSettlement, pk=pk)
    if request.method == 'POST':
        form = FinalSettlementForm(request.POST, instance=obj)
        if form.is_valid():
            obj = form.save(commit=False); obj.status = 'HR_REVIEW'; obj.reviewed_by = request.user; obj.save()
            messages.success(request, 'Final settlement saved for review.')
            return redirect('workforce:exit_detail', obj.exit_case_id)
    else:
        form = FinalSettlementForm(instance=obj)
    return render(request, 'workforce/form.html', {'form': form, 'title': 'Full & Final Settlement'})


@login_required
def exit_document(request, pk, document_type):
    blocker = _require_manager(request)
    if blocker:
        return blocker
    obj = get_object_or_404(ExitCase.objects.select_related('employee', 'employee__user', 'employee__department'), pk=pk)
    allowed = dict(ExitDocument.TYPES)
    if document_type not in allowed:
        messages.error(request, 'Unknown exit document type.')
        return redirect('workforce:exit_detail', pk)
    doc, _ = ExitDocument.objects.get_or_create(exit_case=obj, document_type=document_type, defaults={'generated_by': request.user})
    return render(request, 'workforce/exit_document.html', {'exit_case': obj, 'document': doc, 'document_title': allowed[document_type], 'service_text': obj.service_text})


@login_required
def request_list(request):
    role = _role(request.user)
    if _can_manage(request.user):
        requests = HRRequest.objects.select_related('employee', 'employee__user', 'assigned_to').all()
    else:
        employee = getattr(request.user, 'employee', None)
        requests = HRRequest.objects.filter(employee=employee) if employee else HRRequest.objects.none()
    return render(request, 'workforce/request_list.html', {'requests': requests, 'can_manage': _can_manage(request.user)})


@login_required
def request_create(request):
    employee = getattr(request.user, 'employee', None)
    if not employee:
        messages.error(request, 'An employee profile is required to create an HR request.')
        return redirect('dashboard')
    if request.method == 'POST':
        form = HRRequestForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False); obj.employee = employee; obj.save()
            messages.success(request, 'HR request submitted.')
            return redirect('workforce:request_list')
    else:
        form = HRRequestForm()
    return render(request, 'workforce/form.html', {'form': form, 'title': 'New HR Request'})


@login_required
def organization(request):
    blocker = _require_manager(request)
    if blocker:
        return blocker
    return render(request, 'workforce/organization.html', {
        'locations': Location.objects.filter(is_active=True), 'teams': Team.objects.select_related('department', 'team_lead'),
        'designations': Designation.objects.filter(is_active=True), 'grades': JobGrade.objects.filter(is_active=True),
    })
