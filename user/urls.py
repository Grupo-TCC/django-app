# user/urls.py
from django.urls import path
from . import views  # same folder import

app_name = "user"  # <-- this registers the 'user:' namespace

urlpatterns = [
    path('', views.index, name='index'),
    path('sobre/', views.sobre, name='sobre'),
    path('politica-privacidade/', views.politica_privacidade, name='politica_privacidade'),
    path('termos-de-uso/', views.termos_de_uso, name='termos_de_uso'),
    path('register/', views.register, name='register'),

    # Email verification for new registrations
    path('verify-email/<str:uidb64>/<str:token>/', views.verify_email, name='verify_email'),
    
    # Auto-login link for approved users
    path('login/auto/<str:uidb64>/<str:token>/', views.auto_login, name='auto_login'),
    path("change-profile-picture/", views.change_profile_picture, name="change_profile_picture"),
]
