import csv
import json
import os
import glob

# -- CONFIGURAÇÃO --
# Diretório onde estão os arquivos CSV e os 'cal_*.json'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Dicionário para corrigir nomes inconsistentes encontrados nos CSVs
CORRECOES_NOMES = {
    # Materias
    'bilogia': 'biologia',
    'ed. fisica': 'ed. física',
    'ed. física': 'ed. física',
    'ens. religioso': 'ens. religioso',
    'tec. integradas': 'tec. integradas',
    
    # Professores
    'inca': 'ianca',
    'thais': 'thaís',
    'yasmin-123': 'yasmin',
    'stéphanie': 'stéphanie'
}

def carregar_json(nome_arquivo):
    """Carrega um arquivo JSON do diretório base."""
    caminho_completo = os.path.join(BASE_DIR, nome_arquivo)
    with open(caminho_completo, 'r', encoding='utf-8') as f:
        return json.load(f)

def normalizar_texto(texto):
    """Limpa, converte para minúsculas, padroniza ordinais e aplica correções."""
    if not texto:
        return ""
    # Substitui o sinal de grau '°' pelo indicador ordinal masculino 'º' para consistência
    texto_limpo = texto.strip().lower().replace('°', 'º').replace('\n', ' ')
    return CORRECOES_NOMES.get(texto_limpo, texto_limpo)

