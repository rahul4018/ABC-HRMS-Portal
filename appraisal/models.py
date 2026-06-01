from django.db import models

from apps.employees.models import Employee


class PMR(models.Model):

    STATUS_CHOICES = [

        ('PENDING', 'Pending'),

        ('APPROVED', 'Approved'),

        ('REJECTED', 'Rejected'),

        ('RESUBMIT', 'Resubmit'),

    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='pmrs'
    )

    title = models.CharField(
        max_length=200
    )

    achievements = models.TextField()

    goals = models.TextField()

    supervisor_comment = models.TextField(
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    submitted_date = models.DateTimeField(
        auto_now_add=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = ['-created_at']

        verbose_name = 'PMR'

        verbose_name_plural = 'PMRs'

    def __str__(self):

        return f"{self.employee.employee_id} - {self.title}"