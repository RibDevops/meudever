import csv
import json
import re
from collections import OrderedDict

# Carregar fixtures para mapeamento
with open('cal_fixtures.json', 'r', encoding='utf-8') as f:
    fixtures = json.load(f)

# Carregar o arquivo horarios.json existente
with open('horarios.json', 'r', encoding='utf-8') as f:
    horarios_existentes = json.load(f)

# Criar dicionários de mapeamento
turma_map = {item['fields']['turma']: item['pk'] for item in fixtures if item['model'] == 'cal.Turma'}
dias_map = {item['fields']['dias']: item['pk'] for item in fixtures if item['model'] == 'cal.dias'}
ordem_map = {item['fields']['ordem']: item['pk'] for item in fixtures if item['model'] == 'cal.ordem'}
materia_map = {item['fields']['nome_materia']: item['pk'] for item in fixtures if item['model'] == 'cal.materia'}

# Mapeamento de professores
professor_map = {}
for item in fixtures:
    if item['model'] == 'cal.professor':
        prof_name = item['fields']['nome_professor']
        materia_id = item['fields']['fk_materia']
        professor_id = item['pk']
        professor_map[(prof_name, materia_id)] = professor_id
        # Também mapear apenas por nome para fallback
        professor_map[prof_name] = professor_id

# Função para limpar nomes
def clean_name(name):
    if not name or name == '***':
        return None
    
    name = name.strip()
    # Correções comuns
    corrections = {
        'ẃ': 'ó', 'ş': 'º', 'Bilogia': 'Biologia', 'Inca': 'Ianca',
        'Elvia': 'Elvis', 'Yasmim': 'Yasmin', 'Nara': 'Nara',
        'Thais': 'Thaís', 'Cida': 'Cida', 'Andreia': 'Andreia',
        'Breno': 'Breno', 'Bruno': 'Bruno', 'Viviane': 'Viviane',
        'Angel': 'Angel', 'Stéphanie': 'Stéphanie', 'Marília': 'Marília',
        'Phylipe': 'Phylipe', 'Rafael': 'Rafael', 'Reinaldo': 'Reinaldo',
        'Hamilton': 'Hamilton', 'Pablo': 'Pablo', 'Nildo': 'Nildo',
        'Leonardo': 'Leonardo', 'Lucas': 'Lucas', 'Yasmin': 'Yasmin',
        'Guilherme': 'Guilherme', 'Ianca': 'Ianca'
    }
    
    for wrong, right in corrections.items():
        name = name.replace(wrong, right)
    
    return name.title()

# Função para encontrar professor_id
def find_professor_id(professor_name, materia_nome):
    if not professor_name or professor_name == '***':
        return None
    
    clean_prof = clean_name(professor_name)
    materia_id = materia_map.get(materia_nome)
    
    # Primeiro tentar encontrar por nome e matéria
    if materia_id and (clean_prof, materia_id) in professor_map:
        return professor_map[(clean_prof, materia_id)]
    
    # Depois tentar apenas por nome
    if clean_prof in professor_map:
        return professor_map[clean_prof]
    
    # Fallback: procurar por nome similar
    for (prof_name, mat_id), prof_id in professor_map.items():
        if isinstance(prof_name, str) and clean_prof in prof_name:
            return prof_id
    
    return None

