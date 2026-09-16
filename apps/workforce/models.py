from django.conf import settings
from django.db import models
from django.utils import timezone


class Location(models.Model):
    name = models.CharField(max_length=120, unique=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default='India')
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Team(models.Model):
    name = models.CharField(max_length=120)
    department = models.ForeignKey('employees.Department', on_delete=models.SET_NULL, null=True, blank=True)
    team_lead = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='led_teams')
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = [('name', 'department')]
        ordering = ['name']

    def __str__(self):
        return self.name


class Designation(models.Model):
    name = models.CharField(max_length=120, unique=True)
    level = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class JobGrade(models.Model):
    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=100)
    minimum_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    maximum_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f'{self.code} - {self.name}'


class EmploymentHistory(models.Model):
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='workforce_history')
    effective_date = models.DateField(default=timezone.now)
    event_type = models.CharField(max_length=40, choices=[
        ('JOINING', 'Joining'),
        ('PROBATION', 'Probation'),
        ('CONFIRMATION', 'Confirmation'),
        ('PROMOTION', 'Promotion'),
        ('TRANSFER', 'Transfer'),
        ('SALARY_REVISION', 'Salary Revision'),
        ('MANAGER_CHANGE', 'Manager Change'),
        ('DEPARTMENT_CHANGE', 'Department Change'),
        ('STATUS_CHANGE', 'Status Change'),
        ('OTHER', 'Other'),
    ])
    from_value = models.CharField(max_length=255, blank=True)
    to_value = models.CharField(max_length=255, blank=True)
    remarks = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-effective_date', '-id']


class ApprovalWorkflow(models.Model):
    module = models.CharField(max_length=60)
    action = models.CharField(max_length=60)
    step_order = models.PositiveIntegerField(default=1)
    approver_role = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['module', 'action', 'step_order']
        unique_together = [('module', 'action', 'step_order')]

    def __str__(self):
        return f'{self.module} / {self.action} / {self.step_order}'


class UserModulePermission(models.Model):
    MODULES = [
        ('WORKFORCE', 'Workforce'), ('TALENT', 'Talent'), ('ATTENDANCE', 'Time & Attendance'),
        ('LEAVE', 'Leave'), ('PAYROLL', 'Payroll & Finance'), ('PEOPLE', 'People Operations'),
        ('PERFORMANCE', 'Performance'), ('LEARNING', 'Learning'), ('EXIT', 'Exit & Separation'),
        ('REPORTS', 'Reports & Analytics'), ('ADMIN', 'Administration'),
    ]
    ACTIONS = [('VIEW', 'View'), ('CREATE', 'Create'), ('EDIT', 'Edit'), ('APPROVE', 'Approve'), ('EXPORT', 'Export')]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='workforce_permissions')
    module = models.CharField(max_length=30, choices=MODULES)
    action = models.CharField(max_length=20, choices=ACTIONS, default='VIEW')

    class Meta:
        unique_together = [('user', 'module', 'action')
]


class ExitCase(models.Model):
    TYPES = [
        ('RESIGNATION', 'Resignation'), ('TERMINATION', 'Termination'), ('RETIREMENT', 'Retirement'),
        ('CONTRACT_END', 'Contract End'), ('ABSCONDING', 'Absconding'), ('OTHER', 'Other'),
    ]
    STATUSES = [
        ('DRAFT', 'Draft'), ('PENDING_APPROVAL', 'Pending Approval'), ('APPROVED', 'Approved'),
        ('IN_PROGRESS', 'Exit In Progress'), ('COMPLETED', 'Completed'), ('REJECTED', 'Rejected'), ('CANCELLED', 'Cancelled'),
    ]
    employee = models.ForeignKey('employees.Employee', on_delete=models.PROTECT, related_name='exit_cases')
    exit_type = models.CharField(max_length=30, choices=TYPES)
    reason = models.CharField(max_length=255)
    detailed_reason = models.TextField(blank=True)
    resignation_date = models.DateField(null=True, blank=True)
    requested_last_working_day = models.DateField(null=True, blank=True)
    notice_period_days = models.PositiveIntegerField(default=0)
    notice_waived = models.BooleanField(default=False)
    actual_last_working_day = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUSES, default='DRAFT')
    manager_comments = models.TextField(blank=True)
    hr_comments = models.TextField(blank=True)
    termination_effective_date = models.DateField(null=True, blank=True)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_exit_cases')
    approved_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_exit_cases')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.employee} - {self.get_exit_type_display()}'

    @property
    def service_text(self):
        if not self.employee.joining_date:
            return ''
        end = self.actual_last_working_day or self.termination_effective_date or timezone.localdate()
        start = self.employee.joining_date
        years = end.year - start.year
        months = end.month - start.month
        days = end.day - start.day
        if days < 0:
            months -= 1
            days += 30
        if months < 0:
            years -= 1
            months += 12
        return f'{years} Years, {months} Months, {days} Days'


