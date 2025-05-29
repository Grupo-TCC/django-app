from django.urls import path
from pescasa_feed.views import feed


urlpatterns = [
    path('feed/', feed, name='feed'),
]