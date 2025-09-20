# grading/views.py
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.forms.models import model_to_dict
from .forms import GradeForm

# Import your models
from .models import Student, Grade, Class, Subject

# Student Views
class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'grading/student_dashboard.html'
    context_object_name = 'students'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Student.objects.filter(is_active=True)
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(student_id__icontains=search_query)
            )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add statistics to context
        context['total_students'] = Student.objects.count()
        context['active_students'] = Student.objects.filter(is_active=True).count()
        context['total_classes'] = Class.objects.count()
        
        # Calculate new students this month
        from datetime import datetime, timedelta
        last_month = datetime.now() - timedelta(days=30)
        context['new_students'] = Student.objects.filter(
            created_at__gte=last_month
        ).count()
        
        # Get all classes for filter
        context['classes'] = Class.objects.all()
        
        return context

class StudentDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = 'grading/student_detail.html'
    context_object_name = 'student'

@method_decorator(csrf_exempt, name='dispatch')
class StudentCreateView(LoginRequiredMixin, CreateView):
    model = Student
    template_name = 'grading/student_form.html'
    fields = '__all__'
    success_url = reverse_lazy('grading:student_list')
    
    def form_valid(self, form):
        self.object = form.save()
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            data = {
                'success': True,
                'student': model_to_dict(self.object),
                'message': 'Student created successfully!'
            }
            return JsonResponse(data)
        messages.success(self.request, 'Student created successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False, 
                'errors': form.errors
            }, status=400)
        return super().form_invalid(form)

class StudentUpdateView(LoginRequiredMixin, UpdateView):
    model = Student
    template_name = 'grading/student_form.html'
    fields = '__all__'
    
    def get_success_url(self):
        messages.success(self.request, 'Student updated successfully!')
        return reverse_lazy('grading:student_detail', kwargs={'pk': self.object.pk})

class StudentDeleteView(LoginRequiredMixin, DeleteView):
    model = Student
    template_name = 'grading/student_confirm_delete.html'
    success_url = reverse_lazy('grading:student_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Student deleted successfully!')
        return super().delete(request, *args, **kwargs)

# Grade Views
class GradeListView(LoginRequiredMixin, ListView):
    model = Grade
    template_name = "grading/grade_list.html"
    context_object_name = "grades"
    paginate_by = 20

    def get_queryset(self):
        queryset = Grade.objects.all().select_related("student", "subject")
        search_query = self.request.GET.get("search")
        if search_query:
            queryset = queryset.filter(
                Q(student__first_name__icontains=search_query) |
                Q(student__last_name__icontains=search_query) |
                Q(subject__name__icontains=search_query) |
                Q(assessment_name__icontains=search_query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add statistics
        grades = self.get_queryset()
        total_grades = grades.count()
        
        # Calculate average grade
        if total_grades > 0:
            average_grade = grades.aggregate(avg=Avg('percentage'))['avg']
        else:
            average_grade = None
        
        # Count unique students
        students_graded = grades.values('student').distinct().count()
        
        # Get all subjects for filter
        subjects = Subject.objects.all()
        
        context.update({
            'total_grades': total_grades,
            'average_grade': average_grade,
            'students_graded': students_graded,
            'total_subjects': subjects.count(),
            'subjects': subjects
        })
        
        return context



@method_decorator(csrf_exempt, name='dispatch')
class GradeCreateView(LoginRequiredMixin, CreateView):
    model = Grade
    form_class = GradeForm  # Use the custom form
    template_name = 'grading/grade_form.html'
    success_url = reverse_lazy('grading:grade_list')
    
    def get_initial(self):
        initial = super().get_initial()
        # Pre-select student if coming from student detail page
        student_id = self.request.GET.get('student')
        if student_id:
            try:
                student = Student.objects.get(id=student_id)
                initial['student'] = student
            except Student.DoesNotExist:
                pass
        return initial
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            self.object = form.save()
            data = {
                'success': True,
                'grade': model_to_dict(self.object),
                'message': 'Grade added successfully!'
            }
            return JsonResponse(data)
        messages.success(self.request, 'Grade added successfully!')
        return super().form_valid(form)

# Update the GradeUpdateView to use the custom form
@method_decorator(csrf_exempt, name='dispatch')
class GradeUpdateView(LoginRequiredMixin, UpdateView):
    model = Grade
    form_class = GradeForm  # Use the custom form
    template_name = 'grading/grade_form.html'
    
    def form_valid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            self.object = form.save()
            data = {
                'success': True,
                'grade': model_to_dict(self.object),
                'message': 'Grade updated successfully!'
            }
            return JsonResponse(data)
        messages.success(self.request, 'Grade updated successfully!')
        return super().form_valid(form)

@method_decorator(csrf_exempt, name='dispatch')
class GradeDeleteView(LoginRequiredMixin, DeleteView):
    model = Grade
    template_name = 'grading/grade_confirm_delete.html'
    success_url = reverse_lazy('grading:grade_list')
    
    def delete(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            self.object = self.get_object()
            self.object.delete()
            return JsonResponse({'success': True, 'message': 'Grade deleted successfully!'})
        messages.success(self.request, 'Grade deleted successfully!')
        return super().delete(request, *args, **kwargs)