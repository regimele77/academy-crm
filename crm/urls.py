from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('authentication/', include('authentication.urls')),
    path('student/', include('student.urls')),
    path('instructor/', include('instructor.urls')),
]

# Media must be registered before the web catch-all route.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    path('', include('web.urls')),
]

handler404 = 'web.views.page_not_found'
