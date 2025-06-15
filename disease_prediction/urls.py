from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from dashboard.views import admin_dashboard  # Import the admin_dashboard view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('prediction/', include('prediction.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('admin-dash/', admin_dashboard, name='admin_dash'),  # Add direct URL to admin dashboard
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
