# login/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from cal.models import Escola

# login/forms.py

class RegistroPublicoForm(UserCreationForm):
    """Formulário para registro público onde o usuário define sua própria senha"""
    
    # Remover a seleção de tipo de usuário do formulário público
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'telefone', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite um nome de usuário'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o primeiro nome'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o sobrenome'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'exemplo@email.com'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(00) 00000-0000'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Adicionar classes aos campos de password
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Digite uma senha segura'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirme a senha'
        })
        
        # Adicionar help texts personalizados
        self.fields['password1'].help_text = 'Sua senha deve conter pelo menos 8 caracteres, incluindo letras e números.'
        self.fields['username'].help_text = 'Obrigatório. 150 caracteres ou menos. Letras, números e @/./+/-/_ apenas.'

class RegistroUsuarioForm(forms.ModelForm):
    """Formulário para registro por administradores (com senha padrão)"""
    
    tipo_usuario = forms.ChoiceField(
        choices=User.TIPO_CHOICES,
        label='Tipo de Usuário',
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': 'Selecione o tipo de usuário'
        })
    )
    
    fk_escola = forms.ModelChoiceField(
        queryset=Escola.objects.all(),
        label='Escola',
        required=False,
        empty_label="Selecione uma escola",
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'tipo_usuario', 'fk_escola', 'telefone']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite um nome de usuário'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o primeiro nome'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o sobrenome'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'exemplo@email.com'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(00) 00000-0000'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Restringe as opções baseado no usuário logado
        if self.user and not self.user.is_superuser_type():
            self.fields['tipo_usuario'].choices = [
                (tipo, nome) for tipo, nome in User.TIPO_CHOICES 
                if tipo not in ['superuser', 'admin']
            ]
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.editing_own_profile = kwargs.pop('editing_own_profile', False)
        super().__init__(*args, **kwargs)
        
        # Se estiver editando o próprio perfil, remove a seleção de tipo de usuário
        if self.editing_own_profile:
            self.fields.pop('tipo_usuario', None)
            self.fields.pop('fk_escola', None)
        
        # Restringe as opções baseado no usuário logado
        elif self.user and not self.user.is_superuser_type():
            self.fields['tipo_usuario'].choices = [
                (tipo, nome) for tipo, nome in User.TIPO_CHOICES 
                if tipo not in ['superuser', 'admin']
            ]

class AlterarSenhaForm(forms.Form):
    """Formulário para alteração de senha pelo próprio usuário"""
    
    senha_atual = forms.CharField(
        label='Senha Atual',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite sua senha atual'
        }),
        required=True
    )
    
    nova_senha = forms.CharField(
        label='Nova Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite a nova senha'
        }),
        required=True,
        help_text='Sua senha deve conter pelo menos 8 caracteres, incluindo letras e números.'
    )
    
    confirmar_senha = forms.CharField(
        label='Confirmar Nova Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme a nova senha'
        }),
        required=True
    )
    
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_senha_atual(self):
        senha_atual = self.cleaned_data.get('senha_atual')
        if not self.user.check_password(senha_atual):
            raise forms.ValidationError('Senha atual incorreta.')
        return senha_atual
    
    def clean(self):
        cleaned_data = super().clean()
        nova_senha = cleaned_data.get('nova_senha')
        confirmar_senha = cleaned_data.get('confirmar_senha')
        
        if nova_senha and confirmar_senha and nova_senha != confirmar_senha:
            raise forms.ValidationError('As novas senhas não coincidem.')
        
        return cleaned_data