class ExitClearance(models.Model):
    STATUS = [('PENDING', 'Pending'), ('CLEARED', 'Cleared'), ('ISSUE', 'Issue Found'), ('NA', 'Not Applicable')]
    exit_case = models.ForeignKey(ExitCase, on_delete=models.CASCADE, related_name='clearances')
    department_name = models.CharField(max_length=100)
    owner_name = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='PENDING')
    comments = models.TextField(blank=True)
    cleared_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    cleared_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['department_name']
        unique_together = [('exit_case', 'department_name')]


class ExitInterview(models.Model):
    exit_case = models.OneToOneField(ExitCase, on_delete=models.CASCADE, related_name='exit_interview')
    leaving_reason = models.CharField(max_length=255, blank=True)
    manager_relationship = models.CharField(max_length=100, blank=True)
    work_environment = models.PositiveSmallIntegerField(null=True, blank=True)
    compensation = models.PositiveSmallIntegerField(null=True, blank=True)
    growth_opportunities = models.PositiveSmallIntegerField(null=True, blank=True)
    work_life_balance = models.PositiveSmallIntegerField(null=True, blank=True)
    culture = models.PositiveSmallIntegerField(null=True, blank=True)
    would_recommend = models.BooleanField(null=True, blank=True)
    would_return = models.BooleanField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    hr_summary = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)


class FinalSettlement(models.Model):
    STATUS = [('DRAFT', 'Draft'), ('HR_REVIEW', 'HR Review'), ('FINANCE_REVIEW', 'Finance Review'), ('APPROVED', 'Approved'), ('PAID', 'Paid'), ('CLOSED', 'Closed')]
    exit_case = models.OneToOneField(ExitCase, on_delete=models.CASCADE, related_name='final_settlement')
    salary_due = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    lop = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notice_recovery = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    leave_encashment = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    bonus = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    overtime = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reimbursements = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    loan_recovery = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    asset_recovery = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=30, choices=STATUS, default='DRAFT')
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_settlements')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_settlements')
    paid_at = models.DateTimeField(null=True, blank=True)

    @property
    def gross_total(self):
        return sum([self.salary_due, self.leave_encashment, self.bonus, self.overtime, self.reimbursements])

    @property
    def deductions_total(self):
        return sum([self.lop, self.notice_recovery, self.loan_recovery, self.asset_recovery, self.tax, self.other_deductions])

    @property
    def net_total(self):
        return self.gross_total - self.deductions_total


class ExitDocument(models.Model):
    TYPES = [
        ('RESIGNATION_ACCEPTANCE', 'Resignation Acceptance Letter'),
        ('RELIEVING', 'Relieving Letter'), ('EXPERIENCE', 'Experience Letter'),
        ('SERVICE', 'Service Certificate'), ('TERMINATION', 'Termination Letter'),
        ('CONTRACT_END', 'Contract Completion Letter'), ('NO_DUES', 'No-Dues Certificate'),
        ('EMPLOYMENT', 'Employment Certificate'), ('FINAL_SETTLEMENT', 'Final Settlement Statement'),
    ]
    exit_case = models.ForeignKey(ExitCase, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=40, choices=TYPES)
    issue_date = models.DateField(default=timezone.localdate)
    reference_number = models.CharField(max_length=80, blank=True)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-issue_date', '-id']
        unique_together = [('exit_case', 'document_type')]


class RehireRecord(models.Model):
    employee = models.ForeignKey('employees.Employee', on_delete=models.PROTECT, related_name='rehire_records')
    eligible_for_rehire = models.BooleanField(default=True)
    rehire_notes = models.TextField(blank=True)
    previous_exit_case = models.ForeignKey(ExitCase, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class HRRequest(models.Model):
    STATUS = [('OPEN', 'Open'), ('IN_PROGRESS', 'In Progress'), ('WAITING', 'Waiting'), ('RESOLVED', 'Resolved'), ('CLOSED', 'Closed')]
    PRIORITY = [('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High'), ('URGENT', 'Urgent')]
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='hr_requests')
    category = models.CharField(max_length=80)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY, default='MEDIUM')
    status = models.CharField(max_length=20, choices=STATUS, default='OPEN')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_hr_requests')
    resolution = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
