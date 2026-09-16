from datetime import datetime
import calendar
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.http import HttpResponse
from django.conf import settings
from django.utils.html import escape

from apps.employees.models import Department, Employee, EmployeeLifecycle
from .models import (
    Applicant, JobRequirement, HiringRequest, JobRequirementExtra,
    CandidateProfile, Interview, InterviewFeedback, Offer,
    BackgroundVerification, OnboardingTask, RecruitmentActivity, JobPosting, Assessment,
)

User = get_user_model()

try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
except ImportError:  # pragma: no cover
    colors = None
    TA_CENTER = TA_LEFT = TA_RIGHT = A4 = None
    ParagraphStyle = getSampleStyleSheet = SimpleDocTemplate = Paragraph = Spacer = Table = TableStyle = None


def _can_manage(request):
    role = getattr(request.user, 'role', None)
    portal_role = getattr(request.user, 'portal_role', None)
    return role in {'SUPERVISOR', 'HR_ADMIN', 'HR', 'CEO', 'FOUNDER'} or portal_role in {'ADMIN', 'HR', 'CEO', 'FOUNDER'}


def _manager_required(request):
    if not _can_manage(request):
        messages.error(request, 'You do not have permission to manage recruitment.')
        return False
    return True


def _get_or_create_profile(applicant):
    profile, _ = CandidateProfile.objects.get_or_create(applicant=applicant)
    return profile


def _record(candidate=None, requirement=None, actor=None, action='', from_stage='', to_stage='', notes=''):
    RecruitmentActivity.objects.create(
        candidate=candidate, requirement=requirement or (candidate.applicant.requirement if candidate else None),
        actor=actor, action=action, from_stage=from_stage, to_stage=to_stage, notes=notes
    )



def _department_name(value):
    if not value:
        return ''
    return getattr(value, 'name', value) or ''


def _requirement_extra(requirement):
    try:
        return requirement.workflow_extra
    except Exception:
        return None


def _department_managers(department_name):
    """Return active employees who are sensible manager/assessor choices for a department."""
    qs = Employee.objects.select_related('user', 'department').filter(status='ACTIVE')
    name = _department_name(department_name).strip()
    if name:
        qs = qs.filter(department__name__iexact=name)
    # Prefer department heads, employees with direct reports, and manager/lead roles.
    ids = []
    if name:
        head = Department.objects.select_related('head_employee', 'head_employee__user').filter(name__iexact=name).first()
        if head and head.head_employee_id:
            ids.append(head.head_employee_id)
    managers = list(qs.filter(
        Q(id__in=ids)
        | Q(subordinates__isnull=False)
        | Q(designation__icontains='manager')
        | Q(designation__icontains='lead')
        | Q(designation__icontains='head')
        | Q(designation__icontains='supervisor')
    ).distinct().order_by('user__first_name', 'user__last_name', 'employee_id'))
    if not managers:
        managers = list(qs.order_by('user__first_name', 'user__last_name', 'employee_id'))
    return managers


def _employee_name(employee):
    if not employee:
        return ''
    return employee.user.get_full_name().strip() or employee.employee_id


def _parse_int(value, default=0, minimum=None, maximum=None):
    try:
        result = int(value)
    except (TypeError, ValueError):
        result = default
    if minimum is not None:
        result = max(minimum, result)
    if maximum is not None:
        result = min(maximum, result)
    return result


def _parse_decimal(value, default=None):
    from decimal import Decimal, InvalidOperation
    if value in (None, ''):
        return default
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return default


def _next_employee_id():
    """Return the next ABC employee id, excluding contractor-style ABCC ids."""
    highest = 0
    for value in Employee.objects.values_list('employee_id', flat=True):
        if isinstance(value, str) and value.startswith('ABC') and not value.startswith('ABCC'):
            tail = value[3:]
            if tail.isdigit():
                highest = max(highest, int(tail))
    return f'ABC{highest + 1}'


def _add_months(value, months):
    if not value or not months:
        return value
    month_index = value.month - 1 + int(months)
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return value.replace(year=year, month=month, day=day)

def career_page(request):
    postings = JobPosting.objects.filter(status='PUBLISHED').select_related('requirement', 'requirement__workflow_extra').order_by('-published_at')
    return render(request, 'recruitment/career.html', {'postings': postings})


@login_required
def job_posting_manage(request, pk):
    if not _manager_required(request):
        return redirect('recruitment_dashboard')
    requirement = get_object_or_404(JobRequirement, pk=pk)
    posting, _ = JobPosting.objects.get_or_create(
        requirement=requirement,
        defaults={'slug': f'{requirement.pk}-{requirement.title.lower().replace(" ", "-")[:150]}', 'headline': requirement.title, 'public_description': requirement.description}
    )
    if request.method == 'POST':
        from django.utils.text import slugify
        posting.headline = request.POST.get('headline', requirement.title).strip()
        posting.slug = slugify(request.POST.get('slug') or posting.headline)[:180] + (f'-{requirement.pk}' if not str(requirement.pk) in slugify(request.POST.get('slug') or posting.headline) else '')
        posting.public_description = request.POST.get('public_description', '').strip()
        posting.application_instructions = request.POST.get('application_instructions', '').strip()
        posting.status = request.POST.get('status', 'DRAFT')
        posting.published_at = timezone.now() if posting.status == 'PUBLISHED' and not posting.published_at else posting.published_at
        posting.closed_at = timezone.now() if posting.status == 'CLOSED' else None
        posting.save()
        requirement.status = 'CLOSED' if posting.status == 'CLOSED' else 'OPEN'
        requirement.save(update_fields=['status'])
        messages.success(request, 'Job posting updated.')
        return redirect('requirement_detail', pk=pk)
    return render(request, 'recruitment/job_posting_manage.html', {'requirement': requirement, 'posting': posting, 'statuses': JobPosting.STATUS_CHOICES})


