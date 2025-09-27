from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q, Avg, Count, Max, Min
from .models import Student, Grade, Subject
from .forms import GradeForm

class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'grading/student_list.html'
    context_object_name = 'students'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Student.objects.filter(is_active=True)
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(student_id__icontains=search)
            )
        return queryset

class StudentDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = 'grading/student_detail.html'
    context_object_name = 'student'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.get_object()
        
        # Get all grades for the student
        grades = Grade.objects.filter(student=student).select_related('subject')
        context['grades'] = grades
        
        # Calculate statistics
        if grades.exists():
            # Overall statistics
            grade_stats = grades.aggregate(
                avg_grade=Avg('percentage'),
                total_grades=Count('id'),
                best_grade=Max('percentage'),
                worst_grade=Min('percentage')
            )
            context.update(grade_stats)
            
            # Subject-wise performance
            subject_performance = grades.values('subject__name').annotate(
                avg_score=Avg('percentage'),
                count=Count('id')
            ).order_by('-avg_score')
            context['subject_performance'] = subject_performance
            
            # Grade distribution
            grade_distribution = {
                'A': grades.filter(percentage__gte=90).count(),
                'B': grades.filter(percentage__gte=80, percentage__lt=90).count(),
                'C': grades.filter(percentage__gte=70, percentage__lt=80).count(),
                'D': grades.filter(percentage__gte=60, percentage__lt=70).count(),
                'F': grades.filter(percentage__lt=60).count(),
            }
            context['grade_distribution'] = grade_distribution
            
        return context

class StudentCreateView(LoginRequiredMixin, CreateView):
    model = Student
    template_name = 'grading/student_form.html'
    fields = '__all__'
    success_url = reverse_lazy('grading:student_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Student created successfully!')
        return super().form_valid(form)

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

class GradeListView(LoginRequiredMixin, ListView):
    model = Grade
    template_name = "grading/grade_list.html"
    context_object_name = "grades"
    paginate_by = 20

    def get_queryset(self):
        queryset = Grade.objects.all().select_related("student", "subject")
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(student__first_name__icontains=search) |
                Q(student__last_name__icontains=search) |
                Q(subject__name__icontains=search)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_grades'] = Grade.objects.count()
        context['average_grade'] = Grade.objects.aggregate(avg=Avg('percentage'))['avg'] or 0
        return context

class GradeCreateView(LoginRequiredMixin, CreateView):
    model = Grade
    form_class = GradeForm
    template_name = 'grading/grade_form.html'
    success_url = reverse_lazy('grading:grade_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Grade added successfully!')
        return super().form_valid(form)

class GradeUpdateView(LoginRequiredMixin, UpdateView):
    model = Grade
    form_class = GradeForm
    template_name = 'grading/grade_form.html'
    
    def get_success_url(self):
        messages.success(self.request, 'Grade updated successfully!')
        return reverse_lazy('grading:grade_list')

class GradeDeleteView(LoginRequiredMixin, DeleteView):
    model = Grade
    template_name = 'grading/grade_confirm_delete.html'
    success_url = reverse_lazy('grading:grade_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Grade deleted successfully!')
        return super().delete(request, *args, **kwargs)