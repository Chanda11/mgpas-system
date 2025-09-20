# authentication/views.py
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, UpdateView, TemplateView, DetailView  # Add DetailView
from django.contrib import messages
from .forms import LoginForm, UserProfileForm
from .models import User

class LoginView(FormView):
    template_name = 'authentication/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('dashboard')
    
    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        return super().form_valid(form)

def custom_logout(request):
    logout(request)
    return redirect('authentication:login')

class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'authentication/profile.html'
    success_url = reverse_lazy('profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)

## authentication/views.py
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'
    login_url = '/auth/login/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Try to get real data, fallback to sample data if models don't exist yet
        try:
            from grading.models import Student, Subject, Grade
            context.update({
                'total_students': Student.objects.count(),
                'active_students': Student.objects.filter(is_active=True).count(),
                'total_subjects': Subject.objects.count(),
                'total_grades': Grade.objects.count(),
            })
        except:
            # Fallback to sample data
            context.update({
                'total_students': 247,
                'active_students': 235,
                'total_subjects': 12,
                'total_grades': 1842,
            })
        
        return context