import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# 1. SISTEMA DINÂMICO DE TEMAS (BRANCO, PRETO, AZUL, DOURADO, VERDE E AMARELO)
if "tema_escolhido" not in st.session_state:
    st.session_state.tema_escolhido = "Branco"

# Configuração da página
st.set_page_config(page_title="Portal Copa 2026", page_icon="🏆", layout="wide")

# Dicionário de cores para cada estilo baseado no seu pedido
config_temas = {
    "Branco": {"bg": "#f8f9fa", "card": "#ffffff", "texto": "#1a202c", "borda": "#e2e8f0", "detalhe": "#0077b6"},
    "Preto": {"bg": "#0f172a", "card": "#1e293b", "texto": "#f8f9fa", "borda": "#334155", "detalhe": "#38bdf8"},
    "Azul": {"bg": "#0b1424", "card": "#121e36", "texto": "#f8f9fa", "borda": "#1f3458", "detalhe": "#ffb703"},
    "Dourado": {"bg": "#1c1917", "card": "#292524", "texto": "#fef08a", "borda": "#44403c", "detalhe": "#ca8a04"},
    "Verde e Amarelo": {"bg": "#04351a", "card": "#064e26", "texto": "#ffffff", "borda": "#ffcc00", "detalhe": "#ffcc00"}
}

t = config_temas[st.session_state.tema_escolhido]

# Aplicação do estilo personalizado baseado na escolha
st.markdown(f'''
<style>
    .stApp {{ background-color: {t['bg']}; color: {t['texto']}; }}
    .header-painel {{ display: flex; justify-content: space-between; align-items: center; padding: 15px; background-color: {t['card']}; border-bottom: 3px solid {t['detalhe']}; border-radius: 8px; margin-bottom: 20px; }}
    .logo-site {{ font-size: 1.8rem; font-weight: bold; color: {t['detalhe']}; font-family: 'Arial Black', sans-serif; }}
    .titulo-secao {{ font-size: 1.4rem; font-weight: bold; color: {t['texto']}; margin-bottom: 15px; border-left: 4px solid {t['detalhe']}; padding-left: 10px; }}
    .card-noticia {{ background-color: {t['card']}; padding: 0px; border-radius: 12px; overflow: hidden; border: 1px solid {t['borda']}; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 15px; }}
    .noticia-conteudo {{ padding: 20px; color: {t['texto']}; }}
    .card-jogos-lista {{ background-color: {t['card']}; padding: 12px; border-radius: 8px; margin-bottom: 8px; border: 1px solid {t['borda']}; font-size: 0.95rem; display: flex; justify-content: space-between; align-items: center; }}
    .card-jogo-destaque {{ background-color: {t['card']}; padding: 25px; border-radius: 16px; text-align: center; border: 2px solid {t['detalhe']}; box-shadow: 0 6px 20px rgba(0,0,0,0.05); }}
    .img-carrossel {{ width: 100%; max-height: 360px; object-fit: cover; }}
    .badge-ao-vivo {{ background-color: #2ec4b6; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold; }}
    .badge-tempo {{ background-color: #e63946; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold; }}
    
    /* Abas customizadas estilo UOL */
    .stTabs [data-baseweb="tab-list"] {{ gap: 5px; background-color: transparent; padding: 10px 0; }}
    .stTabs [data-baseweb="tab"] {{ background-color: {t['card']}; color: {t['texto']}; border-radius: 6px 6px 0 0; padding: 12px 20px; border: 1px solid {t['borda']}; font-size: 0.95rem; }}
    .stTabs [aria-selected="true"] {{ background-color: {t['detalhe']} !important; color: #ffffff !important; font-weight: bold; }}
</style>
''', unsafe_allow_html=True)

# 2. BANCO DE DADOS CORE
def conectar_banco():
    return sqlite3.connect('copa_dados_v9.db', check_same_thread=False)

