from datetime import datetime, timedelta, date
from pyexpat.errors import messages
from venv import logger
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.urls import reverse
from django.utils.safestring import mark_safe
import calendar
from django.utils import timezone

from ..models import *
from ..utils import Calendar
from ..forms import EventForm
import logging
from django.shortcuts import redirect

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..models import Event, Escola
from ..forms import EventForm
from datetime import date
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

from django.db.models import F, Value
from django.db.models.functions import Coalesce

def home(request):
    return render(request, 'home.html', {})

def index(request):
    return HttpResponse('hello')

class CalendarView(generic.ListView):
    model = Event
    template_name = 'cal/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        d = get_date(self.request.GET.get('month', None))
        
        # Obter todos os eventos do mês
        # events = Event.objects.filter(
        events = Event.objects.select_related('fk_materia').filter(
            start_time__year=d.year,
            start_time__month=d.month
        )
        
        # Criar calendário com eventos
        cal = Calendar(d.year, d.month)
        html_cal = cal.formatmonth(withyear=True, events=events)
        
        context['calendar'] = mark_safe(html_cal)
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        context['month_name'] = d.strftime("%B")  # Nome completo do mês
        context['year'] = d.year
        return context

def get_date(req_month):
    if req_month:
        year, month = (int(x) for x in req_month.split('-'))
        return date(year, month, day=1)
    return datetime.today()

def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
    return month

def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
    return month

def event(request, event_id=None):
    if request.method == 'POST':
        form = EventForm(request.POST)
        logger.debug("Dados do POST: %s", request.POST)
        print("Dados do POST:", request.POST)
        if form.is_valid():
            dever = form.save()
            messages.success(request, "Dever cadastrado com sucesso.")
            return redirect('cal:listar_eventos')
        else:
            # loga e mostra os erros campo a campo
            logger.warning("Form inválido ao tentar criar cal: %s", form.errors)
            print("Erros do form:", form.errors)
            for field, error_list in form.errors.items():
                for error in error_list:
                    texto = f"Erro no campo {field}: {error}"
                    messages.error(request, texto)
    else:
        form = EventForm()

    escolas = Escola.objects.all()
    return render(request, 'dever/dever_form.html', {'form': form, 'escolas': escolas})




# def listar_eventos(request):
#     eventos = Event.objects.all().order_by('start_time')
#     return render(request, 'cal/lista_eventos.html', {'eventos': eventos})

def excluir_evento(request, event_id):
    evento = get_object_or_404(Event, pk=event_id)
    evento.delete()
    return redirect('cal:listar_eventos')

from django.db.models import F
from django.db.models.functions import Coalesce, Cast
from django.db.models import DateField
from django.db.models import Q
from django.contrib.auth.decorators import login_required

from django.db.models import Q
from django.contrib.auth.decorators import login_required

