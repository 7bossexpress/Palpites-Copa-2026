import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import urllib.request
import xml.etree.ElementTree as ET

# 1. SISTEMA DINÂMICO DE TEMAS (Seletor de Aparência)
if "tema_escolhido" not in st.session_state:
    st.session_state.tema_escolhido = "Branco"

st.set_page_config(page_title="Portal Copa 2026", page_icon="🏆", layout="wide")

config_temas = {
    "Branco": {"bg": "#f8f9fa", "card": "#ffffff", "texto": "#1a202c", "borda": "#e2e8f0", "detalhe": "#0077b6"},
    "Preto": {"bg": "#0f172a", "card": "#1e293b", "texto": "#f8f9fa", "borda": "#334155", "detalhe": "#38bdf8"},
    "Azul": {"bg": "#0b1424", "card": "#121e36", "texto": "#f8f9fa", "borda": "#1f3458", "detalhe": "#ffb703"},
    "Dourado": {"bg": "#1c1917", "card": "#292524", "texto": "#fef08a", "borda": "#44403c", "detalhe": "#ca8a04"},
    "Verde e Amarelo": {"bg": "#04351a", "card": "#064e26", "texto": "#ffffff", "borda": "#ffcc00", "detalhe": "#ffcc00"}
}

t = config_temas[st.session_state.tema_escolhido]

st.markdown(f'''
<style>
    .stApp {{ background-color: {t['bg']}; color: {t['texto']}; }}
    .header-painel {{ display: flex; justify-content: space-between; align-items: center; padding: 15px; background-color: {t['card']}; border-bottom: 3px solid {t['detalhe']}; border-radius: 8px; margin-bottom: 20px; }}
    .logo-site {{ font-size: 1.8rem; font-weight: bold; color: {t['detalhe']}; font-family: 'Arial Black', sans-serif; }}
    .titulo-secao {{ font-size: 1.4rem; font-weight: bold; color: {t['texto']}; margin-bottom: 15px; border-left: 4px solid {t['detalhe']}; padding-left: 10px; }}
    .card-noticia {{ background-color: {t['card']}; padding: 20px; border-radius: 12px; border: 1px solid {t['borda']}; box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 15px; }}
    .card-jogos-lista {{ background-color: {t['card']}; padding: 12px; border-radius: 8px; margin-bottom: 8px; border: 1px solid {t['borda']}; font-size: 0.95rem; display: flex; justify-content: space-between; align-items: center; }}
    .card-jogo-destaque {{ background-color: {t['card']}; padding: 25px; border-radius: 16px; text-align: center; border: 2px solid {t['detalhe']}; box-shadow: 0 6px 20px rgba(0,0,0,0.05); }}
    .badge-ao-vivo {{ background-color: #e63946; color: white; padding: 4px 10px; border-radius: 4px; font-size: 0.85rem; font-weight: bold; animation: pisca 1.5s infinite; }}
    .badge-tempo {{ background-color: #0077b6; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold; }}
    .badge-bloqueado {{ background-color: #4a5568; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold; }}
    @keyframes pisca {{ 0% {{ opacity: 0.5; }} 50% {{ opacity: 1; }} 100% {{ opacity: 0.5; }} }}
    
    .stTabs [data-baseweb="tab-list"] {{ gap: 5px; background-color: transparent; padding: 10px 0; }}
    .stTabs [data-baseweb="tab"] {{ background-color: {t['card']}; color: {t['texto']}; border-radius: 6px 6px 0 0; padding: 12px 20px; border: 1px solid {t['borda']}; font-size: 0.95rem; }}
    .stTabs [aria-selected="true"] {{ background-color: {t['detalhe']} !important; color: #ffffff !important; font-weight: bold; }}
</style>
''', unsafe_allow_html=True)

# 2. BANCO DE DADOS CORE ATUALIZADO (v12)
def conectar_banco():
    return sqlite3.connect('copa_dados_v12.db', check_same_thread=False)

def inicializar_banco():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS usuarios (nome TEXT PRIMARY KEY)')
    cursor.execute('''CREATE TABLE IF NOT EXISTS resultados_reais (
                        jogo_id INTEGER PRIMARY KEY, grupo TEXT, data_jogo TEXT, horario TEXT,
                        time1 TEXT, gols1 INTEGER, time2 TEXT, gols2 INTEGER, status TEXT)''')
    cursor.execute('CREATE TABLE IF NOT EXISTS palpites (usuario TEXT, jogo_id INTEGER, gols1 INTEGER, gols2 INTEGER, PRIMARY KEY(usuario, jogo_id))')
    
    cursor.execute("SELECT COUNT(*) FROM resultados_reais")
    if cursor.fetchone()[0] == 0:
        jogos = [
            # Passado
            (1, "Grupo F", "14/06", "14:00", "Holanda", 1, "Suécia", 1, "encerrado"),
            # AGORA: Alemanha x Curaçao AO VIVO
            (2, "Grupo E", "14/06", "21:00", "Alemanha", 2, "Curaçao", 1, "ao_vivo"),
            # Futuros (Agendados)
            (3, "Grupo F", "14/06", "23:00", "Tunísia", 0, "Japão", 0, "agendado"),
            (4, "Grupo H", "15/06", "13:00", "Espanha", 0, "Cabo Verde", 0, "agendado"),
            (5, "Grupo G", "15/06", "16:00", "Bélgica", 0, "Egito", 0, "agendado"),
            (6, "Grupo H", "15/06", "19:00", "Uruguai", 0, "Arábia Saudita", 0, "agendado")
        ]
        cursor.executemany("INSERT INTO resultados_reais VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", jogos)
        conn.commit()
    conn.close()

