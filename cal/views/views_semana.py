# views_semana.py
from datetime import date, timedelta
from collections import defaultdict
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from ..models import Horarios, Event, Turma, Dias


@login_required
def semana_turma_completa(request, turma_id):
    turma = get_object_or_404(Turma, pk=turma_id)
    
    # Buscar todos os horários da turma
    horarios = Horarios.objects.filter(fk_turma=turma).select_related(
        "fk_dias", "fk_ordem", "fk_professor", "fk_materia"
    ).order_by("fk_dias__id", "fk_ordem__id")
    
    # Buscar todos os eventos da turma
    eventos = Event.objects.filter(fk_turma=turma).select_related(
        "fk_materia", "fk_professor", "fk_livro"
    )
    
    # Criar dicionário para rápido acesso aos eventos por data e matéria
    eventos_por_data_materia = defaultdict(dict)
    for evento in eventos:
        if evento.start_time:
            data_key = evento.start_time.strftime("%Y-%m-%d")
            eventos_por_data_materia[data_key][evento.fk_materia_id] = evento
        if evento.data_entrega:
            data_key = evento.data_entrega.strftime("%Y-%m-%d")
            eventos_por_data_materia[data_key][evento.fk_materia_id] = evento
    
    # Obter a semana atual (segunda a sexta)
    hoje = date.today()
    segunda = hoje - timedelta(days=hoje.weekday())
    sexta = segunda + timedelta(days=4)
    
    # Gerar dados para cada dia da semana
    dias_semana = []
    for i in range(5):  # Segunda a sexta
        dia_data = segunda + timedelta(days=i)
        dia_obj = Dias.objects.get(id=i+1)  # ID 1=Segunda, 2=Terça, etc.
        
        # Filtrar horários deste dia
        horarios_dia = [h for h in horarios if h.fk_dias.id == dia_obj.id]
        
        # Para cada horário, buscar evento correspondente
        linhas_dia = []
        for horario in horarios_dia:
            data_key = dia_data.strftime("%Y-%m-%d")
            evento = eventos_por_data_materia.get(data_key, {}).get(horario.fk_materia_id)
            
            linhas_dia.append({
                'horario': horario.fk_ordem.ordem,
                'disciplina': horario.fk_materia.nome_materia,
                'professor': horario.fk_professor.nome_professor,
                'conteudo': evento.title if evento else '',
                'dever': evento.dever if evento else '',
                'entrega': evento.data_entrega.strftime("%d/%m") if evento and evento.data_entrega else '',
                'livro': evento.fk_livro.nome_livro if evento and evento.fk_livro else ''
            })
        
        dias_semana.append({
            'data': dia_data,
            'nome_dia': dia_obj.dias,
            'linhas': linhas_dia
        })
    
    context = {
        'turma': turma,
        'dias_semana': dias_semana,
        'semana_range': f"{segunda:%d/%m} - {sexta:%d/%m}",
        'tem_dados': any(linhas for dia in dias_semana for linhas in dia['linhas'])
    }
    
    return render(request, 'semana/semana_completa.html', context)