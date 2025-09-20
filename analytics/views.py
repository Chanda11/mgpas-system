# analytics/views.py
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count, Q
from grading.models import Grade, Student, Subject

class AnalyticsDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Overall statistics
        context['total_students'] = Student.objects.count()
        context['active_students'] = Student.objects.filter(is_active=True).count()
        context['total_grades'] = Grade.objects.count()
        context['total_subjects'] = Subject.objects.count()
        
        # Average grades
        context['overall_average'] = Grade.objects.aggregate(avg=Avg('percentage'))['avg']
        
        # Grade distribution
        context['grade_distribution'] = {
            'A': Grade.objects.filter(percentage__gte=90).count(),
            'B': Grade.objects.filter(percentage__gte=80, percentage__lt=90).count(),
            'C': Grade.objects.filter(percentage__gte=70, percentage__lt=80).count(),
            'D': Grade.objects.filter(percentage__gte=60, percentage__lt=70).count(),
            'F': Grade.objects.filter(percentage__lt=60).count()
        }
        
        # Subject averages
        context['subject_averages'] = Grade.objects.values(
            'subject__name'
        ).annotate(
            average=Avg('percentage'),
            count=Count('id')
        ).order_by('subject__name')
        
        # Term averages
        context['term_averages'] = Grade.objects.values(
            'term'
        ).annotate(
            average=Avg('percentage'),
            count=Count('id')
        ).order_by('term')
        
        # Recent activity
        context['recent_grades'] = Grade.objects.select_related(
            'student', 'subject'
        ).order_by('-created_at')[:10]
        
        return context

class SubjectAnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/subject_analytics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subject_id = self.kwargs.get('subject_id')
        
        subject = Subject.objects.get(id=subject_id)
        context['subject'] = subject
        
        # Subject grades
        grades = Grade.objects.filter(subject=subject)
        context['grades'] = grades
        
        # Statistics
        context['average_grade'] = grades.aggregate(avg=Avg('percentage'))['avg']
        context['total_grades'] = grades.count()
        context['students_graded'] = grades.values('student').distinct().count()
        
        # Grade distribution for this subject
        context['grade_distribution'] = {
            'A': grades.filter(percentage__gte=90).count(),
            'B': grades.filter(percentage__gte=80, percentage__lt=90).count(),
            'C': grades.filter(percentage__gte=70, percentage__lt=80).count(),
            'D': grades.filter(percentage__gte=60, percentage__lt=70).count(),
            'F': grades.filter(percentage__lt=60).count()
        }
        
        # Term-wise averages
        context['term_averages'] = grades.values(
            'term'
        ).annotate(
            average=Avg('percentage'),
            count=Count('id')
        ).order_by('term')
        
        return context