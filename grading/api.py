# grading/api.py
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q, Avg, Count
import json
from .models import Student, Class, Grade, Subject

@require_GET
@login_required
def student_list_api(request):
    students = Student.objects.all().values(
        'id', 'first_name', 'last_name', 'student_id', 'email', 
        'is_active', 'enrollment_date', 'current_class'
    )
    return JsonResponse(list(students), safe=False)

@require_GET
@login_required
def grade_list_api(request):
    grades = Grade.objects.all().select_related('student', 'subject').values(
        'id', 'assessment_name', 'assessment_type', 'score', 'max_score', 
        'percentage', 'term', 'date', 'student__first_name', 'student__last_name',
        'subject__name', 'subject__id'
    )
    
    grades_list = []
    for grade in grades:
        grades_list.append({
            'id': grade['id'],
            'student_name': f"{grade['student__first_name']} {grade['student__last_name']}",
            'subject_name': grade['subject__name'],
            'subject': grade['subject__id'],
            'assessment_name': grade['assessment_name'],
            'assessment_type': grade['assessment_type'],
            'assessment_type_display': dict(Grade.AssessmentType.choices)[grade['assessment_type']],
            'score': grade['score'],
            'max_score': grade['max_score'],
            'percentage': float(grade['percentage']),
            'term': grade['term'],
            'term_display': dict(Grade.Term.choices)[grade['term']],
            'date': grade['date'].isoformat() if grade['date'] else None
        })
    
    return JsonResponse(grades_list, safe=False)

@require_GET
@login_required
def subject_list_api(request):
    subjects = Subject.objects.all().values('id', 'name', 'code')
    return JsonResponse(list(subjects), safe=False)

@require_GET
@login_required
def statistics_api(request):
    # Student statistics
    total_students = Student.objects.count()
    active_students = Student.objects.filter(is_active=True).count()
    total_classes = Class.objects.count()
    
    # Students enrolled in the last 30 days
    last_month = timezone.now() - timedelta(days=30)
    new_students = Student.objects.filter(created_at__gte=last_month).count()
    
    # Grade statistics
    total_grades = Grade.objects.count()
    students_graded = Grade.objects.values('student').distinct().count()
    total_subjects = Subject.objects.count()
    
    # Average grade
    average_grade = Grade.objects.aggregate(avg=Avg('percentage'))['avg']
    
    # Grade distribution
    grade_distribution = {
        'A': Grade.objects.filter(percentage__gte=90).count(),
        'B': Grade.objects.filter(percentage__gte=80, percentage__lt=90).count(),
        'C': Grade.objects.filter(percentage__gte=70, percentage__lt=80).count(),
        'D': Grade.objects.filter(percentage__gte=60, percentage__lt=70).count(),
        'F': Grade.objects.filter(percentage__lt=60).count()
    }
    
    # Recent activity
    recent_grades = Grade.objects.order_by('-created_at')[:5].values(
        'student__first_name', 'student__last_name', 'subject__name',
        'assessment_name', 'percentage', 'created_at'
    )
    
    return JsonResponse({
        # Student stats
        'total_students': total_students,
        'active_students': active_students,
        'total_classes': total_classes,
        'new_students': new_students,
        
        # Grade stats
        'total_grades': total_grades,
        'students_graded': students_graded,
        'total_subjects': total_subjects,
        'average_grade': average_grade,
        'grade_distribution': grade_distribution,
        'recent_grades': list(recent_grades)
    })

@require_GET
@login_required
def student_detail_api(request, student_id):
    try:
        student = Student.objects.get(id=student_id)
        student_data = {
            'id': student.id,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'student_id': student.student_id,
            'email': student.email,
            'phone': student.phone,
            'date_of_birth': student.date_of_birth.isoformat() if student.date_of_birth else None,
            'address': student.address,
            'current_class': student.current_class.id if student.current_class else None,
            'current_class_name': student.current_class.name if student.current_class else None,
            'academic_year': student.academic_year.name if student.academic_year else None,
            'enrollment_date': student.enrollment_date.isoformat() if student.enrollment_date else None,
            'is_active': student.is_active,
            'emergency_contact_name': student.emergency_contact_name,
            'emergency_contact_phone': student.emergency_contact_phone
        }
        
        # Get student grades
        grades = Grade.objects.filter(student=student).select_related('subject').values(
            'subject__name', 'assessment_name', 'assessment_type', 'score', 
            'max_score', 'percentage', 'term', 'date'
        )
        
        # Calculate subject averages
        subject_stats = {}
        for grade in grades:
            subject_name = grade['subject__name']
            if subject_name not in subject_stats:
                subject_stats[subject_name] = {
                    'total_score': 0,
                    'count': 0,
                    'grades': []
                }
            subject_stats[subject_name]['total_score'] += float(grade['percentage'])
            subject_stats[subject_name]['count'] += 1
            subject_stats[subject_name]['grades'].append(grade)
        
        # Calculate averages
        for subject, stats in subject_stats.items():
            stats['average_score'] = stats['total_score'] / stats['count'] if stats['count'] > 0 else 0
        
        # Calculate overall average
        overall_avg = sum(stats['average_score'] for stats in subject_stats.values()) / len(subject_stats) if subject_stats else 0
        
        return JsonResponse({
            'student': student_data,
            'grades': list(grades),
            'subject_stats': subject_stats,
            'overall_average': overall_avg
        })
        
    except Student.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)

@require_GET
@login_required
def class_list_api(request):
    classes = Class.objects.all().values('id', 'name', 'academic_year__name')
    return JsonResponse(list(classes), safe=False)

