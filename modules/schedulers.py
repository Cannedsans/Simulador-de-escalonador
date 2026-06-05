import copy
from typing import List

# Cores clássicas da paleta TokyoNight
TOKYONIGHT_COLORS = [
    "#7aa2f7",  # Azul
    "#bb9af7",  # Roxo
    "#7dcfff",  # Ciano claro
    "#e0af68",  # Amarelo/Laranja
    "#9ece6a",  # Verde
    "#f7768e",  # Rosa/Vermelho
    "#b4f9a8",  # Verde menta
    "#2ac3de"   # Ciano escuro
]

def atribuir_cores_tokyonight(tasks):
    """Atribui automaticamente uma cor da paleta TokyoNight para cada task."""
    for idx, task in enumerate(tasks):
        task.color = TOKYONIGHT_COLORS[idx % len(TOKYONIGHT_COLORS)]

def calcular_fcfs(tasks):
    linha = []
    tasks_copia = [copy.copy(t) for t in tasks]
    atribuir_cores_tokyonight(tasks_copia)
    for t in tasks_copia:
        linha.extend([t] * t.burst_time)
    return linha

def calcular_sjf(tasks):
    linha = []
    tasks_copia = [copy.copy(t) for t in tasks]
    atribuir_cores_tokyonight(tasks_copia)
    tasks_ordenadas = sorted(tasks_copia, key=lambda x: x.burst_time)
    for t in tasks_ordenadas:
        linha.extend([t] * t.burst_time)
    return linha

def calcular_prioridades(tasks, quantum=1):
    """
    Escalonamento por Prioridade Dinamico com Compartilhamento Justo.
    - Cada processo roda ate atingir o 'quantum' de tempo.
    - Evita inanicao: Apos rodar 2 tarefas de uma mesma prioridade, 
      o algoritmo prioriza alternar para outra prioridade que possua tarefas prontas.
    """
    linha = []
    tasks_copia = [copy.copy(t) for t in tasks]
    atribuir_cores_tokyonight(tasks_copia)
    
    # Inicializa o tempo restante para o controle da execucao
    for t in tasks_copia:
        t.tempo_restante = t.burst_time

    # Agrupa as tarefas em listas por prioridade
    filas_por_prioridade = {0: [], 1: [], 2: []}
    for t in tasks_copia:
        if t.priority_num in filas_por_prioridade:
            filas_por_prioridade[t.priority_num].append(t)

    # Contadores para rastrear quantas tarefas rodaram consecutivamente em cada prioridade
    tarefas_rodadas_por_prio = {0: 0, 1: 0, 2: 0}
    
    # Guarda qual foi a ultima prioridade executada
    ultima_prio_executada = None

    while any(t.tempo_restante > 0 for t in tasks_copia):
        
        # 1. Identifica quais prioridades possuem processos prontos para rodar
        prioridades_disponiveis = [
            prio for prio, tarefas in filas_por_prioridade.items() 
            if any(t.tempo_restante > 0 for t in tarefas)
        ]
        
        if not prioridades_disponiveis:
            break
            
        # 2. Aplicacao da Regra de Alternancia (Maximo 2 tarefas por prioridade)
        prio_escolhida = None
        
        # Se a ultima prioridade ja rodou 2 tarefas seguidas e existem OUTRAS prioridades com processos prontos:
        if (ultima_prio_executada is not None 
                and tarefas_rodadas_por_prio[ultima_prio_executada] >= 2 
                and len(prioridades_disponiveis) > 1):
            
            # Filtra as outras opcoes tirando a que ja estourou o limite de 2
            outras_prioridades = [p for p in prioridades_disponiveis if p != ultima_prio_executada]
            # Entre as outras, escolhe a de maior prioridade (menor numero)
            prio_escolhida = min(outras_prioridades)
            # Reseta o contador da prioridade antiga que foi pausada
            tarefas_rodadas_por_prio[ultima_prio_executada] = 0
        else:
            # Caso padrao: escolhe a prioridade mais alta (menor numero) disponivel
            prio_escolhida = min(prioridades_disponiveis)

        # 3. Pega a fila da prioridade que foi escolhida para rodar
        fila_atual = filas_por_prioridade[prio_escolhida]
        
        # Encontra a proxima tarefa valida (que tem tempo restante > 0) usando Round Robin interno
        t = fila_atual.pop(0)
        while t.tempo_restante == 0:
            fila_atual.append(t)
            t = fila_atual.pop(0)

        # 4. Define o tempo de execucao baseado no Quantum passado por parametro
        tempo_execucao = min(t.tempo_restante, quantum)
        
        # Aplica os blocos na linha do tempo
        for _ in range(tempo_execucao):
            linha.append(t)
            t.tempo_restante -= 1

        # 5. Atualiza os estados de controle do rodizio
        if ultima_prio_executada == prio_escolhida:
            tarefas_rodadas_por_prio[prio_escolhida] += 1
        else:
            # Se mudou de prioridade agora, conta como a primeira tarefa dessa nova prioridade
            tarefas_rodadas_por_prio[prio_escolhida] = 1
            if ultima_prio_executada is not None:
                # Reseta o contador da prioridade anterior que perdeu o turno
                tarefas_rodadas_por_prio[ultima_prio_executada] = 0
                
        ultima_prio_executada = prio_escolhida

        # Devolve a tarefa para o fim da sua respectiva fila para manter o Round Robin interno ativo
        fila_atual.append(t)

    return linha

def calcular_round_robin(tasks, quantum=2):
    linha = []
    tasks_copia = [copy.copy(t) for t in tasks]
    atribuir_cores_tokyonight(tasks_copia)
    for t in tasks_copia:
        t.tempo_restante = t.burst_time

    fila_rr = tasks_copia.copy()
    while fila_rr:
        t = fila_rr.pop(0)
        tempo_execucao = min(t.tempo_restante, quantum)
        for _ in range(tempo_execucao):
            linha.append(t)
            t.tempo_restante -= 1
        if t.tempo_restante > 0:
            fila_rr.append(t)
    return linha