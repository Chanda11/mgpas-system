# grading/forms.py (create this file if it doesn't exist)
from django import forms
from .models import Grade, Student, Subject

class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'comments': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in ['date', 'comments']:
                field.widget.attrs['class'] = 'form-control'
            
            if field_name == 'student':
                field.queryset = Student.objects.filter(is_active=True)
                field.empty_label = "Select Student"
            
            if field_name == 'subject':
                field.empty_label = "Select Subject"