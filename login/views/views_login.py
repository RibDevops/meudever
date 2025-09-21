# login/views/views_login.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from ..decorators import superuser_required, admin_required, gestao_usuarios_required
from ..forms import RegistroUsuarioForm, RegistroPublicoForm
from login.models import User as CustomUser
import random
import string

# Página inicial
def home(request):
    return render(request, 'home.html')

# Login
# login/views/views_login.py

def login_view(request):
    if request.user.is_authenticated:
        return redirect('cal:home')
    
    form = AuthenticationForm(request, data=request.POST or None)
    next_url = request.GET.get('next', '')  # Obter parâmetro 'next' da URL

    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if user.ativo:
                    login(request, user)
                    if hasattr(user, 'fk_escola') and user.fk_escola:
                        request.session['escola_id'] = user.fk_escola.id
                    
                    # Redirecionar para 'next' se existir, senão para a home
                    next_param = request.POST.get('next', '')
                    if next_param:
                        return redirect(next_param)
                    return redirect('cal:home')
                else:
                    messages.error(request, 'Esta conta está desativada.')
            else:
                messages.error(request, 'Credenciais inválidas.')
    
    return render(request, 'accounts/login.html', {
        'form_login': form,
        'next': next_url  # Passar a variável 'next' para o template
    })

# Logout
def logout_view(request):
    logout(request)
    messages.success(request, 'Você foi desconectado com sucesso.')
    return redirect('login:home')

# Registro público (para novos usuários)
def registro_publico(request):
    if request.user.is_authenticated:
        return redirect('cal:home')
    
    if request.method == 'POST':
        form = RegistroPublicoForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])  # Senha definida pelo usuário
            user.tipo_usuario = 'pai'  # Definir como Pai/Responsável por padrão
            user.save()
            
            messages.success(request, 'Conta criada com sucesso! Faça login para continuar.')
            return redirect('login:login')
    else:
        form = RegistroPublicoForm()
    
    return render(request, 'accounts/registro_publico.html', {'form': form})

# Registro de usuários por administradores (senha padrão)
@gestao_usuarios_required
def registro_usuario(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST, user=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            
            # Define senha padrão
            senha_padrao = '12345678'
            user.set_password(senha_padrao)
            
            # Apenas superusers podem criar outros superusers/admins
            if not request.user.is_superuser_type():
                if form.cleaned_data['tipo_usuario'] in ['superuser', 'admin']:
                    messages.error(request, 'Você não tem permissão para criar este tipo de usuário.')
                    return render(request, 'accounts/registro.html', {'form': form})
            
            user.save()
            messages.success(request, f'Usuário criado com sucesso! Senha inicial: {senha_padrao}')
            return redirect('login:lista_usuarios')
    else:
        form = RegistroUsuarioForm(user=request.user)
    
    return render(request, 'accounts/registro.html', {'form': form})

# Lista de usuários
@gestao_usuarios_required
def lista_usuarios(request):
    usuarios = CustomUser.objects.all()
    
    # Filtra usuários baseado no tipo do usuário logado
    if not request.user.is_admin_type():
        usuarios = usuarios.exclude(tipo_usuario__in=['superuser', 'admin'])
    
    return render(request, 'accounts/lista_usuarios.html', {'usuarios': usuarios})

# Editar usuário
@gestao_usuarios_required
def update_user(request, user_id):
    user_to_edit = get_object_or_404(CustomUser, id=user_id)
    
    # Verifica permissões para editar este usuário específico
    if not request.user.is_superuser_type():
        if user_to_edit.tipo_usuario in ['superuser', 'admin']:
            messages.error(request, 'Você não tem permissão para editar este usuário.')
            return redirect('login:lista_usuarios')
    
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST, instance=user_to_edit, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário atualizado com sucesso!')
            return redirect('login:lista_usuarios')
    else:
        form = RegistroUsuarioForm(instance=user_to_edit, user=request.user)
    
    return render(request, 'accounts/update_user.html', {'form': form, 'user_to_edit': user_to_edit})

# Excluir usuário
@gestao_usuarios_required
def delete_user(request, user_id):
    user_to_delete = get_object_or_404(CustomUser, id=user_id)
    
    # Verifica permissões para deletar este usuário específico
    if not request.user.is_superuser_type():
        if user_to_delete.tipo_usuario in ['superuser', 'admin']:
            messages.error(request, 'Você não tem permissão para deletar este usuário.')
            return redirect('login:lista_usuarios')
    
    if request.method == 'POST':
        user_to_delete.delete()
        messages.success(request, 'Usuário deletado com sucesso!')
        return redirect('login:lista_usuarios')
    
    return render(request, 'accounts/delete_user.html', {'user': user_to_delete})

# login/views/views_login.py - Adicione esta view customizada

from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
import logging

logger = logging.getLogger(__name__)

# login/views/views_login.py - Modifique a view customizada

class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('login:password_reset_done')
    
    def form_valid(self, form):
        email = form.cleaned_data['email']
        print(f"DEBUG: Email recebido: {email}")
        
        # Verificar se o usuário existe
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        if User.objects.filter(email=email).exists():
            print("DEBUG: Usuário encontrado, enviando email...")
        else:
            print("DEBUG: Usuário NÃO encontrado com este email")
        
        response = super().form_valid(form)
        return response