@login_required
def recruitment_dashboard(request):
    requirements = JobRequirement.objects.all().order_by('-created_at')
    applicants = Applicant.objects.select_related('requirement').all()
    profiles = CandidateProfile.objects.select_related('applicant', 'applicant__requirement')
    recent_requirements = []
    for req in requirements[:8]:
        req.application_count = applicants.filter(requirement=req).count()
        recent_requirements.append(req)
    context = {
        'open_positions': requirements.filter(status='OPEN').count(),
        'total_requirements': requirements.count(),
        'total_applicants': applicants.count(),
        'screening_count': profiles.filter(stage__in=['SCREENING', 'HR_SCREENING']).count(),
        'shortlisted_count': profiles.filter(stage='SHORTLISTED').count(),
        'interview_count': profiles.filter(stage='INTERVIEW').count(),
        'selected_count': profiles.filter(stage='SELECTED').count(),
        'offer_pending_count': Offer.objects.filter(status__in=['DRAFT', 'PENDING_APPROVAL', 'GENERATED', 'SENT', 'VIEWED']).count(),
        'joined_count': profiles.filter(stage='JOINED').count(),
        'stage_cards': [(label, profiles.filter(stage=key).count()) for key, label in CandidateProfile.STAGE_CHOICES if key not in {'REJECTED','WITHDRAWN'}],
        'recent_requirements': recent_requirements,
        'recent_candidates': profiles[:8],
    }
    return render(request, 'recruitment/dashboard.html', context)


@login_required
def hiring_request_list(request):
    if not _manager_required(request):
        return redirect('recruitment_dashboard')
    requests = HiringRequest.objects.select_related('requested_by', 'approved_by')
    q = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    if q:
        requests = requests.filter(Q(request_number__icontains=q) | Q(position_title__icontains=q) | Q(department__icontains=q))
    if status:
        requests = requests.filter(status=status)
    return render(request, 'recruitment/hiring_requests.html', {'requests': requests, 'q': q, 'status': status, 'status_choices': HiringRequest.STATUS_CHOICES})


@login_required
def hiring_request_create(request):
    if not _manager_required(request):
        return redirect('recruitment_dashboard')
    if request.method == 'POST':
        obj = HiringRequest.objects.create(
            requested_by=request.user,
            department=request.POST.get('department', '').strip(),
            position_title=request.POST.get('position_title', '').strip(),
            openings=int(request.POST.get('openings') or 1),
            reason=request.POST.get('reason', '').strip(),
            employment_type=request.POST.get('employment_type', '').strip(),
            priority=request.POST.get('priority', 'MEDIUM'),
            required_by=request.POST.get('required_by') or None,
        )
        messages.success(request, f'Hiring request {obj.request_number} created.')
        return redirect('hiring_request_list')
    return render(request, 'recruitment/hiring_request_create.html', {'departments': Department.objects.order_by('name')})


@login_required
def hiring_request_approve(request, pk):
    if not _manager_required(request):
        return redirect('recruitment_dashboard')
    obj = get_object_or_404(HiringRequest, pk=pk)
    obj.status = 'APPROVED'
    obj.approved_by = request.user
    obj.approved_at = timezone.now()
    obj.save(update_fields=['status', 'approved_by', 'approved_at', 'updated_at'])
    messages.success(request, f'{obj.request_number} approved.')
    return redirect('hiring_request_list')


@login_required
def hiring_request_reject(request, pk):
    if not _manager_required(request):
        return redirect('recruitment_dashboard')
    obj = get_object_or_404(HiringRequest, pk=pk)
    obj.status = 'REJECTED'
    obj.save(update_fields=['status', 'updated_at'])
    messages.success(request, f'{obj.request_number} rejected.')
    return redirect('hiring_request_list')


@login_required
def requirement_list(request):
    """
    Display all job requirements with live recruitment pipeline counts.

    The template receives ``rows`` containing:
    - requirement
    - applicant_count
    - interview_count
    - selected_count
    - joined_count
    - rejected_count
    """

    requirements = (
        JobRequirement.objects
        .all()
        .order_by('-created_at')
    )

    q = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()

    if q:
        requirements = requirements.filter(
            Q(title__icontains=q)
            | Q(department__icontains=q)
            | Q(experience__icontains=q)
        )

    if status:
        requirements = requirements.filter(status=status)

    rows = []

    for requirement in requirements:
        applicants = Applicant.objects.filter(
            requirement=requirement
        )

        profiles = CandidateProfile.objects.filter(
            applicant__in=applicants
        )

        rows.append({
            'requirement': requirement,
            'applicant_count': applicants.count(),
            'interview_count': profiles.filter(
                stage='INTERVIEW'
            ).count(),
            'selected_count': profiles.filter(
                stage='SELECTED'
            ).count(),
            'joined_count': profiles.filter(
                stage='JOINED'
            ).count(),
            'rejected_count': profiles.filter(
                stage='REJECTED'
            ).count(),
        })

    return render(
        request,
        'recruitment/requirements.html',
        {
            'rows': rows,
            'q': q,
            'status': status,
        }
    )


