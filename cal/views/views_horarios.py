from collections import defaultdict
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..models import Horarios, Ordem, Escola
from ..forms import HorariosForm

# views_horarios.py
from collections import defaultdict
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from ..models import Horarios, Ordem, Escola, Turma, Dias
from ..forms import HorariosForm

# @login_required
# views_horarios.py
# views_horarios.py
def listar_horarios(request, turma_id=None):
    horarios_por_escola = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    
    # Filtra por turma específica se fornecida
    if turma_id:
        horarios = Horarios.objects.filter(fk_turma_id=turma_id)
    else:
        horarios = Horarios.objects.all()
    
    horarios = horarios.select_related(
        'fk_ordem', 'fk_turma', 'fk_turma__fk_escola', 'fk_professor', 'fk_materia', 'fk_dias'
    ).order_by('fk_turma__fk_escola__nome_escola', 'fk_turma__turma', 'fk_dias__id', 'fk_ordem__id')

    for h in horarios:
        escola_nome = h.fk_turma.fk_escola.nome_escola
        turma_nome = h.fk_turma.turma
        dia_semana = h.fk_dias.dias if h.fk_dias else "Sem dia"
        horarios_por_escola[escola_nome][turma_nome][dia_semana].append(h)

    def convert_defaultdict_to_dict(d):
        if isinstance(d, defaultdict):
            d = {k: convert_defaultdict_to_dict(v) for k, v in d.items()}
        elif isinstance(d, dict):
            d = {k: convert_defaultdict_to_dict(v) for k, v in d.items()}
        return d

    context = {
        'horarios_por_escola': convert_defaultdict_to_dict(horarios_por_escola),
        'tem_horarios': any(horarios),
        'turma_filtrada': turma_id
    }
    return render(request, 'horarios/horario_list.html', context)


# @login_required
def horario_create(request):
    if request.method == 'POST':
        form = HorariosForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Horário cadastrado com sucesso.")
            return redirect('cal:listar_horarios')
    else:
        form = HorariosForm()
    return render(request, 'horarios/horario_form.html', {'form': form})


# @login_required
def horario_update(request, pk):
    horario = get_object_or_404(Horarios, pk=pk)
    if request.method == 'POST':
        form = HorariosForm(request.POST, instance=horario)
        if form.is_valid():
            form.save()
            messages.success(request, "Horário atualizado com sucesso.")
            return redirect('cal:listar_horarios')
    else:
        form = HorariosForm(instance=horario)
    return render(request, 'horarios/horario_form.html', {'form': form})


# @login_required
def horario_delete(request, pk):
    horario = get_object_or_404(Horarios, pk=pk)
    try:
        horario.delete()
        messages.success(request, "Horário deletado com sucesso.")
    except Exception as e:
        messages.error(request, f"Erro ao deletar: {str(e)}")
    return redirect('cal:listar_horarios')