@login_required
def listar_eventos(request):
    # Inicializar queryset base
    deveres = Event.objects.select_related(
        'fk_turma', 'fk_turma__fk_escola', 'fk_materia', 'fk_professor'
    ).annotate(
        data_ordem=Coalesce(
            'data_entrega',
            Cast('data_postagem', output_field=DateField())
        )
    )
    
    # Aplicar filtros baseados no tipo de usuário
    user = request.user
    
    if user.tipo_usuario == 'superuser':
        # Superuser vê tudo - sem filtro adicional
        pass
        
    elif user.tipo_usuario == 'admin':
        # Admin vê tudo da sua escola
        if user.fk_escola:
            deveres = deveres.filter(fk_turma__fk_escola=user.fk_escola)
        else:
            deveres = deveres.none()
            messages.info(request, "Você não está vinculado a nenhuma escola.")
            
    elif user.tipo_usuario == 'coordenador':
        # Coordenador vê tudo da sua escola
        if user.fk_escola:
            deveres = deveres.filter(fk_turma__fk_escola=user.fk_escola)
        else:
            deveres = deveres.none()
            messages.info(request, "Você não está vinculado a nenhuma escola.")
            
    elif user.tipo_usuario == 'professor':
        # Professor vê os seus deveres de TODAS as turmas
        # Busca por correspondência no nome do professor
        professor_nome = user.get_full_name() or user.username
        
        # Primeiro tenta encontrar exatamente pelo nome
        professor_exato = Professor.objects.filter(
            nome_professor__iexact=professor_nome
        ).first()
        
        if professor_exato:
            deveres = deveres.filter(fk_professor=professor_exato)
        else:
            # Se não encontrar exato, busca por partes do nome
            if user.first_name and user.last_name:
                deveres = deveres.filter(
                    Q(fk_professor__nome_professor__icontains=user.first_name) |
                    Q(fk_professor__nome_professor__icontains=user.last_name)
                )
            else:
                deveres = deveres.filter(
                    fk_professor__nome_professor__icontains=professor_nome
                )
        
        # Se ainda não encontrou, mostra mensagem
        if not deveres.exists():
            messages.info(request, f"Nenhum dever encontrado para o professor '{professor_nome}'.")
            
    elif user.tipo_usuario == 'pai':
        # Pai vê os deveres de TODOS os seus filhos
        alunos_filhos = Alunos.objects.filter(fk_user=user).select_related('fk_turma', 'fk_escola')
        
        if not alunos_filhos.exists():
            deveres = deveres.none()
            messages.info(request, "Nenhum aluno vinculado à sua conta.")
        else:
            # Coletar TODAS as turmas dos filhos
            turmas_ids = []
            escolas_ids = []
            
            for aluno in alunos_filhos:
                turmas_ids.append(aluno.fk_turma.id)
                escolas_ids.append(aluno.fk_escola.id)
            
            # Filtrar por TODAS as turmas dos filhos
            deveres = deveres.filter(
                fk_turma__id__in=turmas_ids,
                fk_turma__fk_escola__id__in=escolas_ids
            )
            
            # Adicionar informação de qual filho está relacionado a cada dever
            for dever in deveres:
                # Encontrar TODOS os filhos nesta turma
                filhos_na_turma = alunos_filhos.filter(fk_turma=dever.fk_turma)
                if filhos_na_turma.exists():
                    nomes_filhos = [aluno.nome_aluno for aluno in filhos_na_turma]
                    dever.alunos_nomes = ", ".join(nomes_filhos)
                else:
                    dever.alunos_nomes = "Filho"
            
            if not deveres.exists():
                nomes_filhos = [aluno.nome_aluno for aluno in alunos_filhos]
                messages.info(request, f"Nenhum dever encontrado para seus filhos: {', '.join(nomes_filhos)}")
                
    else:
        # Para outros tipos (aluno, etc.), não mostra nada
        deveres = deveres.none()
        messages.info(request, "Você não tem permissão para visualizar deveres.")
    
    # Ordenar os resultados
    deveres = deveres.order_by('fk_turma__fk_escola__nome_escola', 'fk_turma__turma', 'data_ordem')
    
    # Processar cores baseadas nos dias para entrega
    for dever in deveres:
        dias_para_entrega = dever.dias_para_entrega()
        if dias_para_entrega <= 1:
            dever.cor_fundo = "table-danger"  # Vermelho - Urgente
            dever.status = "Urgente"
        elif dias_para_entrega <= 3:
            dever.cor_fundo = "table-warning"  # Amarelo - Atenção
            dever.status = "Atenção"
        else:
            dever.cor_fundo = "table-success"  # Verde - No prazo
            dever.status = "No prazo"
    
    # Agrupar por escola e turma
    deveres_por_escola = defaultdict(lambda: defaultdict(list))
    for dever in deveres:
        escola_nome = dever.fk_turma.fk_escola.nome_escola
        turma_nome = dever.fk_turma.turma
        deveres_por_escola[escola_nome][turma_nome].append(dever)
    
    def convert_defaultdict_to_dict(d):
        if isinstance(d, defaultdict):
            d = {k: convert_defaultdict_to_dict(v) for k, v in d.items()}
        elif isinstance(d, dict):
            d = {k: convert_defaultdict_to_dict(v) for k, v in d.items()}
        return d
    
    context = {
        'deveres_por_escola': convert_defaultdict_to_dict(deveres_por_escola),
        'tem_deveres': deveres.exists(),
        'user_tipo': user.tipo_usuario,
        'user': user
    }
    
    # Adicionar alunos_filhos no contexto para pais
    if user.tipo_usuario == 'pai':
        context['alunos_filhos'] = Alunos.objects.filter(fk_user=user).select_related('fk_turma', 'fk_escola')
    
    return render(request, 'dever/dever_list.html', context)