@login_required
def requirement_create(request):
    if not _manager_required(request):
        return redirect('recruitment_dashboard')
    if request.method == 'POST':
        req = JobRequirement.objects.create(
            title=request.POST.get('title', '').strip(),
            department=request.POST.get('department', '').strip(),
            openings=int(request.POST.get('openings') or 1),
            experience=request.POST.get('experience', '').strip(),
            description=request.POST.get('description', '').strip(),
            status='OPEN',
        )
        JobRequirementExtra.objects.create(
            requirement=req,
            hiring_request_id=request.POST.get('hiring_request') or None,
            employment_type=request.POST.get('employment_type', '').strip(),
            work_mode=request.POST.get('work_mode', '').strip(),
            location=request.POST.get('location', '').strip(),
            qualification=request.POST.get('qualification', '').strip(),
            salary_min=request.POST.get('salary_min') or None,
            salary_max=request.POST.get('salary_max') or None,
            notice_period=request.POST.get('notice_period', '').strip(),
            joining_timeline=request.POST.get('joining_timeline', '').strip(),
            responsibilities=request.POST.get('responsibilities', '').strip(),
            required_skills=request.POST.get('required_skills', '').strip(),
            preferred_skills=request.POST.get('preferred_skills', '').strip(),
            education=request.POST.get('education', '').strip(),
            certifications=request.POST.get('certifications', '').strip(),
            recruiter_name=request.POST.get('recruiter_name', '').strip(),
            hiring_manager=request.POST.get('hiring_manager', '').strip(),
            target_hiring_date=request.POST.get('target_hiring_date') or None,
            application_deadline=request.POST.get('application_deadline') or None,
            priority=request.POST.get('priority', 'MEDIUM'),
            published_at=timezone.now(),
        )
        messages.success(request, 'Job requirement created and opened for recruitment.')
        return redirect('requirement_detail', pk=req.pk)
    return render(request, 'recruitment/requirement_create.html', {
        'departments': Department.objects.order_by('name'),
        'hiring_requests': HiringRequest.objects.filter(status='APPROVED'),
    })


@login_required
def requirement_detail(request, pk):
    req = get_object_or_404(JobRequirement, pk=pk)
    extra, _ = JobRequirementExtra.objects.get_or_create(requirement=req)
    profiles = CandidateProfile.objects.filter(applicant__requirement=req).select_related('applicant').order_by('-updated_at')
    return render(request, 'recruitment/requirement_detail.html', {'requirement': req, 'extra': extra, 'profiles': profiles})


@login_required
def requirement_close(request, pk):
    if not _manager_required(request):
        return redirect('recruitment_dashboard')
    req = get_object_or_404(JobRequirement, pk=pk)
    req.status = 'CLOSED'
    req.save(update_fields=['status'])
    messages.success(request, 'Job requirement closed.')
    return redirect('requirement_detail', pk=pk)


@login_required
def applicants_list(request, requirement_id=None):
    qs = Applicant.objects.select_related('requirement').all().order_by('-id')
    if requirement_id:
        qs = qs.filter(requirement_id=requirement_id)
        requirement = get_object_or_404(JobRequirement, pk=requirement_id)
    else:
        requirement = None
    q = request.GET.get('q', '').strip()
    stage = request.GET.get('stage', '').strip()
    if q:
        qs = qs.filter(Q(full_name__icontains=q) | Q(email__icontains=q) | Q(phone__icontains=q))
    rows = []
    for a in qs:
        profile = _get_or_create_profile(a)
        if stage and profile.stage != stage:
            continue
        rows.append((a, profile))
    return render(request, 'recruitment/candidates.html', {'rows': rows, 'requirement': requirement, 'q': q, 'stage': stage, 'stages': CandidateProfile.STAGE_CHOICES})


@login_required
def candidate_create(request):
    if not _manager_required(request):
        return redirect('recruitment_dashboard')
    if request.method == 'POST':
        req = get_object_or_404(JobRequirement, pk=request.POST.get('requirement'))
        data = dict(
            requirement=req,
            full_name=request.POST.get('full_name', '').strip(),
            email=request.POST.get('email', '').strip(),
            phone=request.POST.get('phone', '').strip(),
        )
        if 'resume' in [f.name for f in Applicant._meta.fields]:
            data['resume'] = request.FILES.get('resume')
        applicant = Applicant.objects.create(**data)
        profile = CandidateProfile.objects.create(
            applicant=applicant, source=request.POST.get('source', 'DIRECT'),
            current_company=request.POST.get('current_company', '').strip(),
            current_designation=request.POST.get('current_designation', '').strip(),
            location=request.POST.get('location', '').strip(),
            qualification=request.POST.get('qualification', '').strip(),
            skills=request.POST.get('skills', '').strip(),
            total_experience_years=request.POST.get('total_experience_years') or None,
            expected_salary=request.POST.get('expected_salary') or None,
        )
        _record(profile, actor=request.user, action='Candidate Created', to_stage='APPLIED')
        messages.success(request, 'Candidate added to the recruitment pipeline.')
        return redirect('candidate_detail', pk=applicant.pk)
    return render(request, 'recruitment/candidate_create.html', {'requirements': JobRequirement.objects.filter(status='OPEN'), 'sources': CandidateProfile.SOURCE_CHOICES})


@login_required
@login_required
def candidate_detail(request, pk):
    applicant = get_object_or_404(Applicant.objects.select_related('requirement'), pk=pk)
    profile = _get_or_create_profile(applicant)
    interviews = profile.interviews.select_related('feedback', 'interviewer_employee').all()
    assessments = profile.assessments.select_related('assessor_employee').all()
    offer = getattr(profile, 'offer', None)
    background = getattr(profile, 'background_check', None)
    tasks = profile.onboarding_tasks.all()
    activities = profile.activities.all()[:30]
    managers = _department_managers(applicant.requirement.department)
    extra = _requirement_extra(applicant.requirement)
    stage_items = [(key, label) for key, label in CandidateProfile.STAGE_CHOICES if key not in {'REJECTED', 'WITHDRAWN'}]
    stage_index = next((i for i, (key, _) in enumerate(stage_items) if key == profile.stage), 0)
    return render(request, 'recruitment/candidate_detail.html', {
        'applicant': applicant,
        'profile': profile,
        'interviews': interviews,
        'assessments': assessments,
        'offer': offer,
        'background': background,
        'tasks': tasks,
        'activities': activities,
        'stages': CandidateProfile.STAGE_CHOICES,
        'stage_items': stage_items,
        'stage_index': stage_index,
        'sources': CandidateProfile.SOURCE_CHOICES,
        'interview_rounds': Interview.ROUND_CHOICES,
        'interview_modes': Interview.MODE_CHOICES,
        'assessment_statuses': Assessment.STATUS_CHOICES,
        'assessment_types': getattr(Assessment, 'TYPE_CHOICES', []),
        'offer_statuses': Offer.STATUS_CHOICES,
        'department_managers': managers,
        'department_extra': extra,
        'today': timezone.localdate(),
        'candidate_employee': profile.employee,
    })



