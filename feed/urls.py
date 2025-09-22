from django.urls import path
from . import views

app_name = 'feed'

urlpatterns = [
    path('', views.home, name='home'),
    path('post/<int:post_id>/like/', views.toggle_like, name='toggle_like'), 
    path('post/<int:post_id>/comments/', views.comments_api, name='comments_api'),  # GET list / POST create
    path("follow/<int:user_id>/", views.toggle_follow, name="toggle_follow"),
    path("conexao/", views.community, name="conexao"),
    path("settings/", views.settings_view, name="settings"),
    path("artigos/", views.artigos, name="artigos"),
]