from django.db import models

from apps.employees.models import Employee


class Promotion(models.Model):

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

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return f"{self.employee} - {self.new_designation}"