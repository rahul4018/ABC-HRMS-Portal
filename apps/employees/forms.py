from django import forms
from django.contrib.auth import get_user_model

from .models import Employee
from .models import Asset

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
class AssetForm(forms.ModelForm):

    class Meta:

        model = Asset

        fields = [
            'asset_name',
            'asset_code',
            'asset_type',
            'assigned_to',
            'purchase_date',
            'asset_value',
            'status',
            'remarks'
        ]

        widgets = {

            'asset_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter asset name'
                }
            ),

            'asset_code': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter unique asset code'
                }
            ),

            'asset_type': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

            'assigned_to': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

            'purchase_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }
            ),

            'asset_value': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter asset value'
                }
            ),

            'status': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

            'remarks': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Remarks'
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields['assigned_to'].empty_label = (
            'Select Employee'
        )

        self.fields['assigned_to'].label_from_instance = (
            lambda obj: f"{obj.employee_id} - {obj.user.email}"
        )