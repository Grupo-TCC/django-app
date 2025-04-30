from django.urls import path
from pescasa.views import index


urlpatterns = [
    path('', index)
]