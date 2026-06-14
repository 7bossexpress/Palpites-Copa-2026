import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

# 1. CONFIGURAÇÃO VISUAL DA ARENA (TEMA PROFISSIONAL PREMIUM)
st.set_page_config(page_title="Copa de Palpites 2026", page_icon="🏆", layout="wide")

st.markdown('''
<style>
    .stApp { background-color: #0b132b; color: #f8f9fa; }
    .header-painel { display: flex; justify-content: space-between; align-items: center; padding: 15px; background-color: #1c2541; border-bottom: 3px solid #ffb703; border-radius: 5px; margin-bottom: 20px; }
    .logo-site { font-size: 1.8rem; font-weight: bold; color: #ffb703; font-family: 'Arial Black', sans-serif; }
    .card-noticia { background-color: #1c2541; padding: 20px; border-radius: 12px; border-left: 6px solid #ffb703; box-shadow: 0 4px 15px rgba(0,0,0,0.3); margin-bottom: 15px; }
    .card-jogos-lista { background-color: #1c2541; padding: 12px; border-radius: 10px; margin-bottom: 8px; border: 1px solid #3a506b; }
    .card-jogo-destaque { background-color: #1c2541; padding: 25px; border-radius: 15px; text-align: center; border: 2px solid #5bc0be; box-shadow: 0 8px 25px rgba(91,192,190,0.2); }
    .titulo-coluna { font-size: 1.3rem; font-weight: bold; color: #5bc0be; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 1px; }
    .badge-tempo { background-color: #e63946; color: white; padding: 3px 8px; border-radius: 5px; font-size: 0.8rem; font-weight: bold; }
    .badge-bloqueado { background-color: #6c757d; color: white; padding: 3px 8px; border-radius: 5px; font-size: 0.8rem; font-weight: bold; }
</style>
''', unsafe_allow_html=True)

# 2. SISTEMA DE BANCO DE DADOS (SQLite Avançado)
def conectar_banco():
    return sqlite3.connect('copa_premium.db', check_same_thread=False)

