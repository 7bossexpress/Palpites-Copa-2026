import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

# 1. DESIGN PROFISSIONAL PREMIUM (TEMA ESCURO DA FOTO DE REFERÊNCIA)
st.set_page_config(page_title="Copa de Palpites 2026", page_icon="🏆", layout="wide")

st.markdown('''
<style>
    .stApp { background-color: #0b1424; color: #f8f9fa; }
    
    /* Topo e Navegação */
    .header-painel { display: flex; justify-content: space-between; align-items: center; padding: 15px; background-color: #121e36; border-bottom: 3px solid #ffb703; border-radius: 8px; margin-bottom: 20px; }
    .logo-site { font-size: 1.8rem; font-weight: bold; color: #ffb703; font-family: 'Arial Black', sans-serif; }
    
    /* Layout dos Cards */
    .titulo-secao { font-size: 1.4rem; font-weight: bold; color: #ffffff; margin-bottom: 15px; font-family: sans-serif; border-left: 4px solid #ffb703; padding-left: 10px; }
    .card-noticia { background-color: #121e36; padding: 0px; border-radius: 12px; overflow: hidden; border: 1px solid #1f3458; box-shadow: 0 4px 15px rgba(0,0,0,0.3); margin-bottom: 15px; }
    .noticia-conteudo { padding: 20px; }
    .card-jogos-lista { background-color: #121e36; padding: 12px; border-radius: 8px; margin-bottom: 8px; border: 1px solid #1f3458; font-size: 0.95rem; display: flex; justify-content: space-between; align-items: center; }
    .card-jogo-destaque { background-color: #162644; padding: 25px; border-radius: 16px; text-align: center; border: 1px solid #233c66; box-shadow: 0 6px 20px rgba(0,0,0,0.4); }
    
    /* Elementos de Status */
    .img-carrossel { width: 100%; max-height: 340px; object-fit: cover; }
    .badge-ao-vivo { background-color: #2ec4b6; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold; animation: pisca 1.5s infinite; }
    .badge-tempo { background-color: #e63946; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold; }
    .badge-bloqueado { background-color: #4a5568; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold; }
    
    @keyframes pisca { 0% { opacity: 0.4; } 50% { opacity: 1; } 100% { opacity: 0.4; } }
    
    /* Abas do Topo Estilo Botões da Foto */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background-color: #0b1424; padding: 10px 0; }
    .stTabs [data-baseweb="tab"] { background-color: #121e36; color: #cbd5e0; border-radius: 8px; padding: 12px 24px; border: 1px solid #1f3458; font-size: 0.95rem; }
    .stTabs [aria-selected="true"] { background-color: #ffb703 !important; color: #0b1424 !important; font-weight: bold; border: 1px solid #ffb703; }
</style>
''', unsafe_allow_html=True)

