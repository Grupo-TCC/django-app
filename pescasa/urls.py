from django.urls import path
from pescasa.views import index, register


urlpatterns = [
    path('', index),
    path('register/', register, name='register'),
    
]