def inicializar_banco():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS usuarios (nome TEXT PRIMARY KEY)')
    cursor.execute('CREATE TABLE IF NOT EXISTS chat (id INTEGER PRIMARY KEY AUTOINCREMENT, usuario TEXT, mensagem TEXT, sticker TEXT)')
    cursor.execute('''CREATE TABLE IF NOT EXISTS resultados_reais (
                        jogo_id INTEGER PRIMARY KEY, 
                        time1 TEXT, bandeira1 TEXT, 
                        time2 TEXT, bandeira2 TEXT, 
                        gols1 INTEGER, gols2 INTEGER, 
                        horario TEXT, grupo TEXT, encerrado INTEGER DEFAULT 0)''')
    cursor.execute('CREATE TABLE IF NOT EXISTS palpites (usuario TEXT, jogo_id INTEGER, gols1 INTEGER, gols2 INTEGER, PRIMARY KEY(usuario, jogo_id))')
    
    # Gerando os dados reais e datas com horários simulados para controle de 10 minutos
    cursor.execute("SELECT COUNT(*) FROM resultados_reais")
    if cursor.fetchone()[0] == 0:
        jogos = [
            # Passados (Não aparecem para palpitar, servem para o ranking e últimos 4 jogos)
            (1, "Alemanha", "🇩🇪", "Japão", "🇯🇵", 2, 1, "2026-06-13 13:00", "Grupo E", 1),
            (2, "Inglaterra", "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "Irã", "🇮🇷", 6, 2, "2026-06-13 16:00", "Grupo B", 1),
            (3, "Catar", "🇶🇦", "Equador", "🇪🇨", 0, 2, "2026-06-13 19:00", "Grupo A", 1),
            (4, "Estados Unidos", "🇺🇸", "Gales", "🏴󠁧󠁢󠁷󠁬󠁳󠁿", 1, 1, "2026-06-13 22:00", "Grupo B", 1),
            # Jogos de Hoje (Liberados para palpitar até 10 min antes do horário)
            (5, "Brasil", "🇧🇷", "Marrocos", "🇲🇦", 0, 0, "2026-06-14 16:00", "Grupo A", 0),
            (6, "Espanha", "🇪🇸", "Costa Rica", "🇨🇷", 0, 0, "2026-06-14 19:00", "Grupo E", 0),
            # Próximos Jogos (Futuros)
            (7, "Argentina", "🇦🇷", "França", "🇫🇷", 0, 0, "2026-06-15 13:00", "Grupo C", 0),
            (8, "Bélgica", "🇧🇧", "Canadá", "🇨🇦", 0, 0, "2026-06-15 16:00", "Grupo F", 0),
            (9, "Suíça", "🇨🇭", "Camarões", "🇨🇲", 0, 0, "2026-06-16 10:00", "Grupo G", 0),
            (10, "Uruguai", "🇺🇾", "Coreia do Sul", "🇰🇷", 0, 0, "2026-06-16 13:00", "Grupo H", 0)
        ]
        cursor.executemany("INSERT INTO resultados_reais VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", jogos)
        conn.commit()
    conn.close()

inicializar_banco()

# 3. CONTROLE DE BLOQUEIO E ACESSO RESTRITO (NÃO DÁ PRA ALTERAR O NOME)
if "usuario_registrado" not in st.session_state:
    st.session_state.usuario_registrado = None

if st.session_state.usuario_registrado is None:
    st.markdown("<h1 style='text-align:center; color:#ffb703; margin-top:10%;'>🏆 COPA DE PALPITES 2026</h1>", unsafe_allow_html=True)
    st.write("<p style='text-align:center; font-size:1.2rem;'>Crie o seu perfil único para acessar a plataforma. Atenção: Seu nome não poderá ser alterado depois!</p>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        nome_input = st.text_input("Escolha seu Nome / Apelido de Jogador:", placeholder="Ex: Lucas_Hexa").strip()
        if st.button("Confirmar e Trancar Perfil 🔐", use_container_width=True):
            if nome_input:
                conn = conectar_banco()
                cursor = conn.cursor()
                try:
                    cursor.execute("INSERT INTO usuarios VALUES (?)", (nome_input,))
                    conn.commit()
                    st.session_state.usuario_registrado = nome_input
                    st.success(f"Perfil trancado com sucesso para: {nome_input}!")
                    st.rerun()
                except sqlite3.IntegrityError:
                    # Se o usuário já existir no banco, ele entra direto mantendo o histórico
                    st.session_state.usuario_registrado = nome_input
                    st.rerun()
                finally:
                    conn.close()
    st.stop()

usuario_atual = st.session_state.usuario_registrado

# 4. HEADER COM BOTÕES DO MENU PRINCIPAL (ESTILO DA IMAGEM DE REFERÊNCIA)
st.markdown(f'''
<div class="header-painel">
    <div class="logo-site">🏆 COPA DE PALPITES</div>
    <div style="font-weight:bold; color:#5bc0be;">👤 Jogador Trancado: {usuario_atual}</div>
</div>
''', unsafe_allow_html=True)

# Abas em formato de botões de navegação premium no topo
aba_selecionada = st.radio(
    "Navegação do Painel:",
    ["Dashboard Principal", "Tabela Palpites (Fazer Apostas)", "Tabela Copa & Grupos", "Chaveamento / Mata-Mata", "Resenha & Figurinhas", "Informações da Copa", "Notícias Completas"],
    horizontal=True
)

# 5. LÓGICA DO DASHBOARD PRINCIPAL (IGUAL À IMAGEM)
if aba_selecionada == "Dashboard Principal":
    
    # --- SISTEMA DO CARROSSEL DE NOTÍCIAS (5 MELHORES NOTÍCIAS) ---
    if "index_noticia" not in st.session_state:
        st.session_state.index_noticia = 0
        
    noticias = [
        {"titulo": "🚨 Brasil está pronto para a estreia!", "conteúdo": "A comissão técnica confirmou o time titular com três atacantes rápidos. A expectativa para o jogo de hoje contra o Marrocos é quebra de recorde de audiência mundial!"},
        {"titulo": "🏟️ Estádios Inteligentes operam com 100% de capacidade", "conteúdo": "O sistema de climatização avançado garantiu o conforto dos torcedores mesmo nas temperaturas mais elevadas da rodada de abertura."},
        {"titulo": "🧠 Dicas da Inteligência Artificial agitam as redes sociais", "conteúdo": "O algoritmo exclusivo do painel de palpites atingiu 85% de acerto nas tendências dos placares da primeira rodada oficial."},
        {"titulo": "🇫🇷 França chega com desfalque importante de última hora", "conteúdo": "O departamento médico francês confirmou uma leve lesão no treino matinal, deixando o atacante titular de fora do grande clássico contra a Argentina amanhã."},
        {"titulo": "🌍 Clima de festa toma conta dos arredores da Arena Principal", "conteúdo": "Milhares de torcedores de todos os continentes se reuniram promovendo um lindo show de culturas e união através do futebol de qualidade."}
    ]
    
    st.markdown("### 📰 Notícia do Dia")
    col_seta_esq, col_corpo, col_seta_dir = st.columns([1, 15, 1])
    
    with col_seta_esq:
        if st.button("◀", use_container_width=True):
            st.session_state.index_noticia = (st.session_state.index_noticia - 1) % len(noticias)
            st.rerun()
            
    with col_corpo:
        noticia_atual = noticias[st.session_state.index_noticia]
        st.markdown(f'''
        <div class="card-noticia">
            <h4>{noticia_atual['titulo']}</h4>
            <p>{noticia_atual['conteúdo']}</p>
            <small style="color:#5bc0be;">Notícia {st.session_state.index_noticia + 1} de 5 • Arraste para os lados pelas setas</small>
        </div>
        ''', unsafe_allow_html=True)
        
    with col_seta_dir:
        if st.button("▶", use_container_width=True):
            st.session_state.index_noticia = (st.session_state.index_noticia + 1) % len(noticias)
            st.rerun()

    st.write("---")
    
    # --- JOGOS: ÚLTIMOS 4, JOGOS DO DIA E PRÓXIMOS 4 ---
    conn = conectar_banco()
    cursor = conn.cursor()
    
    col_ultimos, col_do_dia, col_proximos = st.columns([1.2, 2, 1.2])
    
    # Coluna 1: Últimos 4 Jogos
    with col_ultimos:
        st.markdown('<div class="titulo-coluna">⏮️ Últimos 4 Jogos</div>', unsafe_allow_html=True)
        cursor.execute("SELECT time1, bandeira1, gols1, gols2, time2, bandeira2 FROM resultados_reais WHERE encerrado=1 ORDER BY horario DESC LIMIT 4")
        ultimos = cursor.fetchall()
        for j in ultimos:
            st.markdown(f'''
            <div class="card-jogos-lista">
                <b>{j[1]} {j[0]}</b> <span style="color:#ffb703; font-weight:bold;">{j[2]} x {j[3]}</span> <b>{j[4]} {j[5]}</b>
            </div>
            ''', unsafe_allow_html=True)
            
    # Coluna 2: Jogos do Dia (Destaque Interativo)
    with col_do_dia:
        st.markdown('<div class="titulo-coluna">⚽ Jogos de Hoje</div>', unsafe_allow_html=True)
        cursor.execute("SELECT jogo_id, time1, bandeira1, time2, bandeira2, horario, grupo FROM resultados_reais WHERE encerrado=0 AND horario LIKE '2026-06-14%'")
        jogos_hoje = cursor.fetchall()
        
        for j in jogos_hoje:
            j_id, t1, b1, t2, b2, hora_str, grupo = j
            hora_jogo = datetime.strptime(hora_str, "%Y-%m-%d %H:%M")
            # Agora estamos em: 2026-06-14 14:22:00
            agora = datetime(2026, 6, 14, 14, 22, 0)
            limite_edicao = hora_jogo - timedelta(minutes=10)
            
            tempo_restante_min = int((hora_jogo - agora).total_seconds() / 60)
            
            st.markdown(f'''
            <div class="card-jogo-destaque">
                <span style="color:#5bc0be; font-weight:bold; font-size:0.9rem;">{grupo}</span>
                <h2 style="margin: 15px 0;">{b1} {t1} vs {t2} {b2}</h2>
                <p>⏰ Horário: <b>{hora_jogo.strftime('%H:%M')}</b></p>
            </div>
            ''', unsafe_allow_html=True)
            
            # Botões de Ação para o Jogo do dia
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button(f"ℹ️ Informações: {t1} x {t2}", key=f"info_{j_id}"):
                    st.info(f"📍 **Estádio Nacional** | 🌦️ Clima: Perfeito 23°C | 🏟️ Status: Lotação Máxima Confirmada para as duas seleções!")
            with col_b2:
                if st.button(f"🤖 Dicas IA: {t1} x {t2}", key=f"ia_{j_id}"):
                    if t1 == "Brasil":
                        st.warning("🧠 **Análise Avançada da IA:** O Brasil tem 74% de probabilidade de vitória com base no retrospecto tático recente contra equipes norte-africanas. Recomendação de aposta: Vitória por 2 gols de diferença.")
                    else:
                        st.warning("🧠 **Análise Avançada da IA:** Jogo equilibrado taticamente no meio de campo. Tendência de poucos gols. Recomendação: Empate ou vitória magra por 1 gol.")
            st.write("---")

    # Coluna 3: Próximos 4 Jogos
    with col_proximos:
        st.markdown('<div class="titulo-coluna">⏭️ Próximos 4 Jogos</div>', unsafe_allow_html=True)
        cursor.execute("SELECT time1, bandeira1, time2, bandeira2, horario FROM resultados_reais WHERE horario > '2026-06-14 23:59' ORDER BY horario ASC LIMIT 4")
        proximos = cursor.fetchall()
        for j in proximos:
            data_formatada = datetime.strptime(j[4], "%Y-%m-%d %H:%M").strftime("%d/%m %H:%M")
            st.markdown(f'''
            <div class="card-jogos-lista">
                <b>{j[1]} {j[0]}</b> vs <b>{j[2]} {j[3]}</b><br>
                <small style="color:#ffb703;">📅 {data_formatada}</small>
            </div>
            ''', unsafe_allow_html=True)
            
    # --- TABELA DOS TIMES QUE VÃO JOGAR HOJE (DINÂMICA NO RODAPÉ) ---
    st.write("---")
    st.markdown("### 📊 Tabela Real Otimizada (Times que jogam Hoje)")
    st.write("Classificação automática do grupo dos times que estão em campo na rodada atual:")
    
    # Criando o dataframe do grupo de hoje para demonstração bonita e limpa
    tabela_grupo_a = {
        "Seleção": ["🇧🇷 Brasil", "🇪🇸 Espanha", "🇲🇦 Marrocos", "🇨🇷 Costa Rica"],
        "P": [3, 3, 0, 0], "J": [1, 1, 1, 1], "V": [1, 1, 0, 0], "SG": [2, 1, -2, -1]
    }
    st.table(pd.DataFrame(tabela_grupo_a).set_index("Seleção"))
    conn.close()

# 6. ABA DE PALPITES: OCULTA JOGOS PASSADOS E EXIGE CONTROLE DE 10 MINUTOS
elif aba_selected == "Tabela Palpites (Fazer Apostas)" or aba_selecionada == "Tabela Palpites (Fazer Apostas)":
    st.header("📋 Seus Palpites Oficiais")
    st.write("Aqui você joga os seus placares. Atenção: O sistema bloqueia os palpites exatamente **10 minutos antes** de o jogo começar!")
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Importante: Buscamos apenas jogos que ainda NÃO aconteceram (oculta os jogos passados!)
    cursor.execute("SELECT jogo_id, time1, bandeira1, time2, bandeira2, horario FROM resultados_reais WHERE encerrado=0 ORDER BY horario ASC")
    jogos_ativos = cursor.fetchall()
    
    # Data fixada do sistema: 2026-06-14 14:22:00
    agora = datetime(2026, 6, 14, 14, 22, 0)
    
    if jogos_ativos:
        with st.form("form_palpites_premium"):
            for jogo in jogos_ativos:
                j_id, t1, b1, t2, b2, hora_str = jogo
                hora_jogo = datetime.strptime(hora_str, "%Y-%m-%d %H:%M")
                
                # Regra dos 10 minutos
                pode_editar = (hora_jogo - agora).total_seconds() > 600
                tempo_restante_min = int((hora_jogo - agora).total_seconds() / 60)
                
                # Resgatar palpite anterior do jogador
                cursor.execute("SELECT gols1, gols2 FROM palpites WHERE usuario=? AND jogo_id=?", (usuario_atual, j_id))
                palp_antigo = cursor.fetchone()
                p1_val = palp_antigo[0] if palp_antigo else 0
                p2_val = palp_antigo[1] if palp_antigo else 0
                
                st.markdown(f"##### {b1} {t1} x {t2} {b2}")
                
                if pode_editar:
                    st.markdown(f'<span class="badge-tempo">⏳ Aberto para palpites! Restam {tempo_restante_min} minutos</span>', unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    with c1:
                        st.number_input(f"Placar {t1}", min_value=0, value=p1_val, key=f"p1_{j_id}")
                    with c2:
                        st.number_input(f"Placar {t2}", min_value=0, value=p2_val, key=f"p2_{j_id}")
                else:
                    st.markdown('<span class="badge-bloqueado">🔒 Bloqueado! Menos de 10 minutos para o início do jogo</span>', unsafe_allow_html=True)
                    st.write(f"Seu palpite final gravado foi: **{p1_val} x {p2_val}**")
                    # Preserva os valores em campos invisíveis
                    st.hidden = st.text_input("", value=str(p1_val), key=f"p1_{j_id}", label_visibility="collapsed")
                    st.hidden2 = st.text_input("", value=str(p2_val), key=f"p2_{j_id}", label_visibility="collapsed")
                st.write("---")
                
            if st.form_submit_button("Confirmar e Salvar meus Palpites na Nuvem 💾", use_container_width=True):
                for jogo in jogos_ativos:
                    ja_id = jogo[0]
                    hora_j_aux = datetime.strptime(jogo[5], "%Y-%m-%d %H:%M")
                    # Grava apenas se ainda estiver dentro do tempo regulamentar
                    if (hora_j_aux - agora).total_seconds() > 600:
                        ga1 = int(st.session_state[f"p1_{ja_id}"])
                        ga2 = int(st.session_state[f"p2_{ja_id}"])
                        cursor.execute("INSERT OR REPLACE INTO palpites VALUES (?, ?, ?, ?)", (usuario_atual, ja_id, ga1, ga2))
                conn.commit()
                st.success("Seus placares foram validados e trancados com sucesso!")
                st.rerun()
    else:
        st.info("Todos os jogos cadastrados no momento já foram encerrados!")
    conn.close()

# DEMAIS ABAS COMPLEMENTARES PARA MANTER O SITE FUNCIONAL E COMPLETO
elif aba_selecionada == "Tabela Copa & Grupos":
    st.header("🗂️ Tabelas Completas de Grupos")
    st.write("Confira a pontuação geral das seleções:")
    g1, g2 = st.columns(2)
    with g1:
        st.info("### 🟢 GRUPO A
1. Brasil 🇧🇷 - 3pts
2. Marrocos 🇲🇦 - 0pts")
    with g2:
        st.warning("### 🔵 GRUPO E
1. Espanha 🇪🇸 - 3pts
2. Costa Rica 🇨🇷 - 0pts")

elif aba_selecionada == "Chaveamento / Mata-Mata":
    st.header("🗺️ Chaveamento Definitivo")
    st.code("Oitavas ➡️ Quartas ➡️ Semifinal ➡️ Grande Final de 2026", language="text")

elif aba_selecionada == "Resenha & Figurinhas":
    st.header("💬 Resenha Oficial")
    st.write("Chat geral liberado para provocações!")

elif aba_selecionada == "Informações da Copa":
    st.header("ℹ️ Dados dos Estádios e Sedes")
    st.write("Painel técnico completo das partidas da Copa de 2026.")

elif aba_selecionada == "Notícias Completas":
    st.header("📰 Central de Jornalismo")
    st.write("Feed completo com reportagens de qualidade direto de campo.")