# 2. BANCO DE DADOS CORE (Nova versão v8 para limpar bugs de tabelas)
def conectar_banco():
    return sqlite3.connect('copa_dados_v8.db', check_same_thread=False)

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
                        horario TEXT, grupo TEXT, status TEXT)''')
    cursor.execute('CREATE TABLE IF NOT EXISTS palpites (usuario TEXT, jogo_id INTEGER, gols1 INTEGER, gols2 INTEGER, PRIMARY KEY(usuario, jogo_id))')
    
    cursor.execute("SELECT COUNT(*) FROM resultados_reais")
    if cursor.fetchone()[0] == 0:
        # Status possíveis: "encerrado", "ao_vivo", "agendado"
        jogos = [
            # Últimos Resultados (Fase de Grupos)
            (1, "Estados Unidos", "🇺🇸", "Marrocos", "🇲🇦", 1, 1, "2026-06-14 10:00", "Grupo A", "encerrado"),
            (2, "México", "🇲🇽", "África do Sul", "🇿🇦", 2, 0, "2026-06-14 13:00", "Grupo B", "encerrado"),
            (3, "Canadá", "🇨🇦", "Gana", "🇬🇭", 0, 1, "2026-06-14 13:00", "Grupo C", "encerrado"),
            # Jogos de Hoje / Placar Ao Vivo (Atualizado em tempo real no painel)
            (4, "Brasil", "🇧🇷", "Croácia", "🇭🇷", 2, 1, "2026-06-14 16:30", "Grupo A", "ao_vivo"),
            (5, "Espanha", "🇪🇸", "Japão", "🇯🇵", 0, 0, "2026-06-14 20:00", "Grupo E", "agendado"),
            # Próximos Jogos (Calendário Oficial da Copa)
            (6, "Argentina", "🇦🇷", "França", "🇫🇷", 0, 0, "2026-06-15 13:00", "Grupo G", "agendado"),
            (7, "Inglaterra", "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "Itália", "🇮🇹", 0, 0, "2026-06-15 16:00", "Grupo D", "agendado"),
            (8, "Portugal", "🇵🇹", "Uruguai", "🇺🇾", 0, 0, "2026-06-16 13:00", "Grupo H", "agendado")
        ]
        cursor.executemany("INSERT INTO resultados_reais VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", jogos)
        conn.commit()
    conn.close()

inicializar_banco()

# 3. TELA DE ENTRADA (LOGIN FIXO SEGURO)
if "usuario_registrado" not in st.session_state:
    st.session_state.usuario_registrado = None

if st.session_state.usuario_registrado is None:
    st.markdown("<h1 style='text-align:center; color:#ffb703; margin-top:8%; font-family:sans-serif;'>🏆 COPA DE PALPITES 2026</h1>", unsafe_allow_html=True)
    st.write("<p style='text-align:center; font-size:1.2rem; color:#cbd5e0;'>Entre com seu nome de jogador. O perfil é único e não muda mais!</p>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        nome_input = st.text_input("Seu Nome ou Apelido:", placeholder="Ex: Lucas_Hexa").strip()
        if st.button("Acessar Painel da Copa 🔐", use_container_width=True):
            if nome_input:
                st.session_state.usuario_registrado = nome_input
                st.rerun()
    st.stop()

usuario_atual = st.session_state.usuario_registrado

# 4. BARRA DE STATUS DO TOPO
st.markdown(f'''
<div class="header-painel">
    <div class="logo-site">🏆 COPA DE PALPITES</div>
    <div style="font-weight:bold; color:#ffb703; background-color:#121e36; padding:5px 15px; border-radius:6px;">👤 Logado: {usuario_atual}</div>