@login_required
def candidate_stage(request, pk):
    if not _manager_required(request):
        return redirect('candidate_detail', pk=pk)
    applicant = get_object_or_404(Applicant, pk=pk)
    profile = _get_or_create_profile(applicant)
    old = profile.stage
    new = request.POST.get('stage', old)
    valid = {key for key, _ in CandidateProfile.STAGE_CHOICES}
    if new not in valid:
        messages.error(request, 'Invalid recruitment stage.')
        return redirect('candidate_detail', pk=pk)
    profile.stage = new
    profile.notes = request.POST.get('notes', profile.notes).strip()
    profile.save()
    _record(profile, actor=request.user, action='Stage Changed', from_stage=old, to_stage=new, notes=profile.notes)
    messages.success(request, f'Candidate moved to {profile.get_stage_display()}.')
    return redirect('candidate_detail', pk=pk)


@login_required
@login_required
def interview_create(request, pk):
    if not _manager_required(request):
        return redirect('candidate_detail', pk=pk)
    applicant = get_object_or_404(Applicant.objects.select_related('requirement'), pk=pk)
    profile = _get_or_create_profile(applicant)
    if request.method != 'POST':
        return redirect('candidate_detail', pk=pk)
    ABCeduled_raw = request.POST.get('ABCeduled_at', '').strip()
    try:
        ABCeduled_at = datetime.fromisoformat(ABCeduled_raw)
    except (TypeError, ValueError):
        messages.error(request, 'Please provide a valid interview date and time.')
        return redirect('candidate_detail', pk=pk)
    if timezone.is_naive(ABCeduled_at):
        ABCeduled_at = timezone.make_aware(ABCeduled_at)
    interviewer_employee = Employee.objects.filter(
        pk=request.POST.get('interviewer_employee')
    ).first()
    managers = _department_managers(applicant.requirement.department)
    allowed_ids = {employee.pk for employee in managers}
    if interviewer_employee and interviewer_employee.pk not in allowed_ids:
        messages.error(request, 'Please select an interviewer from the candidate department manager list.')
        return redirect('candidate_detail', pk=pk)
    interviewer = _employee_name(interviewer_employee) or request.POST.get('interviewer', '').strip()
    if not interviewer:
        messages.error(request, 'Please select an interviewer.')
        return redirect('candidate_detail', pk=pk)
    try:
        interview = Interview.objects.create(
            candidate=profile,
            round_name=request.POST.get('round_name', 'HR_SCREENING'),
            interview_type=request.POST.get('interview_type', 'ONLINE'),
            ABCeduled_at=ABCeduled_at,
            duration_minutes=_parse_int(request.POST.get('duration_minutes'), 30, 15, 480),
            interviewer=interviewer,
            interviewer_employee=interviewer_employee,
            meeting_link=request.POST.get('meeting_link', '').strip(),
            location=request.POST.get('location', '').strip(),
            panel_members=request.POST.get('panel_members', '').strip(),
            notes=request.POST.get('notes', '').strip(),
            created_by=request.user,
        )
    except Exception as exc:
        messages.error(request, f'Unable to ABCedule interview: {exc}')
        return redirect('candidate_detail', pk=pk)
    profile.stage = 'INTERVIEW'
    profile.save(update_fields=['stage', 'updated_at'])
    _record(profile, actor=request.user, action='Interview ABCeduled', to_stage='INTERVIEW', notes=interviewer_note(interview))
    messages.success(request, 'Interview ABCeduled successfully.')
    return redirect('candidate_detail', pk=pk)



@login_required
@login_required
def assessment_create(request, pk):
    if not _manager_required(request):
        return redirect('candidate_detail', pk=pk)
    applicant = get_object_or_404(Applicant.objects.select_related('requirement'), pk=pk)
    profile = _get_or_create_profile(applicant)
    if request.method != 'POST':
        return redirect('candidate_detail', pk=pk)
    assessor_employee = Employee.objects.filter(pk=request.POST.get('assessor_employee')).first()
    managers = _department_managers(applicant.requirement.department)
    allowed_ids = {employee.pk for employee in managers}
    if assessor_employee and assessor_employee.pk not in allowed_ids:
        messages.error(request, 'Please select an assessor from the candidate department manager list.')
        return redirect('candidate_detail', pk=pk)
    assessor = _employee_name(assessor_employee) or request.POST.get('assessor', '').strip()
    if not assessor:
        messages.error(request, 'Please select an assessor.')
        return redirect('candidate_detail', pk=pk)
    assessment_name = request.POST.get('assessment_name', '').strip()
    if not assessment_name:
        messages.error(request, 'Assessment name is required.')
        return redirect('candidate_detail', pk=pk)
    assessment_type = request.POST.get('assessment_type', 'TECHNICAL')
    valid_types = {key for key, _ in getattr(Assessment, 'TYPE_CHOICES', [])}
    if valid_types and assessment_type not in valid_types:
        assessment_type = 'TECHNICAL'
    try:
        assessment = Assessment.objects.create(
            candidate=profile,
            assessment_name=assessment_name,
            assessment_type=assessment_type,
            assessor=assessor,
            assessor_employee=assessor_employee,
            ABCeduled_at=request.POST.get('ABCeduled_at') or None,
            due_at=request.POST.get('due_at') or None,
            duration_minutes=_parse_int(request.POST.get('duration_minutes'), 60, 15, 1440),
            max_score=_parse_decimal(request.POST.get('max_score'), 100),
            passing_score=_parse_decimal(request.POST.get('passing_score'), 60),
            instructions=request.POST.get('instructions', '').strip(),
            status=request.POST.get('status', 'PENDING'),
            created_by=request.user,
        )
    except Exception as exc:
        messages.error(request, f'Unable to create assessment: {exc}')
        return redirect('candidate_detail', pk=pk)
    if assessment.status == 'PENDING':
        profile.stage = 'ASSESSMENT'
        profile.save(update_fields=['stage', 'updated_at'])
    _record(profile, actor=request.user, action='Assessment Created', to_stage=profile.stage, notes=f'{assessment.get_assessment_type_display()} — {assessment.assessment_name}')
    messages.success(request, 'Assessment created successfully.')
    return redirect('candidate_detail', pk=pk)



