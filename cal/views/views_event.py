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
#     instance = Event()
#     if event_id:
#         instance = get_object_or_404(Event, pk=event_id)
#     else:
#         instance = Event()

#     form = EventForm(request.POST or None, instance=instance)
#     if request.POST and form.is_valid():
#         form.save()
#         return HttpResponseRedirect(reverse('cal:event_new'))

#     return render(request, 'cal/event.html', {'form': form})
# def dever_create(request):
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

#@login_required
def listar_eventos(request):
    deveres_por_escola = defaultdict(lambda: defaultdict(list))
    # deveres = Event.objects.select_related('fk_turma', 'fk_turma__fk_escola', 'fk_materia', 'fk_professor').annotate(data_ordem=Coalesce('data_entrega', F('data_postagem'))).order_by('fk_turma__fk_escola__nome_escola', 'fk_turma__turma', 'data_ordem')
    deveres = Event.objects.select_related(
            'fk_turma', 'fk_turma__fk_escola', 'fk_materia', 'fk_professor'
        ).annotate(
            data_ordem=Coalesce(
                'data_entrega',
                Cast('data_postagem', output_field=DateField())
            )
        ).order_by(
            'fk_turma__fk_escola__nome_escola',
            'fk_turma__turma',
            'data_ordem'
        )
    for dever in deveres:
        # print(f'qtd: {dever.dias_para_entrega()}')
        dias_para_entrega = dever.dias_para_entrega()  # CORREÇÃO: usar 'dever'
        if dias_para_entrega <= 1:
            dever.cor_fundo = "vermelho"  # CORREÇÃO: usar 'dever'
        elif dias_para_entrega == 2:
            dever.cor_fundo = "amarelo"  # CORREÇÃO: usar 'dever'
        else:
            dever.cor_fundo = "verde"  # CORREÇÃO: usar 'dever'

        escola_nome = dever.fk_turma.fk_escola.nome_escola  # CORREÇÃO: usar 'dever'
        turma_nome = dever.fk_turma.turma  # CORREÇÃO: usar 'dever'
        deveres_por_escola[escola_nome][turma_nome].append(dever)

    def convert_defaultdict_to_dict(d):
        if isinstance(d, defaultdict):
            d = {k: convert_defaultdict_to_dict(v) for k, v in d.items()}
        elif isinstance(d, dict):
            d = {k: convert_defaultdict_to_dict(v) for k, v in d.items()}
        return d

    context = {
        'deveres_por_escola': convert_defaultdict_to_dict(deveres_por_escola),
        'tem_deveres': any(deveres)
    }

    return render(request, 'dever/dever_list.html', context)


def dever_detail(request, pk):
    dever = get_object_or_404(Event, pk=pk)
    return render(request, 'dever/dever_detail.html', {'dever': dever})

#@login_required
def dever_create(request):
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
