from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    HRMS account.

    Business Employee IDs:
        EMP1, EMP2, ..., EMP40
        C1, C2, ..., C5

    Login User IDs:
        ABC1, ABC2, ..., ABC40
        ABCC1, ABCC2, ..., ABCC5

    The User ID is independent from the business Employee ID.
    Email is optional and can be added later.
    """

    class AccessRole(models.TextChoices):
        MASTER_ADMIN = "MASTER_ADMIN", "Master Admin"
        FOUNDER = "FOUNDER", "Founder"
        HR = "HR", "HR"
        EMPLOYEE = "EMPLOYEE", "Employee"
        CONTRACTOR = "CONTRACTOR", "Contractor"

    class LegacyRole(models.TextChoices):
        SUPERVISOR = "SUPERVISOR", "Supervisor"
        EMPLOYEE = "EMPLOYEE", "Employee"

    role = models.CharField(
        max_length=20,
        choices=LegacyRole.choices,
        default=LegacyRole.EMPLOYEE,
    )

    portal_role = models.CharField(
        max_length=20,
        choices=[
            ("ADMIN", "Admin"),
            ("CEO", "CEO"),
            ("HR", "HR"),
            ("FOUNDER", "Founder"),
            ("EMPLOYEE", "Employee"),
        ],
        default="EMPLOYEE",
    )

    access_role = models.CharField(
        max_length=20,
        choices=AccessRole.choices,
        default=AccessRole.EMPLOYEE,
        db_index=True,
    )

    email = models.EmailField(
        blank=True,
        null=True,
    )

    must_change_password = models.BooleanField(
        default=False,
        help_text="Force a temporary-password user to change password.",
    )

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.access_role = self.AccessRole.MASTER_ADMIN

        if self.access_role in {
            self.AccessRole.MASTER_ADMIN,
            self.AccessRole.FOUNDER,
            self.AccessRole.HR,
        }:
            self.role = self.LegacyRole.SUPERVISOR
        else:
            self.role = self.LegacyRole.EMPLOYEE

        if self.access_role == self.AccessRole.MASTER_ADMIN:
            self.portal_role = "ADMIN"
        elif self.access_role == self.AccessRole.FOUNDER:
            self.portal_role = "FOUNDER"
        elif self.access_role == self.AccessRole.HR:
            self.portal_role = "HR"
        else:
            self.portal_role = "EMPLOYEE"

        super().save(*args, **kwargs)

    @property
    def is_management(self):
        return self.access_role in {
            self.AccessRole.MASTER_ADMIN,
            self.AccessRole.FOUNDER,
            self.AccessRole.HR,
        }

    @property
    def is_master_admin(self):
        return self.access_role == self.AccessRole.MASTER_ADMIN

    @property
    def is_founder(self):
        return self.access_role == self.AccessRole.FOUNDER

    @property
    def is_hr(self):
        return self.access_role == self.AccessRole.HR

    @property
    def is_contractor(self):
        return self.access_role == self.AccessRole.CONTRACTOR

    @property
    def display_name(self):
        return self.get_full_name().strip() or self.username

    @property
    def login_identifier(self):
        return self.username

    def __str__(self):
        return self.display_name


class CompanySettings(models.Model):
    company_name = models.CharField(max_length=200)
    company_address = models.TextField()
    company_email = models.EmailField()
    company_phone = models.CharField(max_length=20)

    company_logo = models.ImageField(
        upload_to="company/",
        blank=True,
        null=True,
    )

    casual_leave_days = models.PositiveIntegerField(default=12)
    earned_leave_days = models.PositiveIntegerField(default=18)
    sick_leave_days = models.PositiveIntegerField(default=12)

    carry_forward_enabled = models.BooleanField(default=True)
    max_carry_forward_days = models.PositiveIntegerField(default=30)

    grace_period_minutes = models.PositiveIntegerField(default=15)

    half_day_hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=4,
    )

    work_start_time = models.TimeField(default="09:00")
    work_end_time = models.TimeField(default="18:00")

    overtime_after_hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=9,
    )

    notice_period_days = models.PositiveIntegerField(default=15)

    notice_period_unit = models.CharField(
        max_length=20,
        choices=[
            ("CALENDAR", "Calendar Days"),
            ("WORKING", "Working Days"),
        ],
        default="CALENDAR",
    )

    salary_cycle = models.CharField(
        max_length=30,
        default="MONTHLY",
    )

    payroll_date_day = models.PositiveIntegerField(default=31)

    payslip_number_format = models.CharField(
        max_length=100,
        default="PS-{YEAR}-{MONTH}-{EMPLOYEE}",
    )

    pf_enabled = models.BooleanField(default=True)
    esi_enabled = models.BooleanField(default=True)
    professional_tax_enabled = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name
