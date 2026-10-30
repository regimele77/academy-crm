from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('authentication/', include('authentication.urls')),
    path('', include('web.urls')),
]

handler404 = 'web.views.page_not_found'
