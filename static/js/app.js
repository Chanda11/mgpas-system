# authentication/views.py - Update DashboardView
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'
    login_url = '/auth/login/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add counts for the navbar badges
        try:
            from grading.models import Student, Subject, Grade
            context.update({
                'total_students': Student.objects.count(),
                'total_grades': Grade.objects.count(),
                'total_subjects': Subject.objects.count(),
            })
        except:
            context.update({
                'total_students': 0,
                'total_grades': 0,
                'total_subjects': 0,
            })
        
        return context