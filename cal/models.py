from django.db import models
from django.urls import reverse
from django.conf import settings  # Adicione esta importação
from datetime import date, datetime
import locale


# **Model Escola**
class Escola(models.Model):
    id = models.AutoField(primary_key=True)
    nome_escola = models.CharField(max_length=100, verbose_name="Nome da escola")
    
    responsaveis = models.ManyToManyField(
        settings.AUTH_USER_MODEL,  # Use settings.AUTH_USER_MODEL
        blank=True,
        related_name="escolas_responsavel"
    )
    
    def __str__(self):
        return self.nome_escola



# **Model Turma**
class Turma(models.Model):
    id = models.AutoField(primary_key=True)
    fk_escola = models.ForeignKey(Escola, on_delete=models.CASCADE, related_name="turma_escola", verbose_name="Nome da escola")
    turma = models.CharField(max_length=100, verbose_name="Nome da turma")

    def __str__(self):
        return self.turma

# **Model Materia**
class Materia(models.Model):
    id = models.AutoField(primary_key=True)
    nome_materia = models.CharField(max_length=100, verbose_name="Nome da matéria")

    def __str__(self):
        return self.nome_materia

# **Model Professor**
class Professor(models.Model):
    id = models.AutoField(primary_key=True)
    fk_escola = models.ForeignKey(Escola, on_delete=models.CASCADE, related_name="professores_escola", verbose_name="Nome da escola")
    fk_materia = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name="professor_materias", verbose_name="Matéria")
    nome_professor = models.CharField(max_length=100, verbose_name="Nome do Professor")

    def __str__(self):
        return self.nome_professor

# **Model Livro**
class Livro(models.Model):
    id = models.AutoField(primary_key=True)
    fk_escola = models.ForeignKey(Escola, on_delete=models.CASCADE, related_name="livro_escola", verbose_name="Nome da escola", default=1)
    fk_materia = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name="livro_materia", verbose_name="Matéria")
    nome_livro = models.CharField(max_length=100, verbose_name="Nome do livro")

    def __str__(self):
        return self.nome_livro

# **Model Aluno**
class Alunos(models.Model):
    id = models.AutoField(primary_key=True)
    fk_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='aluno_user', verbose_name="Responsável")  # Corrigido
    fk_escola = models.ForeignKey(Escola, on_delete=models.CASCADE, related_name="aluno_escola", verbose_name="Escola")
    fk_turma = models.ForeignKey(Turma, on_delete=models.CASCADE, related_name="aluno_turma", verbose_name="Turma")
    nome_aluno = models.CharField(max_length=100, verbose_name="Nome do aluno")

    def __str__(self):
        return self.nome_aluno

class Ordem(models.Model):
    id = models.AutoField(primary_key=True)
    ordem = models.CharField(max_length=20, verbose_name="Ordem do horário")  
    # Exemplo: "1º Horário", "2º Horário", ...

    def __str__(self):
        return self.ordem

# models.py - adicionar campo ordem ao modelo Dias se não existir
class Dias(models.Model):
    id = models.AutoField(primary_key=True)
    dias = models.CharField(max_length=20, verbose_name="Dias")
    ordem = models.IntegerField(verbose_name="Ordem", default=0)  # Adicionar este campo
    
    def __str__(self):
        return self.dias

class Horarios(models.Model):
    id = models.AutoField(primary_key=True)
    fk_dias = models.ForeignKey(
        Dias, on_delete=models.CASCADE,
        related_name="dias_semana", verbose_name="Dias da semana"
    )
    fk_ordem = models.ForeignKey(
        Ordem, on_delete=models.CASCADE,
        related_name="horarios_ordem", verbose_name="Ordem"
    )
    fk_escola = models.ForeignKey(
        Escola, on_delete=models.CASCADE,
        related_name="horarios_escola", verbose_name="Escola"
    )
    fk_turma = models.ForeignKey(
        Turma, on_delete=models.CASCADE,
        related_name="horarios_turma", verbose_name="Turma"
    )
    fk_professor = models.ForeignKey(
        Professor, on_delete=models.CASCADE,
        related_name="horarios_professor", verbose_name="Professor"
    )
    fk_materia = models.ForeignKey(
        Materia, on_delete=models.CASCADE,
        related_name="horarios_materia", verbose_name="Matéria"
    )

    def __str__(self):
        return f"{self.fk_turma} - {self.fk_dias} - {self.fk_ordem} - {self.fk_materia}"


class Event(models.Model):
    id = models.AutoField(primary_key=True)
    fk_escola = models.ForeignKey(Escola, on_delete=models.CASCADE, related_name="dever_escola", verbose_name="Escola")
    fk_turma = models.ForeignKey(Turma, on_delete=models.CASCADE, related_name="dever_turma", verbose_name="Turma")
    fk_professor = models.ForeignKey(Professor, on_delete=models.CASCADE, related_name="dever_professor", verbose_name="Professor")
    fk_materia = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name="dever_materia", verbose_name="Matéria")
    fk_livro = models.ForeignKey(Livro, on_delete=models.CASCADE, null=True, blank=True, related_name="dever_livro", verbose_name="Livro")
    title = models.TextField(verbose_name="Conteúdo Ministrado", null=True, blank=True,)
    start_time = models.DateField(verbose_name="Data da conteúdo ministrado", null=True, blank=True)
    dever = models.TextField(verbose_name="Dever de casa", null=True, blank=True,)
    data_entrega = models.DateField(verbose_name="Data da entrega", null=True, blank=True,)
    data_postagem = models.DateTimeField(auto_now_add=True, null=True, blank=True,)
    
    def horas_restantes(self):
        if self.data_entrega:
            delta = self.data_entrega - date.today()
            return delta.total_seconds() / 3600
        return 0  # sem data de entrega, não tem horas restantes

    def dias_para_entrega(self):
        if self.data_entrega:
            return (self.data_entrega - date.today()).days
        # fallback: usar a data de postagem
        return (self.data_postagem.date() - date.today()).days if self.data_postagem else 0

    def data_formatada(self):
        data_base = self.data_entrega or (self.data_postagem.date() if self.data_postagem else None)
        if not data_base:
            return "N/A"

        try:
            locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
        except locale.Error:
            locale.setlocale(locale.LC_TIME, 'pt_BR')
        return data_base.strftime("%d %A")

    @property
    def get_html_url(self):
        url = reverse('cal:event_edit', args=(self.id,))
        return f'<a href="{url}" class="event">{self.title}</a>'