from django.urls import path
from innovator.views import index, register


urlpatterns = [
    path('', index),
    path('register/', register, name='register'),
    
]