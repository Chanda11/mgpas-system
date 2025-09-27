from django.db.models import Avg, Count, Q, F
from django.utils import timezone
from grading.models import Grade, Student, Subject
from .models import GradeDistribution, StudentPerformance

class AnalyticsCalculator:
    @staticmethod
    def calculate_grade_distribution(subject, academic_year, term):
        """Calculate grade distribution for a subject in given term/year"""
        grades = Grade.objects.filter(
            subject=subject,
            term=term,
            date__year=academic_year.split('-')[0]  # Simple year extraction
        )
        
        total_grades = grades.count()
        if total_grades == 0:
            return None
        
        # Count grades by letter
        a_count = grades.filter(percentage__gte=90).count()
        b_count = grades.filter(percentage__gte=80, percentage__lt=90).count()
        c_count = grades.filter(percentage__gte=70, percentage__lt=80).count()
        d_count = grades.filter(percentage__gte=60, percentage__lt=70).count()
        f_count = grades.filter(percentage__lt=60).count()
        
        avg_score = grades.aggregate(avg=Avg('percentage'))['avg'] or 0
        pass_rate = ((a_count + b_count + c_count + d_count) / total_grades) * 100
        
        distribution, created = GradeDistribution.objects.get_or_create(
            subject=subject,
            academic_year=academic_year,
            term=term
        )
        
        distribution.a_count = a_count
        distribution.b_count = b_count
        distribution.c_count = c_count
        distribution.d_count = d_count
        distribution.f_count = f_count
        distribution.total_students = total_grades
        distribution.average_score = avg_score
        distribution.pass_rate = pass_rate
        distribution.save()
        
        return distribution

    @staticmethod
    def calculate_student_performance(student, academic_year, term):
        """Calculate individual student performance"""
        grades = Grade.objects.filter(
            student=student,
            term=term,
            date__year=academic_year.split('-')[0]
        )
        
        if not grades.exists():
            return None
        
        avg_grade = grades.aggregate(avg=Avg('percentage'))['avg'] or 0
        total_subjects = grades.values('subject').distinct().count()
        
        # Simple trend analysis (compare with previous term if available)
        performance_trend = 'STABLE'
        
        performance, created = StudentPerformance.objects.get_or_create(
            student=student,
            academic_year=academic_year,
            term=term
        )
        
        performance.total_subjects = total_subjects
        performance.average_grade = avg_grade
        performance.performance_trend = performance_trend
        performance.save()
        
        return performance

    @staticmethod
    def get_class_performance(class_obj, academic_year, term):
        """Get performance analytics for entire class"""
        students = Student.objects.filter(current_class=class_obj)
        performance_data = []
        
        for student in students:
            performance = AnalyticsCalculator.calculate_student_performance(
                student, academic_year, term
            )
            if performance:
                performance_data.append(performance)
        
        return sorted(performance_data, key=lambda x: x.average_grade, reverse=True)

    @staticmethod
    def get_subject_comparison(academic_year, term):
        """Compare performance across all subjects"""
        subjects = Subject.objects.all()
        comparison_data = []
        
        for subject in subjects:
            distribution = AnalyticsCalculator.calculate_grade_distribution(
                subject, academic_year, term
            )
            if distribution:
                comparison_data.append({
                    'subject': subject.name,
                    'average_score': distribution.average_score,
                    'pass_rate': distribution.pass_rate,
                    'total_students': distribution.total_students,
                    'grade_distribution': {
                        'A': distribution.a_count,
                        'B': distribution.b_count,
                        'C': distribution.c_count,
                        'D': distribution.d_count,
                        'F': distribution.f_count
                    }
                })
        
        return sorted(comparison_data, key=lambda x: x['average_score'], reverse=True)

class ChartDataGenerator:
    @staticmethod
    def grade_distribution_pie_chart(subject, academic_year, term):
        distribution = GradeDistribution.objects.filter(
            subject=subject,
            academic_year=academic_year,
            term=term
        ).first()
        
        if not distribution:
            return None
        
        return {
            'labels': ['A (90-100%)', 'B (80-89%)', 'C (70-79%)', 'D (60-69%)', 'F (<60%)'],
            'data': [
                distribution.a_count,
                distribution.b_count,
                distribution.c_count,
                distribution.d_count,
                distribution.f_count
            ],
            'backgroundColor': ['#28a745', '#20c997', '#ffc107', '#fd7e14', '#dc3545']
        }

    @staticmethod
    def subject_comparison_bar_chart(academic_year, term):
        subjects_data = AnalyticsCalculator.get_subject_comparison(academic_year, term)
        
        return {
            'labels': [item['subject'] for item in subjects_data],
            'datasets': [{
                'label': 'Average Score',
                'data': [float(item['average_score']) for item in subjects_data],
                'backgroundColor': '#007bff'
            }]
        }

    @staticmethod
    def performance_trend_line_chart(student, academic_year):
        terms = ['TERM1', 'TERM2', 'TERM3']
        term_data = []
        
        for term in terms:
            performance = StudentPerformance.objects.filter(
                student=student,
                academic_year=academic_year,
                term=term
            ).first()
            
            if performance:
                term_data.append(float(performance.average_grade))
            else:
                term_data.append(0)
        
        return {
            'labels': ['Term 1', 'Term 2', 'Term 3'],
            'datasets': [{
                'label': f'{academic_year} Performance',
                'data': term_data,
                'borderColor': '#6f42c1',
                'tension': 0.1
            }]
        }