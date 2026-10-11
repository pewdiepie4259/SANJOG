from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

def health_check(request):
    """Base system health check endpoint."""
    return JsonResponse({
        'status': 'healthy',
        'system': 'SANJOG Food Rescue OS',
        'version': '1.0.0',
        'database': 'PostgreSQL/PostGIS'
    })

urlpatterns = [
    path('', include('apps.organizations.urls')),
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
    path('', include('apps.accounts.urls')),
    
    # API Version 1 Namespace
    path('api/v1/', include([
        path('health/', health_check, name='api_v1_health'),
        path('', include('apps.accounts.urls')),
    ])),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