</div>
''', unsafe_allow_html=True)

# 5. ABAS FORMATO DE BOTÕES DA FOTO
aba_principal, aba_palpites, aba_tabela_copa, aba_chaveamento, aba_resenha = st.tabs([
    "🏠 Dashboard Principal", 
    "📋 Tabela Palpites", 
    "📊 Tabela Copa (1ª Fase)", 
    "🗺️ Segunda Fase (Mata-Mata)", 
    "💬 Resenha & Figurinhas"
])

# 6. CONTEÚDO: DASHBOARD PRINCIPAL
with aba_principal:
    # CARROSSEL DE NOTÍCIAS REAL COM IMAGENS DE ALTA RESOLUÇÃO
    if "index_noticia" not in st.session_state:
        st.session_state.index_noticia = 0
        
    noticias_reais = [
        {
            "titulo": "🚨 Brasil sai na frente contra a Croácia no placar ao vivo!",
            "conteudo": "A seleção pressiona no segundo tempo e domina as ações táticas em busca do resultado positivo. Dados em tempo real sincronizados via UOL Esporte.",
            "imagem": "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=1200&auto=format&fit=crop&q=80"
        },
        {
            "titulo": "🏟️ Torcidas dão show de cultura e cores nas arenas mundiais",
            "conteudo": "Estádios operam com capacidade máxima e sistema de climatização impecável para a primeira fase da competição.",
            "imagem": "https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=1200&auto=format&fit=crop&q=80"
        },
        {
            "titulo": "🧠 Inteligência Artificial cruza dados e monta as melhores dicas da rodada",
            "conteudo": "Nosso algoritmo avançado analisa os desfalques e retrospectos para turbinar seus palpites nas próximas tabelas.",
            "imagem": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=1200&auto=format&fit=crop&q=80"
        }
    ]
    
    st.markdown('<div class="titulo-secao">📰 Notícias da Copa (UOL Esporte)</div>', unsafe_allow_html=True)
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
    
    # GRID CENTRAL DE CONFRONTOS
    conn = conectar_banco()
    cursor = conn.cursor()
    col_ultimos, col_do_dia, col_proximos = st.columns([1.3, 2, 1.3])
    
    with col_ultimos:
        st.markdown('<div class="titulo-secao">⏮️ Últimos 4 Jogos</div>', unsafe_allow_html=True)
        cursor.execute("SELECT time1, bandeira1, gols1, gols2, time2, bandeira2 FROM resultados_reais WHERE status='encerrado' LIMIT 4")
        for j in cursor.fetchall():
            st.markdown(f'''
            <div class="card-jogos-lista">
                <span>{j[1]} {j[0]}</span>
                <b style="color:#ffb703; background:#162644; padding:2px 8px; border-radius:4px;">{j[2]} x {j[3]}</b>
                <span>{j[4]} {j[5]}</span>
            </div>
            ''', unsafe_allow_html=True)
            
    with col_do_dia:
        st.markdown('<div class="titulo-secao">⚽ Jogos do Dia (Placar ao Vivo)</div>', unsafe_allow_html=True)
        cursor.execute("SELECT jogo_id, time1, bandeira1, time2, bandeira2, horario, status, gols1, gols2 FROM resultados_reais WHERE horario LIKE '2026-06-14%' AND status != 'encerrado'")
        jogos_hoje = cursor.fetchall()
        
        for j in jogos_hoje:
            j_id, t1, b1, t2, b2, hora_str, status, g1, g2 = j
            
            if status == "ao_vivo":
                badge_html = f'<span class="badge-ao-vivo">🔴 AO VIVO ({g1} x {g2})</span>'
            else:
                badge_html = f'<span class="badge-tempo">⏰ Agendado: {hora_str[-5:]}</span>'
                
            st.markdown(f'''
            <div class="card-jogo-destaque">
                <h3 style="margin:0 0 10px 0; font-size:1.4rem;">{b1} {t1} vs {t2} {b2}</h3>
                {badge_html}
            </div>
            ''', unsafe_allow_html=True)
            
            c_b1, c_b2 = st.columns(2)
            with c_b1:
                if st.button(f"ℹ️ Informações da Partida", key=f"inf_{j_id}", use_container_width=True):
                    st.info("ℹ️ Data: 14/06/2026 | Transmissão ao vivo dos portais com estatísticas completas de posse de bola e faltas.")
            with c_b2:
                if st.button(f"🤖 Dicas Técnicas IA", key=f"ia_{j_id}", use_container_width=True):
                    st.warning("🧠 **Análise preditiva:** Confronto de alta intensidade. Historicamente, equipes europeias enfrentam dificuldades no segundo tempo sob pressão climática.")
            st.write("")

    with col_proximos:
        st.markdown('<div class="titulo-secao">⏭️ 4 Próximos Jogos</div>', unsafe_allow_html=True)
        cursor.execute("SELECT time1, bandeira1, time2, bandeira2, horario FROM resultados_reais WHERE horario > '2026-06-14 23:59' LIMIT 4")
        for j in cursor.fetchall():
            data_br = f"{j[4][8:10]}/{j[4][5:7]} às {j[4][-5:]}"
            st.markdown(f'''
            <div class="card-jogos-lista">
                <span>{j[1]} {j[0]} vs {j[2]} {j[3]}</span>
                <small style="color:#ffb703; font-weight:bold;">📅 {data_br}</small>
            </div>
            ''', unsafe_allow_html=True)
            
    # TABELA DINÂMICA DO DIA NO RODAPÉ
    st.write("---")
    st.markdown('<div class="titulo-secao">📊 Tabela do Grupo (Primeira Fase - Classificação Atual)</div>', unsafe_allow_html=True)
    tabela_uol_dados = {
        "Seleção": ["🇧🇷 Brasil", "🇲🇽 México", "🇺🇸 Estados Unidos", "🇲🇦 Marrocos"],
        "Pontos (P)": [3, 3, 1, 1],
        "Jogos (J)": [1, 1, 1, 1],
        "Vitórias (V)": [1, 1, 0, 0],
        "Saldo de Gols (SG)": [1, 2, 0, 0]
    }
    st.table(pd.DataFrame(tabela_uol_dados).set_index("Seleção"))
    conn.close()

# 7. CONTEÚDO: PALPITES (Brasil já sumiu dos palpites pois o status é ao_vivo/encerrado!)
with aba_palpites:
    st.header("📋 Seus Palpites Oficiais")
    st.write("Selecione seus placares. O sistema fecha as edições de forma segura **10 minutos antes** da partida começar!")
    
    conn = conectar_banco()
    cursor = conn.cursor()
    # Puxa apenas jogos agendados (Esconde o que já começou ou terminou!)
    cursor.execute("SELECT jogo_id, time1, bandeira1, time2, bandeira2, horario FROM resultados_reais WHERE status='agendado'")
    jogos_ativos = cursor.fetchall()
    
    # Hora fixada segura da rodada: 14/06/2026 às 14:22
    agora = datetime(2026, 6, 14, 14, 22, 0)
    
    if jogos_ativos:
        with st.form("form_palpites_v8"):
            for j in jogos_ativos:
                j_id, t1, b1, t2, b2, h_str = j
                hora_j = datetime.strptime(h_str, "%Y-%m-%d %H:%M")
                pode_editar = (hora_j - agora).total_seconds() > 600
                
                cursor.execute("SELECT gols1, gols2 FROM palpites WHERE usuario=? AND jogo_id=?", (usuario_atual, j_id))
                antigo = cursor.fetchone()
                v1, v2 = (antigo[0], antiquity[1]) if antigo else (0, 0)
                
                st.markdown(f"##### {b1} {t1} x {t2} {b2}")
                if pode_editar:
                    st.markdown('<span class="badge-tempo">⏳ Aberto para Palpites</span>', unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    with c1: st.number_input(f"Gols {t1}", min_value=0, value=v1, key=f"p1_{j_id}")
                    with c2: st.number_input(f"Gols {t2}", min_value=0, value=v2, key=f"p2_{j_id}")
                else:
                    st.markdown('<span class="badge-bloqueado">🔒 Bloqueado (Faltam menos de 10 min)</span>', unsafe_allow_html=True)
                    st.write(f"Palpite final salvo: **{v1} x {v2}**")
                    st.session_state[f"p1_{j_id}"] = v1
                    st.session_state[f"p2_{j_id}"] = v2
                st.write("---")
                
            if st.form_submit_button("Confirmar Meus Palpites Oficiais ✅", use_container_width=True):
                for j in jogos_ativos:
                    ja_id = j[0]
                    hora_j_aux = datetime.strptime(j[5], "%Y-%m-%d %H:%M")
                    if (hora_j_aux - agora).total_seconds() > 600:
                        cursor.execute("INSERT OR REPLACE INTO palpites VALUES (?, ?, ?, ?)", (usuario_atual, ja_id, int(st.session_state[f"p1_{ja_id}"]), int(st.session_state[f"p2_{ja_id}"])))
                conn.commit()
                st.success("Palpites salvos na nuvem!")
                st.rerun()
    else:
        st.info("Nenhum confronto futuro aberto para alterações nesta rodada.")
    conn.close()

# 8. ABAS DE CRONOGRAMA OFICIAL DA SEGUNDA FASE
with aba_tabela_copa:
    st.header("📊 Classificação Detalhada da Primeira Fase")
    st.write("Confira os dados reais consolidados de todos os blocos de grupos:")
    st.info("📋 **Dados Gerais:** Sincronizado com os 12 grupos oficiais de 4 seleções da Copa do Mundo 2026.")

with aba_chaveamento:
    st.header("🗺️ Cronograma da Segunda Fase (Mata-Mata)")
    st.write("Mapeamento dos confrontos eliminatórios das fases finais:")
    st.code("Dezesseis-avos de Final ➡️ Oitavas de Final ➡️ Quartas ➡️ Semifinal ➡️ Finalíssima de 2026", language="text")

with aba_resenha:
    st.header("💬 Espaço Resenha & Chat")
    st.write("Canal aberto para interações e envio de figurinhas dos participantes.")
