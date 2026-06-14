import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

# 1. DESIGN DE ALTA QUALIDADE (TEMA COPA DO MUNDO PREMIUM)
st.set_page_config(page_title="Copa de Palpites 2026", page_icon="🏆", layout="wide")

st.markdown('''
<style>
    /* Cores escuras e modernas inspiradas na foto enviada */
    .stApp { background-color: #0b1424; color: #f8f9fa; }
    
    /* Títulos e Blocos de Conteúdo */
    .titulo-secao { font-size: 1.4rem; font-weight: bold; color: #ffffff; margin-bottom: 15px; font-family: sans-serif; border-left: 4px solid #ffb703; padding-left: 10px; }
    .card-noticia { background-color: #121e36; padding: 0px; border-radius: 12px; overflow: hidden; border: 1px solid #1f3458; box-shadow: 0 4px 15px rgba(0,0,0,0.3); margin-bottom: 15px; }
    .noticia-conteudo { padding: 20px; }
    .card-jogos-lista { background-color: #121e36; padding: 12px; border-radius: 8px; margin-bottom: 8px; border: 1px solid #1f3458; font-size: 0.95rem; display: flex; justify-content: space-between; align-items: center; }
    .card-jogo-destaque { background-color: #162644; padding: 25px; border-radius: 16px; text-align: center; border: 1px solid #233c66; box-shadow: 0 6px 20px rgba(0,0,0,0.4); }
    
    /* Alinhamento de Imagens e Tabelas */
    .img-carrossel { width: 100%; max-height: 350px; object-fit: cover; }
    .stTable { background-color: #121e36; border-radius: 10px; overflow: hidden; }
    
    /* Customização dos Botões de Navegação (Abas) identicos à Imagem */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background-color: #0b1424; padding: 10px 0; }
    .stTabs [data-baseweb="tab"] { background-color: #121e36; color: #cbd5e0; border-radius: 8px; padding: 12px 24px; border: 1px solid #1f3458; font-size: 0.95rem; }
    .stTabs [aria-selected="true"] { background-color: #ffb703 !important; color: #0b1424 !important; font-weight: bold; border: 1px solid #ffb703; }
</style>
''', unsafe_allow_html=True)

# 2. BANCO DE DADOS ATUALIZADO (Zera conflitos anteriores)
def conectar_banco():
    return sqlite3.connect('copa_dados_v7.db', check_same_thread=False)

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
            # ÚLTIMOS JOGOS REAIS (Já encerrados no sistema - Brasil e Marrocos entra aqui como já jogado!)
            (1, "Brasil", "🇧🇷", "Marrocos", "🇲🇦", 2, 0, "2026-06-14 10:00", "Grupo A", 1),
            (2, "Alemanha", "🇩🇪", "Japão", "🇯🇵", 3, 1, "2026-06-14 13:00", "Grupo E", 1),
            (3, "México", "🇲🇽", "Gana", "🇬🇭", 1, 0, "2026-06-14 13:00", "Grupo B", 1),
            # JOGOS DO DIA (Ativos para palpitar na rodada atual - Mais de 10 min para começar)
            (4, "Espanha", "🇪🇸", "Costa Rica", "🇨🇷", 0, 0, "2026-06-14 18:30", "Grupo E", 0),
            (5, "França", "🇫🇷", "Austrália", "🇦🇺", 0, 0, "2026-06-14 21:00", "Grupo D", 0),
            # PRÓXIMOS JOGOS (Futuros)
            (6, "Argentina", "🇦🇷", "Itália", "🇮🇹", 0, 0, "2026-06-15 13:00", "Grupo C", 0),
            (7, "Estados Unidos", "🇺🇸", "Inglaterra", "🏴%b7%b7g", 0, 0, "2026-06-15 16:00", "Grupo B", 0),
            (8, "Uruguai", "🇺🇾", "Portugal", "🇵🇹", 0, 0, "2026-06-16 13:00", "Grupo H", 0)
        ]
        cursor.executemany("INSERT INTO resultados_reais VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", jogos)
        conn.commit()
    conn.close()

