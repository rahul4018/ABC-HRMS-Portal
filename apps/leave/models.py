from django.db import models

from apps.accounts.models import User
from apps.employees.models import Employee


class Leave(models.Model):

    LEAVE_TYPES = [

        ('SICK', 'Sick Leave'),

        ('CASUAL', 'Casual Leave'),

        ('PAID', 'Paid Leave'),

        ('UNPAID', 'Unpaid Leave'),

    ]

    STATUS_CHOICES = [

        ('PENDING', 'Pending'),

        ('APPROVED', 'Approved'),

        ('REJECTED', 'Rejected'),

    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE
    )

    leave_type = models.CharField(
        max_length=20,
        choices=LEAVE_TYPES
    )

    start_date = models.DateField()

    end_date = models.DateField()

    reason = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    applied_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return f"{self.employee} - {self.leave_type}"