from django.db import models
from apps.employees.models import Employee


class Payslip(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='payslips'
    )
    month = models.CharField(max_length=20)
    year = models.IntegerField()
    days_in_month = models.IntegerField(default=30)
    effective_work_days = models.IntegerField(default=30)
    lop = models.IntegerField(default=0)

    # Earnings
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    hra = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    conveyance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    special_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Deductions
    pf = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    esi = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    professional_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    income_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Totals
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-generated_at']
        unique_together = ('employee', 'month', 'year')

    def __str__(self):
        # Fixes potential AttributeError/ObjectDoesNotExist during database operations
        emp_id = self.employee.employee_id if self.employee_id else "Unknown"
        return f"{emp_id} - {self.month} {self.year}"

    def save(self, *args, **kwargs):
        self.gross_salary = (
            self.basic_salary +
            self.hra +
            self.conveyance +
            self.special_allowance +
            self.bonus
        )

        self.total_deductions = (
            self.pf +
            self.esi +
            self.professional_tax +
            self.income_tax +
            self.other_deduction
        )

        self.net_salary = (
            self.gross_salary -
            self.total_deductions
        )

        super().save(*args, **kwargs)