# Função para processar CSV
def process_csv_file(filename):
    try:
        # Tentar diferentes codificações
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'windows-1252']
        rows = []
        
        for encoding in encodings:
            try:
                with open(filename, 'r', encoding=encoding) as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                break
            except UnicodeDecodeError:
                continue
        
        # Encontrar turma
        turma_name = None
        for row in rows:
            for cell in row:
                if cell and 'TURMA' in cell.upper():
                    turma_match = re.search(r'TURMA\s*[-:]?\s*(.+)', cell, re.IGNORECASE)
                    if turma_match:
                        turma_name = turma_match.group(1).strip()
                        break
            if turma_name:
                break
        
        if not turma_name:
            return []
        
        turma_id = turma_map.get(turma_name)
        if not turma_id:
            return []
        
        results = []
        current_dia = None
        current_dia_id = None
        
        for i, row in enumerate(rows):
            # Verificar se é linha de dia da semana
            for cell in row:
                if cell and 'FEIRA' in cell.upper() and '/' in cell:
                    dia_match = re.search(r'([A-ZÇ]+-FEIRA)', cell, re.IGNORECASE)
                    if dia_match:
                        current_dia = dia_match.group(1).upper()
                        current_dia_id = dias_map.get(current_dia)
                    break
            
            # Verificar se é linha de cabeçalho
            if any('HORÁRIO' in cell.upper() for cell in row) and any('DISCIPLINA' in cell.upper() for cell in row):
                # Processar as próximas linhas até encontrar outro cabeçalho ou dia
                for j in range(i + 1, len(rows)):
                    data_row = rows[j]
                    
                    # Parar se encontrar novo dia ou cabeçalho
                    if not any(data_row) or any('FEIRA' in cell.upper() for cell in data_row if cell):
                        break
                    
                    if any('HORÁRIO' in cell.upper() for cell in data_row if cell):
                        break
                    
                    # Extrair dados
                    horario = data_row[0].strip() if len(data_row) > 0 and data_row[0] else ''
                    disciplina = data_row[1].strip() if len(data_row) > 1 and data_row[1] else ''
                    professor = data_row[2].strip() if len(data_row) > 2 and data_row[2] else ''
                    conteudo = data_row[3].strip() if len(data_row) > 3 and data_row[3] else ''
                    atividade = data_row[4].strip() if len(data_row) > 4 and data_row[4] else ''
                    entrega = data_row[5].strip() if len(data_row) > 5 and data_row[5] else ''
                    
                    # Pular linhas inválidas
                    if not horario or not disciplina or 'HORÁRIO' in horario.upper():
                        continue
                    
                    # Mapear valores
                    ordem_id = ordem_map.get(horario)
                    materia_id = materia_map.get(disciplina)
                    
                    if not ordem_id or not materia_id or not current_dia_id:
                        continue
                    
                    professor_id = find_professor_id(professor, disciplina)
                    
                    # Criar entrada
                    entry = OrderedDict([
                        ("model", "cal.horarios"),
                        ("pk", len(results) + 1),  # Manter PK sequencial
                        ("fields", OrderedDict([
                            ("fk_escola", 1),
                            ("fk_turma", turma_id),
                            ("fk_dias", current_dia_id),
                            ("fk_ordem", ordem_id),
                            ("fk_materia", materia_id),
                            ("fk_professor", professor_id),
                            ("conteudo_ministrado", conteudo),
                            ("atividade_casa", atividade),
                            ("data_entrega", entrega)
                        ]))
                    ])
                    
                    results.append(entry)
        
        return results
        
    except Exception as e:
        print(f"Erro ao processar {filename}: {e}")
        return []

# Lista de arquivos CSV para processar
csv_files = [
    '6a.csv', '7a.csv', '7b.csv', '8a.csv', '8b.csv',
    '9a.csv', '9b.csv', '1a.csv', '2a.csv', '2b.csv', '3a.csv'
]

# Processar todos os CSVs
all_horarios = []
for csv_file in csv_files:
    print(f"Processando {csv_file}...")
    horarios = process_csv_file(csv_file)
    all_horarios.extend(horarios)
    print(f"  → {len(horarios)} horários extraídos")

# Atualizar o arquivo horarios.json
with open('horarios_corrigido.json', 'w', encoding='utf-8') as f:
    json.dump(all_horarios, f, ensure_ascii=False, indent=2, separators=(',', ': '))

print(f"\nConversão concluída! {len(all_horarios)} horários salvos em 'horarios_corrigido.json'")