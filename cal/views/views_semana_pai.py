from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import date, timedelta
from collections import defaultdict
from ..models import Alunos, Horarios, Event, Turma, Dias

@login_required
def semana_alunos(request):
    # Verificar se o usuário é um pai/responsável
    if request.user.tipo_usuario != 'pai':
        return render(request, 'semana/erro.html', {
            'mensagem': 'Acesso permitido apenas para pais/responsáveis.'
        })
    
    # Buscar todos os alunos vinculados a este pai/responsável
    alunos = Alunos.objects.filter(fk_user=request.user).select_related(
        'fk_turma', 'fk_escola'
    ).prefetch_related(
        'fk_turma__horarios_turma__fk_dias',
        'fk_turma__horarios_turma__fk_ordem',
        'fk_turma__horarios_turma__fk_professor',
        'fk_turma__horarios_turma__fk_materia',
        'fk_turma__dever_turma__fk_materia',
        'fk_turma__dever_turma__fk_professor',
        'fk_turma__dever_turma__fk_livro'
    )
    
    if not alunos.exists():
        return render(request, 'semana/semana_alunos.html', {
            'alunos': [],
            'mensagem': 'Nenhum aluno vinculado à sua conta.'
        })
    
    # Obter a semana a ser mostrada
    data_referencia_str = request.GET.get('data')
    if data_referencia_str:
        try:
            data_referencia = timezone.datetime.strptime(data_referencia_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            data_referencia = date.today()
    else:
        data_referencia = date.today()
    
    # Calcular segunda e sexta da semana de referência
    segunda = data_referencia - timedelta(days=data_referencia.weekday())
    sexta = segunda + timedelta(days=4)
    
    # Datas para navegação
    semana_anterior = segunda - timedelta(days=7)
    proxima_semana = segunda + timedelta(days=7)
    
    # Preparar dados de cada aluno
    alunos_com_semana = []
    
    for aluno in alunos:
        # Buscar todos os horários da turma do aluno
        horarios = Horarios.objects.filter(fk_turma=aluno.fk_turma).select_related(
            "fk_dias", "fk_ordem", "fk_professor", "fk_materia"
        ).order_by("fk_dias__id", "fk_ordem__id")
        
        # Buscar todos os eventos da turma do aluno
        eventos = Event.objects.filter(fk_turma=aluno.fk_turma).select_related(
            "fk_materia", "fk_professor", "fk_livro"
        )
        
        # Criar dicionário para rápido acesso aos eventos
        eventos_por_data_materia = defaultdict(dict)
        for evento in eventos:
            if evento.start_time:
                data_key = evento.start_time.strftime("%Y-%m-%d")
                eventos_por_data_materia[data_key][evento.fk_materia_id] = evento
            if evento.data_entrega:
                data_key = evento.data_entrega.strftime("%Y-%m-%d")
                eventos_por_data_materia[data_key][evento.fk_materia_id] = evento
        
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
        
        alunos_com_semana.append({
            'aluno': aluno,
            'dias_semana': dias_semana,
            'tem_dados': any(linhas for dia in dias_semana for linhas in dia['linhas'])
        })
    
    context = {
        'alunos': alunos_com_semana,
        'semana_range': f"{segunda:%d/%m} - {sexta:%d/%m}",
        'semana_anterior': semana_anterior.strftime('%Y-%m-%d'),
        'proxima_semana': proxima_semana.strftime('%Y-%m-%d'),
        'data_atual': data_referencia.strftime('%Y-%m-%d'),
        'hoje': date.today().strftime('%Y-%m-%d')
    }
    
    return render(request, 'semana/semana_alunos.html', context)