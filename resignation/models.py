from django.db import models
from django.core.exceptions import ValidationError
from apps.employees.models import Employee


class Resignation(models.Model):
    """Employee resignation and offboarding workflow."""

    STATUS_CHOICES = [
        ('PENDING', 'Pending HR Review'),
        ('APPROVED', 'Approved'),
        ('NOTICE_PERIOD', 'Notice Period'),
        ('EARLY_RELEASE_REQUESTED', 'Early Release Requested'),
        ('REJECTED', 'Rejected'),
        ('SENT_BACK', 'Sent Back'),
        ('EXIT_PROCESS', 'Exit Process'),
        ('COMPLETED', 'Completed'),
        ('WITHDRAWN', 'Withdrawn'),
    ]

    HANDOVER_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
    ]

    NOTICE_UNIT_CHOICES = [
        ('CALENDAR', 'Calendar Days'),
        ('WORKING', 'Working Days'),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='resignations'
    )

    resignation_date = models.DateField(null=True,
        blank=True)

    notice_period_days = models.PositiveIntegerField(default=15)

    notice_period_unit = models.CharField(
        max_length=20,
        choices=NOTICE_UNIT_CHOICES,
        default='CALENDAR'
    )

    expected_last_working_day = models.DateField(
    null=True,
    blank=True
)

    # Kept for backward compatibility with the existing module/UI/database.
    # This is synchronized to the expected LWD unless an approved early release
    # date is being used as the actual LWD.
    last_working_day = models.DateField()

    requested_early_release_date = models.DateField(
        null=True,
        blank=True
    )

    early_release_reason = models.TextField(
        blank=True,
        null=True
    )

    reason = models.TextField()

    additional_comments = models.TextField(
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    supervisor_remark = models.TextField(
        blank=True,
        null=True
    )

    handover_status = models.CharField(
        max_length=20,
        choices=HANDOVER_CHOICES,
        default='PENDING'
    )

    handover_notes = models.TextField(
        blank=True,
        null=True
    )

    exit_interview_completed = models.BooleanField(default=False)
    assets_cleared = models.BooleanField(default=False)
    documents_cleared = models.BooleanField(default=False)
    payroll_cleared = models.BooleanField(default=False)
    full_final_settlement_completed = models.BooleanField(default=False)
    experience_letter_issued = models.BooleanField(default=False)
    relieving_letter_issued = models.BooleanField(default=False)
    account_deactivated = models.BooleanField(default=False)

    exit_date = models.DateField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Resignation'
        verbose_name_plural = 'Resignations'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['expected_last_working_day']),
            models.Index(fields=['employee', 'status']),
        ]

    def __str__(self):
        return (
            f"{self.employee.employee_id} - "
            f"{self.employee.user.email} - "
            f"{self.status}"
        )

    @property
    def days_remaining(self):
        from django.utils import timezone
        if self.exit_date:
            return 0
        return max((self.last_working_day - timezone.localdate()).days, 0)

    @property
    def exit_progress(self):
        checklist = [
            self.handover_status == 'COMPLETED',
            self.exit_interview_completed,
            self.assets_cleared,
            self.documents_cleared,
            self.payroll_cleared,
            self.full_final_settlement_completed,
            self.experience_letter_issued,
            self.relieving_letter_issued,
            self.account_deactivated,
        ]
        return int(sum(checklist) * 100 / len(checklist))

    def clean(self):
        super().clean()
        if self.requested_early_release_date and self.expected_last_working_day:
            if self.requested_early_release_date >= self.expected_last_working_day:
                raise ValidationError({
                    'requested_early_release_date':
                        'Early release date must be before the expected last working day.'
                })
