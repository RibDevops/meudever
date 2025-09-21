# login/decorators.py

from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import user_passes_test
from functools import wraps
from django.shortcuts import redirect

def tipo_usuario_required(tipos_permitidos):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login:login')
            
            if request.user.tipo_usuario in tipos_permitidos or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            return HttpResponseForbidden("Você não tem permissão para acessar esta página.")
        return _wrapped_view
    return decorator

# Decoradores específicos
def superuser_required(view_func):
    return user_passes_test(
        lambda u: u.is_authenticated and (u.tipo_usuario == 'superuser' or u.is_superuser),
        login_url='login:login'
    )(view_func)

def admin_required(view_func):
    return user_passes_test(
        lambda u: u.is_authenticated and (u.tipo_usuario in ['superuser', 'admin'] or u.is_superuser),
        login_url='login:login'
    )(view_func)

def gestao_usuarios_required(view_func):
    return tipo_usuario_required(['superuser', 'admin', 'coordenador'])(view_func)