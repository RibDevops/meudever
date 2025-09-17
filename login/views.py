# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, redirect
# from django.contrib.auth import authenticate, login, logout
# from.forms import RegistroUsuarioForm, LoginForm
# from django.shortcuts import redirect
# from django.contrib.auth import authenticate, login
# from django.contrib import messages
# from django.contrib.auth.forms import AuthenticationForm
# from django.contrib.auth import authenticate, login
# from django.contrib import messages
# from django.shortcuts import redirect, render
# from django.contrib.auth.models import User
# from rolepermissions.roles import assign_role


# #import necessary module
# class GroupViewSet(viewset.ModelViewSet):
#     """
#     Model View Set for Group
#     """

#     serializer_class = GroupSerializer
#     queryset = Group.objects.all()
#     pagination_class = None
#     permission_classes = [IsAuthenticated, IsAdminUser]
#     lookup_field = "pk"
#     http_method_names = ("get", "post", "patch", "delete")

#     def list(self, request, *args, **kwargs):
#         return super().list(request, fields=("id", "name"), *args, **kwargs)

# #@login_required(login_url='/login/')
# def registro_view(request):
#     if request.method == 'POST':
#         form = RegistroUsuarioForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('login:login')
#     else:
#         form = RegistroUsuarioForm()
#     return render(request, 'accounts/registro.html', {'form': form})

# # def login_view(request):
# #     if request.method == 'POST':
# #         form = LoginForm(data=request.POST)
# #         if form.is_valid():
# #             user = form.get_user()
# #             login(request, user)
# #             return redirect('/')
# #     else:
# #         form = LoginForm()
# #     return render(request, 'accounts/login.html', {'form': form})

# def logout_view(request):
#     logout(request)
#     return redirect('/')

# from django.shortcuts import render

# def home(request):
#     return render(request, 'home.html')  # Altere para o template correto



# def login_view(request):
#     # Instancia o formulário de autenticação
#     form = AuthenticationForm(request, data=request.POST or None)

#     if request.method == 'POST':
#         if form.is_valid():
#             username = form.cleaned_data.get('username')
#             password = form.cleaned_data.get('password')
#             user = authenticate(request, username=username, password=password)
            
#             if user is not None:
#                 login(request, user)
                
#                 # Crie a sessão com o ID da escola do usuário, caso o usuário tenha o campo 'escola'
#                 if hasattr(user, 'escola'):
#                     request.session['escola_id'] = user.escola.id
#                 return redirect('login:home')

#             else:
#                 messages.error(request, 'Credenciais inválidas.')
    
#     # Renderiza a página de login para GET ou se a autenticação falhar
#     return render(request, 'login.html', {'form_login': form})

