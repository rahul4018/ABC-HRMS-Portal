from django import forms
from django.contrib.auth import get_user_model

from .models import Employee


User = get_user_model()


class EmployeeCreateForm(forms.ModelForm):

    email = forms.EmailField()

    username = forms.CharField()

    password = forms.CharField(
        widget=forms.PasswordInput
    )

    class Meta:

        model = Employee

        fields = [
            'department',
            'designation',
            'phone',
            'address',
            'joining_date',
            'profile_picture',
            'salary',
            'status',
        ]

    def save(self, commit=True):

        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            role='EMPLOYEE'
        )

        employee_count = Employee.objects.count() + 1

        employee = super().save(commit=False)

        employee.user = user

        employee.employee_id = f"SCH{employee_count:04d}"

        if commit:
            employee.save()

        return employee