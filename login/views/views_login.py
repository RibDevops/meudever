from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from ..forms import RegistroUsuarioForm
# from ..forms import RegistroUsuarioForm, LoginForm
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from rolepermissions.roles import assign_role

from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from ..forms import RegistroUsuarioForm
from ..models import User as Usuarios


#@login_required(login_url='/login/')
def lista_usuarios(request):
    usuarios = Usuarios.objects.all()
    return render(request, 'accounts/lista_usuarios.html', {'usuarios': usuarios})

#@login_required(login_url='/login/')
def registro_view(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login:lista_usuarios')
    else:
        form = RegistroUsuarioForm()
    return render(request, 'accounts/registro.html', {'form': form})

#@login_required(login_url='/login/')
def update_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('login:lista_usuarios')
    else:
        form = RegistroUsuarioForm(instance=user)
    return render(request, 'accounts/update_user.html', {'form': form})

#@login_required(login_url='/login/')
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect('login:lista_usuarios')
    return render(request, 'accounts/delete_user.html', {'user': user})



# #@login_required(login_url='/login/')
# def registro_view(request):
#     if request.method == 'POST':
#         form = RegistroUsuarioForm(request.POST)
#         print("Dados do POST:", request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('login:registro')
#     else:
#         form = RegistroUsuarioForm()
#     return render(request, 'accounts/registro.html', {'form': form})

# def login_view(request):
#     if request.method == 'POST':
#         form = LoginForm(data=request.POST)
#         if form.is_valid():
#             user = form.get_user()
#             login(request, user)
#             return redirect('/')
#     else:
#         form = LoginForm()
#     return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('/')

from django.shortcuts import render

def home(request):
    return render(request, 'home.html')  # Altere para o template correto



def login_view(request):
    # Instancia o formulário de autenticação
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # Crie a sessão com o ID da escola do usuário, caso o usuário tenha o campo 'escola'
                if hasattr(user, 'escola'):
                    request.session['escola_id'] = user.escola.id
                # return redirect('login:home')
                return redirect('cal:dever_list')

            else:
                messages.error(request, 'Credenciais inválidas.')
    
    # Renderiza a página de login para GET ou se a autenticação falhar
    return render(request, 'login.html', {'form_login': form})

