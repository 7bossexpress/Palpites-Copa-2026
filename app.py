import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

# 1. CONFIGURAÇÃO VISUAL IDÊNTICA AO DESIGN DA FOTO
st.set_page_config(page_title="Copa de Palpites 2026", page_icon="🏆", layout="wide")

st.markdown('''
<style>
    /* Cores do fundo e textos baseados na imagem de referência */
    .stApp { background-color: #0b1424; color: #f8f9fa; }
    
    /* Títulos e Containers */
    .titulo-secao { font-size: 1.4rem; font-weight: bold; color: #ffffff; margin-bottom: 15px; font-family: sans-serif; }
    .card-noticia { background-color: #121e36; padding: 20px; border-radius: 8px; border-left: 5px solid #ffb703; margin-bottom: 15px; }
    .card-jogos-lista { background-color: #121e36; padding: 12px; border-radius: 6px; margin-bottom: 8px; border: 1px solid #1f3458; font-size: 0.95rem; }
    .card-jogo-destaque { background-color: #162644; padding: 20px; border-radius: 12px; text-align: center; border: 1px solid #233c66; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }
    
    /* Badges de tempo */
    .badge-tempo { background-color: #e63946; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold; }
    .badge-bloqueado { background-color: #4a5568; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold; }
    
    /* Customização dos botões do topo (Abas) para parecer o menu da foto */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: #0b1424; }
    .stTabs [data-baseweb="tab"] { background-color: #121e36; color: #a0aec0; border-radius: 6px; padding: 10px 20px; border: none; }
    .stTabs [aria-selected="true"] { background-color: #ffb703 !important; color: #0b1424 !important; font-weight: bold; }
</style>
''', unsafe_allow_html=True)

