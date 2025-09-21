# from django.contrib import admin

# # Register your models here.
# from .models import User

# admin.site.register(User)

from django.contrib import admin
from .models import User, TipoUsuario

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'tipo_usuario', 'fk_escola', 'ativo']
    list_filter = ['tipo_usuario', 'ativo', 'fk_escola']
    search_fields = ['username', 'email', 'first_name', 'last_name']

@admin.register(TipoUsuario)
class TipoUsuarioAdmin(admin.ModelAdmin):
    list_display = ['nome', 'descricao']
    filter_horizontal = ['permissoes']