from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from authentication.views import DashboardView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('auth/', include('authentication.urls')),
    path('grading/', include('grading.urls')),
    path('analytics/', include('analytics.urls')),
    path('reporting/', include('reporting.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)