# login/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from cal.models import Escola, Professor

class TipoUsuario(models.Model):
    TIPOS = (
        ('superuser', 'Superusuário'),
        ('admin', 'Administrador'),
        ('coordenador', 'Coordenador'),
        ('professor', 'Professor'),
        ('aluno', 'Aluno'),
        ('pai', 'Pai/Responsável'),
    )
    
    nome = models.CharField(max_length=50, choices=TIPOS, unique=True)
    descricao = models.TextField(blank=True)
    permissoes = models.ManyToManyField(
        Permission,
        verbose_name='permissoes',
        blank=True,
        related_name='tipos_usuario'
    )
    
    class Meta:
        verbose_name = 'Tipo de Usuário'
        verbose_name_plural = 'Tipos de Usuário'
    
    def __str__(self):
        return self.get_nome_display()

class User(AbstractUser):
    TIPO_CHOICES = (
        ('superuser', 'Superusuário'),
        ('admin', 'Administrador'),
        ('coordenador', 'Coordenador'),
        ('professor', 'Professor'),
        ('aluno', 'Aluno'),
        ('pai', 'Pai/Responsável'),
    )
    
    fk_escola = models.ForeignKey(
        Escola,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Escola"
    )
    fk_professor = models.ForeignKey(
        Professor,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Professor"
    )
    tipo_usuario = models.CharField(max_length=20, choices=TIPO_CHOICES, default='professor')
    telefone = models.CharField(max_length=20, blank=True)
    ativo = models.BooleanField(default=True)

    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name="custom_user_groups",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="custom_user_permissions",
        related_query_name="user",
    )

    class Meta:
        db_table = 'custom_user'
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
    
    def __str__(self):
        return f"{self.username} ({self.get_tipo_usuario_display()})"
    
    # Métodos de verificação de tipo de usuário
    def is_superuser_type(self):
        return self.tipo_usuario == 'superuser'
    
    def is_admin_type(self):
        return self.tipo_usuario in ['superuser', 'admin']
    
    def can_manage_users(self):
        return self.tipo_usuario in ['superuser', 'admin', 'coordenador']
    
    def is_pai_type(self):
        return self.tipo_usuario == 'pai'
