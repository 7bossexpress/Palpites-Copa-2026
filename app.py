import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

# 1. CONFIGURAÇÃO VISUAL PREMIUM (TEMA COPA SEU DESIGN)
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

# 2. BANCO DE DADOS ATUALIZADO (copa_v4 evita conflitos anteriores)
def conectar_banco():
    return sqlite3.connect('copa_dados_v4.db', check_same_thread=False)

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
            # Últimos jogos (Passados)
            (1, "Alemanha", "🇩🇪", "Japão", "🇯🇵", 2, 1, "2026-06-13 13:00", "Grupo E", 1),
            (2, "Inglaterra", "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "Irã", "🇮🇷", 6, 2, "2026-06-13 16:00", "Grupo B", 1),
            (3, "Catar", "🇶🇦", "Equador", "🇪🇨", 0, 2, "2026-06-13 19:00", "Grupo A", 1),
            (4, "Estados Unidos", "🇺🇸", "Gales", "🏴󠁧󠁢󠁷󠁬󠁳󠁿", 1, 1, "2026-06-13 22:00", "Grupo B", 1),
            # Jogos de Hoje (Simulando data atual da Copa de 2026)
            (5, "Brasil", "🇧🇷", "Marrocos", "🇲🇦", 0, 0, "2026-06-14 16:00", "Grupo A", 0),
            (6, "Espanha", "🇪🇸", "Costa Rica", "🇨🇷", 0, 0, "2026-06-14 19:00", "Grupo E", 0),
            # Próximos Jogos (Futuros)
            (7, "Argentina", "🇦🇷", "França", "🇫🇷", 0, 0, "2026-06-15 13:00", "Grupo C", 0),
            (8, "Bélgica", "🇧🇪", "Canadá", "🇨🇦", 0, 0, "2026-06-15 16:00", "Grupo F", 0),
            (9, "Suíça", "🇨🇭", "Camarões", "🇨🇲", 0, 0, "2026-06-16 10:00", "Grupo G", 0),
            (10, "Uruguai", "🇺🇾", "Coreia do Sul", "🇰🇷", 0, 0, "2026-06-16 13:00", "Grupo H", 0)
        ]
        cursor.executemany("INSERT INTO resultados_reais VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", jogos)
        conn.commit()
    conn.close()

inicializar_banco()

# 3. TELA DE ENTRADA DEFINITIVA (LOGIN SEM MUDANÇA)
if "usuario_registrado" not in st.session_state:
    st.session_state.usuario_registrado = None

