from django.core.management.base import BaseCommand
from grading.models import Student, Subject, Grade, Class, AcademicYear
from authentication.models import User
import random
from datetime import date

class Command(BaseCommand):
    help = 'Populate sample data'
    
    def handle(self, *args, **options):
        # Create academic year
        ay, created = AcademicYear.objects.get_or_create(
            name="2024-2025",
            defaults={'start_date': date(2024, 1, 15), 'end_date': date(2024, 12, 15), 'is_current': True}
        )
        
        # Create classes
        classes = []
        for name in ['Grade 7A', 'Grade 7B', 'Grade 8A']:
            cls, created = Class.objects.get_or_create(name=name, academic_year=ay)
            classes.append(cls)
        
        # Create subjects
        subjects = []
        for name, code in [('Mathematics', 'MATH'), ('English', 'ENG'), ('Science', 'SCI')]:
            sub, created = Subject.objects.get_or_create(name=name, code=code)
            subjects.append(sub)
        
        # Create students
        for i in range(20):
            Student.objects.create(
                first_name=f"Student{i+1}",
                last_name="Demo",
                student_id=f"MGS{2024000 + i}",
                date_of_birth=date(2010, 1, 1),
                current_class=random.choice(classes),
                academic_year=ay,
                enrollment_date=date(2024, 1, 15),
                is_active=True
            )
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))