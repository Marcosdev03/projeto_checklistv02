# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings  # Importe 'settings'
from django.http import FileResponse, Http404
import os
from django.views.static import serve as static_serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]


# Serve Vite assets directly from STATIC_ROOT/frontend/assets at /assets/*
def serve_frontend_asset(request, path):
    try:
        static_root = settings.STATIC_ROOT
        if not static_root:
            raise Http404('Static root not configured')
        # verificar vários locais onde o build pode ter sido colocado
        candidates = [
            os.path.join(str(static_root), 'frontend', 'assets', path),
            os.path.join(str(static_root), 'assets', path),
            os.path.join(str(static_root), path),
            os.path.join(settings.BASE_DIR, 'staticfiles', 'frontend', 'assets', path),
            os.path.join(settings.BASE_DIR, 'staticfiles', 'assets', path),
        ]
        for candidate in candidates:
            if os.path.exists(candidate):
                return FileResponse(open(candidate, 'rb'))
    except Exception:
        raise Http404('Asset not found')
    raise Http404('Asset not found')

urlpatterns += [
    path('assets/<path:path>', serve_frontend_asset),
]


# Serve the frontend SPA index.html at root (uses collectstatic output)
def serve_spa_index(request):
    # caminho esperado: STATIC_ROOT/frontend/index.html
    index_path = None
    try:
        static_root = settings.STATIC_ROOT
        if static_root:
            candidate = os.path.join(str(static_root), 'frontend', 'index.html')
            if os.path.exists(candidate):
                index_path = candidate
    except Exception:
        index_path = None

    # fallback: try project staticfiles directory
    if not index_path:
        base_candidate = os.path.join(settings.BASE_DIR, 'staticfiles', 'frontend', 'index.html')
        if os.path.exists(base_candidate):
            index_path = base_candidate

    if index_path:
        return FileResponse(open(index_path, 'rb'), content_type='text/html')
    raise Http404('SPA index.html not found')

urlpatterns += [
    path('', serve_spa_index),
]

# Adicionamos a documentação apenas se estivermos em modo DEBUG
if settings.DEBUG:
    from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
    urlpatterns += [
        path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
        path('api/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    ]