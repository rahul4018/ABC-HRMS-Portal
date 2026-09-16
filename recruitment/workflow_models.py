from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.employees.models import Employee


class HiringRequest(models.Model):
    PRIORITY_CHOICES = [
        ('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High'), ('URGENT', 'Urgent')
    ]
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'), ('PENDING', 'Pending Approval'), ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'), ('CLOSED', 'Closed')
    ]
    request_number = models.CharField(max_length=40, unique=True, editable=False)
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='hiring_requests')
    department = models.CharField(max_length=150)
    position_title = models.CharField(max_length=150)
    openings = models.PositiveIntegerField(default=1)
    reason = models.TextField(blank=True)
    employment_type = models.CharField(max_length=50, blank=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    required_by = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_hiring_requests')
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.request_number:
            prefix = timezone.now().strftime('%Y%m')
            last = HiringRequest.objects.filter(request_number__startswith=f'HR-{prefix}-').order_by('-id').first()
            number = (int(last.request_number.rsplit('-', 1)[-1]) + 1) if last else 1
            self.request_number = f'HR-{prefix}-{number:04d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.request_number} - {self.position_title}'


class JobPosting(models.Model):
    STATUS_CHOICES = [('DRAFT', 'Draft'), ('PUBLISHED', 'Published'), ('PAUSED', 'Paused'), ('CLOSED', 'Closed')]
    requirement = models.OneToOneField('recruitment.JobRequirement', on_delete=models.CASCADE, related_name='job_posting')
    slug = models.SlugField(max_length=180, unique=True)
    headline = models.CharField(max_length=220, blank=True)
    public_description = models.TextField(blank=True)
    application_instructions = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    published_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.headline or self.requirement.title


class JobRequirementExtra(models.Model):
    requirement = models.OneToOneField('recruitment.JobRequirement', on_delete=models.CASCADE, related_name='workflow_extra')
    hiring_request = models.ForeignKey(HiringRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name='requirements')
    employment_type = models.CharField(max_length=50, blank=True)
    work_mode = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=150, blank=True)
    qualification = models.CharField(max_length=200, blank=True)
    salary_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    notice_period = models.CharField(max_length=80, blank=True)
    joining_timeline = models.CharField(max_length=80, blank=True)
    responsibilities = models.TextField(blank=True)
    required_skills = models.TextField(blank=True)
    preferred_skills = models.TextField(blank=True)
    education = models.CharField(max_length=200, blank=True)
    certifications = models.CharField(max_length=300, blank=True)
    recruiter_name = models.CharField(max_length=150, blank=True)
    hiring_manager = models.CharField(max_length=150, blank=True)
    target_hiring_date = models.DateField(null=True, blank=True)
    application_deadline = models.DateField(null=True, blank=True)
    priority = models.CharField(max_length=20, choices=HiringRequest.PRIORITY_CHOICES, default='MEDIUM')
    published_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'Extra: {self.requirement}'


class CandidateProfile(models.Model):
    STAGE_CHOICES = [
        ('APPLIED', 'Applied'), ('SCREENING', 'Screening'), ('SHORTLISTED', 'Shortlisted'),
        ('HR_SCREENING', 'HR Screening'), ('INTERVIEW', 'Interview'), ('ASSESSMENT', 'Assessment'),
        ('SELECTED', 'Selected'), ('OFFER', 'Offer'), ('OFFER_ACCEPTED', 'Offer Accepted'),
        ('BACKGROUND_CHECK', 'Background Check'), ('PREBOARDING', 'Preboarding'),
        ('ONBOARDING', 'Onboarding'), ('JOINED', 'Joined'), ('REJECTED', 'Rejected'),
        ('WITHDRAWN', 'Withdrawn')
    ]
    SOURCE_CHOICES = [
        ('DIRECT', 'Direct'), ('REFERRAL', 'Employee Referral'), ('LINKEDIN', 'LinkedIn'),
        ('JOB_PORTAL', 'Job Portal'), ('CAREER_PAGE', 'Career Page'), ('AGENCY', 'Agency'), ('OTHER', 'Other')
    ]
    applicant = models.OneToOneField('recruitment.Applicant', on_delete=models.CASCADE, related_name='workflow_profile')
    stage = models.CharField(max_length=30, choices=STAGE_CHOICES, default='APPLIED')
    source = models.CharField(max_length=30, choices=SOURCE_CHOICES, default='DIRECT')
    current_company = models.CharField(max_length=180, blank=True)
    current_designation = models.CharField(max_length=180, blank=True)
    total_experience_years = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    expected_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    notice_period = models.CharField(max_length=80, blank=True)
    location = models.CharField(max_length=150, blank=True)
    qualification = models.CharField(max_length=200, blank=True)
    skills = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    employee = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='recruitment_profiles')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.applicant.full_name} - {self.get_stage_display()}'


