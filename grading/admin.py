from django.contrib import admin
from .models import AcademicYear, Class, Subject, Student, Grade

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_current')
    list_filter = ('is_current',)

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'academic_year', 'teacher')
    list_filter = ('academic_year',)

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'student_id', 'current_class', 'is_active')
    list_filter = ('current_class', 'is_active', 'academic_year')
    search_fields = ('first_name', 'last_name', 'student_id')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'assessment_name', 'score', 'percentage', 'term', 'date')
    list_filter = ('subject', 'term', 'assessment_type', 'date')
    search_fields = ('student__first_name', 'student__last_name', 'assessment_name')
    readonly_fields = ('percentage', 'created_at', 'updated_at')