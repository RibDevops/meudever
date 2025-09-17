from django.db import models
from django.contrib.auth.models import AbstractUser



class User(AbstractUser):
    # Use string reference em vez de import direto
    # fk_escola = models.ManyToManyField(
    #     'cal.Escola',
    #     null=True,
    #     blank=True,
    #     related_name="login_escola",
    #     verbose_name="Escola",
    #     default=None  # Mude para None ou um valor válido
    # )
    # fk_escola = models.ForeignKey(Escola, null=True, blank=True, on_delete=models.SET_NULL)
    fk_escola = models.ForeignKey('cal.Escola', null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Escola")

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name="custom_user_groups",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="custom_user_permissions",
        related_query_name="user",
    )

    class Meta:
        db_table = 'custom_user'  # Nome personalizado da tabela