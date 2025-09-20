from django.urls import path, re_path
from . import views
from django.urls import path
from cal.views.views_ajax import *
from cal.views.views_dever import *
from cal.views.views_semana import *
from cal.views import *
from django.urls import path
# from cal.views import (home)

app_name = 'cal'

urlpatterns = [
    path('', views.home, name='home'),

    path('index/', views.index, name='index'),
    path('calendar/', views.CalendarView.as_view(), name='calendar'),
    path('event/new/', views.event, name='event_new'),
    path('eventos/', views.listar_eventos, name='listar_eventos'),
    path('eventos/excluir/<int:event_id>/', views.excluir_evento, name='excluir_evento'),

    re_path(r'^event/edit/(?P<event_id>\d+)/$', views.event, name='event_edit'),

    path('lista/', listar_eventos, name='listar_eventos'),
    path('<int:pk>/', dever_detail, name='dever_detail'),
    path('novo/', dever_create, name='dever_create'),
    path('<int:pk>/editar/', dever_update, name='dever_update'),
    path('<int:pk>/deletar/', dever_delete, name='dever_delete'),

    # Outras rotas
    # path('ajax/get-professores/<int:escola_id>/', views.get_professores_by_escola, name='get_professores_by_escola'),
    # path('ajax/get-materia/<int:professor_id>/', views.get_materia_by_professor, name='get_materia_by_professor'),
    # path('ajax/get-livros/<int:materia_id>/', views.get_livros_by_materia, name='get_livros_by_materia'),


    path('ajax/get-professores/<int:escola_id>/', views_ajax.get_professores_by_escola, name='get_professores'),
    path('ajax/get-turmas/<int:escola_id>/', views_ajax.get_turmas_by_escola, name='get_turmas'),
    path('ajax/get-materia/<int:professor_id>/', views_ajax.get_materia_by_professor, name='get_materia'),
    # path('ajax/get-livros/<int:materia_id>/', views_ajax.get_livros_by_materia, name='get_livros'),
    path('ajax/get-livros/<int:materia_id>/<int:escola_id>/', views.get_livros_ajax, name='get_livros_ajax'),


    # URLs para Escola
    path('escolas/', views.lista_escolas, name='lista_escolas'),
    path('escolas/nova/', views.cria_escolas, name='cria_escolas'),
    path('escolas/<pk>/atualiza/', views.atualiza_escolas, name='atualiza_escolas'),
    path('escolas/<pk>/deleta/', views.deleta_escolas, name='deleta_escolas'),

    # URLs para Turma
    path('turma/', views.lista_turma, name='lista_turma'),
    # path('turmas/', views.lista_turma, name='lista_turma'),
    path('turma/nova/', views.cria_turma, name='cria_turma'),
    path('turma/<pk>/atualiza/', views.atualiza_turma, name='atualiza_turma'),
    path('turma/<pk>/deleta/', views.deleta_turma, name='deleta_turma'),

    # Exemplo para Materia:
    path('materia/', views.lista_materia, name='lista_materia'),
    path('materia/nova/', views.cria_materia, name='cria_materia'),
    path('materia/<pk>/atualiza/', views.atualiza_materia, name='atualiza_materia'),
    path('materia/<pk>/deleta/', views.deleta_materia, name='deleta_materia'),

    # Exemplo para professor:
    path('professor/', views.lista_professor, name='lista_professor'),
    path('professor/nova/', views.cria_professor, name='cria_professor'),
    path('professor/<pk>/atualiza/', views.atualiza_professor, name='atualiza_professor'),
    path('professor/<pk>/deleta/', views.deleta_professor, name='deleta_professor'),

    # Exemplo para livro:
    path('livro/', views.lista_livro, name='lista_livro'),
    path('livro/nova/', views.cria_livro, name='cria_livro'),
    path('livro/<pk>/atualiza/', views.atualiza_livro, name='atualiza_livro'),
    path('livro/<pk>/deleta/', views.deleta_livro, name='deleta_livro'),

    # Exemplo para aluno:
    path('alunos/', views.lista_alunos, name='lista_alunos'),
    path('alunos/nova/', views.cria_alunos, name='cria_alunos'),
    path('alunos/<pk>/atualiza/', views.atualiza_alunos, name='atualiza_alunos'),
    path('alunos/<pk>/deleta/', views.deleta_alunos, name='deleta_alunos'),

    # novos para Horarios
    # path('horarios/', views_horarios.listar_horarios, name='listar_horarios'),
    path('horarios/create/', views_horarios.horario_create, name='horario_create'),
    path('horarios/<int:pk>/update/', views_horarios.horario_update, name='horario_update'),
    # path('horarios/<int:pk>/update/', views.horario_update, name='horario_update'),
    path('horarios/<int:pk>/delete/', views_horarios.horario_delete, name='horario_delete'),
    # path('horarios/<int:pk>/delete/', views.horario_delete, name='horario_delete'),

        # ... outras URLs
    path('horarios/', views.listar_horarios, name='listar_horarios'),
    path('horarios/turma/<int:turma_id>/', views.listar_horarios, name='listar_horarios_turma'),

    path('semana/completa/<int:turma_id>/', views_semana.semana_turma_completa, name='semana_completa'),



    
    # path('horarios/create/', views.horario_create, name='horario_create'),
    
    
    
]
