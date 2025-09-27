from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.AnalyticsDashboardView.as_view(), name='dashboard'),
    path('grades/', views.GradeAnalyticsView.as_view(), name='grade_analytics'),
    path('students/', views.StudentAnalyticsView.as_view(), name='student_analytics'),
]