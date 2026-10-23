from django.urls import path
from .views import about, contact, home, missing, privacy, terms

urlpatterns = [
    path('', home, name='home'),
    path('home/', home),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('terms/', terms, name='terms'),
    path('privacy/', privacy, name='privacy'),
    path('<path:resource>', missing),
]
