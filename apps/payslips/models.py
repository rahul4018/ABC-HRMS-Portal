from django.db import models

from apps.employees.models import Employee


class Payslip(models.Model):

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE
    )

    month = models.CharField(
        max_length=20
    )

    year = models.IntegerField()

    basic_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    bonus = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    deductions = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    net_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    generated_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        ordering = ['-generated_at']

    def __str__(self):

        return (
            f"{self.employee.user.email} - "
            f"{self.month} {self.year}"
        )