if st.session_state.usuario_registrado is None:
    st.markdown("<h1 style='text-align:center; color:#ffb703; margin-top:10%;'>🏆 COPA DE PALPITES 2026</h1>", unsafe_allow_html=True)
    st.write("<p style='text-align:center; font-size:1.2rem;'>Digite seu nome para acessar. Uma vez escolhido, ele não mudará!</p>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        nome_input = st.text_input("Seu Nome / Apelido de Jogador:", placeholder="Ex: Lucas_Hexa").strip()
        if st.button("Entrar e Trancar Perfil 🔐", use_container_width=True):
            if nome_input:
                st.session_state.usuario_registrado = nome_input
                st.rerun()
    st.stop()

usuario_atual = st.session_state.usuario_registrado

# 4. BARRA DE MENUS SUPERIOR
st.markdown(f'''
<div class="header-painel">
    <div class="logo-site">🏆 COPA DE PALPITES</div>
    <div style="font-weight:bold; color:#5bc0be;">👤 Perfil: {usuario_atual}</div>
</div>
''', unsafe_allow_html=True)

aba_selecionada = st.radio(
    "Escolha a aba:",
    ["Dashboard Principal", "Tabela Palpites", "Tabela Copa", "Chaveamento / Mata-Mata", "Resenha & Figurinhas", "Informações", "Notícias"],
    horizontal=True
)

# 5. CONTEÚDO DAS ABAS
if aba_selecionada == "Dashboard Principal":
    # Carrossel de Notícias
    if "index_noticia" not in st.session_state:
        st.session_state.index_noticia = 0
        
    noticias = [
        {"titulo": "🚨 Estreia da Seleção!", "conteudo": "Brasil confirmado com força máxima para encarar o Marrocos hoje!"},
        {"titulo": "🏟️ Sedes Prontas", "conteudo": "Gramados impecáveis e tecnologia de ponta operando nos estádios."},
        {"titulo": "🧠 Dicas de IA bombando", "conteudo": "Mecanismo inteligente auxiliando os melhores palpites da rodada."},
        {"titulo": "🇫🇷 Alerta na França", "conteudo": "Mudança tática de última hora mexe com o clássico contra a Argentina."},
        {"titulo": "🌍 Festa Mundial", "conteudo": "Torcedores do mundo inteiro fazem a festa na abertura da rodada."}
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
            <p>{noticia_atual['conteudo']}</p>
        </div>
        ''', unsafe_allow_html=True)
        
    with col_seta_dir:
        if st.button("▶", use_container_width=True):
            st.session_state.index_noticia = (st.session_state.index_noticia + 1) % len(noticias)
            st.rerun()

    st.write("---")
    
    # Grid de Jogos (Últimos, Hoje e Próximos)
    conn = conectar_banco()
    cursor = conn.cursor()
    col_ultimos, col_do_dia, col_proximos = st.columns([1.2, 2, 1.2])
    
    with col_ultimos:
        st.markdown('<div class="titulo-coluna">⏮️ Últimos 4 Jogos</div>', unsafe_allow_html=True)
        cursor.execute("SELECT time1, bandeira1, gols1, gols2, time2, bandeira2 FROM resultados_reais WHERE encerrado=1 LIMIT 4")
        for j in cursor.fetchall():
            st.markdown(f'<div class="card-jogos-lista">{j[1]} {j[0]} <b style="color:#ffb703;">{j[2]}x{j[3]}</b> {j[4]} {j[5]}</div>', unsafe_allow_html=True)
            
    with col_do_dia:
        st.markdown('<div class="titulo-coluna">⚽ Jogos de Hoje</div>', unsafe_allow_html=True)
        cursor.execute("SELECT jogo_id, time1, bandeira1, time2, bandeira2, horario FROM resultados_reais WHERE encerrado=0 AND horario LIKE '2026-06-14%'")
        for j in cursor.fetchall():
            j_id, t1, b1, t2, b2, hora_str = j
            st.markdown(f'<div class="card-jogo-destaque"><h2>{b1} {t1} vs {t2} {b2}</h2><p>⏰ Horário: <b>{hora_str[-5:]}</b></p></div>', unsafe_allow_html=True)
            
            c_b1, c_b2 = st.columns(2)
            with c_b1:
                if st.button(f"ℹ️ Info {t1}x{t2}", key=f"inf_{j_id}"):
                    st.info("🏟️ Clima: Perfeito 22°C | Estádio Lotado!")
            with c_b2:
                if st.button(f"🤖 Dica IA {t1}x{t2}", key=f"ia_{j_id}"):
                    st.warning("🧠 IA indica favoritismo do time mandante com chances de placar magro.")
            st.write("---")

    with col_proximos:
        st.markdown('<div class="titulo-coluna">⏭️ Próximos 4 Jogos</div>', unsafe_allow_html=True)
        cursor.execute("SELECT time1, bandeira1, time2, bandeira2, horario FROM resultados_reais WHERE horario > '2026-06-14 23:59' LIMIT 4")
        for j in cursor.fetchall():
            st.markdown(f'<div class="card-jogos-lista">{j[1]} {j[0]} vs {j[4]} {j[2]}<br><small style="color:#ffb703;">📅 {j[5][5:10]} às {j[5][-5:]}</small></div>', unsafe_allow_html=True)
            
    # Tabela Dinâmica Inferior
    st.write("---")
    st.markdown("### 📊 Tabela Real Otimizada (Times que jogam Hoje)")
    tabela_a = {"Seleção": ["🇧🇷 Brasil", "🇪🇸 Espanha", "🇲🇦 Marrocos", "🇨🇷 Costa Rica"], "P": [3, 3, 0, 0], "J": [1, 1, 1, 1]}
    st.table(pd.DataFrame(tabela_a).set_index("Seleção"))
    conn.close()

elif aba_selecionada == "Tabela Palpites":
    st.header("📋 Seus Palpites da Copa")
    st.write("Insira seus palpites. A edição fecha automaticamente 10 minutos antes do jogo!")
    
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT jogo_id, time1, bandeira1, time2, bandeira2, horario FROM resultados_reais WHERE encerrado=0")
    jogos_ativos = cursor.fetchall()
    
    agora = datetime(2026, 6, 14, 14, 22, 0) # Data fixada do sistema
    
    if jogos_ativos:
        with st.form("form_palpites_v4"):
            for j in jogos_ativos:
                j_id, t1, b1, t2, b2, h_str = j
                hora_j = datetime.strptime(h_str, "%Y-%m-%d %H:%M")
                pode_editar = (hora_j - agora).total_seconds() > 600
                
                cursor.execute("SELECT gols1, gols2 FROM palpites WHERE usuario=? AND jogo_id=?", (usuario_atual, j_id))
                antigo = cursor.fetchone()
                v1, v2 = (antigo[0], antigo[1]) if antigo else (0, 0)
                
                st.markdown(f"##### {b1} {t1} x {t2} {b2}")
                if pode_editar:
                    st.markdown('<span class="badge-tempo">⏳ Edição Liberada</span>', unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    with c1: st.number_input(f"Gols {t1}", min_value=0, value=v1, key=f"p1_{j_id}")
                    with c2: st.number_input(f"Gols {t2}", min_value=0, value=v2, key=f"p2_{j_id}")
                else:
                    st.markdown('<span class="badge-bloqueado">🔒 Bloqueado (Faltam menos de 10 min)</span>', unsafe_allow_html=True)
                    st.write(f"Palpitado: {v1} x {v2}")
                    st.session_state[f"p1_{j_id}"] = v1
                    st.session_state[f"p2_{j_id}"] = v2
                st.write("---")
                
            if st.form_submit_button("Salvar Meus Palpites ✅", use_container_width=True):
                for j in jogos_ativos:
                    ja_id = j[0]
                    hora_j_aux = datetime.strptime(j[5], "%Y-%m-%d %H:%M")
                    if (hora_j_aux - agora).total_seconds() > 600:
                        cursor.execute("INSERT OR REPLACE INTO palpites VALUES (?, ?, ?, ?)", (usuario_atual, ja_id, int(st.session_state[f"p1_{ja_id}"]), int(st.session_state[f"p2_{ja_id}"])))
                conn.commit()
                st.success("Palpites salvos com sucesso!")
                st.rerun()
    conn.close()

else:
    st.info("Aba em desenvolvimento. O painel principal e de palpites já estão 100% operacionais!")
