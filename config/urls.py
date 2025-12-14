"""
URL configuration for the config project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from store.secure_admin import secure_admin_site

urlpatterns = [
    path('admin/', admin.site.urls),
    path('secure-admin/', secure_admin_site.urls),
    path('', include('store.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers
handler404 = 'store.views.error_404'
handler500 = 'store.views.error_500'
