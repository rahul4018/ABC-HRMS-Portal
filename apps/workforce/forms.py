from django import forms
from .models import ExitCase, ExitClearance, ExitInterview, FinalSettlement, HRRequest


class ExitCaseForm(forms.ModelForm):
    class Meta:
        model = ExitCase
        fields = [
            'employee', 'exit_type', 'reason', 'detailed_reason', 'resignation_date',
            'requested_last_working_day', 'notice_period_days', 'notice_waived',
            'actual_last_working_day', 'termination_effective_date', 'manager_comments', 'hr_comments'
        ]
        widgets = {
            'resignation_date': forms.DateInput(attrs={'type': 'date'}),
            'requested_last_working_day': forms.DateInput(attrs={'type': 'date'}),
            'actual_last_working_day': forms.DateInput(attrs={'type': 'date'}),
            'termination_effective_date': forms.DateInput(attrs={'type': 'date'}),
            'detailed_reason': forms.Textarea(attrs={'rows': 4}),
            'manager_comments': forms.Textarea(attrs={'rows': 3}),
            'hr_comments': forms.Textarea(attrs={'rows': 3}),
        }


class ExitClearanceForm(forms.ModelForm):
    class Meta:
        model = ExitClearance
        fields = ['department_name', 'owner_name', 'status', 'comments']
        widgets = {'comments': forms.Textarea(attrs={'rows': 3})}


class ExitInterviewForm(forms.ModelForm):
    class Meta:
        model = ExitInterview
        exclude = ['exit_case', 'completed_at']
        widgets = {'feedback': forms.Textarea(attrs={'rows': 5}), 'hr_summary': forms.Textarea(attrs={'rows': 4})}


class FinalSettlementForm(forms.ModelForm):
    class Meta:
        model = FinalSettlement
        exclude = ['exit_case', 'reviewed_by', 'approved_by', 'status', 'paid_at']


class HRRequestForm(forms.ModelForm):
    class Meta:
        model = HRRequest
        fields = ['category', 'subject', 'description', 'priority']
        widgets = {'description': forms.Textarea(attrs={'rows': 5})}