@login_required
@login_required
def assessment_update(request, pk):
    if not _manager_required(request):
        return redirect('recruitment_dashboard')
    assessment = get_object_or_404(Assessment, pk=pk)
    if request.method != 'POST':
        return redirect('candidate_detail', pk=assessment.candidate.applicant_id)
    assessment.score = _parse_decimal(request.POST.get('score'), None)
    assessment.max_score = _parse_decimal(request.POST.get('max_score'), assessment.max_score or 100)
    assessment.passing_score = _parse_decimal(request.POST.get('passing_score'), getattr(assessment, 'passing_score', 60))
    assessment.result = request.POST.get('result', '').strip()
    assessment.feedback = request.POST.get('feedback', '').strip()
    assessment.status = request.POST.get('status', assessment.status)
    if assessment.status == 'COMPLETED' and not assessment.result:
        if assessment.score is not None and assessment.max_score:
            assessment.result = 'PASS' if assessment.score >= assessment.passing_score else 'FAIL'
    assessment.save()
    profile = assessment.candidate
    if assessment.status == 'COMPLETED':
        profile.stage = 'SELECTED' if assessment.result.upper() in {'PASS', 'PASSED', 'SELECT', 'SELECTED'} else 'SCREENING'
        profile.save(update_fields=['stage', 'updated_at'])
        _record(profile, actor=request.user, action='Assessment Completed', to_stage=profile.stage, notes=assessment.result)
    messages.success(request, 'Assessment updated successfully.')
    return redirect('candidate_detail', pk=assessment.candidate.applicant_id)



def interviewer_note(interview):
    return f'{interview.get_round_name_display()} with {interview.interviewer}'


@login_required
def interview_feedback(request, pk):
    if not _manager_required(request):
        return redirect('recruitment_dashboard')
    interview = get_object_or_404(Interview, pk=pk)
    feedback = getattr(interview, 'feedback', None)
    if request.method == 'POST':
        feedback, _ = InterviewFeedback.objects.get_or_create(interview=interview)
        for field in ['technical_skills', 'communication', 'problem_solving', 'culture_fit']:
            try:
                value = max(0, min(5, int(request.POST.get(field) or 0)))
            except (TypeError, ValueError):
                value = 0
            setattr(feedback, field, value)
        try:
            supplied_overall = float(request.POST.get('overall_rating') or 0)
        except (TypeError, ValueError):
            supplied_overall = 0
        feedback.overall_rating = max(0, min(5, supplied_overall))
        if feedback.overall_rating == 0:
            feedback.overall_rating = round((feedback.technical_skills + feedback.communication + feedback.problem_solving + feedback.culture_fit) / 4, 1)
        feedback.recommendation = request.POST.get('recommendation', 'HOLD')
        if feedback.recommendation not in {key for key, _ in InterviewFeedback.RECOMMENDATIONS}:
            feedback.recommendation = 'HOLD'
        feedback.comments = request.POST.get('comments', '').strip()
        feedback.submitted_by = request.user
        feedback.save()
        interview.status = 'COMPLETED'
        interview.save(update_fields=['status'])
        profile = interview.candidate
        if feedback.recommendation == 'REJECT':
            profile.stage = 'REJECTED'
        elif feedback.recommendation in {'HIRE', 'STRONG_HIRE'}:
            profile.stage = 'SELECTED'
        else:
            profile.stage = 'SCREENING'
        profile.save(update_fields=['stage', 'updated_at'])
        _record(profile, actor=request.user, action='Interview Feedback Submitted', to_stage=profile.stage, notes=feedback.comments)
        messages.success(request, 'Interview feedback saved.')
        return redirect('candidate_detail', pk=interview.candidate.applicant_id)
    return render(request, 'recruitment/interview_feedback.html', {'interview': interview, 'feedback': feedback, 'recommendations': InterviewFeedback.RECOMMENDATIONS})


