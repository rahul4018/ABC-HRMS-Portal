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
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=200
    )

    achievements = models.TextField()

    goals = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    submitted_date = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title