inicializar_banco()

# 3. TELA DE ENTRADA BLOQUEADA (NOME TRANCADO)
if "usuario_registrado" not in st.session_state:
    st.session_state.usuario_registrado = None

if st.session_state.usuario_registrado is None:
    st.markdown("<h1 style='text-align:center; color:#ffb703; margin-top:8%; font-family:sans-serif;'>🏆 COPA DE PALPITES 2026</h1>", unsafe_allow_html=True)
    st.write("<p style='text-align:center; font-size:1.2rem; color:#cbd5e0;'>Digite seu nome para acessar o painel. Ele não poderá ser alterado depois!</p>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        nome_input = st.text_input("Seu Nome ou Apelido de Jogador:", placeholder="Ex: Lucas_Hexa").strip()
        if st.button("Entrar e Trancar Perfil 🔐", use_container_width=True):
            if nome_input:
                st.session_state.usuario_registrado = nome_input
                st.rerun()
    st.stop()

usuario_atual = st.session_state.usuario_registrado

# 4. BARRA FIXA SUPERIOR
st.markdown(f'''
<div class="header-painel">
    <div class="logo-site">🏆 COPA DE PALPITES</div>
    <div style="font-weight:bold; color:#ffb703; background-color:#121e36; padding:5px 15px; border-radius:6px;">👤 Perfil: {usuario_atual}</div>
</div>
''', unsafe_allow_html=True)

# 5. ABAS PREMIUM EM FORMATO DE BOTÕES SUPERIORES
aba_principal, aba_palpites, aba_tabela_copa, aba_chaveamento, aba_resenha = st.tabs([
    "🏠 Dashboard Principal", 
    "📋 Tabela Palpites", 
    "📊 Tabela Copa", 
    "🗺️ Chaveamento / Mata-Mata", 
    "💬 Resenha & Figurinhas"
])

# 6. CONTEÚDO: DASHBOARD PRINCIPAL
with aba_principal:
    # CARROSSEL DE NOTÍCIAS REAL COM IMAGENS DE ALTA QUALIDADE
    if "index_noticia" not in st.session_state:
        st.session_state.index_noticia = 0
        
    noticias_reais = [
        {
            "titulo": "🚨 Seleção Brasileira vence a primeira na Copa de 2026!",
            "conteudo": "Com grande atuação tática, o Brasil bateu o Marrocos por 2x0 na estreia. Cobertura completa dos bastidores direto dos portais esportivos.",
            "imagem": "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=1200&auto=format&fit=crop&q=80"
        },
        {
            "titulo": "🏟️ Torcedores lotam as arenas na rodada de abertura",
            "conteudo": "A festa das torcidas espalha cores e muita energia pelas cidades-sede da maior competição do mundo.",
            "imagem": "https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=1200&auto=format&fit=crop&q=80"
        },
        {
            "titulo": "🧠 Inteligência Artificial calcula probabilidades para os jogos de hoje",
            "conteudo": "Confira os dados matemáticos e dicas táticas exclusivas do nosso algoritmo antes de enviar seus palpites.",
            "imagem": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=1200&auto=format&fit=crop&q=80"
        }
    ]
    
    st.markdown('<div class="titulo-secao">📰 Notícias do Dia (UOL Esporte)</div>', unsafe_allow_html=True)
    col_seta_esq, col_corpo, col_seta_dir = st.columns([1, 15, 1])
    
    with col_seta_esq:
        st.write("<br><br><br><br>", unsafe_allow_html=True)
        if st.button("◀", key="btn_esq", use_container_width=True):
            st.session_state.index_noticia = (st.session_state.index_noticia - 1) % len(noticias_reais)
            st.rerun()
            
    with col_corpo:
        noticia_atual = noticias_reais[st.session_state.index_noticia]
        st.markdown(f'''
        <div class="card-noticia">
            <img src="{noticia_atual['imagem']}" class="img-carrossel">
            <div class="noticia-conteudo">
                <h3 style="margin:0 0 8px 0; color:#ffb703;">{noticia_atual['titulo']}</h3>
                <p style="margin:0; color:#e2e8f0; line-height:1.5;">{noticia_atual['conteudo']}</p>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
    with col_seta_dir:
        st.write("<br><br><br><br>", unsafe_allow_html=True)
        if st.button("▶", key="btn_dir", use_container_width=True):
            st.session_state.index_noticia = (st.session_state.index_noticia + 1) % len(noticias_reais)
            st.rerun()

    st.write("---")
    
    # GRID PRINCIPAL DE JOGOS (ÚLTIMOS, HOJE, PRÓXIMOS)
    conn = conectar_banco()
    cursor = conn.cursor()
    col_ultimos, col_do_dia, col_proximos = st.columns([1.3, 2, 1.3])
    
    with col_ultimos:
        st.markdown('<div class="titulo-secao">⏮️ Últimos Resultados</div>', unsafe_allow_html=True)
        cursor.execute("SELECT time1, bandeira1, gols1, gols2, time2, bandeira2 FROM resultados_reais WHERE encerrado=1 ORDER BY jogo_id DESC LIMIT 4")
        for j in cursor.fetchall():
            st.markdown(f'''
            <div class="card-jogos-lista">
                <span>{j[1]} {j[0]}</span>
                <b style="color:#ffb703; background:#162644; padding:2px 8px; border-radius:4px;">{j[2]} x {j[3]}</b>
                <span>{j[4]} {j[5]}</span>
            </div>
            ''', unsafe_allow_html=True)
            
    with col_do_dia:
        st.markdown('<div class="titulo-secao">⚽ Jogos de Hoje</div>', unsafe_allow_html=True)
        cursor.execute("SELECT jogo_id, time1, bandeira1, time2, bandeira2, horario FROM resultados_reais WHERE encerrado=0 AND horario LIKE '2026-06-14%'")
        jogos_hoje = cursor.fetchall()
        
        for j in jogos_hoje:
            j_id, t1, b1, t2, b2, hora_str = j
            st.markdown(f'''
            <div class="card-jogo-destaque">
                <h3 style="margin:0 0 10px 0; font-size:1.4rem;">{b1} {t1} vs {t2} {b2}</h3>
                <span class="badge-tempo">⏰ Horário Real: {hora_str[-5:]}</span>
            </div>
            ''', unsafe_allow_html=True)
            
            c_b1, c_b2 = st.columns(2)
            with c_b1:
                if st.button(f"ℹ️ Informações da Partida", key=f"inf_{j_id}", use_container_width=True):
                    st.info("ℹ️ **Informações de Campo:** Gramado impecável e clima de 21°C. Transmissão oficial confirmada.")
            with c_b2:
                if st.button(f"🤖 Dicas Técnicas IA", key=f"ia_{j_id}", use_container_width=True):
                    st.warning("🧠 **Dica IA:** Equipe mandante possui 65% de chance de controle de jogo na primeira etapa.")
            st.write("")

    with col_proximos:
        st.markdown('<div class="titulo-secao">⏭️ Próximos Confrontos</div>', unsafe_allow_html=True)
        cursor.execute("SELECT time1, bandeira1, time2, bandeira2, horario FROM resultados_reais WHERE horario > '2026-06-14 23:59' ORDER BY horario ASC LIMIT 4")
        for j in cursor.fetchall():
            data_br = f"{j[4][8:10]}/{j[4][5:7]} às {j[4][-5:]}"
            st.markdown(f'''
            <div class="card-jogos-lista">
                <span>{j[1]} {j[0]} vs {j[2]} {j[3]}</span>
                <small style="color:#ffb703; font-weight:bold;">📅 {data_br}</small>
            </div>
            ''', unsafe_allow_html=True)
            
    # TABELA REAL NO RODAPÉ
    st.write("---")
    st.markdown('<div class="titulo-secao">📊 Tabela de Classificação do Grupo (Rodada Atual)</div>', unsafe_allow_html=True)
    tabela_real_dados = {
        "Seleção": ["🇧🇷 Brasil", "🇨🇦 Canadá", "🇲🇦 Marrocos", "🇭🇷 Croácia"],
        "Pontos (P)": [3, 3, 0, 0],
        "Jogos (J)": [1, 1, 1, 0],
        "Vitórias (V)": [1, 1, 0, 0],
        "Saldo Gols (SG)": [2, 1, -1, 0]
    }
    st.table(pd.DataFrame(tabela_real_dados).set_index("Seleção"))
    conn.close()

# 7. CONTEÚDO: MEUS PALPITES (Brasil já sumiu, pois já jogou!)
with aba_palpites:
    st.header("📋 Seus Palpites da Copa")
    st.write("Insira seus placares. O sistema fecha a edição exatamente **10 minutos antes** do jogo!")
    
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT jogo_id, time1, bandeira1, time2, bandeira2, horario FROM resultados_reais WHERE encerrado=0")
    jogos_ativos = cursor.fetchall()
    
    # Hora simulada do sistema: 14 de Junho de 2026 às 14:22
    agora = datetime(2026, 6, 14, 14, 22, 0)
    
    if jogos_ativos:
        with st.form("form_palpites_v7"):
            for j in jogos_ativos:
                j_id, t1, b1, t2, b2, h_str = j
                hora_j = datetime.strptime(h_str, "%Y-%m-%d %H:%M")
                pode_editar = (hora_j - agora).total_seconds() > 600
                
                cursor.execute("SELECT gols1, gols2 FROM palpites WHERE usuario=? AND jogo_id=?", (usuario_atual, j_id))
                antigo = cursor.fetchone()
                v1, v2 = (antigo[0], antigo[1]) if antigo else (0, 0)
                
                st.markdown(f"##### {b1} {t1} x {t2} {b2}")
                if pode_editar:
                    st.markdown('<span class="badge-tempo">⏳ Aberto para Alterações</span>', unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    with c1: st.number_input(f"Gols {t1}", min_value=0, value=v1, key=f"p1_{j_id}")
                    with c2: st.number_input(f"Gols {t2}", min_value=0, value=v2, key=f"p2_{j_id}")
                else:
                    st.markdown('<span class="badge-bloqueado">🔒 Bloqueado (Menos de 10 min restantes)</span>', unsafe_allow_html=True)
                    st.write(f"Palpite gravado: **{v1} x {v2}**")
                    st.session_state[f"p1_{j_id}"] = v1
                    st.session_state[f"p2_{j_id}"] = v2
                st.write("---")
                
            if st.form_submit_button("Confirmar e Salvar Meus Palpites ✅", use_container_width=True):
                for j in jogos_ativos:
                    ja_id = j[0]
                    hora_j_aux = datetime.strptime(j[5], "%Y-%m-%d %H:%M")
                    if (hora_j_aux - agora).total_seconds() > 600:
                        cursor.execute("INSERT OR REPLACE INTO palpites VALUES (?, ?, ?, ?)", (usuario_atual, ja_id, int(st.session_state[f"p1_{ja_id}"]), int(st.session_state[f"p2_{ja_id}"])))
                conn.commit()
                st.success("Seus palpites foram guardados com sucesso!")
                st.rerun()
    else:
        st.info("Nenhuma partida aberta para palpites na rodada atual.")
    conn.close()

# 8. OUTRAS ABAS
with aba_tabela_copa:
    st.header("📊 Tabelas de Classificação Geral")
    st.info("### Grupo A\n1. Brasil - 3pts\n2. Canadá - 3pts\n3. Marrocos - 0pts\n4. Croácia - 0pts")
with aba_chaveamento:
    st.header("🗺️ Chaveamento / Mata-Mata")
    st.code("Fase de Grupos -> Oitavas -> Quartas -> Semifinal -> Final", language="text")
with aba_resenha:
    st.header("💬 Resenha Geral")
    st.write("Espaço reservado para o chat e interações da galera.")