#@login_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

@login_required
def dever_create(request):
    print('dever_create')

    # Se for POST, processa o formulário
    if request.method == "POST":
        form = EventForm(request.POST, user=request.user)

        if form.is_valid():
            event = form.save(commit=False)  # Não salva ainda, podemos ajustar campos extras

            # Para professores, garantir que fk_escola, fk_professor e fk_materia estão corretos
            if request.user.tipo_usuario == "professor" and hasattr(request.user, 'fk_professor'):
                professor = request.user.fk_professor
                event.fk_professor = professor
                event.fk_escola = professor.fk_escola
                event.fk_materia = professor.fk_materia

            # Para coordenador, podemos garantir que fk_escola vem do usuário
            elif request.user.tipo_usuario == "coordenador":
                if hasattr(request.user, 'fk_escola'):
                    event.fk_escola = request.user.fk_escola

            # Salva o objeto
            event.save()
            print(f"Evento salvo: {event.id}")

            # Redireciona para lista ou página de sucesso
            return redirect('cal:listar_eventos')

        else:
            print("Form inválido")
            print(form.errors)  # mostra os erros no console
    else:
        # Se não for POST, apenas exibe o formulário
        form = EventForm(user=request.user)

    # Monta o contexto para o template
    context = {
        'form': form,
        'escolas': Escola.objects.all(),
    }

    # Adiciona professor/materia para usuários do tipo professor
    if request.user.tipo_usuario == "professor" and hasattr(request.user, 'fk_professor'):
        professor = request.user.fk_professor
        context['professor_usuario'] = professor
        context['materia_id'] = professor.fk_materia.id if hasattr(professor, 'fk_materia') else None

    return render(request, "dever/dever_form.html", context)




#@login_required
def dever_update(request, pk):
    dever = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=dever)
        if form.is_valid():
            form.save()
            messages.success(request, "Atualizado com sucesso.")
            return redirect('cal:listar_eventos')
        else:
            for field, error_list in form.errors.items():
                for error in error_list:
                    messages.error(request, f"Erro no campo {field}: {error}")
    else:
        form = EventForm(instance=dever)
        escolas = Escola.objects.all()
    return render(request, 'dever/dever_update.html', {'form': form, 'escolas': escolas})

def dever_delete(request, pk):
    dever = get_object_or_404(Event, pk=pk)
    try:
        dever.delete()  # CORREÇÃO: usar 'dever' em vez de 'cal'
        messages.success(request, "Dever deletado com sucesso.")
    except Exception as e:
        messages.error(request, f"Erro ao deletar: {str(e)}")
    return redirect('cal:listar_eventos')


# @login_required
def listar_horarios(request):
    horarios_por_escola = defaultdict(lambda: defaultdict(list))

    horarios = Horarios.objects.select_related(
        'fk_ordem', 'fk_turma', 'fk_turma__fk_escola', 'fk_professor', 'fk_materia'
    ).order_by('fk_turma__fk_escola__nome_escola', 'fk_turma__turma', 'fk_ordem__id')

    for h in horarios:
        escola_nome = h.fk_turma.fk_escola.nome_escola
        turma_nome = h.fk_turma.turma
        horarios_por_escola[escola_nome][turma_nome].append(h)

    def convert_defaultdict_to_dict(d):
        if isinstance(d, defaultdict):
            d = {k: convert_defaultdict_to_dict(v) for k, v in d.items()}
        elif isinstance(d, dict):
            d = {k: convert_defaultdict_to_dict(v) for k, v in d.items()}
        return d

    context = {
        'horarios_por_escola': convert_defaultdict_to_dict(horarios_por_escola),
        'tem_horarios': any(horarios)
    }

    return render(request, 'horarios/horario_list.html', context)
