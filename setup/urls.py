from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from innovator import views as innovator_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('verify/<str:uidb64>/<str:token>/', innovator_views.verify_email, name='verify_email'),
    path('', include('innovator.urls') ),
    path('feed/', include("feed.urls", namespace='feed')),
    path('logout/', auth_views.LogoutView.as_view(next_page='register'), name='logout')
] 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


