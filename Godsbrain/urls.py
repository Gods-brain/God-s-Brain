"""
URL configuration for Godsbrain project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from users.views import (RegisterView,
                         ProfileView,
                         LoadMorePost,
                         CustomPasswordResetView,
                         CustomPasswordResetConfirmView)
from django.contrib.auth import views as auth_view
from django.conf.urls.static import static
from django.conf import settings
from django.urls import reverse_lazy


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("posts.urls")),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', auth_view.LoginView.as_view(template_name="users/login.html"), name="login"),
    path('logout/', auth_view.LogoutView.as_view(template_name="users/logout.html"), name="logout"),
    path('profile/<str:username>', ProfileView.as_view(), name='profile'),
    path('load_post/', LoadMorePost.as_view(), name='load_post'),
    path('password-change/', auth_view.PasswordChangeView.as_view(template_name="users/password_change_form.html", success_url=reverse_lazy('passdone')), name='passchange'),
    path('password-done/', auth_view.PasswordChangeDoneView.as_view(template_name="users/password_change_done.html"), name='passdone'),
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_view.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_view.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), name='password_reset_complete'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
