from django.forms import ModelForm, DateInput
from cal.models import Event
from django import forms
from .models import Event, Materia, Escola, Turma, Materia, Professor, Livro, Alunos
from django import forms
from django.contrib.auth.models import User

class EventForm(ModelForm):
    class Meta:
        model = Event
        widgets = {
            'start_time': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),  # Somente data
            'data_entrega': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),    # Somente data
        }
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['placeholder'] = 'ex: CP José - 14:00h'
        # Remove os input_formats com hora, pois agora só queremos a data
        self.fields['start_time'].input_formats = ('%Y-%m-%d',)  # Formato ISO para data
        self.fields['data_entrega'].input_formats = ('%Y-%m-%d',)   # Formato ISO para data
    
    #  def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
        # Filtra as matérias se um professor foi selecionado
        if 'fk_professor' in self.data:
            try:
                professor_id = int(self.data.get('fk_professor'))
                # self.fields['fk_materia'].queryset = Materia.objects.filter(materias_professor=professor_id)
                self.fields['fk_materia'].queryset = Materia.objects.filter(professor_materias=professor_id)

            except (ValueError, TypeError):
                pass  # Se fk_professor não for válido, ignora o filtro
        else:
            self.fields['fk_materia'].queryset = Materia.objects.none()

# class EventForm(forms.ModelForm):
#     class Meta:
#         model = Event
#         fields = ['fk_escola', 'fk_turma', 'fk_materia', 'fk_livro', 'fk_professor', 'conteudo','dever', 'data_entrega', 'data_conteudo']
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Filtra as matérias se um professor foi selecionado
#         if 'fk_professor' in self.data:
#             try:
#                 professor_id = int(self.data.get('fk_professor'))
#                 # self.fields['fk_materia'].queryset = Materia.objects.filter(materias_professor=professor_id)
#                 self.fields['fk_materia'].queryset = Materia.objects.filter(professor_materias=professor_id)

#             except (ValueError, TypeError):
#                 pass  # Se fk_professor não for válido, ignora o filtro
#         else:
#             self.fields['fk_materia'].queryset = Materia.objects.none()



class EscolaForm(forms.ModelForm):
    class Meta:
        model = Escola
        fields = ('nome_escola',)
        widgets = {
            'nome_escola': forms.TextInput(attrs={
                'class': 'form-control mb-3',  # Adiciona classes CSS para estilização
                'placeholder': 'Digite o nome da escola aqui',  # Define um placeholder
                'eadonly': False,  # Campo pode ser editado (se quiser somente leitura, trocar por True)
                'data-toggle': 'tooltip',  # Adiciona um atributo de dados para tooltip
                'title': 'Nome da instituição de ensino',  # Define a dica do tooltip
                'size': '50',  # Define o tamanho visível do campo
                'onblur': 'this.value=this.value.toUpperCase()',  # Converte para maiúsculas ao sair do campo
                'equired': 'equired',  # Campo é obrigatório (pode ser removido se não for necessário)
                'pattern': '[A-Za-záéíóúÁÉÍÓÚ\s]+',  # Define um padrão de entrada (letras e espaços)
                'tyle': 'border-radius: 5px; box-shadow: 0 0 5px #ccc;'  # Adiciona estilos CSS inline
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


from django import forms
from .models import Horarios

class HorariosForm(forms.ModelForm):
    class Meta:
        model = Horarios
        # fields = '__all__'
        fields = ['fk_escola', 'fk_dias', 'fk_ordem', 'fk_turma', 'fk_professor', 'fk_materia']
