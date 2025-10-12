from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from. import views
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('otp/', include('notifications.urls')),
    path('tickets/', include('tickets.urls')),
    path('', views.main_page, name='main_page')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