@login_required
@login_required
def offer_create(request, pk):
    if not _manager_required(request):
        return redirect('candidate_detail', pk=pk)
    applicant = get_object_or_404(Applicant.objects.select_related('requirement'), pk=pk)
    profile = _get_or_create_profile(applicant)
    if request.method != 'POST':
        return redirect('candidate_detail', pk=pk)
    managers = _department_managers(applicant.requirement.department)
    manager = Employee.objects.filter(pk=request.POST.get('reporting_manager_employee')).first()
    allowed_ids = {employee.pk for employee in managers}
    if manager and manager.pk not in allowed_ids:
        messages.error(request, 'Please select a reporting manager from the candidate department.')
        return redirect('candidate_detail', pk=pk)
    designation = request.POST.get('designation', applicant.requirement.title).strip()
    department = request.POST.get('department', applicant.requirement.department).strip()
    location = request.POST.get('location', '').strip()
    extra = _requirement_extra(applicant.requirement)
    if not location and extra:
        location = getattr(extra, 'location', '') or ''
    employment_type = request.POST.get('employment_type', getattr(extra, 'employment_type', '') if extra else '').strip()
    work_mode = request.POST.get('work_mode', getattr(extra, 'work_mode', '') if extra else '').strip()
    offered_ctc = _parse_decimal(request.POST.get('offered_ctc'), None)
    joining_date = request.POST.get('joining_date') or None
    expiry_date = request.POST.get('expiry_date') or None
    offer, _ = Offer.objects.get_or_create(candidate=profile, defaults={
        'designation': designation,
        'department': department,
        'created_by': request.user,
    })
    offer.offered_ctc = offered_ctc
    offer.designation = designation
    offer.department = department
    offer.location = location
    offer.reporting_manager = _employee_name(manager)
    offer.reporting_manager_employee = manager
    offer.employment_type = employment_type
    offer.work_mode = work_mode
    offer.probation_months = _parse_int(request.POST.get('probation_months'), 6, 0, 60)
    offer.joining_date = joining_date
    offer.expiry_date = expiry_date
    offer.status = 'PENDING_APPROVAL'
    offer.created_by = offer.created_by or request.user
    offer.save()
    profile.stage = 'OFFER'
    profile.save(update_fields=['stage', 'updated_at'])
    _record(profile, actor=request.user, action='Offer Created', to_stage='OFFER', notes=offer.offer_number)
    messages.success(request, f'Offer {offer.offer_number} is ready for approval.')
    return redirect('candidate_detail', pk=pk)



@login_required
@login_required
def offer_approve(request, pk):
    if not _manager_required(request):
        return redirect('recruitment_dashboard')
    offer = get_object_or_404(Offer.objects.select_related('candidate', 'candidate__applicant'), pk=pk)
    if offer.status not in {'PENDING_APPROVAL', 'DRAFT'}:
        messages.info(request, f'Offer {offer.offer_number} is already {offer.get_status_display().lower()}.')
        return redirect('candidate_detail', pk=offer.candidate.applicant_id)
    offer.status = 'GENERATED'
    offer.approved_by = request.user
    offer.save(update_fields=['status', 'approved_by'])
    _record(offer.candidate, actor=request.user, action='Offer Approved', to_stage='OFFER', notes=offer.offer_number)
    messages.success(request, f'Offer {offer.offer_number} approved and ready to send.')
    return redirect('candidate_detail', pk=offer.candidate.applicant_id)



@login_required

@login_required
def offer_pdf(request, pk):
    if not _manager_required(request):
        return redirect('candidate_detail', pk=pk)
    if SimpleDocTemplate is None:
        messages.error(request, 'PDF generation is unavailable because ReportLab is not installed.')
        return redirect('candidate_detail', pk=pk)
    offer = get_object_or_404(Offer.objects.select_related('candidate', 'candidate__applicant'), pk=pk)
    applicant = offer.candidate.applicant
    company = None
    try:
        from apps.accounts.models import CompanySettings
        company = CompanySettings.objects.first()
    except Exception:
        company = None
    company_name = getattr(company, 'company_name', None) or 'ABC HRMS Portal'
    company_address = getattr(company, 'company_address', None) or 'Bengaluru, Karnataka'
    company_email = getattr(company, 'company_email', None) or 'hr@ABC HRMS Portal.com'
    company_phone = getattr(company, 'company_phone', None) or ''
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{offer.offer_number}.pdf"'
    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=46, leftMargin=46, topMargin=42, bottomMargin=42)
    styles = getSampleStyleSheet()
    title = ParagraphStyle('OfferTitle', parent=styles['Title'], alignment=TA_CENTER, fontSize=17, leading=21, spaceAfter=6)
    small_center = ParagraphStyle('OfferSmall', parent=styles['Normal'], alignment=TA_CENTER, fontSize=8.5, leading=11, textColor=colors.HexColor('#5b6472'))
    body = ParagraphStyle('OfferBody', parent=styles['BodyText'], fontSize=10, leading=15, spaceAfter=8)
    section = ParagraphStyle('OfferSection', parent=styles['Heading3'], fontSize=10.5, leading=13, textColor=colors.HexColor('#173a7a'), spaceBefore=8, spaceAfter=5)
    right = ParagraphStyle('OfferRight', parent=body, alignment=TA_RIGHT)
    story = [
        Paragraph(escape(company_name), title),
        Paragraph(escape(company_address), small_center),
        Paragraph(escape(' | '.join(x for x in [company_email, company_phone] if x)), small_center),
        Spacer(1, 14),
        Paragraph('OFFER OF EMPLOYMENT', title),
        Paragraph(f'<b>Offer No:</b> {escape(offer.offer_number)} &nbsp;&nbsp; <b>Date:</b> {offer.offer_date.strftime("%d %b %Y") if offer.offer_date else timezone.localdate().strftime("%d %b %Y")}', body),
        Paragraph(f'Dear <b>{escape(applicant.full_name)}</b>,', body),
        Paragraph(f'We are pleased to offer you the position of <b>{escape(offer.designation)}</b> with {escape(company_name)}.', body),
        Paragraph('Employment Details', section),
    ]
    rows = [
        ['Position', offer.designation or '-'],
        ['Department', offer.department or '-'],
        ['Reporting Manager', offer.reporting_manager or '-'],
        ['Employment Type', getattr(offer, 'employment_type', '') or '-'],
        ['Work Mode', getattr(offer, 'work_mode', '') or '-'],
        ['Annual CTC', f'₹ {offer.offered_ctc:,.2f}' if offer.offered_ctc is not None else '-'],
        ['Joining Date', offer.joining_date.strftime('%d %b %Y') if offer.joining_date else '-'],
        ['Probation', f'{offer.probation_months} months' if getattr(offer, 'probation_months', 0) else 'No probation'],
        ['Offer Valid Until', offer.expiry_date.strftime('%d %b %Y') if offer.expiry_date else '-'],
    ]
    table = Table(rows, colWidths=[145, 315])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f3f6fb')),
        ('TEXTCOLOR', (0,0), (0,-1), colors.HexColor('#344054')),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (1,0), (1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#d9e0ea')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
    ]))
    story.append(table)
    story += [
        Paragraph('Terms & Conditions', section),
        Paragraph(f'Your employment will be subject to the policies, procedures, confidentiality requirements, and applicable employment terms of {escape(company_name)}. This offer is conditional on completion of the required onboarding and verification formalities.', body),
        Paragraph('Acceptance', section),
        Paragraph('Please sign and return this offer as confirmation of your acceptance. We look forward to welcoming you to the team.', body),
        Spacer(1, 26),
        Paragraph('______________________________ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ______________________________', body),
        Paragraph('Candidate Signature &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; For the Company', small_center),
    ]
    doc.build(story)
    return response

