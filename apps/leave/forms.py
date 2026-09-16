class HolidayForm(forms.ModelForm):

    class Meta:

        model = Holiday

        fields = '__all__'

        widgets = {

            'holiday_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }
            ),

            'name': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'holiday_type': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3
                }
            )
        }