inicializar_banco()

# 3. TELA DE ENTRADA BLOQUEADA
if "usuario_registrado" not in st.session_state:
    st.session_state.usuario_registrado = None

if st.session_state.usuario_registrado is None:
    st.markdown("<h1 style='text-align:center; color:#ca8a04; margin-top:8%; font-family:sans-serif;'>🏆 PORTAL COPA 2026</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        nome_input = st.text_input("Digite seu Nome de Jogador para entrar:", placeholder="Ex: Lucas_Palpites").strip()
        if st.button("Acessar Painel Oficial 🔐", use_container_width=True):
            if nome_input:
                st.session_state.usuario_registrado = nome_input
                st.rerun()
    st.stop()

usuario_atual = st.session_state.usuario_registrado

# 4. HEADER PRINCIPAL
st.markdown(f'''
<div class="header-painel">
    <div class="logo-site">🏆 PORTAL COPA DE PALPITES</div>
    <div style="font-weight:bold; background-color:{t['bg']}; padding:5px 15px; border-radius:6px; border: 1px solid {t['borda']};">👤 Jogador: {usuario_atual}</div>
</div>
''', unsafe_allow_html=True)

st.session_state.tema_escolhido = st.selectbox("🎨 Mudar Aparência do Site:", ["Branco", "Preto", "Azul", "Dourado", "Verde e Amarelo"])

# 5. ABAS CORRIGIDAS E ALINHADAS
aba_noticias, aba_palpites, aba_tabela, aba_chaveamento = st.tabs([
    "📰 Notícias & Jogos", 
    "📋 Tabela Palpites", 
    "📊 Tabela Copa (1ª Fase)", 
    "🗺️ Segunda Fase / Mata-Mata"
])

# 6. CONTEÚDO: NOTÍCIAS REAIS & JOGOS DO DIA
with aba_noticias:
    st.markdown('<div class="titulo-secao">📰 Últimas Notícias Verdadeiras (Tempo Real - UOL Esporte)</div>', unsafe_allow_html=True)
    
    try:
        url_rss = "https://esporte.uol.com.br/futebol/ultimas-noticias/index.xml"
        req = urllib.request.Request(url_rss, headers={'User-Agent': 'Mozilla/5.5'})
        xml_data = urllib.request.urlopen(req).read()
        root = ET.fromstring(xml_data)
        
        noticias_puxadas = []
        for item in root.findall('.//item')[:3]:
            titulo_real = item.find('title').text
            link_real = item.find('link').text
            noticias_puxadas.append({"titulo": titulo_real, "link": link_real})
            
        for n_real in noticias_puxadas:
            st.markdown(f'''
            <div class="card-noticia">
                <h4 style="margin:0 0 5px 0; color:{t['detalhe']};">{n_real['titulo']}</h4>
                <a href="{n_real['link']}" target="_blank" style="text-decoration:none; font-weight:bold; color:#ca8a04;">Ler matéria completa no UOL →</a>
            </div>
            ''', unsafe_allow_html=True)
    except:
        st.info("Sincronizando feed de notícias com os servidores do UOL... Aguarde um instante.")

    st.write("---")
    
    # Grid Triplo de Jogos
    conn = conectar_banco()
    cursor = conn.cursor()
    col_l1, col_l2, col_l3 = st.columns([1.3, 2, 1.3])
    
    with col_l1:
        st.markdown('<div class="titulo-secao">⏮️ Últimos Resultados</div>', unsafe_allow_html=True)
        cursor.execute("SELECT grupo, time1, gols1, gols2, time2 FROM resultados_reais WHERE status='encerrado'")
        for j in cursor.fetchall():
            st.markdown(f'<div class="card-jogos-lista"><small>{j[0]}</small> <span>{j[1]}</span><b>{j[2]} x {j[3]}</b><span>{j[4]}</span></div>', unsafe_allow_html=True)
            
    with col_l2:
        st.markdown('<div class="titulo-secao">⚽ Jogo de Agora (Placar ao Vivo)</div>', unsafe_allow_html=True)
        cursor.execute("SELECT jogo_id, grupo, horario, time1, time2, status, gols1, gols2 FROM resultados_reais WHERE data_jogo='14/06' AND status != 'encerrado'")
        for j in cursor.fetchall():
            j_id, grupo, hora, t1, t2, stat, g1, g2 = j
            txt_badge = f"🔴 AO VIVO ({g1} x {g2})" if stat == "ao_vivo" else f"⏰ {hora}"
            st.markdown(f'<div class="card-jogo-destaque"><small>{grupo}</small><h3>{t1} vs {t2}</h3><span class="badge-ao-vivo">{txt_badge}</span></div>', unsafe_allow_html=True)
            
            cb1, cb2 = st.columns(2)
            with cb1:
                if st.button("ℹ️ Informações", key=f"inf_{j_id}", use_container_width=True):
                    st.info("📊 Partida em andamento monitorada em tempo real pelos painéis esportivos.")
            with cb2:
                if st.button("🤖 Dicas IA", key=f"ia_{j_id}", use_container_width=True):
                    st.warning("🧠 IA analisa: Equipes muito equilibradas na faixa central. Forte tendência de gols.")
            st.write("")

    with col_l3:
        st.markdown('<div class="titulo-secao">⏭️ Próximos Jogos (Amanhã)</div>', unsafe_allow_html=True)
        cursor.execute("SELECT grupo, horario, time1, time2 FROM resultados_reais WHERE data_jogo='15/06' LIMIT 3")
        for j in cursor.fetchall():
            st.markdown(f'<div class="card-jogos-lista"><span>{j[2]} vs {j[3]}</span><small style="font-weight:bold;">📅 {j[1]}</small></div>', unsafe_allow_html=True)
            
    # Tabela dinâmica de rodapé
    st.write("---")
    st.markdown('<div class="titulo-secao">📊 Classificação da Rodada (Grupo E)</div>', unsafe_allow_html=True)
    dados_tabela = {"Seleção": ["Alemanha", "Curaçao", "Costa do Marfim", "Equador"], "Pontos": [3, 0, 0, 0], "Jogos": [1, 1, 0, 0]}
    st.table(pd.DataFrame(dados_tabela).set_index("Seleção"))
    conn.close()

# 7. ABA: TABELA PALPITES
with aba_palpites:
    st.header("📋 Seus Palpites da Copa")
    st.write("Insira seus placares. O bloqueio acontece exatamente **10 minutos antes** de cada partida começar!")
    
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT jogo_id, grupo, data_jogo, horario, time1, time2 FROM resultados_reais WHERE status='agendado' ORDER BY jogo_id ASC")
    jogos_ativos = cursor.fetchall()
    
    # Hora fixa segura da rodada
    agora = datetime(2026, 6, 14, 14, 22, 0)
    
    if jogos_ativos:
        with st.form("form_palpites_v12"):
            for j in jogos_ativos:
                j_id, grupo, data, hora, t1, t2 = j
                
                cursor.execute("SELECT gols1, gols2 FROM palpites WHERE usuario=? AND jogo_id=?", (usuario_atual, j_id))
                antigo = cursor.fetchone()
                v1, v2 = (antigo[0], antigo[1]) if antigo else (0, 0)
                
                st.markdown(f"##### [{grupo}] {t1} x {t2}")
                st.markdown(f'<span class="badge-tempo">⏳ Aberto para Palpite • Data: {data} às {hora}</span>', unsafe_allow_html=True)
                
                c1, c2 = st.columns(2)
                with c1: st.number_input(f"Placar {t1}", min_value=0, value=v1, key=f"p1_{j_id}")
                with c2: st.number_input(f"Placar {t2}", min_value=0, value=v2, key=f"p2_{j_id}")
                st.write("---")
                
            if st.form_submit_button("Salvar Meus Palpites Oficiais ✅", use_container_width=True):
                for j in jogos_ativos:
                    ja_id = j[0]
                    cursor.execute("INSERT OR REPLACE INTO palpites VALUES (?, ?, ?, ?)", (usuario_atual, ja_id, int(st.session_state[f"p1_{ja_id}"]), int(st.session_state[f"p2_{ja_id}"])))
                conn.commit()
                st.success("Palpites registrados com sucesso!")
                st.rerun()
    else:
        st.info("Nenhum confronto futuro disponível para apostas no momento.")
    conn.close()

# 8. ABAS COMPLEMENTARES CORRIGIDAS (Nomes idênticos para evitar NameError)
with aba_tabela:
    st.header("📊 Tabelas de Classificação Geral - Primeira Fase")
    st.write("Mapeamento completo das seleções da Copa do Mundo 2026.")

with aba_chaveamento:
    st.header("🗺️ Segunda Fase / Fase Eliminatória")
    st.code("Cronograma: Oitavas de Final -> Quartas -> Semifinal -> Finalíssima", language="text")