@login_required
def offer_status(request, pk):
    if not _manager_required(request):
        return redirect('recruitment_dashboard')
    offer = get_object_or_404(Offer.objects.select_related('candidate', 'candidate__applicant'), pk=pk)
    status = request.POST.get('status', offer.status).strip().upper()
    valid = {key for key, _ in Offer.STATUS_CHOICES}
    if status not in valid:
        messages.error(request, 'Invalid offer status.')
        return redirect('candidate_detail', pk=offer.candidate.applicant_id)
    if status == 'SENT' and offer.status not in {'GENERATED', 'VIEWED'}:
        messages.error(request, 'Approve the offer before sending it to the candidate.')
        return redirect('candidate_detail', pk=offer.candidate.applicant_id)
    old = offer.status
    offer.status = status
    if status == 'SENT' and not offer.sent_at:
        offer.sent_at = timezone.now()
    if status == 'VIEWED' and not offer.sent_at:
        offer.sent_at = timezone.now()
    if status == 'ACCEPTED':
        offer.accepted_at = timezone.now()
        offer.candidate.stage = 'OFFER_ACCEPTED'
        offer.candidate.save(update_fields=['stage', 'updated_at'])
    elif status == 'DECLINED':
        offer.declined_reason = request.POST.get('declined_reason', offer.declined_reason).strip()
        offer.candidate.stage = 'REJECTED'
        offer.candidate.save(update_fields=['stage', 'updated_at'])
    offer.save()
    _record(offer.candidate, actor=request.user, action='Offer Status Updated', from_stage=old, to_stage=status, notes=offer.declined_reason if status == 'DECLINED' else offer.offer_number)
    messages.success(request, f'Offer {offer.offer_number} updated to {offer.get_status_display()}.')
    return redirect('candidate_detail', pk=offer.candidate.applicant_id)



@login_required
def background_update(request, pk):
    if not _manager_required(request):
        return redirect('candidate_detail', pk=pk)
    profile = _get_or_create_profile(get_object_or_404(Applicant, pk=pk))
    bg, _ = BackgroundVerification.objects.get_or_create(candidate=profile)
    bg.vendor = request.POST.get('vendor', '').strip()
    bg.status = request.POST.get('status', 'IN_PROGRESS')
    for field in ['identity_check', 'address_check', 'education_check', 'employment_check', 'criminal_check']:
        setattr(bg, field, field in request.POST)
    bg.comments = request.POST.get('comments', '').strip()
    if bg.status == 'IN_PROGRESS' and not bg.started_at:
        bg.started_at = timezone.now()
    if bg.status in {'CLEARED', 'ISSUE_FOUND', 'WAIVED'}:
        bg.completed_at = timezone.now()
    bg.save()
    if bg.status == 'CLEARED':
        profile.stage = 'PREBOARDING'
        profile.save(update_fields=['stage', 'updated_at'])
    _record(profile, actor=request.user, action='Background Verification Updated', to_stage=profile.stage, notes=bg.status)
    messages.success(request, 'Background verification updated.')
    return redirect('candidate_detail', pk=pk)


@login_required
def onboarding_task_create(request, pk):
    if not _manager_required(request):
        return redirect('candidate_detail', pk=pk)
    profile = _get_or_create_profile(get_object_or_404(Applicant, pk=pk))
    if request.method == 'POST':
        OnboardingTask.objects.create(
            candidate=profile,
            title=request.POST.get('title', '').strip(),
            category=request.POST.get('category', 'HR'),
            owner=request.POST.get('owner', '').strip(),
            due_date=request.POST.get('due_date') or None,
            notes=request.POST.get('notes', '').strip(),
        )
        profile.stage = 'ONBOARDING'
        profile.save(update_fields=['stage', 'updated_at'])
        _record(profile, actor=request.user, action='Onboarding Task Added', to_stage='ONBOARDING')
        messages.success(request, 'Onboarding task created.')
    return redirect('candidate_detail', pk=pk)


@login_required
def onboarding_task_toggle(request, pk):
    if not _manager_required(request):
        return redirect('recruitment_dashboard')
    task = get_object_or_404(OnboardingTask, pk=pk)
    task.status = 'DONE' if task.status != 'DONE' else 'PENDING'
    task.completed_at = timezone.now() if task.status == 'DONE' else None
    task.save(update_fields=['status', 'completed_at'])
    return redirect('candidate_detail', pk=task.candidate.applicant_id)


