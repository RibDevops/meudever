# views_semana.py
from asyncio import events
from datetime import date, timedelta
from collections import defaultdict
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from ..models import Horarios, Event, Turma, Dias


@login_required
def semana_turma_completa(request, turma_id):
    turma = get_object_or_404(Turma, pk=turma_id)
    
    # Obter a semana a ser mostrada (parâmetro opcional)
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
        'semana_anterior': semana_anterior.strftime('%Y-%m-%d'),
        'proxima_semana': proxima_semana.strftime('%Y-%m-%d'),
        'data_atual': data_referencia.strftime('%Y-%m-%d'),
        'hoje': date.today().strftime('%Y-%m-%d'),
        'tem_dados': any(linhas for dia in dias_semana for linhas in dia['linhas'])
    }
    
    return render(request, 'semana/semana_completa.html', context)


# views_semana.py - Adicione estas importações no topo
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from io import BytesIO
from datetime import datetime


# @login_required
# def gerar_pdf_todas_turmas(request):
#     # Buscar todas as turmas que têm horários registrados
#     from django.db.models import Exists, OuterRef
    
#     horarios_existem = Horarios.objects.filter(fk_turma=OuterRef('pk'))
#     turmas_com_horarios = Turma.objects.filter(
#         Exists(horarios_existem)
#     ).distinct().order_by('turma')
    
#     if not turmas_com_horarios:
#         return HttpResponse("Nenhuma turma com horários registrados encontrada.")
    
#     # Criar buffer para o PDF
#     buffer = BytesIO()
#     pdf = canvas.Canvas(buffer, pagesize=A4)  # Mudado para retrato (A4 normal)
    
#     # Configurações iniciais
#     width, height = A4
#     margin = 15 * mm
#     y_position = height - margin
#     line_height = 5 * mm
    
#     # Estilos
#     styles = getSampleStyleSheet()
#     title_style = ParagraphStyle(
#         'CustomTitle',
#         parent=styles['Title'],
#         fontSize=14,
#         spaceAfter=12,
#         alignment=1  # Centro
#     )
    
#     subtitle_style = ParagraphStyle(
#         'CustomSubtitle',
#         parent=styles['Heading2'],
#         fontSize=12,
#         spaceAfter=8,
#         alignment=1
#     )
    
#     normal_style = ParagraphStyle(
#         'CustomNormal',
#         parent=styles['Normal'],
#         fontSize=8,
#         alignment=0  # Justificado
#     )
    
#     table_header_style = ParagraphStyle(
#         'TableHeader',
#         parent=styles['Normal'],
#         fontSize=7,
#         alignment=1,  # Centro
#         textColor=colors.white,
#         fontName='Helvetica-Bold'
#     )
    
#     table_cell_style = ParagraphStyle(
#         'TableCell',
#         parent=styles['Normal'],
#         fontSize=6,
#         alignment=1,  # Centro
#         leading=8  # Espaçamento entre linhas
#     )
    
#     # Para cada turma, gerar a semana
#     for turma in turmas_com_horarios:
#         # Nova página para cada turma
#         if y_position < margin + 150:  # Verificar espaço para próxima turma
#             pdf.showPage()
#             y_position = height - margin
        
#         # Título principal
#         title = Paragraph("Controle de Conteúdos e Atividades", title_style)
#         title.wrapOn(pdf, width - 2 * margin, height)
#         title.drawOn(pdf, margin, y_position)
#         y_position -= 15 * mm
        
#         # Nome da escola e turma
#         escola_nome = turma.fk_escola.nome_escola if hasattr(turma, 'fk_escola') and turma.fk_escola else "COLÉGIO"
#         turma_info = Paragraph(f"{escola_nome} - {turma.turma}", subtitle_style)
#         turma_info.wrapOn(pdf, width - 2 * margin, height)
#         turma_info.drawOn(pdf, margin, y_position)
#         y_position -= 10 * mm
        
#         # Buscar dados da semana atual para a turma
#         data_referencia = date.today()
#         segunda = data_referencia - timedelta(days=data_referencia.weekday())
#         sexta = segunda + timedelta(days=4)
        
#         # Navegação de semanas
#         semana_anterior = segunda - timedelta(days=7)
#         proxima_semana = segunda + timedelta(days=7)
        
#         semana_texto = Paragraph(f"<b>Semana:</b> {segunda.strftime('%d/%m')} - {sexta.strftime('%d/%m')}", normal_style)
#         semana_texto.wrapOn(pdf, width - 2 * margin, height)
#         semana_texto.drawOn(pdf, margin, y_position)
#         y_position -= 8 * mm
        
#         # Linha divisória
#         pdf.line(margin, y_position, width - margin, y_position)
#         y_position -= 5 * mm
        
