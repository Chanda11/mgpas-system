from django.db import models
from django.utils.translation import gettext_lazy as _
from grading.models import Student, Subject, Class
from authentication.models import User

class ReportTemplate(models.Model):
    class ReportType(models.TextChoices):
        STUDENT_REPORT = 'STUDENT', _('Student Report Card')
        CLASS_SUMMARY = 'CLASS', _('Class Summary Report')
        SCHOOL_SUMMARY = 'SCHOOL', _('School Summary Report')
    
    name = models.CharField(max_length=100)
    report_type = models.CharField(max_length=20, choices=ReportType.choices)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class GeneratedReport(models.Model):
    class ReportFormat(models.TextChoices):
        PDF = 'PDF', _('PDF')
        EXCEL = 'EXCEL', _('Excel')
        HTML = 'HTML', _('HTML')
    
    report_template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    parameters = models.JSONField(default=dict)
    format = models.CharField(max_length=10, choices=ReportFormat.choices, default='PDF')
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-generated_at']
    
    def __str__(self):
        return self.title