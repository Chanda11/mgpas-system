# grading/urls.py
from django.urls import path
from . import views
from .api import (
    student_list_api, grade_list_api, subject_list_api, statistics_api,
    student_detail_api, class_list_api, grade_statistics_api,
    bulk_grade_upload_api, search_api, dashboard_stats_api
)

app_name = 'grading'

urlpatterns = [
    # Student URLs
    path('students/', views.StudentListView.as_view(), name='student_list'),
    path('students/add/', views.StudentCreateView.as_view(), name='student_add'),
    path('students/<int:pk>/', views.StudentDetailView.as_view(), name='student_detail'),
    path('students/<int:pk>/edit/', views.StudentUpdateView.as_view(), name='student_edit'),
    path('students/<int:pk>/delete/', views.StudentDeleteView.as_view(), name='student_delete'),
    
    # Grade URLs
    path('grades/', views.GradeListView.as_view(), name='grade_list'),
    path('grades/add/', views.GradeCreateView.as_view(), name='grade_add'),
    path('grades/<int:pk>/edit/', views.GradeUpdateView.as_view(), name='grade_edit'),
    path('grades/<int:pk>/delete/', views.GradeDeleteView.as_view(), name='grade_delete'),
    
    # API endpoints
    path('api/students/', student_list_api, name='student_api_list'),
    path('api/students/<int:student_id>/', student_detail_api, name='student_api_detail'),
    path('api/grades/', grade_list_api, name='grade_api_list'),
    path('api/subjects/', subject_list_api, name='subject_api_list'),
    path('api/classes/', class_list_api, name='class_api_list'),
    path('api/statistics/', statistics_api, name='statistics_api'),
    path('api/grade-stats/', grade_statistics_api, name='grade_stats_api'),
    path('api/bulk-grades/', bulk_grade_upload_api, name='bulk_grade_upload'),
    path('api/search/', search_api, name='search_api'),
    path('api/dashboard-stats/', dashboard_stats_api, name='dashboard_stats_api'),
]