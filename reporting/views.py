from django.views.generic import TemplateView, FormView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import GeneratedReport, ReportTemplate
from .forms import StudentReportForm, ClassReportForm, SchoolReportForm
from .services import ReportGenerator

class ReportsDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'reporting/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_reports'] = GeneratedReport.objects.filter(generated_by=self.request.user).count()
        context['recent_reports'] = GeneratedReport.objects.filter(generated_by=self.request.user)[:5]
        return context

class StudentReportView(LoginRequiredMixin, FormView):
    template_name = 'reporting/student_report.html'
    form_class = StudentReportForm
    success_url = reverse_lazy('reporting:dashboard')
    
    def form_valid(self, form):
        try:
            student = form.cleaned_data['student']
            academic_year = form.cleaned_data['academic_year']
            term = form.cleaned_data['term']
            format = form.cleaned_data['format']
            
            response = ReportGenerator.generate_student_report_card(student, academic_year, term, format)
            
            # Save report record
            template, created = ReportTemplate.objects.get_or_create(
                report_type='STUDENT',
                defaults={'name': 'Student Report Card'}
            )
            
            GeneratedReport.objects.create(
                report_template=template,
                title=f"Report - {student.get_full_name()}",
                generated_by=self.request.user,
                parameters={'student_id': student.id},
                format=format
            )
            
            messages.success(self.request, 'Report generated successfully!')
            return response
            
        except Exception as e:
            messages.error(self.request, f'Error: {str(e)}')
            return self.form_invalid(form)

class ClassReportView(LoginRequiredMixin, FormView):
    template_name = 'reporting/class_report.html'
    form_class = ClassReportForm
    success_url = reverse_lazy('reporting:dashboard')
    
    def form_valid(self, form):
        messages.info(self.request, 'Class report functionality coming soon!')
        return super().form_valid(form)

class SchoolReportView(LoginRequiredMixin, FormView):
    template_name = 'reporting/school_report.html'
    form_class = SchoolReportForm
    success_url = reverse_lazy('reporting:dashboard')
    
    def form_valid(self, form):
        messages.info(self.request, 'School report functionality coming soon!')
        return super().form_valid(form)

class ReportHistoryView(LoginRequiredMixin, ListView):
    model = GeneratedReport
    template_name = 'reporting/report_history.html'
    context_object_name = 'reports'
    
    def get_queryset(self):
        return GeneratedReport.objects.filter(generated_by=self.request.user)