# 2. BANCO DE DADOS ATUALIZADO (Zera o histórico antigo bugado)
def conectar_banco():
    return sqlite3.connect('copa_dados_v5.db', check_same_thread=False)

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
    
    cursor.execute("SELECT COUNT(*) FROM resultados_reais")
    if cursor.fetchone()[0] == 0:
        jogos = [
            # ÚLTIMOS JOGOS (Já aconteceram - Brasil e Marrocos já jogou aqui!)
            (1, "Brasil", "🇧🇷", "Marrocos", "🇲🇦", 2, 0, "2026-06-14 13:00", "Grupo A", 1),
            (2, "Alemanha", "🇩🇪", "Japão", "🇯🇵", 1, 1, "2026-06-14 13:00", "Grupo E", 1),
            (3, "Inglaterra", "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "Irã", "🇮🇷", 3, 0, "2026-06-14 13:00", "Grupo B", 1),
            (4, "Estados Unidos", "🇺🇸", "Gales", "🏴󠁧󠁢󠁷󠁬󠁳󠁿", 1, 2, "2026-06-14 13:00", "Grupo B", 1),
            # JOGOS DO DIA (De hoje, mais tarde - Para palpitar)
            (5, "Espanha", "🇪🇸", "Costa Rica", "🇨🇷", 0, 0, "2026-06-14 16:30", "Grupo E", 0),
            (6, "França", "🇫🇷", "Austrália", "🇦🇺", 0, 0, "2026-06-14 20:00", "Grupo D", 0),
            # PRÓXIMOS JOGOS (Futuros)
            (7, "Argentina", "🇦🇷", "Arábia Saudita", "🇸🇦", 0, 0, "2026-06-15 13:00", "Grupo C", 0),
            (8, "Bélgica", "🇧🇪", "Canadá", "🇨🇦", 0, 0, "2026-06-15 16:00", "Grupo F", 0),
            (9, "Suíça", "🇨🇭", "Camarões", "🇨🇲", 0, 0, "2026-06-16 10:00", "Grupo G", 0),
            (10, "Uruguai", "🇺🇾", "Coreia do Sul", "🇰🇷", 0, 0, "2026-06-16 13:00", "Grupo H", 0)
        ]
        cursor.executemany("INSERT INTO resultados_reais VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", jogos)
        conn.commit()
    conn.close()

inicializar_banco()

# 3. TELA DE ENTRADA BLOQUEADA (LOGIN ÚNICO)
if "usuario_registrado" not in st.session_state:
    st.session_state.usuario_registrado = None

if st.session_state.usuario_registrado is None:
    st.markdown("<h1 style='text-align:center; color:#ffb703; margin-top:10%; font-family:sans-serif;'>🏆 COPA DE PALPITES 2026</h1>", unsafe_allow_html=True)
    st.write("<p style='text-align:center; font-size:1.2rem; color:#a0aec0;'>Crie o seu perfil único para entrar. Seu nome não poderá ser alterado depois!</p>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        nome_input = st.text_input("Escolha seu Nome / Apelido de Jogador:", placeholder="Ex: Lucas_Hexa").strip()
        if st.button("Confirmar e Entrar 🔐", use_container_width=True):
            if nome_input:
                st.session_state.usuario_registrado = nome_input
                st.rerun()
    st.stop()

usuario_atual = st.session_state.usuario_registrado

# 4. BOTÕES DE NAVEGAÇÃO IGUAIS À FOTO (Usando as abas nativas do Streamlit estilizadas)
aba_principal, aba_palpites, aba_tabela_copa, aba_chaveamento, aba_resenha, aba_informacoes, aba_noticias = st.tabs([
    "🏠 Dashboard Principal", 
    "📋 Tabela Palpites", 
    "📊 Tabela Copa", 
    "🗺️ Chaveamento / Mata-Mata", 
    "💬 Resenha & Figurinhas", 
    "ℹ️ Informações da Copa", 
    "📰 Notícias"
])

# 5. CONTEÚDO: DASHBOARD PRINCIPAL
with aba_principal:
    # CARROSSEL DE NOTÍCIAS (Início da página)
    if "index_noticia" not in st.session_state:
        st.session_state.index_noticia = 0
        
    noticias = [
        {"titulo": "🚨 Brasil estreia com vitória sólida!", "conteudo": "A seleção bateu o Marrocos por 2x0 com show da torcida. O Hexa começou!"},
        {"titulo": "🏟️ Climatização dos Estádios surpreende positivamente", "conteudo": "Tecnologia de ponta mantém arenas em 22°C constantes para atletas e fãs."},
        {"titulo": "🧠 Inteligência Artificial aponta tendências para os jogos de hoje", "conteudo": "Nosso algoritmo analisou Espanha e França. Veja os palpites na aba ao lado!"},
        {"titulo": "🇫🇷 França chega pressionada para o jogo da noite", "conteudo": "Com mudanças táticas, os franceses buscam iniciar com o pé direito contra a Austrália."},
        {"titulo": "🌍 Clima de união toma conta das cidades-sede", "conteudo": "Festa pacífica e espetáculo cultural marcam a primeira semana oficial da Copa."}
    ]
    
    st.markdown('<div class="titulo-secao">📰 Notícia do Dia</div>', unsafe_allow_html=True)
    col_seta_esq, col_corpo, col_seta_dir = st.columns([1, 15, 1])
    
    with col_seta_esq:
        if st.button("◀", key="btn_esq", use_container_width=True):
            st.session_state.index_noticia = (st.session_state.index_noticia - 1) % len(noticias)
            st.rerun()
            
    with col_corpo:
        noticia_atual = noticias[st.session_state.index_noticia]
        st.markdown(f'''
        <div class="card-noticia">
            <h4 style="margin:0 0 5px 0; color:#ffb703;">{noticia_atual['titulo']}</h4>
            <p style="margin:0; color:#cbd5e0;">{noticia_atual['conteudo']}</p>
        </div>
        ''', unsafe_allow_html=True)
        
    with col_seta_dir:
        if st.button("▶", key="btn_dir", use_container_width=True):
            st.session_state.index_noticia = (st.session_state.index_noticia + 1) % len(noticias)
            st.rerun()

    st.write("---")
    
    # GRID DE JOGOS (Últimos, Hoje e Próximos)
    conn = conectar_banco()
    cursor = conn.cursor()
    
    col_ultimos, col_do_dia, col_proximos = st.columns([1.3, 2, 1.3])
    
    with col_ultimos:
        st.markdown('<div class="titulo-secao">⏮️ Últimos 4 Jogos</div>', unsafe_allow_html=True)
        cursor.execute("SELECT time1, bandeira1, gols1, gols2, time2, bandeira2 FROM resultados_reais WHERE encerrado=1 LIMIT 4")
        for j in cursor.fetchall():
            st.markdown(f'<div class="card-jogos-lista">{j[1]} {j[0]} <b style="color:#ffb703;">{j[2]} x {j[3]}</b> {j[4]} {j[5]}</div>', unsafe_allow_html=True)
            
    with col_do_dia:
        st.markdown('<div class="titulo-secao">⚽ Jogos de Hoje</div>', unsafe_allow_html=True)
        cursor.execute("SELECT jogo_id, time1, bandeira1, time2, bandeira2, horario FROM resultados_reais WHERE encerrado=0 AND horario LIKE '2026-06-14%'")
        jogos_hoje = cursor.fetchall()
        
        for j in jogos_hoje:
            j_id, t1, b1, t2, b2, hora_str = j
            hora_limpa = hora_str[-5:] # Pega apenas o "16:30" ou "20:00"
            
            st.markdown(f'''
            <div class="card-jogo-destaque">
                <h3 style="margin:0 0 10px 0;">{b1} {t1} vs {t2} {b2}</h3>
                <span style="color:#a0aec0; font-size:0.9rem;">⏰ Horário: <b>{hora_limpa}</b></span>
            </div>
            ''', unsafe_allow_html=True)
            
            c_b1, c_b2 = st.columns(2)
            with c_b1:
                if st.button(f"ℹ️ Informações", key=f"inf_{j_id}", use_container_width=True):
                    st.info("🏟️ Clima ideal de 21°C. Estádios com lotação máxima esgotada!")
            with c_b2:
                if st.button(f"🤖 Dicas IA", key=f"ia_{j_id}", use_container_width=True):
                    st.warning("🧠 IA indica favoritismo da equipe mandante com placar abaixo de 2.5 gols.")
            st.write("")

    with col_proximos:
        st.markdown('<div class="titulo-secao">⏭️ Próximos 4 Jogos</div>', unsafe_allow_html=True)
        cursor.execute("SELECT time1, bandeira1, time2, bandeira2, horario FROM resultados_reais WHERE horario > '2026-06-14 23:59' LIMIT 4")
        for j in cursor.fetchall():
            # Formata a data de "2026-06-15 13:00" para "15/06 às 13:00"
            data_br = f"{j[4][8:10]}/{j[4][5:7]} às {j[4][-5:]}"
            st.markdown(f'<div class="card-jogos-lista">{j[1]} {j[0]} vs {j[2]} {j[3]}<br><small style="color:#ffb703;">📅 {data_br}</small></div>', unsafe_allow_html=True)
            
    # TABELA DO RODAPÉ (Times que jogam hoje)
    st.write("---")
    st.markdown('<div class="titulo-secao">📊 Tabela do Grupo (Times que jogam Hoje)</div>', unsafe_allow_html=True)
    tabela_a = {"Seleção": ["🇧🇷 Brasil", "🇪🇸 Espanha", "🇲🇦 Marrocos", "🇨🇷 Costa Rica"], "Pontos": [3, 0, 0, 0], "Jogos": [1, 0, 1, 0]}
    st.table(pd.DataFrame(tabela_a).set_index("Seleção"))
    conn.close()

# 6. CONTEÚDO: MEUS PALPITES (Apenas jogos que NÃO aconteceram e trava de 10 min)
with aba_palpites:
    st.header("📋 Seus Palpites Oficiais")
    st.write("Diga seus placares! A edição fecha automaticamente **10 minutos antes** da partida.")
    
    conn = conectar_banco()
    cursor = conn.cursor()
    # Puxa APENAS jogos ativos (O Brasil já sumiu daqui!)
    cursor.execute("SELECT jogo_id, time1, bandeira1, time2, bandeira2, horario FROM resultados_reais WHERE encerrado=0")
    jogos_ativos = cursor.fetchall()
    
    # Hora atual simulada: 14 de Junho de 2026 às 14:22
    agora = datetime(2026, 6, 14, 14, 22, 0)
    
    if jogos_ativos:
        with st.form("form_palpites_v5"):
            for j in jogos_ativos:
                j_id, t1, b1, t2, b2, h_str = j
                hora_j = datetime.strptime(h_str, "%Y-%m-%d %H:%M")
                
                # Faz a conta para ver se faltam mais de 10 minutos (600 segundos)
                pode_editar = (hora_j - agora).total_seconds() > 600
                
                cursor.execute("SELECT gols1, gols2 FROM palpites WHERE usuario=? AND jogo_id=?", (usuario_atual, j_id))
                antigo = cursor.fetchone()
                v1, v2 = (antigo[0], antigo[1]) if antigo else (0, 0)
                
                st.markdown(f"##### {b1} {t1} x {t2} {b2}")
                if pode_editar:
                    st.markdown('<span class="badge-tempo">⏳ Aberto para Palpites</span>', unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    with c1: st.number_input(f"Gols {t1}", min_value=0, value=v1, key=f"p1_{j_id}")
                    with c2: st.number_input(f"Gols {t2}", min_value=0, value=v2, key=f"p2_{j_id}")
                else:
                    st.markdown('<span class="badge-bloqueado">🔒 Palpites Bloqueados</span>', unsafe_allow_html=True)
                    st.write(f"Seu palpite final gravado foi: **{v1} x {v2}**")
                    st.session_state[f"p1_{j_id}"] = v1
                    st.session_state[f"p2_{j_id}"] = v2
                st.write("---")
                
            if st.form_submit_button("Salvar Todos Meus Palpites ✅", use_container_width=True):
                for j in jogos_ativos:
                    ja_id = j[0]
                    hora_j_aux = datetime.strptime(j[5], "%Y-%m-%d %H:%M")
                    if (hora_j_aux - agora).total_seconds() > 600:
                        cursor.execute("INSERT OR REPLACE INTO palpites VALUES (?, ?, ?, ?)", (usuario_atual, ja_id, int(st.session_state[f"p1_{ja_id}"]), int(st.session_state[f"p2_{ja_id}"])))
                conn.commit()
                st.success("Palpites guardados com sucesso!")
                st.rerun()
    else:
        st.info("Não há jogos abertos para palpite no momento.")
    conn.close()

# 7. CONTEÚDO DAS OUTRAS ABAS DO TOPO
with aba_tabela_copa:
    st.header("📊 Classificação Geral dos Grupos")
    st.info("### Grupo A\n1. Brasil - 3pts\n2. Marrocos - 0pts")
with aba_chaveamento:
    st.header("🗺️ Chaveamento do Mata-Mata")
    st.code("Quartas de Final -> Semifinal -> Finalíssima", language="text")
with aba_resenha:
    st.header("💬 Resenha & Respostas")
    st.write("Área do chat ativo da galera.")
with aba_informacoes:
    st.header("ℹ️ Informações de Campo")
    st.write("Dados técnicos de arbitragem e estádios.")
with aba_noticias:
    st.header("📰 Mural Completo de Notícias")
    st.write("Feed com o jornalismo completo da Copa do Mundo de 2026.")
