# analytics/urls.py
from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.AnalyticsDashboardView.as_view(), name='dashboard'),
    path('subject/<int:subject_id>/', views.SubjectAnalyticsView.as_view(), name='subject_analytics'),
]