from django.urls import path
from . import views

app_name = 'reporting'

urlpatterns = [
    path('', views.ReportingDashboardView.as_view(), name='dashboard'),
    path('student/<int:student_id>/', views.StudentReportView.as_view(), name='student_report'),
    path('class/<int:class_id>/', views.ClassReportView.as_view(), name='class_report'),
    path('export/csv/', views.CSVExportView.as_view(), name='csv_export'),
]