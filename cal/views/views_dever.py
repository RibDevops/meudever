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

#@login_required
def listar_eventos(request):
    deveres_por_escola = defaultdict(lambda: defaultdict(list))

    deveres = Event.objects.select_related(
        'fk_turma', 'fk_turma__fk_escola', 'fk_materia', 'fk_professor'
    ).all().order_by('fk_turma__fk_escola__nome_escola', 'fk_turma__turma', 'data_entrega')

    for dever in deveres:
        dias_para_entrega = cal.dias_para_entrega()
        if dias_para_entrega <= 1:
            cal.cor_fundo = "vermelho"
        elif dias_para_entrega == 2:
            cal.cor_fundo = "amarelo"
        else:
            cal.cor_fundo = "verde"

        escola_nome = cal.fk_turma.fk_escola.nome_escola
        turma_nome = cal.fk_turma.turma
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

    return render(request, 'dever/listar_eventos.html', context)


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

#@login_required
def dever_delete(request, pk):
    dever = get_object_or_404(Event, pk=pk)
    try:
        cal.delete()
        messages.success(request, "Dever deletado com sucesso.")
    except Exception as e:
        messages.error(request, f"Erro ao deletar: {str(e)}")
    return redirect('cal:listar_eventos')
