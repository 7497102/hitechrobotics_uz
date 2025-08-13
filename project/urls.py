from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include

from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),  # <- / (root url)
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('admin/', permanent=True)),
    path('api/', include('hitechroboticsapp.urls')),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
