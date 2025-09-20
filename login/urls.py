from django.contrib import admin
from django.urls import path, include
from .views import *
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'login' 

urlpatterns = [
    path('', views.home, name='home'),
    path('registro/', views.registro_view, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('update_user/<int:user_id>/', views.update_user, name='update_user'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),

    # URLs de reset de senha
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset.html'), name='reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_sent.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_form.html'), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_complete'),

    # ADICIONE ESTAS DUAS LINHAS PARA RESOLVER O ERRO:
    path('accounts/login/', views.login_view, name='accounts_login'),
    path('accounts/logout/', views.logout_view, name='accounts_logout'),
]