#         # Buscar horários da turma
#         horarios = Horarios.objects.filter(fk_turma=turma).select_related(
#             "fk_dias", "fk_ordem", "fk_professor", "fk_materia"
#         ).order_by("fk_dias__id", "fk_ordem__id")
        
#         # Buscar eventos da turma para a semana atual
#         eventos = Event.objects.filter(
#             fk_turma=turma,
#             start_time__gte=segunda,
#             start_time__lte=segunda + timedelta(days=6)
#         ).select_related("fk_materia", "fk_professor", "fk_livro")
        
#         # Criar dicionário para eventos
#         eventos_por_data_materia = defaultdict(dict)
#         for evento in eventos:
#             if evento.start_time:
#                 data_key = evento.start_time.strftime("%Y-%m-%d")
#                 eventos_por_data_materia[data_key][evento.fk_materia_id] = evento
        
#         # Gerar dados para cada dia da semana
#         for i in range(5):  # Segunda a sexta
#             dia_data = segunda + timedelta(days=i)
#             dia_obj = Dias.objects.get(id=i+1)
            
#             # Verificar espaço para novo dia
#             if y_position < margin + 100:
#                 pdf.showPage()
#                 y_position = height - margin
            
#             # Cabeçalho do dia
#             dia_header = Paragraph(f"<b>{dia_obj.dias} - {dia_data.strftime('%d/%m/%Y')}</b>", subtitle_style)
#             dia_header.wrapOn(pdf, width - 2 * margin, height)
#             dia_header.drawOn(pdf, margin, y_position)
#             y_position -= 8 * mm
            
#             # Filtrar horários deste dia
#             horarios_dia = [h for h in horarios if h.fk_dias.id == dia_obj.id]
            
#             if horarios_dia:
#                 # Criar tabela para o dia
#                 table_data = []
                
#                 # Cabeçalho da tabela
#                 header_row = [
#                     Paragraph('Horário', table_header_style),
#                     Paragraph('Disciplina', table_header_style),
#                     Paragraph('Professor', table_header_style),
#                     Paragraph('Conteúdo Ministrado', table_header_style),
#                     Paragraph('Dever', table_header_style),
#                     Paragraph('Data de Entrega', table_header_style),
#                     Paragraph('Livro', table_header_style)
#                 ]
#                 table_data.append(header_row)
                
#                 # Dados da tabela
#                 for horario in horarios_dia:
#                     data_key = dia_data.strftime("%Y-%m-%d")
#                     evento = eventos_por_data_materia.get(data_key, {}).get(horario.fk_materia_id)
                    
#                     row = [
#                         Paragraph(f"{horario.fk_ordem.ordem}º Horário", table_cell_style),
#                         Paragraph(horario.fk_materia.nome_materia, table_cell_style),
#                         Paragraph(horario.fk_professor.nome_professor, table_cell_style),
#                         Paragraph(evento.title if evento else "-", table_cell_style),
#                         Paragraph(evento.dever if evento else "-", table_cell_style),
#                         Paragraph(evento.data_entrega.strftime("%d/%m") if evento and evento.data_entrega else "-", table_cell_style),
#                         Paragraph(evento.fk_livro.nome_livro if evento and evento.fk_livro else "-", table_cell_style)
#                     ]
#                     table_data.append(row)
                
#                 # Criar tabela
#                 col_widths = [20*mm, 25*mm, 25*mm, 30*mm, 25*mm, 20*mm, 25*mm]
#                 table = Table(table_data, colWidths=col_widths, repeatRows=1)
                
#                 # Estilo da tabela
#                 table.setStyle(TableStyle([
#                     ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
#                     ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
#                     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                     ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                     ('FONTSIZE', (0, 0), (-1, 0), 7),
#                     ('FONTSIZE', (0, 1), (-1, -1), 6),
#                     ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
#                     ('BACKGROUND', (0, 1), (-1, -1), colors.white),
#                     ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                 ]))
                
#                 # Desenhar tabela
#                 table.wrapOn(pdf, width - 2 * margin, height)
#                 table_height = len(table_data) * 4 * mm
                
#                 if y_position - table_height < margin:
#                     pdf.showPage()
#                     y_position = height - margin
                
#                 table.drawOn(pdf, margin, y_position - table_height)
#                 y_position -= table_height + 8 * mm
#             else:
#                 # Se não há horários para este dia
#                 sem_dados = Paragraph("Nenhum horário registrado para este dia.", normal_style)
#                 sem_dados.wrapOn(pdf, width - 2 * margin, height)
#                 sem_dados.drawOn(pdf, margin, y_position)
#                 y_position -= 8 * mm
            
