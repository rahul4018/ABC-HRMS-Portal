from django.db import models

from apps.employees.models import Employee


class Promotion(models.Model):

    STATUS_CHOICES = [

        ('PENDING', 'Pending'),

        ('APPROVED', 'Approved'),

        ('REJECTED', 'Rejected'),

    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE
    )

    old_designation = models.CharField(
        max_length=100
    )

    new_designation = models.CharField(
        max_length=100
    )

    effective_date = models.DateField()

    remarks = models.TextField(
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = ['-created_at']

        verbose_name = "Promotion"

        verbose_name_plural = "Promotions"

    def __str__(self):

        return (
            f"{self.employee.employee_id} - "
            f"{self.employee.user.email} - "
            f"{self.new_designation}"
        )