@login_required
@login_required
def convert_candidate_to_employee(request, pk):
    if not _manager_required(request):
        return redirect('candidate_detail', pk=pk)
    with transaction.atomic():
        applicant = get_object_or_404(Applicant.objects.select_related('requirement'), pk=pk)
        profile = _get_or_create_profile(applicant)
        if profile.employee_id or getattr(applicant, 'employee_created', False):
            messages.info(request, 'Candidate is already linked to an employee.')
            return redirect('candidate_detail', pk=pk)
        offer = getattr(profile, 'offer', None)
        if not offer or offer.status != 'ACCEPTED':
            messages.error(request, 'The candidate must have an accepted offer before employee conversion.')
            return redirect('candidate_detail', pk=pk)

        full_name = (applicant.full_name or '').strip() or (applicant.email.split('@')[0] if applicant.email else 'New Employee')
        parts = full_name.split()
        first_name = parts[0]
        last_name = ' '.join(parts[1:])
        employee_id = _next_employee_id()
        # Login is deliberately based on employee ID to match the HRMS onboarding policy.
        user = User.objects.create_user(
            username=employee_id,
            email=(applicant.email or '').strip() or None,
            password='temp@123',
            first_name=first_name,
            last_name=last_name,
        )
        user_fields = {field.name for field in User._meta.fields}
        update_fields = []
        if 'must_change_password' in user_fields:
            user.must_change_password = True
            update_fields.append('must_change_password')
        if 'access_role' in user_fields:
            user.access_role = 'EMPLOYEE'
            update_fields.append('access_role')
        if 'portal_role' in user_fields:
            user.portal_role = 'EMPLOYEE'
            update_fields.append('portal_role')
        if update_fields:
            user.save(update_fields=update_fields)

        extra = _requirement_extra(applicant.requirement)
        department = Department.objects.filter(name__iexact=offer.department).first() or Department.objects.filter(name__iexact=applicant.requirement.department).first()
        reporting_manager = getattr(offer, 'reporting_manager_employee', None)
        employee = Employee.objects.create(
            employee_id=employee_id,
            user=user,
            department=department,
            reporting_manager=reporting_manager,
            designation=offer.designation or applicant.requirement.title,
            employment_type=offer.employment_type or (getattr(extra, 'employment_type', '') if extra else '') or 'FULL_TIME',
            work_mode=offer.work_mode or (getattr(extra, 'work_mode', '') if extra else '') or 'OFFICE',
            phone=applicant.phone or '',
            address='To be completed during employee onboarding.',
            location=offer.location or (getattr(extra, 'location', '') if extra else '') or 'Demo City',
            joining_date=offer.joining_date or timezone.localdate(),
            probation_end_date=(offer.joining_date or timezone.localdate()) if offer.probation_months == 0 else None,
            salary=offer.offered_ctc or 0,
            status='ACTIVE',
            profile_status='PROFILE_PENDING',
        )
        if offer.probation_months and offer.joining_date:
            employee.probation_end_date = _add_months(offer.joining_date, offer.probation_months)
            employee.save(update_fields=['probation_end_date', 'updated_at'])
        EmployeeLifecycle.objects.get_or_create(employee=employee, defaults={'offer_letter_issued': True})
        default_tasks = [
            ('HR Documents', 'HR'), ('IT / Accounts', 'IT'), ('Equipment Allocation', 'ASSET'),
            ('Policy Acceptance', 'POLICY'), ('Orientation', 'ORIENTATION'), ('Training Plan', 'TRAINING'),
            ('Manager Introduction', 'MANAGER'),
        ]
        for title, category in default_tasks:
            OnboardingTask.objects.get_or_create(candidate=profile, title=title, defaults={'category': category, 'owner': 'HR'})
        profile.employee = employee
        profile.stage = 'ONBOARDING'
        profile.save(update_fields=['employee', 'stage', 'updated_at'])
        if hasattr(applicant, 'employee_created'):
            applicant.employee_created = True
        if hasattr(applicant, 'status'):
            applicant.status = 'ONBOARDED'
        applicant.save(update_fields=[field for field in ['employee_created', 'status'] if hasattr(applicant, field)])
        _record(profile, actor=request.user, action='Candidate Converted to Employee', to_stage='ONBOARDING', notes=employee.employee_id)
    messages.success(request, f'{full_name} converted successfully. Employee ID: {employee_id}. Temporary password: temp@123.')
    return redirect('candidate_detail', pk=pk)



@login_required
def recruitment_interviews(request):
    if not _manager_required(request):
        return redirect('recruitment_dashboard')
    interviews = Interview.objects.select_related('candidate', 'candidate__applicant').all()
    return render(request, 'recruitment/interviews.html', {'interviews': interviews})


@login_required
def recruitment_offers(request):
    if not _manager_required(request):
        return redirect('recruitment_dashboard')
    offers = Offer.objects.select_related('candidate', 'candidate__applicant').all()
    return render(request, 'recruitment/offers.html', {'offers': offers})


@login_required
def recruitment_onboarding(request):
    if not _manager_required(request):
        return redirect('recruitment_dashboard')
    profiles = CandidateProfile.objects.filter(stage__in=['PREBOARDING', 'ONBOARDING', 'JOINED']).select_related('applicant')
    return render(request, 'recruitment/onboarding.html', {'profiles': profiles})


@login_required
def recruitment_reports(request):
    profiles = CandidateProfile.objects.all()
    data = [(label, profiles.filter(stage=key).count()) for key, label in CandidateProfile.STAGE_CHOICES]
    return render(request, 'recruitment/reports.html', {'stage_data': data, 'requirements_count': JobRequirement.objects.count(), 'applicants_count': Applicant.objects.count(), 'joined_count': profiles.filter(stage='JOINED').count()})
