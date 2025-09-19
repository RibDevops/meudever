import csv
import json
import os
import glob

# Definir o diretório onde os arquivos estão localizados
BASE_DIR = '/home/suporte/dev/agendamento/json/csv/'

# Carregar os dados de referência
def carregar_json(nome_arquivo):
    caminho_completo = os.path.join(BASE_DIR, nome_arquivo)
    with open(caminho_completo, 'r', encoding='utf-8') as f:
        return json.load(f)

# Carregar todos os dados de referência
print("Carregando arquivos JSON...")
dias_data = carregar_json('cal_dias.json')
ordem_data = carregar_json('cal_ordem.json')
materia_data = carregar_json('cal_materia.json')
professor_data = carregar_json('cal_professor.json')
turma_data = carregar_json('cal_turma.json')
escola_data = carregar_json('cal_escola.json')

# Criar dicionários para busca rápida
dias_map = {dia['dias'].lower(): dia['id'] for dia in dias_data}
ordem_map = {ordem['ordem'].lower(): ordem['id'] for ordem in ordem_data}
materia_map = {materia['nome_materia'].lower(): materia['id'] for materia in materia_data}
professor_map = {prof['nome_professor'].lower(): prof['id'] for prof in professor_data}
turma_map = {turma['turma'].lower(): turma['id'] for turma in turma_data}

# A escola é fixa (id=1)
escola_id = 1

def processar_csv(arquivo_csv):
    print(f"\n=== Processando {arquivo_csv} ===")
    
    # Extrair o nome da turma do nome do arquivo (ex: 2a.csv -> 2°A)
    nome_arquivo = os.path.basename(arquivo_csv)
    nome_turma = nome_arquivo.replace('.csv', '').upper()
    
    # Formatar para o padrão (ex: 2A -> 2°A)
    if len(nome_turma) == 2:
        nome_turma = f"{nome_turma[0]}°{nome_turma[1]}"
    
    print(f"Procurando turma: {nome_turma}")
    
    # Obter o ID da turma
    turma_id = turma_map.get(nome_turma.lower())
    if not turma_id:
        print(f"ERRO: Turma {nome_turma} não encontrada no arquivo cal_turma.json")
        return []
    
    horarios = []
    dia_atual = None
    pk_counter = 1
    cabecalho_encontrado = False
    
    caminho_csv = os.path.join(BASE_DIR, arquivo_csv)
    with open(caminho_csv, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        for i, linha in enumerate(reader):
            # Pular linhas vazias
            if not any(linha):
                continue
                
            # Verificar se é um cabeçalho de dia
            if len(linha) == 1:
                linha_texto = linha[0].lower()
                for dia in dias_map.keys():
                    if dia in linha_texto:
                        dia_atual = dia
                        cabecalho_encontrado = False  # Resetar flag de cabeçalho
                        print(f"Encontrado dia: {dia_atual}")
                        break
                continue
                
            # Verificar se é o cabeçalho da tabela (apenas uma vez por dia)
            if not cabecalho_encontrado and linha and any('horário' in cell.lower() for cell in linha):
                cabecalho_encontrado = True
                print("Cabeçalho da tabela encontrado")
                continue
                
            # Processar linha de horário (apenas se já encontramos o cabeçalho)
            if cabecalho_encontrado and dia_atual and len(linha) >= 3:
                horario = linha[0].strip().lower()
                materia = linha[1].strip().lower()
                professor = linha[2].strip().lower()
                
                # Pular linhas vazias ou incompletas
                if not all([horario, materia, professor]):
                    continue
                
                print(f"Processando: Dia={dia_atual}, Horário={horario}, Matéria={materia}, Professor={professor}")
                
                # Obter IDs das referências
                dia_id = dias_map.get(dia_atual)
                ordem_id = ordem_map.get(horario)
                materia_id = materia_map.get(materia)
                professor_id = professor_map.get(professor)
                
                # Debug das buscas
                print(f"  Dia ID: {dia_id} (buscando: {dia_atual})")
                print(f"  Ordem ID: {ordem_id} (buscando: {horario})")
                print(f"  Matéria ID: {materia_id} (buscando: {materia})")
                print(f"  Professor ID: {professor_id} (buscando: {professor})")
                
                # Validar se todos os IDs foram encontrados
                if not all([dia_id, ordem_id, materia_id, professor_id]):
                    print(f"AVISO: Dados não encontrados para - Dia: {dia_atual}, Horário: {horario}, Matéria: {materia}, Professor: {professor}")
                    continue
                
                # Criar entrada de horário
                horario_entry = {
                    "model": "cal.Horarios",
                    "pk": pk_counter,
                    "fields": {
                        "fk_dias": dia_id,
                        "fk_ordem": ordem_id,
                        "fk_escola": escola_id,
                        "fk_turma": turma_id,
                        "fk_professor": professor_id,
                        "fk_materia": materia_id
                    }
                }
                
                horarios.append(horario_entry)
                pk_counter += 1
                print("Horário adicionado com sucesso!")
    
    return horarios

def main():
    # Encontrar todos os arquivos CSV no diretório
    padrao_csv = os.path.join(BASE_DIR, "*.csv")
    arquivos_csv = glob.glob(padrao_csv)
    
    if not arquivos_csv:
        print(f"Nenhum arquivo CSV encontrado em {BASE_DIR}.")
        return
    
    print(f"Arquivos CSV encontrados: {[os.path.basename(f) for f in arquivos_csv]}")
    
    # Processar cada arquivo CSV
    for arquivo_csv in arquivos_csv:
        nome_arquivo = os.path.basename(arquivo_csv)
        print(f"\n{'='*50}")
        print(f"Processando {nome_arquivo}...")
        horarios = processar_csv(nome_arquivo)
        
        if horarios:
            # Gerar nome do arquivo de saída
            nome_saida = arquivo_csv.replace('.csv', '.json')
            
            # Salvar como JSON
            with open(nome_saida, 'w', encoding='utf-8') as f:
                json.dump(horarios, f, indent=2, ensure_ascii=False)
            
            print(f"Arquivo {nome_saida} gerado com {len(horarios)} horários.")
        else:
            print(f"Nenhum horário válido encontrado em {nome_arquivo}.")

if __name__ == "__main__":
    main()