class Assessment(models.Model):
    TYPE_CHOICES = [
        ('TECHNICAL', 'Technical'), ('APTITUDE', 'Aptitude'),
        ('COMMUNICATION', 'Communication'), ('CODING', 'Coding'),
        ('DOMAIN', 'Domain Knowledge'), ('HR', 'HR Assessment'),
        ('MANAGERIAL', 'Managerial'), ('PRACTICAL', 'Practical Task'),
        ('CUSTOM', 'Custom'),
    ]
    STATUS_CHOICES = [('PENDING', 'Pending'), ('COMPLETED', 'Completed'), ('CANCELLED', 'Cancelled')]
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='assessments')
    assessment_name = models.CharField(max_length=180)
    assessment_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='TECHNICAL')
    duration_minutes = models.PositiveIntegerField(default=60)
    ABCeduled_at = models.DateTimeField(null=True, blank=True)
    due_at = models.DateTimeField(null=True, blank=True)
    assessor = models.CharField(max_length=180, blank=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    passing_score = models.DecimalField(max_digits=5, decimal_places=2, default=60)
    instructions = models.TextField(blank=True)
    assessor_employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='recruitment_assessments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    result = models.CharField(max_length=40, blank=True)
    feedback = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class Interview(models.Model):
    ROUND_CHOICES = [
        ('HR_SCREENING', 'HR Screening'), ('TECHNICAL_1', 'Technical Round 1'),
        ('TECHNICAL_2', 'Technical Round 2'), ('MANAGERIAL', 'Managerial Round'),
        ('HR_FINAL', 'HR Final')
    ]
    MODE_CHOICES = [('ONLINE', 'Online'), ('ONSITE', 'On-site'), ('PHONE', 'Phone')]
    STATUS_CHOICES = [('ABCEDULED', 'ABCeduled'), ('COMPLETED', 'Completed'), ('CANCELLED', 'Cancelled'), ('NO_SHOW', 'No Show')]
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='interviews')
    round_name = models.CharField(max_length=30, choices=ROUND_CHOICES, default='HR_SCREENING')
    interview_type = models.CharField(max_length=20, choices=MODE_CHOICES, default='ONLINE')
    ABCeduled_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=30)
    interviewer = models.CharField(max_length=180)
    interviewer_employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='recruitment_interviews')
    meeting_link = models.URLField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ABCEDULED')
    panel_members = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['ABCeduled_at']


class InterviewFeedback(models.Model):
    RECOMMENDATIONS = [('STRONG_HIRE', 'Strong Hire'), ('HIRE', 'Hire'), ('HOLD', 'Hold'), ('REJECT', 'Reject')]
    interview = models.OneToOneField(Interview, on_delete=models.CASCADE, related_name='feedback')
    technical_skills = models.PositiveSmallIntegerField(default=0)
    communication = models.PositiveSmallIntegerField(default=0)
    problem_solving = models.PositiveSmallIntegerField(default=0)
    culture_fit = models.PositiveSmallIntegerField(default=0)
    overall_rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    recommendation = models.CharField(max_length=20, choices=RECOMMENDATIONS, default='HOLD')
    comments = models.TextField(blank=True)
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)


class Offer(models.Model):
    STATUS_CHOICES = [('DRAFT', 'Draft'), ('PENDING_APPROVAL', 'Pending Approval'), ('GENERATED', 'Generated'), ('SENT', 'Sent'), ('VIEWED', 'Viewed'), ('ACCEPTED', 'Accepted'), ('DECLINED', 'Declined'), ('EXPIRED', 'Expired'), ('CANCELLED', 'Cancelled')]
    candidate = models.OneToOneField(CandidateProfile, on_delete=models.CASCADE, related_name='offer')
    offer_number = models.CharField(max_length=40, unique=True, editable=False)
    offered_ctc = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    designation = models.CharField(max_length=180)
    department = models.CharField(max_length=180)
    location = models.CharField(max_length=180, blank=True)
    joining_date = models.DateField(null=True, blank=True)
    reporting_manager = models.CharField(max_length=180, blank=True)
    reporting_manager_employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='recruitment_offers')
    employment_type = models.CharField(max_length=50, blank=True)
    work_mode = models.CharField(max_length=50, blank=True)
    probation_months = models.PositiveIntegerField(default=6)
    offer_date = models.DateField(default=timezone.localdate)
    expiry_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='DRAFT')
    sent_at = models.DateTimeField(null=True, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    declined_reason = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_offers')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.offer_number:
            prefix = timezone.now().strftime('%Y%m')
            last = Offer.objects.filter(offer_number__startswith=f'OFF-{prefix}-').order_by('-id').first()
            number = (int(last.offer_number.rsplit('-', 1)[-1]) + 1) if last else 1
            self.offer_number = f'OFF-{prefix}-{number:04d}'
        super().save(*args, **kwargs)


class BackgroundVerification(models.Model):
    STATUS_CHOICES = [('NOT_STARTED', 'Not Started'), ('IN_PROGRESS', 'In Progress'), ('CLEARED', 'Cleared'), ('ISSUE_FOUND', 'Issue Found'), ('WAIVED', 'Waived')]
    candidate = models.OneToOneField(CandidateProfile, on_delete=models.CASCADE, related_name='background_check')
    vendor = models.CharField(max_length=180, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_STARTED')
    identity_check = models.BooleanField(default=False)
    address_check = models.BooleanField(default=False)
    education_check = models.BooleanField(default=False)
    employment_check = models.BooleanField(default=False)
    criminal_check = models.BooleanField(default=False)
    comments = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)


class OnboardingTask(models.Model):
    STATUS_CHOICES = [('PENDING', 'Pending'), ('IN_PROGRESS', 'In Progress'), ('DONE', 'Done'), ('BLOCKED', 'Blocked')]
    CATEGORY_CHOICES = [('HR', 'HR Documents'), ('IT', 'IT / Accounts'), ('ASSET', 'Equipment'), ('POLICY', 'Policy'), ('ORIENTATION', 'Orientation'), ('TRAINING', 'Training'), ('MANAGER', 'Manager')]
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='onboarding_tasks')
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='HR')
    owner = models.CharField(max_length=180, blank=True)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    employee_acknowledged = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['status', 'due_date', 'id']


class RecruitmentActivity(models.Model):
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='activities', null=True, blank=True)
    requirement = models.ForeignKey('recruitment.JobRequirement', on_delete=models.CASCADE, null=True, blank=True, related_name='activities')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=120)
    from_stage = models.CharField(max_length=30, blank=True)
    to_stage = models.CharField(max_length=30, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
