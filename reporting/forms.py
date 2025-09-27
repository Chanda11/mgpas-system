from django import forms
from grading.models import Student, Class

class StudentReportForm(forms.Form):
    student = forms.ModelChoiceField(
        queryset=Student.objects.filter(is_active=True),
        empty_label="Select Student",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    academic_year = forms.ChoiceField(
        choices=[('2024-2025', '2024-2025')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    term = forms.ChoiceField(
        choices=[
            ('TERM1', 'Term 1'),
            ('TERM2', 'Term 2'),
            ('TERM3', 'Term 3'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    format = forms.ChoiceField(
        choices=[
            ('PDF', 'PDF'),
            ('EXCEL', 'Excel'),
            ('HTML', 'HTML'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class ClassReportForm(forms.Form):
    class_obj = forms.ModelChoiceField(
        queryset=Class.objects.all(),
        empty_label="Select Class",
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Class"
    )
    academic_year = forms.ChoiceField(
        choices=[('2024-2025', '2024-2025')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    term = forms.ChoiceField(
        choices=[
            ('TERM1', 'Term 1'),
            ('TERM2', 'Term 2'),
            ('TERM3', 'Term 3'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    format = forms.ChoiceField(
        choices=[
            ('PDF', 'PDF'),
            ('EXCEL', 'Excel'),
            ('HTML', 'HTML'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class SchoolReportForm(forms.Form):
    academic_year = forms.ChoiceField(
        choices=[('2024-2025', '2024-2025')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    term = forms.ChoiceField(
        choices=[
            ('TERM1', 'Term 1'),
            ('TERM2', 'Term 2'),
            ('TERM3', 'Term 3'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    format = forms.ChoiceField(
        choices=[
            ('PDF', 'PDF'),
            ('EXCEL', 'Excel'),
            ('HTML', 'HTML'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )