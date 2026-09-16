from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from apps.employees.models import Employee


class Leave(models.Model):
    LEAVE_TYPES = [
        ('CASUAL', 'Casual Leave'),
        ('SICK', 'Sick Leave'),
        ('EARNED', 'Earned Leave'),
        ('OPTIONAL', 'Optional Holiday'),
        ('MATERNITY', 'Maternity Leave'),
        ('PATERNITY', 'Paternity Leave'),
        ('BEREAVEMENT', 'Bereavement Leave'),
        ('LOSS_OF_PAY', 'Loss Of Pay (LOP)'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled'),
    ]

    DURATION_CHOICES = [
        ('FULL_DAY', 'Full Day'),
        ('HALF_DAY', 'Half Day'),
    ]

    HALF_DAY_CHOICES = [
        ('MORNING', 'Morning'),
        ('AFTERNOON', 'Afternoon'),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='leaves'
    )
    leave_type = models.CharField(max_length=30, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.DecimalField(max_digits=5, decimal_places=1, default=1, editable=False)

    duration_type = models.CharField(
        max_length=20,
        choices=DURATION_CHOICES,
        default='FULL_DAY'
    )
    half_day_period = models.CharField(
        max_length=20,
        choices=HALF_DAY_CHOICES,
        blank=True,
        null=True
    )

    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_leaves'
    )
    applied_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    remarks = models.TextField(blank=True, null=True)
    review_comment = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-applied_at']
        verbose_name = "Leave Request"
        verbose_name_plural = "Leave Requests"
        indexes = [
            models.Index(fields=['status', 'start_date']),
            models.Index(fields=['employee', 'start_date']),
        ]

    def __str__(self):
        return f"{self.employee.employee_id} - {self.get_leave_type_display()} ({self.total_days} Days)"

    def business_days(self):
        """Count weekdays excluding active company holidays."""
        from .models import Holiday
        if not self.start_date or not self.end_date or self.end_date < self.start_date:
            return 0
        holiday_dates = set(
            Holiday.objects.filter(
                is_active=True,
                holiday_date__range=(self.start_date, self.end_date)
            ).values_list('holiday_date', flat=True)
        )
        current = self.start_date
        count = 0
        while current <= self.end_date:
            if current.weekday() < 5 and current not in holiday_dates:
                count += 1
            current += timedelta(days=1)
        return count

    def clean(self):
        super().clean()

        if self.end_date < self.start_date:
            raise ValidationError({'end_date': 'End date cannot be before start date.'})

        if self.duration_type == 'HALF_DAY':
            if self.start_date != self.end_date:
                raise ValidationError(
                    {'end_date': 'Half-day leave must use the same start and end date.'}
                )
            if not self.half_day_period:
                raise ValidationError(
                    {'half_day_period': 'Select Morning or Afternoon.'}
                )
        else:
            self.half_day_period = None

        overlapping = Leave.objects.filter(
            employee=self.employee,
            status__in=['PENDING', 'APPROVED'],
            start_date__lte=self.end_date,
            end_date__gte=self.start_date,
        )
        if self.pk:
            overlapping = overlapping.exclude(pk=self.pk)

        if overlapping.exists():
            raise ValidationError('An overlapping leave request already exists.')

        requested_days = self.calculate_days()

        if self.leave_type in {'CASUAL', 'SICK', 'EARNED'}:
            balance, _ = LeaveBalance.objects.get_or_create(employee=self.employee)

            available = {
                'CASUAL': balance.remaining_casual_leave,
                'SICK': balance.remaining_sick_leave,
                'EARNED': balance.remaining_earned_leave,
            }[self.leave_type]

            if requested_days > available and self.status != 'CANCELLED':
                raise ValidationError(
                    f"Insufficient {self.get_leave_type_display()} balance. "
                    f"Requested: {requested_days}, Available: {available}"
                )

    def calculate_days(self):
        """Weekdays minus active company holidays; half day = 0.5."""
        days = self.business_days()
        if self.duration_type == 'HALF_DAY':
            return 0.5 if days else 0
        return days

    def save(self, *args, **kwargs):
        if self.start_date and self.end_date:
            self.total_days = self.calculate_days()

        old_status = None
        old_employee_id = None
        old_leave_type = None
        old_days = 0

        if self.pk:
            old = Leave.objects.get(pk=self.pk)
            old_status = old.status
            old_employee_id = old.employee_id
            old_leave_type = old.leave_type
            old_days = old.total_days or 0

        if old_status == 'PENDING' and self.status in ['APPROVED', 'REJECTED']:
            if not self.approved_at:
                self.approved_at = timezone.now()

        super().save(*args, **kwargs)

        if self.status != old_status:
            balance, _ = LeaveBalance.objects.get_or_create(employee=self.employee)

            if self.status == 'APPROVED' and old_status != 'APPROVED':
                balance.adjust_used_leaves(self.leave_type, self.total_days)
            elif old_status == 'APPROVED' and self.status in ['CANCELLED', 'REJECTED']:
                balance.adjust_used_leaves(self.leave_type, -old_days)

    @property
    def status_label(self):
        return self.get_status_display()


class LeaveBalance(models.Model):
    employee = models.OneToOneField(
        Employee,
        on_delete=models.CASCADE,
        related_name='leave_balance'
    )

    casual_leave = models.PositiveIntegerField(default=12)
    sick_leave = models.PositiveIntegerField(default=12)
    earned_leave = models.PositiveIntegerField(default=18)

    used_casual_leave = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    used_sick_leave = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    used_earned_leave = models.DecimalField(max_digits=5, decimal_places=1, default=0)

    updated_at = models.DateTimeField(auto_now=True)

    @property
    def remaining_casual_leave(self):
        return max(float(self.casual_leave) - float(self.used_casual_leave), 0)

    @property
    def remaining_sick_leave(self):
        return max(float(self.sick_leave) - float(self.used_sick_leave), 0)

    @property
    def remaining_earned_leave(self):
        return max(float(self.earned_leave) - float(self.used_earned_leave), 0)

    def adjust_used_leaves(self, leave_type, days):
        if leave_type == 'CASUAL':
            self.used_casual_leave = max(float(self.used_casual_leave) + float(days), 0)
        elif leave_type == 'SICK':
            self.used_sick_leave = max(float(self.used_sick_leave) + float(days), 0)
        elif leave_type == 'EARNED':
            self.used_earned_leave = max(float(self.used_earned_leave) + float(days), 0)
        self.save(update_fields=[
            'used_casual_leave', 'used_sick_leave',
            'used_earned_leave', 'updated_at'
        ])

    def __str__(self):
        return f"{self.employee.employee_id} Leave Balance"


class LeavePolicy(models.Model):
    leave_type = models.CharField(max_length=30, choices=Leave.LEAVE_TYPES, unique=True)
    annual_allocation = models.PositiveIntegerField(default=12)
    is_paid = models.BooleanField(default=True)
    carry_forward = models.BooleanField(default=False)
    max_carry_forward = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['leave_type']

    def __str__(self):
        return f"{self.get_leave_type_display()} Policy"


class Holiday(models.Model):
    HOLIDAY_TYPES = [
        ('NATIONAL', 'National Holiday'),
        ('FESTIVAL', 'Festival Holiday'),
        ('OPTIONAL', 'Optional Holiday'),
        ('COMPANY', 'Company Holiday'),
    ]

    name = models.CharField(max_length=200)
    holiday_date = models.DateField(unique=True)
    holiday_type = models.CharField(
        max_length=20,
        choices=HOLIDAY_TYPES,
        default='NATIONAL'
    )
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['holiday_date']

    def __str__(self):
        return f"{self.name} ({self.holiday_date})"
