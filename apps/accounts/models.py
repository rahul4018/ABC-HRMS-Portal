from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    class Role(models.TextChoices):

        SUPERVISOR = 'SUPERVISOR', 'Supervisor'

        EMPLOYEE = 'EMPLOYEE', 'Employee'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.EMPLOYEE
    )

    email = models.EmailField(
        unique=True
    )

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = [
        'username'
    ]

    def save(self, *args, **kwargs):

        if self.is_superuser:

            self.role = self.Role.SUPERVISOR

        super().save(
            *args,
            **kwargs
        )

    def __str__(self):

        return self.email


class CompanySettings(models.Model):

    company_name = models.CharField(
        max_length=200
    )

    company_address = models.TextField()

    company_email = models.EmailField()

    company_phone = models.CharField(
        max_length=20
    )

    company_logo = models.ImageField(
        upload_to='company/',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):

        return self.company_name