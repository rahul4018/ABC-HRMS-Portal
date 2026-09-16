from django import forms
from django.contrib.auth import get_user_model

from .models import Employee, Asset


User = get_user_model()


# ==========================================================
# EMPLOYEE MODEL FIELD GROUP
# ==========================================================

EMPLOYEE_DATA_FIELDS = [
    'department',
    'reporting_manager',
    'designation',
    'employment_type',
    'work_mode',
    'phone',
    'address',
    'location',
    'date_of_birth',
    'gender',
    'marital_status',
    'blood_group',
    'nationality',
    'joining_date',
    'probation_end_date',
    'exit_date',
    'salary',
    'bank_name',
    'account_holder_name',
    'account_number',
    'ifsc_code',
    'pan_number',
    'aadhaar_number',
    'passport_number',
    'pf_number',
    'esi_number',
    'uan_number',
    'emergency_contact_name',
    'emergency_contact_number',
    'emergency_contact_relation',
    'status',
    'profile_picture',
]


# ==========================================================
# EMPLOYEE CREATE FORM
# ==========================================================

class EmployeeCreateForm(forms.ModelForm):
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Employee email (optional)',
            }
        )
    )

    username = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'User ID',
            }
        )
    )

    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Temporary password',
            }
        )
    )

    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'First name',
            }
        )
    )

    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Last name',
            }
        )
    )

    class Meta:
        model = Employee
        fields = EMPLOYEE_DATA_FIELDS

        widgets = {
            'joining_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                }
            ),
            'probation_end_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                }
            ),
            'exit_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                }
            ),
            'date_of_birth': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                }
            ),
            'address': forms.Textarea(
                attrs={
                    'rows': 4,
                    'class': 'form-control',
                }
            ),
            'department': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),
            'reporting_manager': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),
            'employment_type': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),
            'work_mode': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),
            'gender': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),
            'marital_status': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),
            'status': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),
            'profile_picture': forms.ClearableFileInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            'salary': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'min': '0',
                }
            ),
            'phone': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Phone number',
                }
            ),
            'location': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Work location',
                }
            ),
            'blood_group': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Blood group',
                }
            ),
            'nationality': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Nationality',
                }
            ),
            'bank_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Bank name',
                }
            ),
            'account_holder_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Account holder name',
                }
            ),
            'account_number': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Account number',
                }
            ),
            'ifsc_code': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'IFSC code',
                }
            ),
            'pan_number': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'PAN number',
                }
            ),
            'aadhaar_number': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Aadhaar number',
                }
            ),
            'passport_number': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Passport number',
                }
            ),
            'pf_number': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'PF number',
                }
            ),
            'esi_number': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'ESI number',
                }
            ),
            'uan_number': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'UAN number',
                }
            ),
            'emergency_contact_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Emergency contact name',
                }
            ),
            'emergency_contact_number': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Emergency contact number',
                }
            ),
            'emergency_contact_relation': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Relationship',
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['reporting_manager'].required = False
        self.fields['reporting_manager'].queryset = (
            Employee.objects
            .select_related('user')
            .order_by('employee_id')
        )

        self._add_text_classes()

    def _add_text_classes(self):
        for name, field in self.fields.items():
            if isinstance(
                field.widget,
                (
                    forms.TextInput,
                    forms.EmailInput,
                    forms.PasswordInput,
                )
            ):
                field.widget.attrs.setdefault(
                    'class',
                    'form-control',
                )

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data.get('email') or '',
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            role='EMPLOYEE',
            is_active=True,
        )

        # Force the new employee through the first-login password flow.
        if hasattr(user, 'must_change_password'):
            user.must_change_password = True

        employee = super().save(commit=False)
        employee.user = user

        # Newly created employee profiles must be completed and reviewed.
        if hasattr(employee, 'profile_status'):
            employee.profile_status = 'PROFILE_PENDING'
        if hasattr(employee, 'profile_submitted_at'):
            employee.profile_submitted_at = None

        if commit:
            user.save()
            employee.save()

        return employee


# ==========================================================
# EMPLOYEE UPDATE FORM
# ==========================================================

class EmployeeUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
            }
        )
    )

    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
            }
        )
    )

    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
            }
        )
    )

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
            }
        )
    )

    class Meta:
        model = Employee
        fields = EMPLOYEE_DATA_FIELDS

        widgets = {
            'joining_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                }
            ),
            'probation_end_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                }
            ),
            'exit_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                }
            ),
            'date_of_birth': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                }
            ),
            'address': forms.Textarea(
                attrs={
                    'rows': 4,
                    'class': 'form-control',
                }
            ),
            'department': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),
            'reporting_manager': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),
            'employment_type': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),
            'work_mode': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),
            'gender': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),
            'marital_status': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),
            'status': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),
            'profile_picture': forms.ClearableFileInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            'salary': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'min': '0',
                }
            ),
            'phone': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            'location': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            'blood_group': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            'nationality': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            'bank_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            'account_holder_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            'account_number': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            'ifsc_code': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            'pan_number': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            'aadhaar_number': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            'passport_number': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            'pf_number': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            'esi_number': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            'uan_number': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            'emergency_contact_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            'emergency_contact_number': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            'emergency_contact_relation': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        employee = self.instance

        if (
            employee
            and employee.pk
            and getattr(employee, 'user', None)
        ):
            self.fields['first_name'].initial = employee.user.first_name
            self.fields['last_name'].initial = employee.user.last_name
            self.fields['email'].initial = employee.user.email
            self.fields['username'].initial = employee.user.username

        self.fields['reporting_manager'].required = False
        self.fields['reporting_manager'].queryset = (
            Employee.objects
            .select_related('user')
            .exclude(
                pk=getattr(
                    employee,
                    'pk',
                    None,
                )
            )
            .order_by('employee_id')
        )

        for name, field in self.fields.items():
            if isinstance(
                field.widget,
                (
                    forms.TextInput,
                    forms.EmailInput,
                )
            ):
                field.widget.attrs.setdefault(
                    'class',
                    'form-control',
                )

    def clean_email(self):
        email = self.cleaned_data.get('email') or ''

        if not email:
            return ''

        qs = (
            User.objects
            .filter(email=email)
            .exclude(pk=self.instance.user_id)
        )

        if qs.exists():
            raise forms.ValidationError(
                'This email address is already in use.'
            )

        return email

    def clean_username(self):
        username = self.cleaned_data['username']

        qs = (
            User.objects
            .filter(username=username)
            .exclude(pk=self.instance.user_id)
        )

        if qs.exists():
            raise forms.ValidationError(
                'This username is already in use.'
            )

        return username

    def save(self, commit=True):
        employee = super().save(commit=commit)

        if commit and employee.user_id:
            user = employee.user

            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data.get('email') or ''
            user.username = self.cleaned_data['username']

            user.save(
                update_fields=[
                    'first_name',
                    'last_name',
                    'email',
                    'username',
                ]
            )

        return employee


# ==========================================================
# MY PROFILE / EMPLOYEE SELF-SERVICE FORM
# ==========================================================

