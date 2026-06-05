import streamlit as st
from dataclasses import asdict
import matplotlib.pyplot as plt
import time

from modules.task import Task
import modules.schedulers as schedulers

st.set_page_config(layout="wide", page_title='Simulador de escalonamento', page_icon='📊')

if "tasks" not in st.session_state:
    st.session_state.tasks = []

st.title("Simulador de Escalonamento de CPU Multi-Algoritmos")

colu1, colu2 = st.columns(2)

# COLUNA 1: Cadastro das tarefas 
with colu1:
    proximo_id = len(st.session_state.tasks) + 1
    
    with st.form(key="form_cadastro", clear_on_submit=True):
        st.subheader("Cadastrar Novo Processo")
        col1, col2, col3 = st.columns([2, 2, 2])

        with col1:
            name = st.text_input("Nome", value=f"P{proximo_id}")
        with col2:
            burst_time = st.number_input("Burst Time (s)", min_value=1, max_value=30, value=2)
        with col3:
            priority_num = st.selectbox("Prioridade (0=Alta)", options=[2, 1, 0])

        botao_adicionar = st.form_submit_button("➕ Adicionar à Fila")

    if botao_adicionar:
        if name in [t.name for t in st.session_state.tasks]:
            st.error("Já existe um processo com esse nome!")
        else:
            # A cor temporária aqui será sobrescrita pela paleta TokyoNight no scheduler
            st.session_state.tasks.append(Task(name, priority_num, "#ffffff", burst_time))
            st.rerun()

    # Mostra as taks cadastradas e permite remover elas
    st.subheader("Fila de Prontos")
    if st.session_state.tasks:
        st.dataframe([asdict(t) for t in st.session_state.tasks], width='stretch',column_config={"color": None})

        if st.button("Limpar Todas as Tasks"):
            st.session_state.tasks = []
            st.rerun()

# ==========================================
# COLUNA 2: GRÁFICOS INDEPENDENTES POR ABA
# ==========================================
with colu2:
    # Inicializa os estados de controle da simulação infinita
    if "simulando" not in st.session_state:
        st.session_state.simulando = False
    if "tempo_infinito" not in st.session_state:
        st.session_state.tempo_infinito = 0

    # Botões de controle de fluxo
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("Iniciar Loop Infinito", type="primary", disabled=st.session_state.simulando):
            st.session_state.simulando = True
            st.session_state.tempo_infinito = 0
            st.rerun()
            
    with col_btn2:
        if st.button("Parar Simulação", type="secondary", disabled=not st.session_state.simulando):
            st.session_state.simulando = False
            st.rerun()

    ab1, ab2, ab3, ab4 = st.tabs(["FCFS", "SJF", "Prioridades", "Round Robin"])
    
    def criar_grafico(linha_tempo, limite_tempo):
        fig, ax = plt.subplots(figsize=(10, 4), facecolor="#1a1b26")
        ax.set_facecolor("#24283b")
        
        niveis_prioridade = [0, 1, 2]
        labels_prioridade = ["0 SO", "1", "2"]
        
        ax.set_yticks(niveis_prioridade)
        ax.set_yticklabels(labels_prioridade, fontsize=11, fontweight='bold', color="#a9b1d6")
        ax.invert_yaxis()
        
        ax.set_xlim(0, max(len(linha_tempo), 1))
        ax.set_ylim(2.5, -0.5)
        
        ax.set_xlabel("Tempo (segundos)", color="#a9b1d6", fontweight='bold')
        ax.set_ylabel("Prioridade", color="#a9b1d6", fontweight='bold')
        ax.tick_params(colors="#a9b1d6")
        
        for spine in ax.spines.values():
            spine.set_color("#414868")
            
        ax.grid(axis='x', linestyle='--', alpha=0.3, color="#565f89")

        # Plotando os blocos de tempo até o limite atual
        for t in range(limite_tempo):
            t_task = linha_tempo[t]
            y_prio = t_task.priority_num 
            
            ax.barh(y_prio, width=1, left=t, color=t_task.color, edgecolor='#1a1b26', height=0.5)
            ax.text(t + 0.5, y_prio, t_task.name, ha='center', va='center', 
                    color='#15161e', fontsize=10, fontweight='bold') 
        
        return fig

    # Função que gerencia o estado do gráfico dentro de sua própria aba
    def gerenciar_aba_grafico(aba_alvo, linha_tempo_algoritmo, modo_loop):
        with aba_alvo:
            if not linha_tempo_algoritmo:
                st.warning("Nenhum processo para simular nesta aba.")
                return

            total_tempo = len(linha_tempo_algoritmo)

            if modo_loop:
                # Calcula o segundo atual baseado no contador global e aplica o resto (%) para resetar no fim da fila
                segundo_atual = st.session_state.tempo_infinito % total_tempo
                task_ativa = linha_tempo_algoritmo[segundo_atual]
                
                st.markdown(f"**Tempo Atual:** `{segundo_atual + 1}s` de `{total_tempo}s` | Na CPU: **{task_ativa.name}**")
                
                fig = criar_grafico(linha_tempo_algoritmo, segundo_atual + 1)
                st.pyplot(fig)
                plt.close(fig)
            else:
                # Se não está rodando a animação, mostra o gráfico estático completo
                st.write("Visão geral do escalonamento:")
                fig = criar_grafico(linha_tempo_algoritmo, total_tempo)
                st.pyplot(fig)
                plt.close(fig)

    # Pré-calcula as linhas de tempo se houver tarefas cadastradas
    if st.session_state.tasks:
        linha_fcfs = schedulers.calcular_fcfs(st.session_state.tasks)
        linha_sjf = schedulers.calcular_sjf(st.session_state.tasks)
        linha_prioridades = schedulers.calcular_prioridades(st.session_state.tasks)
        linha_rr = schedulers.calcular_round_robin(st.session_state.tasks, quantum=2)
    else:
        linha_fcfs = linha_sjf = linha_prioridades = linha_rr = []

    # Executa a renderização das abas
    gerenciar_aba_grafico(ab1, linha_fcfs, modo_loop=st.session_state.simulando)
    gerenciar_aba_grafico(ab2, linha_sjf, modo_loop=st.session_state.simulando)
    gerenciar_aba_grafico(ab3, linha_prioridades, modo_loop=st.session_state.simulando)
    gerenciar_aba_grafico(ab4, linha_rr, modo_loop=st.session_state.simulando)

    # Motor do Loop Infinito
    # Se o estado simulando for True, incrementa o tempo, aguarda e força o rerun da página inteira
    if st.session_state.simulando and st.session_state.tasks:
        time.sleep(0.4)  # Velocidade da animação (segundos por frame)
        st.session_state.tempo_infinito += 1
        st.rerun()

    if st.session_state.simulando and not st.session_state.tasks:
        st.session_state.simulando = False
        st.warning("Adicione processos na fila antes de simular.")
    elif not st.session_state.tasks:
        st.info("Cadastre os processos acima para liberar os gráficos do simulador.")