#             # Linha divisória entre dias
#             if i < 4:  # Não desenhar após o último dia
#                 pdf.line(margin, y_position, width - margin, y_position)
#                 y_position -= 5 * mm
        
#         # Espaço entre turmas
#         y_position -= 10 * mm
    
#     # Finalizar PDF
#     pdf.save()
    
#     # Configurar resposta
#     buffer.seek(0)
#     response = HttpResponse(buffer, content_type='application/pdf')
#     response['Content-Disposition'] = 'attachment; filename="relatorio_semanal_todas_turmas.pdf"'
    
#     return response









# Adicionar esta função no views_semana.py
@login_required
def semana_geral(request):
    # Buscar todas as turmas que têm horários registrados
    from django.db.models import Exists, OuterRef
    
    horarios_existem = Horarios.objects.filter(fk_turma=OuterRef('pk'))
    turmas_com_horarios = Turma.objects.filter(
        Exists(horarios_existem)
    ).distinct().order_by('turma')
    
    # Obter a semana a ser mostrada (parâmetro opcional)
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
    
    # Para cada turma, buscar dados da semana
    turmas_com_dados = []
    
    for turma in turmas_com_horarios:
        # Buscar todos os horários da turma
        horarios = Horarios.objects.filter(fk_turma=turma).select_related(
            "fk_dias", "fk_ordem", "fk_professor", "fk_materia"
        ).order_by("fk_dias__id", "fk_ordem__id")
        
        # Buscar todos os eventos da turma para a semana
        eventos = Event.objects.filter(
            fk_turma=turma,
            start_time__gte=segunda,
            start_time__lte=segunda + timedelta(days=6)
        ).select_related("fk_materia", "fk_professor", "fk_livro")
        
        # Criar dicionário para rápido acesso aos eventos por data e matéria
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
            dia_obj = Dias.objects.get(id=i+1)
            
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
        
        # Adicionar turma com dados à lista
        turmas_com_dados.append({
            'turma': turma,
            'dias_semana': dias_semana,
            'tem_dados': any(linhas for dia in dias_semana for linhas in dia['linhas'])
        })
    
    context = {
        'turmas_com_dados': turmas_com_dados,
        'semana_range': f"{segunda:%d/%m} - {sexta:%d/%m}",
        'semana_anterior': semana_anterior.strftime('%Y-%m-%d'),
        'proxima_semana': proxima_semana.strftime('%Y-%m-%d'),
        'data_atual': data_referencia.strftime('%Y-%m-%d'),
        'hoje': date.today().strftime('%Y-%m-%d'),
        'total_turmas': len(turmas_com_dados)
    }
    
    return render(request, 'semana/semana_geral.html', context)






















