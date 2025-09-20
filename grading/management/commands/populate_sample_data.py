from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from grading.models import AcademicYear, Class, Subject, Student, Grade
from datetime import date, timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Populates the database with sample data'
    
    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create academic year
        academic_year, created = AcademicYear.objects.get_or_create(
            name="2024-2025",
            defaults={
                'start_date': date(2024, 9, 1),
                'end_date': date(2025, 6, 30),
                'is_current': True
            }
        )
        
        # Create classes
        classes = []
        for class_name in ['Grade 7A', 'Grade 7B', 'Grade 8A', 'Grade 8B', 'Grade 9A', 'Grade 9B']:
            class_obj, created = Class.objects.get_or_create(
                name=class_name,
                academic_year=academic_year,
                defaults={'teacher': None}
            )
            classes.append(class_obj)
        
        # Create subjects
        subjects = []
        subject_data = [
            ('MATH', 'Mathematics'),
            ('ENG', 'English'),
            ('SCI', 'Science'),
            ('HIST', 'History'),
            ('GEO', 'Geography'),
            ('ART', 'Art'),
            ('PE', 'Physical Education'),
            ('MUS', 'Music')
        ]
        
        for code, name in subject_data:
            subject, created = Subject.objects.get_or_create(
                code=code,
                defaults={'name': name}
            )
            subjects.append(subject)
        
        # Create students
        first_names = ['John', 'Jane', 'Michael', 'Emily', 'David', 'Sarah', 'James', 'Emma', 'Robert', 'Olivia']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
        
        students = []
        for i in range(50):
            class_obj = random.choice(classes)
            student = Student.objects.create(
                first_name=random.choice(first_names),
                last_name=random.choice(last_names),
                student_id=f"STU{1000 + i}",
                date_of_birth=date(2010 - random.randint(0, 2), random.randint(1, 12), random.randint(1, 28)),
                email=f"student{1000 + i}@musenga.edu",
                phone=f"260-97{random.randint(1000000, 9999999)}",
                address=f"{random.randint(1, 100)} Main Street, Lusaka",
                current_class=class_obj,
                academic_year=academic_year,
                enrollment_date=date(2024, 9, 1),
                graduation_year=2027,
                emergency_contact_name=f"Parent {random.choice(first_names)} {random.choice(last_names)}",
                emergency_contact_phone=f"260-96{random.randint(1000000, 9999999)}",
                is_active=True
            )
            students.append(student)
        
        # Create some grades
        assessment_types = ['EXAM', 'TEST', 'QUIZ', 'ASSIGNMENT', 'PROJECT']
        terms = ['TERM1', 'TERM2', 'TERM3']
        
        for student in students:
            for subject in random.sample(subjects, 5):  # Each student takes 5 subjects
                for term in terms:
                    for assessment_type in assessment_types:
                        Grade.objects.create(
                            student=student,
                            subject=subject,
                            assessment_name=f"{subject.name} {assessment_type.capitalize()}",
                            assessment_type=assessment_type,
                            score=random.randint(60, 95),
                            max_score=100,
                            term=term,
                            date=date(2024, random.randint(9, 12) if term == 'TERM1' else 
                                     random.randint(1, 3) if term == 'TERM2' else 
                                     random.randint(4, 6)),
                            comments=f"Good performance in {subject.name}",
                            created_by=None
                        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created sample data: '
                f'{AcademicYear.objects.count()} academic years, '
                f'{Class.objects.count()} classes, '
                f'{Subject.objects.count()} subjects, '
                f'{Student.objects.count()} students, '
                f'{Grade.objects.count()} grades'
            )
        )