from django.urls import path
from . import views

app_name = 'reporting'

urlpatterns = [
    path('', views.ReportsDashboardView.as_view(), name='dashboard'),
    path('student/', views.StudentReportView.as_view(), name='student_report'),
    path('class/', views.ClassReportView.as_view(), name='class_report'),
    path('school/', views.SchoolReportView.as_view(), name='school_report'),
    path('history/', views.ReportHistoryView.as_view(), name='report_history'),
]