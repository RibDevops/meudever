from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from ..forms import AlterarSenhaForm, RegistroUsuarioForm
from login.models import User as CustomUser

@login_required
def alterar_senha(request):
    if request.method == 'POST':
        form = AlterarSenhaForm(request.user, request.POST)
        if form.is_valid():
            user = request.user
            user.set_password(form.cleaned_data['nova_senha'])
            user.save()
            update_session_auth_hash(request, user)  # Mantém o usuário logado
            messages.success(request, 'Senha alterada com sucesso!')
            return redirect('login:perfil')
    else:
        form = AlterarSenhaForm(request.user)
    
    return render(request, 'accounts/alterar_senha.html', {'form': form})

@login_required
def perfil(request):
    return render(request, 'accounts/perfil.html', {'usuario': request.user})

@login_required
def editar_perfil(request):
    usuario = request.user
    
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST, instance=usuario, user=request.user, editing_own_profile=True)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('login:perfil')
    else:
        form = RegistroUsuarioForm(instance=usuario, user=request.user, editing_own_profile=True)
    
    return render(request, 'accounts/editar_perfil.html', {'form': form, 'usuario': usuario})