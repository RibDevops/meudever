from django.forms import ModelForm, DateInput
from cal.models import Event
from django import forms
from .models import Event, Horarios, Materia, Escola, Turma, Materia, Professor, Livro, Alunos
from django.contrib.auth.models import User

class EventForm(ModelForm):
    class Meta:
        model = Event
        widgets = {
            'start_time': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'data_entrega': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'conteudo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'dever': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'start_time': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(EventForm, self).__init__(*args, **kwargs)
        
        
        self.fields['title'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'ex: CP José - 14:00h'
        })
        
        # Remove os input_formats com hora
        self.fields['start_time'].input_formats = ('%Y-%m-%d',)
        self.fields['data_entrega'].input_formats = ('%Y-%m-%d',)
        self.fields['start_time'].input_formats = ('%Y-%m-%d',)
        
        # Aplica as regras de permissão baseadas no tipo de usuário
        self.apply_user_permissions()

    def apply_user_permissions(self):
        if not self.user:
            return
            
        if self.user.is_superuser:
            # Superuser pode ver tudo - não fazemos alterações
            return
            
        elif hasattr(self.user, 'coordenador'):
            # Coordenador - oculta campo escola
            if 'fk_escola' in self.fields:
                self.fields['fk_escola'].widget = forms.HiddenInput()
                # Define a escola do coordenador como valor inicial
                if hasattr(self.user.coordenador, 'fk_escola'):
                    self.fields['fk_escola'].initial = self.user.coordenador.fk_escola
                    
        elif hasattr(self.user, 'professor'):
            # Professor - oculta escola, professor e matéria
            professor_profile = self.user.professor
            
            if 'fk_escola' in self.fields:
                self.fields['fk_escola'].widget = forms.HiddenInput()
                self.fields['fk_escola'].initial = professor_profile.fk_escola
                
            if 'fk_professor' in self.fields:
                self.fields['fk_professor'].widget = forms.HiddenInput()
                self.fields['fk_professor'].initial = professor_profile
                
            if 'fk_materia' in self.fields:
                self.fields['fk_materia'].widget = forms.HiddenInput()
                self.fields['fk_materia'].initial = professor_profile.fk_materia

    # Mantém a lógica de filtro de matérias
    def clean(self):
        cleaned_data = super().clean()
        
        # Filtra as matérias se um professor foi selecionado (para superuser)
        if self.user and self.user.is_superuser and 'fk_professor' in cleaned_data:
            try:
                professor_id = cleaned_data.get('fk_professor').id
                self.fields['fk_materia'].queryset = Materia.objects.filter(professor_materias=professor_id)
            except (ValueError, TypeError, AttributeError):
                pass
                
        return cleaned_data

# Os outros forms permanecem iguais
class EscolaForm(forms.ModelForm):
    class Meta:
        model = Escola
        fields = ('nome_escola',)
        widgets = {
            'nome_escola': forms.TextInput(attrs={
                'class': 'form-control mb-3',
                'placeholder': 'Digite o nome da escola aqui',
                'onblur': 'this.value=this.value.toUpperCase()',
                'pattern': '[A-Za-záéíóúÁÉÍÓÚ\s]+',
                'style': 'border-radius: 5px; box-shadow: 0 0 5px #ccc;'
            })
        }

class TurmaForm(forms.ModelForm):
    class Meta:
        model = Turma
        fields = ('fk_escola', 'turma')

class MateriaForm(forms.ModelForm):
    class Meta:
        model = Materia
        fields = ('nome_materia',)

class ProfessorForm(forms.ModelForm):
    class Meta:
        model = Professor
        fields = ('fk_escola', 'fk_materia', 'nome_professor')

class LivrosForm(forms.ModelForm):
    class Meta:
        model = Livro
        fields = ('fk_escola', 'fk_materia', 'nome_livro')

class AlunosForm(forms.ModelForm):
    class Meta:
        model = Alunos
        fields = ('fk_user', 'fk_escola', 'fk_turma', 'nome_aluno')

class HorariosForm(forms.ModelForm):
    class Meta:
        model = Horarios
        fields = ['fk_escola', 'fk_dias', 'fk_ordem', 'fk_turma', 'fk_professor', 'fk_materia']