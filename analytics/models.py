from django.db import models
from django.utils.translation import gettext_lazy as _
from grading.models import Student, Grade, Subject, Class
from authentication.models import User

class AnalyticsDashboard(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class GradeDistribution(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    academic_year = models.CharField(max_length=50)
    term = models.CharField(max_length=10, choices=Grade.Term.choices)
    
    # Grade counts
    a_count = models.IntegerField(default=0)
    b_count = models.IntegerField(default=0)
    c_count = models.IntegerField(default=0)
    d_count = models.IntegerField(default=0)
    f_count = models.IntegerField(default=0)
    
    total_students = models.IntegerField(default=0)
    average_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    pass_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    calculated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['subject', 'academic_year', 'term']
    
    def __str__(self):
        return f"{self.subject} - {self.academic_year} - {self.term}"

class StudentPerformance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    academic_year = models.CharField(max_length=50)
    term = models.CharField(max_length=10, choices=Grade.Term.choices)
    
    total_subjects = models.IntegerField(default=0)
    average_grade = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    rank_in_class = models.IntegerField(null=True, blank=True)
    total_attendance = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    performance_trend = models.CharField(
        max_length=10,
        choices=[('IMPROVING', 'Improving'), ('STABLE', 'Stable'), ('DECLINING', 'Declining')],
        default='STABLE'
    )
    
    calculated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'academic_year', 'term']
    
    def __str__(self):
        return f"{self.student} - {self.academic_year} - {self.term}"