def processar_csv(arquivo_csv, turma_map, dias_map, ordem_map, materia_map, professor_map, pk_inicial):
    """Processa um único arquivo CSV e retorna a lista de horários."""
    print(f"\n--- Processando {os.path.basename(arquivo_csv)} ---")
    
    # Extrai o nome da turma do nome do arquivo (ex: 9b.csv -> 9°B)
    nome_arquivo_base = os.path.basename(arquivo_csv)
    nome_turma_formatado = nome_arquivo_base.replace('.csv', '').upper()
    if len(nome_turma_formatado) == 2 and nome_turma_formatado[0].isdigit():
        nome_turma_formatado = f"{nome_turma_formatado[0]}°{nome_turma_formatado[1]}"

    turma_id = turma_map.get(normalizar_texto(nome_turma_formatado))
    if not turma_id:
        print(f"AVISO: Turma '{nome_turma_formatado}' não encontrada. Pulando arquivo.")
        return []

    horarios_encontrados = []
    pk_atual = pk_inicial
    dia_atual_id = None

    with open(arquivo_csv, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        cabecalho_encontrado = False
        
        for linha in reader:
            if not any(celula.strip() for celula in linha):
                continue

            texto_linha_normalizado = normalizar_texto(' '.join(linha))
            
            # Encontra o dia da semana
            if 'feira' in texto_linha_normalizado:
                dia_encontrado = False
                for dia_nome, dia_id in dias_map.items():
                    if dia_nome in texto_linha_normalizado:
                        dia_atual_id = dia_id
                        print(f"Dia alterado para: {dia_nome.title()}")
                        cabecalho_encontrado = False # Reseta o cabeçalho para o novo dia
                        dia_encontrado = True
                        break
                if dia_encontrado:
                    continue

            # Encontra o cabeçalho da tabela de horários
            if 'horário' in texto_linha_normalizado and 'disciplina' in texto_linha_normalizado:
                cabecalho_encontrado = True
                print("Cabeçalho da tabela encontrado.")
                continue

            # Processa as linhas de dados se um dia e um cabeçalho foram encontrados
            if dia_atual_id and cabecalho_encontrado and len(linha) >= 3:
                ordem_str = normalizar_texto(linha[0])
                materia_str = normalizar_texto(linha[1])
                professor_str = normalizar_texto(linha[2])

                if not all([ordem_str, materia_str]): # Professor pode estar vazio
                    continue

                # Busca os IDs correspondentes
                ordem_id = ordem_map.get(ordem_str)
                materia_id = materia_map.get(materia_str)
                # Se professor_str for vazio, o map buscará a chave '' que definimos no main()
                professor_id = professor_map.get(professor_str)
                
                if all([ordem_id, materia_id, professor_id]):
                    horario_entry = {
                        "model": "cal.Horarios",
                        "pk": pk_atual,
                        "fields": {
                            "fk_dias": dia_atual_id,
                            "fk_ordem": ordem_id,
                            "fk_escola": 1, # ID fixo da escola
                            "fk_turma": turma_id,
                            "fk_professor": professor_id,
                            "fk_materia": materia_id
                        }
                    }
                    horarios_encontrados.append(horario_entry)
                    pk_atual += 1
                else:
                    print(f"  [FALHA] Não foi possível mapear: Ordem='{linha[0]}', Matéria='{linha[1]}', Prof='{linha[2]}'")
                    if not ordem_id: print(f"    - Ordem '{ordem_str}' não encontrada.")
                    if not materia_id: print(f"    - Matéria '{materia_str}' não encontrada.")
                    if not professor_id: print(f"    - Professor '{professor_str}' não encontrado.")

    print(f"--> {len(horarios_encontrados)} horários válidos encontrados em {os.path.basename(arquivo_csv)}.")
    return horarios_encontrados

def main():
    """Função principal para orquestrar o processo."""
    print("1. Carregando arquivos JSON de referência...")
    
    # Carregando dados
    dias_data = carregar_json('cal_dias.json')
    ordem_data = carregar_json('cal_ordem.json')
    materia_data = carregar_json('cal_materia.json')
    professor_data = carregar_json('cal_professor.json')
    turma_data = carregar_json('cal_turma.json')

    # Criando dicionários de mapeamento (maps) para busca rápida
    dias_map = {normalizar_texto(d['dias']): d['id'] for d in dias_data}
    ordem_map = {normalizar_texto(o['ordem']): o['id'] for o in ordem_data}
    materia_map = {normalizar_texto(m['nome_materia']): m['id'] for m in materia_data}
    professor_map = {normalizar_texto(p['nome_professor']): p['id'] for p in professor_data}
    turma_map = {normalizar_texto(t['turma']): t['id'] for t in turma_data}
    
    # Adicionar mapeamento especial para Projeto de Vida sem professor fixo
    # Supondo que "Projeto de Vida" como professor tem ID 26 no arquivo de professores
    if 'projeto de vida' in professor_map:
        professor_map[''] = professor_map['projeto de vida']
    
    print("2. Encontrando arquivos CSV para processar...")
    arquivos_csv = glob.glob(os.path.join(BASE_DIR, "*.csv"))
    
    if not arquivos_csv:
        print("Nenhum arquivo .csv encontrado no diretório.")
        return

    print(f"   Encontrados: {[os.path.basename(f) for f in sorted(arquivos_csv)]}")

    todos_os_horarios = []
    pk_contador = 1
    
    print("\n3. Iniciando processamento dos arquivos...")
    for arquivo in sorted(arquivos_csv):
        horarios_do_arquivo = processar_csv(
            arquivo, turma_map, dias_map, ordem_map, materia_map, professor_map, pk_inicial=pk_contador
        )
        if horarios_do_arquivo:
            todos_os_horarios.extend(horarios_do_arquivo)
            pk_contador = todos_os_horarios[-1]['pk'] + 1 if todos_os_horarios else 1

    if not todos_os_horarios:
        print("\nNenhum horário válido foi gerado a partir dos arquivos CSV.")
        return

    # Salvar o resultado unificado
    caminho_saida = os.path.join(BASE_DIR, 'horarios_geral.json')
    with open(caminho_saida, 'w', encoding='utf-8') as f:
        json.dump(todos_os_horarios, f, indent=2, ensure_ascii=False)

    print(f"\n==================================================")
    print(f"✅ Processo concluído com sucesso!")
    print(f"Total de {len(todos_os_horarios)} horários foram salvos em '{caminho_saida}'")
    print(f"==================================================")

if __name__ == "__main__":
    main()

#tteste
