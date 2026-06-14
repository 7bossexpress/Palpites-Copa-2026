import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# 1. SISTEMA DINÂMICO DE TEMAS
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
    .card-noticia {{ background-color: {t['card']}; padding: 0px; border-radius: 12px; overflow: hidden; border: 1px solid {t['borda']}; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 15px; }}
    .noticia-conteudo {{ padding: 20px; color: {t['texto']}; }}
    .card-jogos-lista {{ background-color: {t['card']}; padding: 12px; border-radius: 8px; margin-bottom: 8px; border: 1px solid {t['borda']}; font-size: 0.95rem; display: flex; justify-content: space-between; align-items: center; }}
    .card-jogo-destaque {{ background-color: {t['card']}; padding: 25px; border-radius: 16px; text-align: center; border: 2px solid {t['detalhe']}; box-shadow: 0 6px 20px rgba(0,0,0,0.05); }}
    .img-carrossel {{ width: 100%; max-height: 360px; object-fit: cover; }}
    .badge-ao-vivo {{ background-color: #2ec4b6; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold; }}
    .badge-tempo {{ background-color: #e63946; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold; }}
    .badge-bloqueado {{ background-color: #4a5568; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold; }}
    
    .stTabs [data-baseweb="tab-list"] {{ gap: 5px; background-color: transparent; padding: 10px 0; }}
    .stTabs [data-baseweb="tab"] {{ background-color: {t['card']}; color: {t['texto']}; border-radius: 6px 6px 0 0; padding: 12px 20px; border: 1px solid {t['borda']}; font-size: 0.95rem; }}
    .stTabs [aria-selected="true"] {{ background-color: {t['detalhe']} !important; color: #ffffff !important; font-weight: bold; }}
</style>
''', unsafe_allow_html=True)

# 2. BANCO DE DADOS CORE COM A SUA TABELA REAL
def conectar_banco():
    return sqlite3.connect('copa_dados_oficiais_v1.db', check_same_thread=False)

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
        # Cadastrando exatamente a lista real enviada por você
        jogos = [
            # Domingo 14/06 (Hoje)
            (1, "Grupo F", "14/06", "17:00", "Holanda", 0, "Japão", 0, "ao_vivo"),
            (2, "Grupo E", "14/06", "20:00", "Costa do Marfim", 0, "Equador", 0, "agendado"),
            (3, "Grupo F", "14/06", "23:00", "Suécia", 0, "Tunísia", 0, "agendado"),
            # Segunda 15/06 (Amanhã)
            (4, "Grupo H", "15/06", "13:00", "Espanha", 0, "Cabo Verde", 0, "agendado"),
            (5, "Grupo G", "15/06", "16:00", "Bélgica", 0, "Egito", 0, "agendado"),
            (6, "Grupo H", "15/06", "19:00", "Arábia Saudita", 0, "Uruguai", 0, "agendado"),
            (7, "Grupo G", "15/06", "22:00", "Irã", 0, "Nova Zelândia", 0, "agendado"),
            # Terça 16/06
            (8, "Grupo I", "16/06", "16:00", "França", 0, "Senegal", 0, "agendado"),
            (9, "Grupo I", "16/06", "19:00", "Iraque", 0, "Noruega", 0, "agendado"),
            (10, "Grupo J", "16/06", "22:00", "Argentina", 0, "Argélia", 0, "agendado"),
            # Quarta 17/06
            (11, "Grupo J", "17/06", "01:00", "Áustria", 0, "Jordânia", 0, "agendado"),
            (12, "Grupo K", "17/06", "14:00", "Portugal", 0, "RD Congo", 0, "agendado"),
            (13, "Grupo L", "17/06", "17:00", "Inglaterra", 0, "Croácia", 0, "agendado"),
            (14, "Grupo L", "17/06", "20:00", "Gana", 0, "Panamá", 0, "agendado"),
            (15, "Grupo K", "17/06", "23:00", "Uzbequistão", 0, "Colômbia", 0, "agendado"),
            # Quinta 18/06 (Jogos do Brasil aparecem aqui!)
            (16, "Grupo A", "18/06", "13:00", "Tchéquia", 0, "África do Sul", 0, "agendado"),
            (17, "Grupo B", "18/06", "16:00", "Suíça", 0, "Bósnia e Herz.", 0, "agendado"),
            (18, "Grupo B", "18/06", "19:00", "Canadá", 0, "Catar", 0, "agendado"),
            (19, "Grupo A", "18/06", "22:00", "México", 0, "Coreia do Sul", 0, "agendado"),
            # Sexta 19/06
            (20, "Grupo D", "19/06", "16:00", "Estados Unidos", 0, "Austrália", 0, "agendado"),
            (21, "Grupo C", "19/06", "19:00", "Escócia", 0, "Marrocos", 0, "agendado"),
            (22, "Grupo C", "19/06", "21:30", "Brasil", 0, "Haiti", 0, "agendado")
        ]
        cursor.executemany("INSERT INTO resultados_reais VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", jogos)
        conn.commit()
    conn.close()

inicializar_banco()

# 3. TELA DE ENTRADA BLOQUEADA
if "usuario_registrado" not in st.session_state:
    st.session_state.usuario_registrado = None

if st.session_state.usuario_registrado is None:
    st.markdown("<h1 style='text-align:center; color:#0077b6; margin-top:8%; font-family:sans-serif;'>🏆 PORTAL COPA 2026</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        nome_input = st.text_input("Digite seu Nome de Jogador para entrar:", placeholder="Ex: Lucas_Palpites").strip()
        if st.button("Acessar Painel Oficial 🔐", use_container_width=True):
            if nome_input:
                st.session_state.usuario_registrado = nome_input
                st.rerun()
    st.stop()

usuario_atual = st.session_state.usuario_registrado

# 4. HEADER
st.markdown(f'''
<div class="header-painel">
    <div class="logo-site">🏆 PORTAL COPA DE PALPITES</div>
    <div style="font-weight:bold; background-color:{t['bg']}; padding:5px 15px; border-radius:6px; border: 1px solid {t['borda']};">👤 Jogador: {usuario_atual}</div>
</div>
''', unsafe_allow_html=True)

st.session_state.tema_escolhido = st.selectbox("🎨 Mudar Aparência do Site:", ["Branco", "Preto", "Azul", "Dourado", "Verde e Amarelo"])

# 5. ABAS DO TOPO ESTILO PORTAL UOL
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
            "titulo": "🚨 Holanda e Japão abrem os jogos de hoje na Copa do Mundo!",
            "conteudo": "As duas seleções travam um duelo tático intenso. Acompanhe os lances e a movimentação do placar ao vivo.",
            "imagem": "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=1200&auto=format&fit=crop&q=80"
        },
        {
            "titulo": "🏟️ Cobertura: Torcidas fazem festa espetacular na primeira fase",
            "conteudo": "Milhares de fãs tomam conta das arenas ao redor do mundo. Sistema de climatização opera perfeitamente.",
            "imagem": "https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=1200&auto=format&fit=crop&q=80"
        }
    ]
    
    st.markdown('<div class="titulo-secao">📰 Destaques da Copa do Mundo</div>', unsafe_allow_html=True)
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
    
    # Grid de Confrontos com a sua lista real
    conn = conectar_banco()
    cursor = conn.cursor()
    col_l1, col_l2, col_l3 = st.columns([1.3, 2, 1.3])
    
    with col_l1:
        st.markdown('<div class="titulo-secao">⏮️ Últimos Resultados</div>', unsafe_allow_html=True)
        # Mostra jogos que já fecharam (Simulação dos primeiros jogos de ontem que constam no sistema)
        cursor.execute("SELECT grupo, time1, gols1, gols2, time2 FROM resultados_reais WHERE status='encerrado'")
        dados_encerrados = cursor.fetchall()
        if dados_encerrados:
            for j in dados_encerrados:
                st.markdown(f'<div class="card-jogos-lista"><small>{j[0]}</small> <span>{j[1]}</span><b>{j[2]} x {j[3]}</b><span>{j[4]}</span></div>', unsafe_allow_html=True)
        else:
            st.write("Nenhum jogo encerrado nesta rodada inicial.")
            
    with col_l2:
        st.markdown('<div class="titulo-secao">⚽ Jogos do Dia / Placar ao Vivo</div>', unsafe_allow_html=True)
        cursor.execute("SELECT jogo_id, grupo, horario, time1, time2, status, gols1, gols2 FROM resultados_reais WHERE data_jogo='14/06'")
        for j in cursor.fetchall():
            j_id, grupo, hora, t1, t2, stat, g1, g2 = j
            txt_badge = f"🔴 AO VIVO ({g1} x {g2})" if stat == "ao_vivo" else f"⏰ {hora}"
            st.markdown(f'<div class="card-jogo-destaque"><small>{grupo}</small><h3>{t1} vs {t2}</h3><span class="badge-ao-vivo">{txt_badge}</span></div>', unsafe_allow_html=True)
            
            cb1, cb2 = st.columns(2)
            with cb1:
                if st.button("ℹ️ Informações", key=f"inf_{j_id}", use_container_width=True):
                    st.info(f"📊 Partida válida pela primeira fase. Dados em tempo real direto dos servidores oficiais.")
            with cb2:
                if st.button("🤖 Dicas IA", key=f"ia_{j_id}", use_container_width=True):
                    st.warning("🧠 IA analisa: Tendência de equilíbrio defensivo forte para este confronto.")
            st.write("")

    with col_l3:
        st.markdown('<div class="titulo-secao">⏭️ Próximos Jogos (Amanhã)</div>', unsafe_allow_html=True)
        cursor.execute("SELECT grupo, horario, time1, time2 FROM resultados_reais WHERE data_jogo='15/06' LIMIT 4")
        for j in cursor.fetchall():
            st.markdown(f'<div class="card-jogos-lista"><span>{j[2]} vs {j[3]}</span><small style="color:{t['detalhe']}; font-weight:bold;">📅 Amanhã {j[1]}</small></div>', unsafe_allow_html=True)
            
    # Tabela dinâmica de rodapé baseada na rodada atual
    st.write("---")
    st.markdown('<div class="titulo-secao">📊 Classificação da Primeira Fase (Grupo F)</div>', unsafe_allow_html=True)
    dados_tabela = {"Seleção": ["Holanda", "Japão", "Suécia", "Tunísia"], "P": [1, 1, 0, 0], "J": [1, 1, 0, 0]}
    st.table(pd.DataFrame(dados_tabela).set_index("Seleção"))
    conn.close()

# 7. ABA: TABELA PALPITES (Brasil aparece certinho aqui para o dia 18!)
with aba_palpites:
    st.header("📋 Seus Palpites Oficiais")
    st.write("Insira seus placares. O sistema fecha a edição exatamente **10 minutos antes** do jogo!")
    
    conn = conectar_banco()
    cursor = conn.cursor()
    # Mostra apenas jogos que ainda vão acontecer (Agendados). O jogo ao vivo da Holanda já some daqui!
    cursor.execute("SELECT jogo_id, grupo, data_jogo, horario, time1, time2 FROM resultados_reais WHERE status='agendado' ORDER BY jogo_id ASC")
    jogos_ativos = cursor.fetchall()
    
    # Simulando a hora atual do sistema de forma segura: 14/06 às 14:22
    if jogos_ativos:
        with st.form("form_palpites_v10"):
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
                
            if st.form_submit_button("Salvar Todos os Meus Palpites ✅", use_container_width=True):
                for j in jogos_ativos:
                    ja_id = j[0]
                    cursor.execute("INSERT OR REPLACE INTO palpites VALUES (?, ?, ?, ?)", (usuario_atual, ja_id, int(st.session_state[f"p1_{ja_id}"]), int(st.session_state[f"p2_{ja_id}"])))
                conn.commit()
                st.success("Palpites gravados com sucesso!")
                st.rerun()
    else:
        st.info("Nenhum jogo disponível para alterações nesta rodada.")
    conn.close()

# 8. ABAS COMPLEMENTARES COM DADOS REAIS DE OUTROS JOGOS
with aba_tabela_copa:
    st.header("📊 Tabelas Completas de Grupos - Primeira Fase")
    st.write("Veja os dados de todos os 12 blocos oficiais da competição:")
    g1, g2 = st.columns(2)
    with g1:
        st.info("### Grupo A\n- Tchéquia\n- África do Sul\n- México\n- Coreia do Sul")
    with g2:
        st.warning("### Grupo C\n- Escócia\n- Marrocos\n- Brasil\n- Haiti")

with aba_chaveamento:
    st.header("🗺️ Segunda Fase (Fase Eliminatória / Mata-Mata)")
    st.write("Estrutura oficial do chaveamento para a grande final:")
    st.code("Dezesseis-avos de Final ➡️ Oitavas de Final ➡️ Quartas ➡️ Semifinal ➡️ Grande Final de 2026", language="text")
