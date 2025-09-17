from django.contrib import admin
from django.urls import path, include
from .views import *
from django.urls import path
from . import views  # Importe suas views
from django.urls import path
from django.contrib.auth import views as auth_views
app_name = 'login' 
urlpatterns = [
    # path('logar_usuario', logar_usuario, name="logar_usuario"),
    # path('cadastrar_usuario', cadastrar_usuario, name="cadastrar_usuario"),
    # path('index', index, name="index"),
    # path('logout/', views.logout_view, name='logout'),
 
    path('', views.home, name='home'),  # URL para a home
    path('registro/', views.registro_view, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('update_user/<int:user_id>/', views.update_user, name='update_user'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),

    path('reset_password/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset.html'), name='reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_sent.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_form.html'), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_complete'),

]
