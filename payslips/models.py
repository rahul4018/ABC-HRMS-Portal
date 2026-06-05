from django.db import models
from apps.employees.models import Employee


class Payslip(models.Model):
    STATUS_CHOICES = [
        ('GENERATED', 'Generated'),
        ('PAID', 'Paid'),
        ('HOLD', 'Hold'),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='payslips'
    )
    month = models.CharField(max_length=20)
    year = models.IntegerField()
    
    # Earnings breakdown
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    hra = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Deductions breakdown
    pf = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    professional_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Final Payout calculation storage
    net_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='GENERATED')
    remarks = models.TextField(blank=True, null=True)
    
    # Metadata timestamps
    generated_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-generated_at']
        unique_together = ('employee', 'month', 'year')

    def __str__(self):
        return f"{self.employee.employee_id} - {self.month} {self.year}"

    @property
    def gross_salary(self):
        return self.basic_salary + self.hra + self.allowance + self.bonus

    @property
    def total_deductions(self):
        return self.pf + self.professional_tax + self.other_deduction

    def save(self, *args, **kwargs):
        """Automatically calculate and populate net salary right before database write operations."""
        self.net_salary = self.gross_salary - self.total_deductions
        super().save(*args, **kwargs)