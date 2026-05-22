from django import forms
from django.contrib.auth import get_user_model

from .models import Employee

User = get_user_model()


class EmployeeCreateForm(forms.ModelForm):

    email = forms.EmailField()

    username = forms.CharField()

    password = forms.CharField(
        widget=forms.PasswordInput()
    )

    class Meta:

        model = Employee

        fields = [
            'department',
            'designation',
            'phone',
            'address',
            'joining_date',
            'salary',
            'status',
            'profile_picture',
        ]

        widgets = {

            'joining_date': forms.DateInput(
                attrs={'type': 'date'}
            ),

            'address': forms.Textarea(
                attrs={'rows': 4}
            ),
        }

    def save(self, commit=True):

        user = User.objects.create_user(

            username=self.cleaned_data['username'],

            email=self.cleaned_data['email'],

            password=self.cleaned_data['password'],

            role='EMPLOYEE'
        )

        employee = super().save(commit=False)

        employee.user = user

        if commit:
            employee.save()

        return employee


class EmployeeUpdateForm(forms.ModelForm):

    class Meta:

        model = Employee

        fields = [
            'department',
            'designation',
            'phone',
            'address',
            'joining_date',
            'salary',
            'status',
            'profile_picture',
        ]

        widgets = {

            'joining_date': forms.DateInput(
                attrs={'type': 'date'}
            ),

            'address': forms.Textarea(
                attrs={'rows': 4}
            ),
        }