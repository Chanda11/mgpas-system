from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

# Import your custom views
from authentication.views import DashboardView, ProfileView  # Add ProfileView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/auth/login/', permanent=False)),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('profile/', ProfileView.as_view(), name='profile'),  # Add this line
    path('auth/', include('authentication.urls')),
    path('grading/', include('grading.urls')),
    path('analytics/', include('analytics.urls')),
    path('reporting/', include('reporting.urls')),
    
    # PWA URLs
    path('', include('pwa.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)