from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count, Q
from grading.models import Student, Grade, Subject, Class

class AnalyticsDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            # Basic statistics
            context['total_students'] = Student.objects.filter(is_active=True).count()
            context['total_subjects'] = Subject.objects.count()
            context['total_grades'] = Grade.objects.count()
            
            # Average grade
            avg_grade = Grade.objects.aggregate(avg=Avg('percentage'))['avg']
            context['overall_average'] = round(avg_grade, 2) if avg_grade else 0
            
            # Top performing students
            top_students = Student.objects.annotate(
                avg_grade=Avg('grade__percentage'),
                grade_count=Count('grade')
            ).filter(avg_grade__isnull=False, grade_count__gte=1).order_by('-avg_grade')[:5]
            context['top_students'] = top_students
            
            # Subject performance
            subject_performance = Subject.objects.annotate(
                avg_score=Avg('grade__percentage'),
                total_grades=Count('grade')
            ).filter(avg_score__isnull=False).order_by('-avg_score')[:5]
            context['subject_performance'] = subject_performance
            
            # Class performance
            class_performance = Class.objects.annotate(
                avg_grade=Avg('student__grade__percentage'),
                student_count=Count('student', filter=Q(student__is_active=True))
            ).filter(student_count__gt=0).order_by('-avg_grade')[:5]
            context['class_performance'] = class_performance
            
        except Exception as e:
            # Fallback data
            context.update({
                'total_students': 0,
                'total_subjects': 0,
                'total_grades': 0,
                'overall_average': 0,
                'top_students': [],
                'subject_performance': [],
                'class_performance': [],
            })
        
        return context

class GradeAnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/grade_analytics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subjects'] = Subject.objects.all()
        return context

class StudentAnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/student_analytics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['students'] = Student.objects.filter(is_active=True)
        return context