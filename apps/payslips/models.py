from django.db import models
from django.utils import timezone
from apps.employees.models import Employee


class Payslip(models.Model):
    PAYMENT_MODE_CHOICES = [
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('CASH', 'Cash'),
        ('CHEQUE', 'Cheque'),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='payslips'
    )
    payslip_number = models.CharField(max_length=40, unique=True, blank=True, null=True)
    month = models.CharField(max_length=20)
    year = models.IntegerField()
    pay_date = models.DateField(default=timezone.localdate)
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODE_CHOICES, default='BANK_TRANSFER')

    # Attendance / payable days
    days_in_month = models.IntegerField(default=30)
    effective_work_days = models.IntegerField(default=30)
    lop = models.IntegerField(default=0)

    # Earnings
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    hra = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    conveyance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    special_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    overtime = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Employee deductions
    pf = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    esi = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    professional_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    income_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    lop_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Employer contributions (not deducted from employee net salary)
    employer_pf = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    employer_esi = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    employer_other = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Totals
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_employer_contribution = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-generated_at']
        unique_together = ('employee', 'month', 'year')

    def __str__(self):
        emp_id = self.employee.employee_id if self.employee_id else 'Unknown'
        return f"{self.payslip_number or emp_id} - {self.month} {self.year}"

    @property
    def total_cost_to_company(self):
        return self.gross_salary + self.total_employer_contribution

    def save(self, *args, **kwargs):
        if not self.payslip_number:
            month_map = {
                name: number for number, name in enumerate(
                    ['January', 'February', 'March', 'April', 'May', 'June',
                     'July', 'August', 'September', 'October', 'November', 'December'],
                    start=1
                )
            }
            month_num = month_map.get(str(self.month).strip().title(), 0)
            self.payslip_number = f"PAY-{self.year}-{month_num:02d}-{self.employee.employee_id}"
        self.gross_salary = (
            self.basic_salary + self.hra + self.conveyance +
            self.special_allowance + self.overtime + self.bonus +
            self.other_earnings
        )
        self.total_deductions = (
            self.pf + self.esi + self.professional_tax +
            self.income_tax + self.lop_deduction + self.other_deduction
        )
        self.net_salary = self.gross_salary - self.total_deductions
        self.total_employer_contribution = (
            self.employer_pf + self.employer_esi + self.employer_other
        )
        super().save(*args, **kwargs)
