# login/urls.py

from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.contrib.auth import views as auth_views

from login.views.password_reset_views import CustomPasswordResetView
from . import views

app_name = 'login' 

urlpatterns = [
    # Páginas principais
    path('', views.home, name='home'),
    
    # Autenticação
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro_publico, name='registro_publico'),
    
    # Gestão de usuários (apenas para administradores)
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/registro/', views.registro_usuario, name='registro_usuario'),
    path('usuarios/editar/<int:user_id>/', views.update_user, name='update_user'),
    path('usuarios/excluir/<int:user_id>/', views.delete_user, name='delete_user'),
    

    path('password_reset/', 
         views.CustomPasswordResetView.as_view(), 
         name='password_reset'),
    
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ), 
         name='password_reset_done'),
    
    # URL IMPORTANTE: Configurar com template personalizado
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html',
             success_url='/reset/done/'
         ), 
         name='password_reset_confirm'),
    
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
]