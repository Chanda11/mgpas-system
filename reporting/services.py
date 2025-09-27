import os
from datetime import datetime
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models import Avg
from grading.models import Student, Grade, Subject, Class

class ReportGenerator:
    @staticmethod
    def generate_student_report_card(student, academic_year, term, format='PDF'):
        grades = Grade.objects.filter(student=student, term=term).select_related('subject')
        
        avg_grade = grades.aggregate(avg=Avg('percentage'))['avg'] or 0
        total_subjects = grades.values('subject').distinct().count()
        
        context = {
            'student': student,
            'academic_year': academic_year,
            'term': term,
            'grades': grades,
            'average_grade': avg_grade,
            'total_subjects': total_subjects,
            'generated_date': datetime.now().strftime('%Y-%m-%d'),
        }
        
        if format == 'PDF':
            return ReportGenerator._generate_pdf_report('reporting/student_report_card.html', context, f"report_{student.student_id}")
        elif format == 'EXCEL':
            return ReportGenerator._generate_excel_report(context, f"report_{student.student_id}")
        else:
            return ReportGenerator._generate_html_report('reporting/student_report_card.html', context)
    
    @staticmethod
    def _generate_pdf_report(template_name, context, filename):
        try:
            html_string = render_to_string(template_name, context)
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
            
            # Simple PDF generation (you'll need xhtml2pdf installed)
            # For now, return HTML response
            return HttpResponse(html_string, content_type='text/html')
        except Exception as e:
            return HttpResponse(f'Error: {str(e)}')
    
    @staticmethod
    def _generate_excel_report(context, filename):
        try:
            # Simple Excel generation would go here
            # For now, return a message
            response = HttpResponse(f"Excel report for {filename} would be generated here")
            response['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"'
            return response
        except Exception as e:
            return HttpResponse(f'Error: {str(e)}')
    
    @staticmethod
    def _generate_html_report(template_name, context):
        try:
            html_content = render_to_string(template_name, context)
            return HttpResponse(html_content)
        except Exception as e:
            return HttpResponse(f'Error: {str(e)}')