def inicializar_banco():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS usuarios (nome TEXT PRIMARY KEY)')
    cursor.execute('''CREATE TABLE IF NOT EXISTS resultados_reais (
                        jogo_id INTEGER PRIMARY KEY, time1 TEXT, bandeira1 TEXT, 
                        time2 TEXT, bandeira2 TEXT, gols1 INTEGER, gols2 INTEGER, 
                        horario TEXT, grupo TEXT, status TEXT)''')
    cursor.execute('CREATE TABLE IF NOT EXISTS palpites (usuario TEXT, jogo_id INTEGER, gols1 INTEGER, gols2 INTEGER, PRIMARY KEY(usuario, jogo_id))')
    
    cursor.execute("SELECT COUNT(*) FROM resultados_reais")
    if cursor.fetchone()[0] == 0:
        jogos = [
            (1, "Estados Unidos", "🇺🇸", "Marrocos", "🇲🇦", 1, 1, "2026-06-14 10:00", "Grupo A", "encerrado"),
            (2, "México", "🇲🇽", "África do Sul", "🇿🇦", 2, 0, "2026-06-14 13:00", "Grupo B", "encerrado"),
            (3, "Brasil", "🇧🇷", "Croácia", "🇭🇷", 2, 1, "2026-06-14 16:30", "Grupo A", "ao_vivo"),
            (4, "Espanha", "🇪🇸", "Japão", "🇯🇵", 0, 0, "2026-06-14 20:00", "Grupo E", "agendado"),
            (5, "Argentina", "🇦🇷", "França", "🇫🇷", 0, 0, "2026-06-15 13:00", "Grupo G", "agendado"),
            (6, "Inglaterra", "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "Itália", "🇮🇹", 0, 0, "2026-06-15 16:00", "Grupo D", "agendado")
        ]
        cursor.executemany("INSERT INTO resultados_reais VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", jogos)
        conn.commit()
    conn.close()

inicializar_banco()

# 3. ENTRADA DE USUÁRIO (NOME FIXO)
if "usuario_registrado" not in st.session_state:
    st.session_state.usuario_registrado = None

if st.session_state.usuario_registrado is None:
    st.markdown("<h1 style='text-align:center; color:#ca8a04; margin-top:8%; font-family:sans-serif;'>🏆 PORTAL COPA 2026</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        nome_input = st.text_input("Digite seu Nome para acessar o site:", placeholder="Ex: Lucas_Aposta").strip()
        if st.button("Acessar Conteúdo Oficial 🔐", use_container_width=True):
            if nome_input:
                st.session_state.usuario_registrado = nome_input
                st.rerun()
    st.stop()

usuario_atual = st.session_state.usuario_registrado

# 4. BARRA DO TOPO E SELETOR DE CORES INTERATIVO
st.markdown(f'''
<div class="header-painel">
    <div class="logo-site">🏆 PORTAL COPA DE PALPITES</div>
    <div style="font-weight:bold; background-color:{t['bg']}; padding:5px 15px; border-radius:6px; border: 1px solid {t['borda']};">👤 Perfil: {usuario_atual}</div>
</div>
''', unsafe_allow_html=True)

# Caixa de seleção para mudar as cores do site inteiro
st.session_state.tema_escolhido = st.selectbox(
    "🎨 Personalizar Aparência do Site:", 
    ["Branco", "Preto", "Azul", "Dourado", "Verde e Amarelo"]
)

# 5. ABAS PRINCIPAIS DO SITE (IGUAL AOS PORTAIS DE ESPORTE)
aba_noticias, aba_palpites, aba_tabela, aba_chaveamento = st.tabs([
    "📰 Notícias & Jogos", 
    "📋 Tabela Palpites", 
    "📊 Tabela Copa (1ª Fase)", 
    "🗺️ Segunda Fase / Mata-Mata"
])

# 6. CONTEÚDO: NOTÍCIAS & JOGOS DO DIA
with aba_noticias:
    # Carrossel de Fotos com notícias reais
    if "index_noticia" not in st.session_state:
        st.session_state.index_noticia = 0
        
    noticias_reais = [
        {
            "titulo": "🚨 UOL Esporte: Brasil estreia com vitória em jogo tenso contra a Croácia!",
            "conteudo": "A seleção comandou o placar ao vivo e somou os primeiros pontos. Torcida faz festa gigante nos arredores da arena.",
            "imagem": "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=1200&auto=format&fit=crop&q=80"
        },
        {
            "titulo": "🏟️ Cobertura: Logística e tecnologia de resfriamento dão show na abertura",
            "conteudo": "Estádios mantém clima agradável e recebem torcidas de todos os continentes com segurança máxima.",
            "imagem": "https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=1200&auto=format&fit=crop&q=80"
        }
    ]
    
    st.markdown('<div class="titulo-secao">📰 Principais Destaques do Dia</div>', unsafe_allow_html=True)
    c_seta_f, c_corpo_f, c_seta_t = st.columns([1, 15, 1])
    
    with c_seta_f:
        st.write("<br><br><br><br>", unsafe_allow_html=True)
        if st.button("◀", key="esq_p"):
            st.session_state.index_noticia = (st.session_state.index_noticia - 1) % len(noticias_reais)
            st.rerun()
            
    with c_corpo_f:
        n = noticias_reais[st.session_state.index_noticia]
        st.markdown(f'''
        <div class="card-noticia">
            <img src="{n['imagem']}" class="img-carrossel">
            <div class="noticia-conteudo">
                <h3 style="margin:0 0 5px 0;">{n['titulo']}</h3>
                <p style="margin:0; line-height:1.5;">{n['conteudo']}</p>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
    with c_seta_t:
        st.write("<br><br><br><br>", unsafe_allow_html=True)
        if st.button("▶", key="dir_p"):
            st.session_state.index_noticia = (st.session_state.index_noticia + 1) % len(noticias_reais)
            st.rerun()

    st.write("---")
    
    # Grid de Confrontos triplo do portal
    conn = conectar_banco()
    cursor = conn.cursor()
    col_l1, col_l2, col_l3 = st.columns([1.3, 2, 1.3])
    
    with col_l1:
        st.markdown('<div class="titulo-secao">⏮️ Últimos Resultados</div>', unsafe_allow_html=True)
        cursor.execute("SELECT time1, bandeira1, gols1, gols2, time2, bandeira2 FROM resultados_reais WHERE status='encerrado'")
        for j in cursor.fetchall():
            st.markdown(f'<div class="card-jogos-lista"><span>{j[1]} {j[0]}</span><b>{j[2]} x {j[3]}</b><span>{j[4]} {j[5]}</span></div>', unsafe_allow_html=True)
            
    with col_l2:
        st.markdown('<div class="titulo-secao">⚽ Jogos em Andamento / Hoje</div>', unsafe_allow_html=True)
        cursor.execute("SELECT jogo_id, time1, bandeira1, time2, bandeira2, horario, status, gols1, gols2 FROM resultados_reais WHERE horario LIKE '2026-06-14%' AND status != 'encerrado'")
        for j in cursor.fetchall():
            j_id, t1, b1, t2, b2, hora_s, stat, g1, g2 = j
            txt_badge = f"🔴 AO VIVO ({g1} x {g2})" if stat == "ao_vivo" else f"⏰ {hora_s[-5:]}"
            st.markdown(f'<div class="card-jogo-destaque"><h3>{b1} {t1} vs {t2} {b2}</h3><span class="badge-ao-vivo">{txt_badge}</span></div>', unsafe_allow_html=True)
            
            cb1, cb2 = st.columns(2)
            with cb1:
                if st.button("ℹ️ Informações", key=f"inf_{j_id}", use_container_width=True):
                    st.info("📊 Dados oficiais de escalação e transmissão ao vivo ativas nos portais parceiros.")
            with cb2:
                if st.button("🤖 Dicas IA", key=f"ia_{j_id}", use_container_width=True):
                    st.warning("🧠 Algoritmo indica alta probabilidade de gol nos minutos finais do confronto.")
            st.write("")

    with col_l3:
        st.markdown('<div class="titulo-secao">⏭️ Próximos Confrontos</div>', unsafe_allow_html=True)
        cursor.execute("SELECT time1, bandeira1, time2, bandeira2, horario FROM resultados_reais WHERE horario > '2026-06-14 23:59' LIMIT 4")
        for j in cursor.fetchall():
            st.markdown(f'<div class="card-jogos-lista"><span>{j[1]} {j[0]} vs {j[2]} {j[3]}</span><small>📅 {j[4][8:10]}/{j[4][5:7]} às {j[4][-5:]}</small></div>', unsafe_allow_html=True)
            
    # Tabela dinâmica de rodapé
    st.write("---")
    st.markdown('<div class="titulo-secao">📊 Classificação da Rodada (Fase de Grupos)</div>', unsafe_allow_html=True)
    dados_tabela = {"Seleção": ["🇧🇷 Brasil", "🇲🇽 México", "🇺🇸 Estados Unidos", "🇲🇦 Marrocos"], "P": [3, 3, 1, 1], "J": [1, 1, 1, 1]}
    st.table(pd.DataFrame(dados_tabela).set_index("Seleção"))
    conn.close()

# 7. ABA: TABELA PALPITES (SÓ JOGOS AGENDADOS + CONTAGEM DE 10 MINUTOS)
with aba_palpites:
    st.header("📋 Seus Palpites da Copa")
    st.write("Insira seus placares. O bloqueio acontece exatamente **10 minutos antes** de cada partida!")
    
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT jogo_id, time1, bandeira1, time2, bandeira2, horario FROM resultados_reais WHERE status='agendado'")
    jogos_ativos = cursor.fetchall()
    
    # Hora simulada do sistema (14/06/2026 às 14:22)
    agora = datetime(2026, 6, 14, 14, 22, 0)
    
    if jogos_ativos:
        with st.form("form_palpites_v9"):
            for j in jogos_ativos:
                j_id, t1, b1, t2, b2, h_str = j
                hora_j = datetime.strptime(h_str, "%Y-%m-%d %H:%M")
                pode_editar = (hora_j - agora).total_seconds() > 600
                
                cursor.execute("SELECT gols1, gols2 FROM palpites WHERE usuario=? AND jogo_id=?", (usuario_atual, j_id))
                antigo = cursor.fetchone()
                v1, v2 = (antigo[0], antigo[1]) if antigo else (0, 0)
                
                st.markdown(f"##### {b1} {t1} x {t2} {b2}")
                if pode_editar:
                    st.markdown('<span class="badge-tempo">⏳ Aberto para Edição</span>', unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    with c1: st.number_input(f"Placar {t1}", min_value=0, value=v1, key=f"p1_{j_id}")
                    with c2: st.number_input(f"Placar {t2}", min_value=0, value=v2, key=f"p2_{j_id}")
                else:
                    st.markdown('<span class="badge-bloqueado">🔒 Bloqueado (Faltam menos de 10 min)</span>', unsafe_allow_html=True)
                    st.write(f"Palpite gravado: **{v1} x {v2}**")
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
                st.success("Palpites registrados com sucesso!")
                st.rerun()
    else:
        st.info("Nenhum jogo futuro disponível para apostas no momento.")
    conn.close()

# 8. ABAS COMPLEMENTARES DE ACORDO COM O DESIGN DO UOL
with aba_tabela_copa:
    st.header("📊 Tabelas Completas - Primeira Fase")
    st.info("Mapeamento dos 12 grupos oficiais de 4 seleções da Copa do Mundo 2026.")

with aba_chaveamento:
    st.header("🗺️ Segunda Fase (Fase Eliminatória)")
    st.code("Chaveamento Oficial: Dezesseis-avos -> Oitavas de Final -> Quartas -> Semifinal -> Final", language="text")
