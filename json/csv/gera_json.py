import csv
import json
import re
from collections import OrderedDict

# Carregar fixtures para mapeamento
with open('cal_fixtures.json', 'r', encoding='utf-8') as f:
    fixtures = json.load(f)

# Criar dicionários de mapeamento
turma_map = {item['fields']['turma']: item['pk'] for item in fixtures if item['model'] == 'cal.Turma'}
dias_map = {item['fields']['dias']: item['pk'] for item in fixtures if item['model'] == 'cal.dias'}
ordem_map = {item['fields']['ordem']: item['pk'] for item in fixtures if item['model'] == 'cal.ordem'}
materia_map = {item['fields']['nome_materia']: item['pk'] for item in fixtures if item['model'] == 'cal.materia'}

# Mapeamento de professores (nome + matéria para evitar conflitos)
professor_map = {}
for item in fixtures:
    if item['model'] == 'cal.professor':
        prof_name = item['fields']['nome_professor']
        materia_id = item['fields']['fk_materia']
        professor_map[(prof_name, materia_id)] = item['pk']

# Função para detectar codificação
def detect_encoding(filename):
    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'windows-1252']
    for encoding in encodings:
        try:
            with open(filename, 'r', encoding=encoding) as f:
                f.read()
            return encoding
        except UnicodeDecodeError:
            continue
    return 'utf-8'  # fallback

# Função para limpar e padronizar nomes
def clean_name(name):
    if not name:
        return None
    name = name.strip()
    # Corrigir nomes conhecidos
    name = name.replace('ẃ', 'ó').replace('ş', 'º').replace('Bilogia', 'Biologia')
    name = name.replace('Inca', 'Ianca').replace('Elvia', 'Elvis')
    name = name.replace('Yasmim', 'Yasmin').replace('Nildo', 'Nildo')
    # Remover caracteres especiais problemáticos
    name = re.sub(r'[^\w\sÀ-ÿ]', '', name)
    return name.title()

# Função para processar um arquivo CSV
def process_csv_file(filename):
    encoding = detect_encoding(filename)
    
    with open(filename, 'r', encoding=encoding) as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    # Encontrar a turma
    turma_line = None
    for i, row in enumerate(rows):
        for cell in row:
            if cell and 'TURMA' in cell.upper():
                turma_line = i
                break
        if turma_line is not None:
            break
    
    if turma_line is None:
        print(f"  Turma não encontrada em {filename}")
        return []
    
    # Extrair nome da turma
    turma_text = rows[turma_line][0].strip()
    turma_match = re.search(r'TURMA\s*[-:]?\s*(.+)', turma_text, re.IGNORECASE)
    if turma_match:
        turma_name = turma_match.group(1).strip()
    else:
        turma_name = turma_text.replace('TURMA', '').replace('-', '').strip()
    
    turma_id = turma_map.get(turma_name)
    if not turma_id:
        print(f"  Turma não mapeada: '{turma_name}'")
        return []
    
    print(f"  Processando turma: {turma_name} (ID: {turma_id})")
    
    # Encontrar dias da semana
    results = []
    pk_counter = 300  # Começar de um número alto para evitar conflitos
    
    for i, row in enumerate(rows):
        for cell in row:
            if cell and 'FEIRA' in cell.upper() and '/' in cell:
                # Encontrar o dia da semana
                dia_text = cell.strip()
                dia_match = re.search(r'([A-ZÇ]+-FEIRA)', dia_text, re.IGNORECASE)
                if dia_match:
                    dia_name = dia_match.group(1).upper()
                    dia_id = dias_map.get(dia_name)
                    
                    if not dia_id:
                        print(f"  Dia não encontrado: {dia_name}")
                        continue
                    
                    # Próximas linhas contêm os horários
                    header_found = False
                    header_row = None
                    for j in range(i+1, min(i+10, len(rows))):
                        if any('HORÁRIO' in cell.upper() for cell in rows[j]) and any('DISCIPLINA' in cell.upper() for cell in rows[j]):
                            header_found = True
                            header_row = j
                            break
                    
                    if not header_found:
                        continue
                    
                    # Processar as linhas de horários
                    for k in range(header_row+1, len(rows)):
                        if not any(rows[k]):  # Linha vazia
                            continue
                        
                        if any('FEIRA' in cell.upper() for cell in rows[k]):  # Novo dia encontrado
                            break
                        
                        # Extrair dados da linha
                        horario = rows[k][0].strip() if len(rows[k]) > 0 and rows[k][0] else ''
                        disciplina = rows[k][1].strip() if len(rows[k]) > 1 and rows[k][1] else ''
                        professor = rows[k][2].strip() if len(rows[k]) > 2 and rows[k][2] else ''
                        conteudo = rows[k][3].strip() if len(rows[k]) > 3 and rows[k][3] else ''
                        atividade = rows[k][4].strip() if len(rows[k]) > 4 and rows[k][4] else ''
                        entrega = rows[k][5].strip() if len(rows[k]) > 5 and rows[k][5] else ''
                        
                        # Pular linhas inválidas
                        if not horario or not disciplina or 'HORÁRIO' in horario.upper():
                            continue
                        
                        # Mapear valores
                        ordem_id = ordem_map.get(horario)
                        materia_id = materia_map.get(disciplina)
                        
                        if not ordem_id:
                            print(f"    Horário não mapeado: '{horario}'")
                            continue
                        if not materia_id:
                            print(f"    Matéria não mapeada: '{disciplina}'")
                            continue
                        
                        # Encontrar professor_id
                        professor_clean = clean_name(professor)
                        professor_id = None
                        
                        if professor_clean and materia_id:
                            # Primeira tentativa: buscar por nome e matéria
                            professor_id = professor_map.get((professor_clean, materia_id))
                            
                            # Segunda tentativa: buscar apenas por nome
                            if not professor_id:
                                for (prof_name, mat_id), prof_id in professor_map.items():
                                    if prof_name == professor_clean:
                                        professor_id = prof_id
                                        break
                        
                        if not professor_id:
                            print(f"    Professor não encontrado: '{professor}' -> '{professor_clean}' para matéria {disciplina}")
                            professor_id = None
                        
                        # Criar entrada
                        entry = OrderedDict([
                            ("model", "cal.Horarios"),
                            ("pk", pk_counter),
                            ("fields", OrderedDict([
                                ("fk_escola", 1),
                                ("fk_turma", turma_id),
                                # ("fk_dias", dia_id),
                                ("fk_ordem", ordem_id),
                                ("fk_materia", materia_id),
                                ("fk_professor", professor_id),
                                # ("conteudo_ministrado", conteudo),
                                # ("atividade_casa", atividade),
                                # ("data_entrega", entrega)
                            ]))
                        ])
                        
                        results.append(entry)
                        pk_counter += 1
    
    print(f"  {len(results)} horários processados para {turma_name}")
    return results

# Processar todos os arquivos CSV
csv_files = ['8b.csv', '9a.csv', '9b.csv', '1a.csv', '2a.csv', '2b.csv', '3a.csv', '6a.csv', '7a.csv', '7b.csv', '8a.csv']

all_results = []
for csv_file in csv_files:
    print(f"Processando {csv_file}...")
    try:
        results = process_csv_file(csv_file)
        all_results.extend(results)
    except Exception as e:
        print(f"  Erro ao processar {csv_file}: {e}")

# Salvar resultados em um arquivo JSON
with open('horarios_completos.json', 'w', encoding='utf-8') as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)

print(f"Conversão concluída! {len(all_results)} registros salvos em 'horarios_completos.json'")