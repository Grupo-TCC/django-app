# user/urls.py
from django.urls import path
from . import views  # same folder import

app_name = "user"  # <-- this registers the 'user:' namespace

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),

    # email verification + innovator step
    path('verify/<str:uidb64>/<str:token>/', views.verify_email, name='verify_email'),
    # NEW: one-time auto login link
    path('login/auto/<str:uidb64>/<str:token>/', views.auto_login, name='auto_login'),
    path("change-profile-picture/", views.change_profile_picture, name="change_profile_picture"),
]
