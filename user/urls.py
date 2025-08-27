# user/urls.py
from django.urls import path
from . import views  # same folder import

app_name = "user"  # <-- this registers the 'user:' namespace

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),

    # email verification + innovator step
    path('verify/<str:uidb64>/<str:token>/', views.verify_email, name='verify_email'),
    path('innovator/identity/<str:uidb64>/<str:token>/', views.innovator_identity, name='innovator_identity'),
    path('innovator/identity/done/', views.innovator_identity_done, name='innovator_identity_done'),
    # NEW: one-time auto login link
    path('login/auto/<str:uidb64>/<str:token>/', views.auto_login, name='auto_login'),
]