@login_required
def gerar_pdf_todas_turmas(request):
    from django.db.models import Exists, OuterRef
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from io import BytesIO
    from datetime import date, timedelta
    from collections import defaultdict
    from reportlab.pdfgen import canvas

    # Buscar todas as turmas que têm horários registrados
    horarios_existem = Horarios.objects.filter(fk_turma=OuterRef('pk'))
    turmas_com_horarios = Turma.objects.filter(
        Exists(horarios_existem)
    ).distinct().order_by('turma')
    
    if not turmas_com_horarios:
        return HttpResponse("Nenhuma turma com horários registrados encontrada.")
    
    # Criar buffer para o PDF
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    
    # Configurações iniciais
    width, height = A4
    margin = 15 * mm
    y_position = height - margin
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=14,
        spaceAfter=12,
        alignment=1
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=12,
        spaceAfter=8,
        alignment=1
    )
    
    day_header_style = ParagraphStyle(
        'DayHeader',
        parent=styles['Heading3'],
        fontSize=10,
        spaceAfter=5,
        alignment=0,
        fontName='Helvetica-Bold',
        textColor=colors.darkblue  # Cor para o cabeçalho do dia
    )
    
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontSize=7,
        alignment=1,
        textColor=colors.white,
        fontName='Helvetica-Bold'
    )
    
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontSize=6,
        alignment=1,
        leading=8
    )

    for turma in turmas_com_horarios:
        if y_position < margin + 150:
            pdf.showPage()
            y_position = height - margin
        
        # Título principal
        title = Paragraph("Controle de Conteúdos e Atividades", title_style)
        title.wrapOn(pdf, width - 2 * margin, height)
        title.drawOn(pdf, margin, y_position)
        y_position -= 15 * mm
        
        # Nome da escola e turma
        escola_nome = turma.fk_escola.nome_escola if hasattr(turma, 'fk_escola') and turma.fk_escola else "COLÉGIO PERPÉTUO SOCORRO"
        turma_info = Paragraph(f"{escola_nome} - {turma.turma}", subtitle_style)
        turma_info.wrapOn(pdf, width - 2 * margin, height)
        turma_info.drawOn(pdf, margin, y_position)
        y_position -= 10 * mm
        
        data_referencia = date.today()
        segunda = data_referencia - timedelta(days=data_referencia.weekday())
        sexta = segunda + timedelta(days=4)
        
        semana_texto = Paragraph(f"<b>Semana:</b> {segunda.strftime('%d/%m')} - {sexta.strftime('%d/%m')}", day_header_style)
        semana_texto.wrapOn(pdf, width - 2 * margin, height)
        semana_texto.drawOn(pdf, margin, y_position)
        y_position -= 8 * mm
        
        pdf.line(margin, y_position, width - margin, y_position)
        y_position -= 5 * mm
        
        horarios = Horarios.objects.filter(fk_turma=turma).select_related(
            "fk_dias", "fk_ordem", "fk_professor", "fk_materia"
        ).order_by("fk_dias__id", "fk_ordem__id")
        
        eventos = Event.objects.filter(
            fk_turma=turma,
            start_time__gte=segunda,
            start_time__lte=segunda + timedelta(days=6)
        ).select_related("fk_materia", "fk_professor", "fk_livro")
        
        eventos_por_data_materia = defaultdict(dict)
        for evento in eventos:
            if evento.start_time:
                data_key = evento.start_time.strftime("%Y-%m-%d")
                eventos_por_data_materia[data_key][evento.fk_materia_id] = evento
        
        for i in range(5):
            dia_data = segunda + timedelta(days=i)
            dia_obj = Dias.objects.get(id=i + 1)
            
            if y_position < margin + 100:
                pdf.showPage()
                y_position = height - margin
            
            # Cabeçalho do dia mais destacado
            dia_header = Paragraph(f"<b>{dia_obj.dias} - {dia_data.strftime('%d/%m/%Y')}</b>", day_header_style)
            dia_header.wrapOn(pdf, width - 2 * margin, height)
            dia_header.drawOn(pdf, margin, y_position)
            y_position -= 8 * mm
            
            horarios_dia = [h for h in horarios if h.fk_dias.id == dia_obj.id]
            
            if horarios_dia:
                table_data = []
                header_row = [
                    Paragraph('Horário', table_header_style),
                    Paragraph('Disciplina', table_header_style),
                    Paragraph('Professor', table_header_style),
                    Paragraph('Conteúdo Ministrado', table_header_style),
                    Paragraph('Dever', table_header_style),
                    Paragraph('Data de Entrega', table_header_style),
                    Paragraph('Livro', table_header_style)
                ]
                table_data.append(header_row)
                
                for horario in horarios_dia:
                    data_key = dia_data.strftime("%Y-%m-%d")
                    evento = eventos_por_data_materia.get(data_key, {}).get(horario.fk_materia_id)
                    
                    row = [
                        Paragraph(f"{horario.fk_ordem.ordem}º Horário", table_cell_style),
                        Paragraph(horario.fk_materia.nome_materia, table_cell_style),
                        Paragraph(horario.fk_professor.nome_professor, table_cell_style),
                        Paragraph(evento.title if evento else "-", table_cell_style),
                        Paragraph(evento.dever if evento else "-", table_cell_style),
                        Paragraph(evento.data_entrega.strftime("%d/%m") if evento and evento.data_entrega else "-", table_cell_style),
                        Paragraph(evento.fk_livro.nome_livro if evento and evento.fk_livro else "-", table_cell_style)
                    ]
                    table_data.append(row)
                
                col_widths = [20*mm, 25*mm, 25*mm, 30*mm, 25*mm, 20*mm, 25*mm]
                table = Table(table_data, colWidths=col_widths, repeatRows=1)
                
                # Estilo da tabela com cores
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.navy),  # Cor de fundo azul escuro
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 7),
                    ('FONTSIZE', (0, 1), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    # Alterna a cor das linhas
                    ('BACKGROUND', (0, 2), (-1, -1), colors.lightblue),
                ]))
                
                table.wrapOn(pdf, width - 2 * margin, height)
                table_height = table._height
                
                if y_position - table_height < margin:
                    pdf.showPage()
                    y_position = height - margin
                
                table.drawOn(pdf, margin, y_position - table_height)
                y_position -= table_height + 8 * mm
            else:
                sem_dados = Paragraph("Nenhum horário registrado para este dia.", table_cell_style)
                sem_dados.wrapOn(pdf, width - 2 * margin, height)
                sem_dados.drawOn(pdf, margin, y_position)
                y_position -= 8 * mm
            
            if i < 4:
                pdf.line(margin, y_position, width - margin, y_position)
                y_position -= 5 * mm
        
        y_position -= 10 * mm
    
    pdf.save()
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_semanal_todas_turmas.pdf"'
    
    return response