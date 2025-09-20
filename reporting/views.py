from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from grading.models import Student, Grade, Class
from django.shortcuts import get_object_or_404
import csv
from django.utils import timezone

class ReportingDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'reporting/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['classes'] = Class.objects.all()
        return context

class StudentReportView(LoginRequiredMixin, TemplateView):
    template_name = 'reporting/student_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student_id = self.kwargs['student_id']
        student = get_object_or_404(Student, id=student_id)
        
        # Get all grades for this student
        grades = Grade.objects.filter(student=student)
        
        # Calculate subject statistics
        subject_stats = {}
        for grade in grades:
            if grade.subject.name not in subject_stats:
                subject_stats[grade.subject.name] = {
                    'total_score': 0,
                    'count': 0,
                    'avg_score': 0
                }
            subject_stats[grade.subject.name]['total_score'] += float(grade.percentage)
            subject_stats[grade.subject.name]['count'] += 1
        
        # Calculate averages
        for subject, stats in subject_stats.items():
            stats['avg_score'] = stats['total_score'] / stats['count'] if stats['count'] > 0 else 0
        
        # Calculate overall average
        overall_avg = sum(stats['avg_score'] for stats in subject_stats.values()) / len(subject_stats) if subject_stats else 0
        
        context['student'] = student
        context['grades'] = grades
        context['subject_stats'] = subject_stats
        context['overall_avg'] = overall_avg
        
        return context

class CSVExportView(LoginRequiredMixin, View):
    def get(self, request):
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="mgpas_export_{}.csv"'.format(
            timezone.now().strftime("%Y%m%d_%H%M%S")
        )
        
        writer = csv.writer(response)
        writer.writerow(['Student', 'Subject', 'Assessment', 'Type', 'Score', 'Max Score', 'Percentage', 'Term', 'Date'])
        
        grades = Grade.objects.all().select_related('student', 'subject')
        for grade in grades:
            writer.writerow([
                f"{grade.student.first_name} {grade.student.last_name}",
                grade.subject.name,
                grade.assessment_name,
                grade.get_assessment_type_display(),
                grade.score,
                grade.max_score,
                grade.percentage,
                grade.get_term_display(),
                grade.date
            ])
        
        return response

class ClassReportView(LoginRequiredMixin, TemplateView):
    template_name = 'reporting/class_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        class_id = self.kwargs['class_id']
        class_obj = get_object_or_404(Class, id=class_id)
        
        # Get students in this class
        students = Student.objects.filter(current_class=class_obj)
        
        context['class'] = class_obj
        context['students'] = students
        
        return context