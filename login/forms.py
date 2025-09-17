from email.headerregistry import Group
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User
from django.contrib.auth.models import Group


# class RegistroUsuarioForm(UserCreationForm):
#     class Meta:
#         model = User
#         fields = ['username', 'email', 'profile', 'password1', 'password2']

# class LoginForm(AuthenticationForm):
#     username = forms.CharField(label='Username')
#     password = forms.CharField(label='Password', widget=forms.PasswordInput)

from django import forms
from django.contrib.auth.models import Group
from .models import User  # Supondo que você tenha um modelo User customizado

class RegistroUsuarioForm(forms.ModelForm):
    group = forms.ChoiceField(choices=[('COORDENADOR', 'Coordenador'), ('PROFESSOR', 'Professor'), ('PAI', 'Pai'), ('ALUNO', 'Aluno')])

    class Meta:
        model = User
        fields = ['fk_escola', 'username', 'email', 'password', 'group']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        group_name = self.cleaned_data["group"]
        user.save()

        # Criar ou obter o grupo e adicionar o usuário a ele
        group, _ = Group.objects.get_or_create(name=group_name)
        user.groups.add(group)

        return user