class MyProfileUpdateForm(forms.ModelForm):
    """
    Employee self-service onboarding/update form.

    Employees may edit their own:
    - First name / last name
    - Email, when available
    - Phone
    - Date of birth
    - Gender
    - Marital status
    - Blood group
    - Nationality
    - Address
    - Location
    - PAN / Aadhaar / Passport
    - Bank details
    - Emergency contact
    - Profile picture

    HR/master-controlled fields are intentionally excluded:
    - Employee ID
    - Department
    - Designation
    - Reporting manager
    - Employment type
    - Work mode
    - Joining date
    - Probation end date
    - Exit date
    - Salary
    - PF number
    - ESI number
    - UAN number
    - Employment status
    """

    first_name = forms.CharField(
        max_length=150,
        required=True,
        label='First Name',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter first name',
            }
        )
    )

    last_name = forms.CharField(
        max_length=150,
        required=True,
        label='Last Name',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter last name',
            }
        )
    )

    email = forms.EmailField(
        required=False,
        label='Email',
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Email address (optional)',
            }
        )
    )

    class Meta:
        model = Employee

        fields = [
            'phone',
            'date_of_birth',
            'gender',
            'marital_status',
            'blood_group',
            'nationality',
            'address',
            'location',
            'pan_number',
            'aadhaar_number',
            'passport_number',
            'bank_name',
            'account_holder_name',
            'account_number',
            'ifsc_code',
            'emergency_contact_name',
            'emergency_contact_number',
            'emergency_contact_relation',
            'profile_picture',
        ]

        widgets = {
            'phone': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter phone number',
                }
            ),
            'date_of_birth': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                }
            ),
            'gender': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),
            'marital_status': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),
            'blood_group': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'e.g. O+',
                }
            ),
            'nationality': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'e.g. Indian',
                }
            ),
            'address': forms.Textarea(
                attrs={
                    'rows': 4,
                    'class': 'form-control',
                    'placeholder': 'Enter complete address',
                }
            ),
            'location': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'City / Work location',
                }
            ),
            'pan_number': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'PAN number',
                    'autocomplete': 'off',
                }
            ),
            'aadhaar_number': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Aadhaar number',
                    'autocomplete': 'off',
                }
            ),
            'passport_number': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Passport number',
                    'autocomplete': 'off',
                }
            ),
            'bank_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Bank name',
                }
            ),
            'account_holder_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Account holder name',
                }
            ),
            'account_number': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Bank account number',
                    'autocomplete': 'off',
                }
            ),
            'ifsc_code': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'IFSC code',
                    'autocomplete': 'off',
                }
            ),
            'emergency_contact_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Emergency contact name',
                }
            ),
            'emergency_contact_number': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Emergency contact number',
                }
            ),
            'emergency_contact_relation': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Relationship',
                }
            ),
            'profile_picture': forms.ClearableFileInput(
                attrs={
                    'class': 'form-control',
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        employee = self.instance

        if (
            employee
            and employee.pk
            and employee.user_id
        ):
            self.fields['first_name'].initial = employee.user.first_name
            self.fields['last_name'].initial = employee.user.last_name
            self.fields['email'].initial = employee.user.email

        # Make the important onboarding fields required.
        required_employee_fields = [
            'phone',
            'date_of_birth',
            'gender',
            'marital_status',
            'nationality',
            'address',
            'location',
            'emergency_contact_name',
            'emergency_contact_number',
            'emergency_contact_relation',
        ]

        for field_name in required_employee_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True

        # Identity and bank fields are intentionally optional because
        # availability can vary by employee/country and HR may verify them.
        for field_name in [
            'blood_group',
            'pan_number',
            'aadhaar_number',
            'passport_number',
            'bank_name',
            'account_holder_name',
            'account_number',
            'ifsc_code',
        ]:
            if field_name in self.fields:
                self.fields[field_name].required = False

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip()

        if not email:
            return ''

        qs = (
            User.objects
            .filter(email__iexact=email)
            .exclude(pk=self.instance.user_id)
        )

        if qs.exists():
            raise forms.ValidationError(
                'This email address is already in use.'
            )

        return email

    def clean_phone(self):
        phone = (self.cleaned_data.get('phone') or '').strip()

        if phone and len(phone) > 15:
            raise forms.ValidationError(
                'Phone number must not exceed 15 characters.'
            )

        return phone

    def clean_emergency_contact_number(self):
        number = (
            self.cleaned_data
            .get('emergency_contact_number') or ''
        ).strip()

        if number and len(number) > 15:
            raise forms.ValidationError(
                'Emergency contact number must not exceed 15 characters.'
            )

        return number

    def clean_pan_number(self):
        value = (self.cleaned_data.get('pan_number') or '').strip().upper()

        if value and len(value) > 20:
            raise forms.ValidationError(
                'PAN number is too long.'
            )

        return value

    def clean_aadhaar_number(self):
        value = (
            self.cleaned_data
            .get('aadhaar_number') or ''
        ).strip()

        if value and len(value) > 20:
            raise forms.ValidationError(
                'Aadhaar number is too long.'
            )

        return value

    def clean_passport_number(self):
        value = (
            self.cleaned_data
            .get('passport_number') or ''
        ).strip().upper()

        if value and len(value) > 20:
            raise forms.ValidationError(
                'Passport number is too long.'
            )

        return value

    def clean_ifsc_code(self):
        value = (
            self.cleaned_data
            .get('ifsc_code') or ''
        ).strip().upper()

        if value and len(value) > 20:
            raise forms.ValidationError(
                'IFSC code is too long.'
            )

        return value

    def save(self, commit=True):
        employee = super().save(commit=commit)

        if commit and employee.user_id:
            user = employee.user

            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data.get('email') or ''

            user.save(
                update_fields=[
                    'first_name',
                    'last_name',
                    'email',
                ]
            )

        return employee


# ==========================================================
# ASSET FORM
# ==========================================================

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
            'remarks',
        ]

        widgets = {
            'asset_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter asset name',
                }
            ),
            'asset_code': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter unique asset code',
                }
            ),
            'asset_type': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),
            'assigned_to': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),
            'purchase_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                }
            ),
            'asset_value': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter asset value',
                    'step': '0.01',
                    'min': '0',
                }
            ),
            'status': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),
            'remarks': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Remarks',
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['assigned_to'].empty_label = 'Select Employee'

        self.fields['assigned_to'].label_from_instance = (
            lambda obj: (
                f"{obj.employee_id} - "
                f"{obj.user.email or obj.user.username}"
            )
        )
