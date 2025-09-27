from django.db import models
from django.utils.translation import gettext_lazy as _
from authentication.models import User

class AcademicYear(models.Model):
    name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

class Class(models.Model):
    name = models.CharField(max_length=50)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.academic_year})"

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Student(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    student_id = models.CharField(max_length=20, unique=True)
    date_of_birth = models.DateField()
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    current_class = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, blank=True)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    enrollment_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.student_id})"
    
    class Meta:
        ordering = ['last_name', 'first_name']

class Grade(models.Model):
    class Term(models.TextChoices):
        TERM1 = 'TERM1', _('Term 1')
        TERM2 = 'TERM2', _('Term 2')
        TERM3 = 'TERM3', _('Term 3')
    
    class AssessmentType(models.TextChoices):
        EXAM = 'EXAM', _('Exam')
        TEST = 'TEST', _('Test')
        QUIZ = 'QUIZ', _('Quiz')
        ASSIGNMENT = 'ASSIGNMENT', _('Assignment')
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    assessment_name = models.CharField(max_length=100)
    assessment_type = models.CharField(max_length=20, choices=AssessmentType.choices)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, editable=False)
    term = models.CharField(max_length=10, choices=Term.choices)
    date = models.DateField()
    comments = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        self.percentage = (self.score / self.max_score) * 100
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.student} - {self.subject} - {self.score}"
    
    def get_grade_letter(self):
        if self.percentage >= 90: return 'A'
        elif self.percentage >= 80: return 'B'
        elif self.percentage >= 70: return 'C'
        elif self.percentage >= 60: return 'D'
        else: return 'F'
    
    class Meta:
        ordering = ['-date', 'student']