@require_GET
@login_required
def grade_statistics_api(request):
    # Get filter parameters
    term = request.GET.get('term')
    subject_id = request.GET.get('subject_id')
    assessment_type = request.GET.get('assessment_type')
    
    # Build filter
    filters = Q()
    if term:
        filters &= Q(term=term)
    if subject_id:
        filters &= Q(subject_id=subject_id)
    if assessment_type:
        filters &= Q(assessment_type=assessment_type)
    
    # Get filtered grades
    grades = Grade.objects.filter(filters)
    
    # Calculate statistics
    total_grades = grades.count()
    average_grade = grades.aggregate(avg=Avg('percentage'))['avg']
    max_grade = grades.aggregate(max=Avg('percentage'))['max']
    min_grade = grades.aggregate(min=Avg('percentage'))['min']
    
    # Grade distribution
    grade_distribution = {
        'A': grades.filter(percentage__gte=90).count(),
        'B': grades.filter(percentage__gte=80, percentage__lt=90).count(),
        'C': grades.filter(percentage__gte=70, percentage__lt=80).count(),
        'D': grades.filter(percentage__gte=60, percentage__lt=70).count(),
        'F': grades.filter(percentage__lt=60).count()
    }
    
    # Subject-wise averages
    subject_averages = grades.values('subject__name').annotate(
        average=Avg('percentage'),
        count=Count('id')
    ).order_by('subject__name')
    
    # Term-wise averages
    term_averages = grades.values('term').annotate(
        average=Avg('percentage'),
        count=Count('id')
    ).order_by('term')
    
    return JsonResponse({
        'total_grades': total_grades,
        'average_grade': average_grade,
        'max_grade': max_grade,
        'min_grade': min_grade,
        'grade_distribution': grade_distribution,
        'subject_averages': list(subject_averages),
        'term_averages': list(term_averages)
    })

@csrf_exempt
@require_POST
@login_required
def bulk_grade_upload_api(request):
    try:
        data = json.loads(request.body)
        grades_data = data.get('grades', [])
        results = []
        
        for grade_data in grades_data:
            try:
                # Check if grade already exists
                grade, created = Grade.objects.get_or_create(
                    student_id=grade_data['student_id'],
                    subject_id=grade_data['subject_id'],
                    assessment_name=grade_data['assessment_name'],
                    term=grade_data['term'],
                    defaults={
                        'assessment_type': grade_data.get('assessment_type', 'TEST'),
                        'score': grade_data['score'],
                        'max_score': grade_data.get('max_score', 100),
                        'date': grade_data.get('date', timezone.now().date()),
                        'comments': grade_data.get('comments', ''),
                        'created_by': request.user
                    }
                )
                
                if not created:
                    # Update existing grade
                    grade.assessment_type = grade_data.get('assessment_type', grade.assessment_type)
                    grade.score = grade_data['score']
                    grade.max_score = grade_data.get('max_score', grade.max_score)
                    grade.date = grade_data.get('date', grade.date)
                    grade.comments = grade_data.get('comments', grade.comments)
                    grade.save()
                
                results.append({
                    'success': True,
                    'grade_id': grade.id,
                    'created': created,
                    'message': 'Grade processed successfully'
                })
                
            except Exception as e:
                results.append({
                    'success': False,
                    'error': str(e),
                    'data': grade_data
                })
        
        return JsonResponse({'results': results})
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_GET
@login_required
def search_api(request):
    query = request.GET.get('q', '')
    search_type = request.GET.get('type', 'all')
    
    results = {}
    
    if search_type in ['all', 'students']:
        students = Student.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(student_id__icontains=query) |
            Q(email__icontains=query)
        )[:10].values('id', 'first_name', 'last_name', 'student_id')
        results['students'] = list(students)
    
    if search_type in ['all', 'grades']:
        grades = Grade.objects.filter(
            Q(student__first_name__icontains=query) |
            Q(student__last_name__icontains=query) |
            Q(subject__name__icontains=query) |
            Q(assessment_name__icontains=query)
        )[:10].values(
            'id', 'student__first_name', 'student__last_name',
            'subject__name', 'assessment_name', 'percentage'
        )
        results['grades'] = list(grades)
    
    if search_type in ['all', 'subjects']:
        subjects = Subject.objects.filter(
            Q(name__icontains=query) |
            Q(code__icontains=query)
        )[:10].values('id', 'name', 'code')
        results['subjects'] = list(subjects)
    
    return JsonResponse(results)

@require_GET
@login_required
def dashboard_stats_api(request):
    # Real-time dashboard statistics
    total_students = Student.objects.count()
    active_students = Student.objects.filter(is_active=True).count()
    total_grades = Grade.objects.count()
    total_subjects = Subject.objects.count()
    
    # Today's activity
    today = timezone.now().date()
    today_grades = Grade.objects.filter(created_at__date=today).count()
    today_students = Student.objects.filter(created_at__date=today).count()
    
    # Recent grades
    recent_grades = Grade.objects.select_related('student', 'subject').order_by('-created_at')[:5].values(
        'student__first_name', 'student__last_name', 'subject__name',
        'assessment_name', 'percentage', 'created_at'
    )
    
    # Grade distribution
    grade_distribution = {
        'A': Grade.objects.filter(percentage__gte=90).count(),
        'B': Grade.objects.filter(percentage__gte=80, percentage__lt=90).count(),
        'C': Grade.objects.filter(percentage__gte=70, percentage__lt=80).count(),
        'D': Grade.objects.filter(percentage__gte=60, percentage__lt=70).count(),
        'F': Grade.objects.filter(percentage__lt=60).count()
    }
    
    return JsonResponse({
        'total_students': total_students,
        'active_students': active_students,
        'total_grades': total_grades,
        'total_subjects': total_subjects,
        'today_grades': today_grades,
        'today_students': today_students,
        'recent_grades': list(recent_grades),
        'grade_distribution': grade_distribution
    })