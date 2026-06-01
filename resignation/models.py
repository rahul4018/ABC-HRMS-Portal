from django.db import models

from apps.employees.models import Employee


class Resignation(models.Model):

    STATUS_CHOICES = [

        ('PENDING', 'Pending'),

        ('APPROVED', 'Approved'),

        ('REJECTED', 'Rejected'),

        ('SENT_BACK', 'Sent Back'),

    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='resignations'
    )

    reason = models.TextField()

    last_working_day = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    supervisor_remark = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = ['-created_at']

        verbose_name = 'Resignation'

        verbose_name_plural = 'Resignations'

    def __str__(self):

        return (
            f"{self.employee.employee_id} - "
            f"{self.employee.user.email} - "
            f"{self.status}"
        )