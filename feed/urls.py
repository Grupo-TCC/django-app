from django.urls import path
from . import views

app_name = 'feed'

urlpatterns = [
    path('', views.home, name='home'),
    path('post/<int:post_id>/like/', views.toggle_like, name='toggle_like'), 
]