# Vamos recriar o código completo em Python para o arquivo app.py
# Modificações:
# 1. Tela de Entrada limpa pedindo o nome para acessar o site.
# 2. Design moderno no tema Copa do Mundo (Cores verde, amarelo, azul, dourado).
# 3. Informações dos Próximos Jogos em destaque (Fase de Grupos Completa e Simulações).
# 4. Abas organizadas: 📋 Dar Palpites, 📊 Ranking Geral, 🗂️ Grupos da Copa, 🗺️ Chaveamento (Mata-Mata), 💬 Resenha.

app_code_v2 = """import streamlit as st
import sqlite3
import pandas as pd

# 1. CONFIGURAÇÃO DA PÁGINA COM ESTILO COPA DO MUNDO
st.set_page_config(page_title="Arena Copa do Mundo 2026", page_icon="⚽", layout="wide")

# Estilização CSS para deixar o layout moderno e bonito (Tema Futebol)
st.markdown('''
<style>
    .stApp {
        background-color: #0d1b2a;
        color: #f8f9fa;
    }
    .titulo-principal {
        text-align: center;
        color: #ffb703;
        font-family: 'Arial Black', Gadget, sans-serif;
        font-size: 3rem;
        margin-bottom: 20px;
    }
    .card-jogo {
        background-color: #1b263b;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #00b4d8;
        margin-bottom: 10px;
    }
    .nome-time {
        font-size: 1.2rem;
        font-weight: bold;
    }
</style>
''', unsafe_allow_html=True)

# 2. BANCO DE DADOS (SQLite)
def conectar_banco():
    return sqlite3.connect('copa_dados_v2.db', check_same_thread=False)

def inicializar_banco():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS chat (id INTEGER PRIMARY KEY AUTOINCREMENT, usuario TEXT, mensagem TEXT, sticker TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS resultados_reais (jogo_id INTEGER PRIMARY KEY, rodada TEXT, time1 TEXT, time2 TEXT, gols1 INTEGER, gols2 INTEGER, encerrado INTEGER DEFAULT 0)')
    cursor.execute('CREATE TABLE IF NOT EXISTS palpites (id INTEGER PRIMARY KEY AUTOINCREMENT, usuario TEXT, jogo_id INTEGER, gols1 INTEGER, gols2 INTEGER, UNIQUE(usuario, jogo_id))')
    
    # Inserir os jogos iniciais da Fase de Grupos se estiver vazio
    cursor.execute("SELECT COUNT(*) FROM resultados_reais")
    if cursor.fetchone()[0] == 0:
        jogos_iniciais = [
            (1, "Rodada 1", "Brasil", "Marrocos", 0, 0, 0),
            (2, "Rodada 1", "Espanha", "Japão", 0, 0, 0),
            (3, "Rodada 1", "Argentina", "França", 0, 0, 0),
            (4, "Rodada 1", "EUA", "Itália", 0, 0, 0),
            (5, "Rodada 2", "Brasil", "Espanha", 0, 0, 0),
            (6, "Rodada 2", "Marrocos", "Japão", 0, 0, 0),
        ]
        cursor.executemany("INSERT INTO resultados_reais VALUES (?, ?, ?, ?, ?, ?, ?)", jogos_iniciais)
        conn.commit()
    conn.close()

inicializar_banco()

# 3. TELA DE ENTRADA (LOGIN DE ACESSO)
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

if st.session_state.usuario_logado is None:
    st.markdown('<div class="titulo-principal">🏆 Bem-vindo à Arena Copa 2026</div>', unsafe_allow_html=True)
    st.write("<p style='text-align: center; font-size:1.2rem;'>Para entrar e começar a palpitar com seus amigos, digite o seu nome abaixo:</p>", unsafe_allow_html=True)
    
    col_central_1, col_central_2, col_central_3 = st.columns([1, 2, 1])
    with col_central_2:
        nome_entrada = st.text_input("Seu Nome ou Apelido:", placeholder="Ex: JoãoGamer, AdminSecret, Lucas_M").strip()
        botao_entrar = st.button("Entrar no Painel da Copa ⚽", use_container_width=True)
        
        if botao_entrar and nome_entrada:
            st.session_state.usuario_logado = nome_entrada
            st.rerun()
    st.stop()  # Trava a execução do código aqui para ninguém ver o site sem colocar o nome primeiro.

# --- SE O USUÁRIO ESTIVER LOGADO, MOSTRA O SITE COMPLETO ABAIXO ---

usuario_atual = st.session_state.usuario_logado

# Menu Lateral de Logout e Controle do Admin
st.sidebar.markdown(f"### 👤 Logado como: **{usuario_atual}**")
if usuario_atual == "AdminSecret":
    st.sidebar.success("👑 Modo Organizador Ativo!")
if st.sidebar.button("Sair / Mudar de Conta 🚪"):
    st.session_state.usuario_logado = None
    st.rerun()

# Cabeçalho Principal do Painel
st.markdown('<div class="titulo-principal">⚽ Central da Copa do Mundo 2026</div>', unsafe_allow_html=True)

# Bloco com Informações dos Próximos Jogos em Destaque no Topo
st.markdown("### 📅 Próximos Grandes Confrontos")
col_j1, col_j2, col_j3 = st.columns(3)
with col_j1:
    st.markdown('<div class="card-jogo"><span class="nome-time">🇧🇷 Brasil x Marrocos 🇲🇦</span><br><small>Fase de Grupos • Hoje às 16h</small></div>', unsafe_allow_html=True)
with col_j2:
    st.markdown('<div class="card-jogo"><span class="nome-time">🇪🇸 Espanha x Japão 🇯🇵</span><br><small>Fase de Grupos • Amanhã às 13h</small></div>', unsafe_allow_html=True)
with col_j3:
    st.markdown('<div class="card-jogo"><span class="nome-time">🇦🇷 Argentina x França 🇫🇷</span><br><small>Fase de Grupos • Depois de amanhã às 21h</small></div>', unsafe_allow_html=True)

# 4. CRIAÇÃO DAS ABAS ORGANIZADAS E LEGAIS
aba_palpites, aba_ranking, aba_grupos, aba_chaveamento, aba_chat = st.tabs([
    "📋 Dar Meus Palpites", 
    "📊 Ranking Geral", 
    "🗂️ Grupos & Atualizações", 
    "🗺️ Chaveamento / Mata-Mata",
    "💬 Resenha & Figurinhas"
])

# --- ABA 1: DAR PALPITES ---
with aba_palpites:
    st.header("📝 Faça suas apostas!")
    st.write("Insira os placares abaixo e clique no botão no final para salvar tudo de uma vez.")
    
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT jogo_id, rodada, time1, time2, encerrado, gols1, gols2 FROM resultados_reais")
    jogos = cursor.fetchall()
    
    with st.form("form_palpites_v2"):
        for jogo in jogos:
            j_id, rodada, t1, t2, enc, r1, r2 = jogo
            st.markdown(f"##### **{rodada} - Jogo #{j_id}:** {t1} x {t2}")
            if enc:
                st.markdown(f"⚠️ *Jogo Encerrado! Placar Real Oficial: {r1} x {r2}*")
                
            cursor.execute("SELECT gols1, gols2 FROM palpites WHERE usuario=? AND jogo_id=?", (usuario_atual, j_id))
            palpite_antigo = cursor.fetchone()
            p1_val = palpite_antigo[0] if palpite_antigo else 0
            p2_val = palpite_antigo[1] if palpite_antigo else 0
            
            c1, c2 = st.columns(2)
            with c1:
                st.number_input(f"Gols de {t1}", min_value=0, value=p1_val, key=f"p1_{j_id}")
            with c2:
                st.number_input(f"Gols de {t2}", min_value=0, value=p2_val, key=f"p2_{j_id}")
            st.write("---")
            
        if st.form_submit_button("Salvar Todos os Meus Palpites ✅", use_container_width=True):
            for j_aux in jogos:
                ja_id = j_aux[0]
                ga1 = st.session_state[f"p1_{ja_id}"]
                ga2 = st.session_state[f"p2_{ja_id}"]
                cursor.execute("INSERT OR REPLACE INTO palpites (usuario, jogo_id, gols1, gols2) VALUES (?, ?, ?, ?)", (usuario_atual, ja_id, ga1, ga2))
            conn.commit()
            st.success("Seus palpites foram guardados com sucesso!")
            st.rerun()

    # Painel Secreto do Admin (Organizador) para colocar placar real dos jogos
    if usuario_atual == "AdminSecret":
        st.write("---")
        st.subheader("⚙️ Painel de Resultados do Organizador")
        for jogo in jogos:
            j_id, rodada, t1, t2, enc, r1, r2 = jogo
            with st.expander(f"Definir Placar Oficial - Jogo #{j_id} ({t1} x {t2})"):
                res1 = st.number_input(f"Placar Real {t1}", min_value=0, value=r1, key=f"res1_{j_id}")
                res2 = st.number_input(f"Placar Real {t2}", min_value=0, value=r2, key=f"res2_{j_id}")
                finalizar = st.checkbox("Encerrar partida e dar pontos?", value=bool(enc), key=f"enc_{j_id}")
                if st.button(f"Salvar Resultado Oficial Jogo #{j_id}"):
                    cursor.execute("UPDATE resultados_reais SET gols1=?, gols2=?, encerrado=? WHERE jogo_id=?", (res1, res2, 1 if finalizar else 0, j_id))
                    conn.commit()
                    st.success("Resultado oficial computado!")
                    st.rerun()
    conn.close()

# --- ABA 2: RANKING GERAL ---
with aba_ranking:
    st.header("📊 Quem está ganhando o Bolão?")
    
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT usuario, jogo_id, gols1, gols2 FROM palpites")
    todos_palpites = cursor.fetchall()
    cursor.execute("SELECT jogo_id, gols1, gols2, encerrado FROM resultados_reais WHERE encerrado=1")
    resultados_oficiais = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}
    conn.close()
    
    pontos_usuarios = {}
    for palp in todos_palpites:
        user, j_id, pg1, pg2 = palp
        if user not in pontos_usuarios:
            pontos_usuarios[user] = 0
        if j_id in resultados_oficiais:
            rg1, rg2 = resultados_oficiais[j_id]
            if pg1 == rg1 and pg2 == rg2:
                pontos_usuarios[user] += 25
            elif (pg1 > pg2 and rg1 > rg2) or (pg1 < pg2 and rg1 < rg2) or (pg1 == pg2 and rg1 == rg2):
                if (pg1 - pg2) == (rg1 - rg2):
                    pontos_usuarios[user] += 18
                else:
                    pontos_usuarios[user] += 10
                    
    if pontos_usuarios:
        df = pd.DataFrame(list(pontos_usuarios.items()), columns=["Nome do Amigo", "Pontos Acumulados"])
        df = df.sort_values(by="Pontos Acumulados", ascending=False).reset_index(drop=True)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Nenhum ponto computado ainda. Aguardando o início e encerramento de jogos pelo Organizador.")

# --- ABA 3: GRUPOS E ATUALIZAÇÕES ---
with aba_grupos:
    st.header("🗂️ Grupos Oficiais da Copa do Mundo 2026")
    st.write("Confira como estão divididos os principais grupos desta simulação:")
    
    g_col1, g_col2 = st.columns(2)
    with g_col1:
        st.info("### 🟢 GRUPO A\n1. Brasil 🇧🇷\n2. Espanha 🇪🇸\n3. Marrocos 🇲🇦\n4. Japão 🇯🇵")
    with g_col2:
        st.warning("### 🔵 GRUPO B\n1. Argentina 🇦🇷\n2. França 🇫🇷\n3. EUA 🇺🇸\n4. Itália 🇮🇹")
        
    st.write("---")
    st.subheader("📢 Atualizações e Notícias Rápidas")
    st.markdown('''
    - **[Notícia]** Seleção Brasileira chega focada para a estreia em busca do Hexa!
    - **[Logística]** Estádios prontos e gramados impecáveis na América do Norte.
    ''')

# --- ABA 4: CHAVEAMENTO / MATA-MATA ---
with aba_chaveamento:
    st.header("🗺️ Árvore de Chaveamento (Mata-Mata)")
    st.write("Os dois melhores de cada grupo avançam para o Chaveamento Final. Veja como vai ficar:")
    
    ch_col1, ch_col2, ch_col3 = st.columns(3)
    with ch_col1:
        st.markdown("### 🏆 Quartas de Final")
        st.code("Jogo 1: 1º Grupo A x 2º Grupo B\nJogo 2: 1º Grupo B x 2º Grupo A", language="text")
    with ch_col2:
        st.markdown("### ⚡ Semifinais")
        st.code("Vencedor Jogo 1 x Vencedor Jogo 2", language="text")
    with ch_col3:
        st.markdown("### 👑 Grande Final")
        st.code("[ Vencedor Semi 1 x Vencedor Semi 2 ]", language="text")

# --- ABA 5: CHAT & RESENHA ---
with aba_chat:
    st.header("💬 Resenha ao Vivo")
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    stickers_lista = ["⚽", "🏆", "🇧🇷", "🔥", "👑", "🤣", "💥", "👀"]
    with st.form("form_chat_v2", clear_on_submit=True):
        msg = st.text_input("Mande sua mensagem ou provocação:")
        stk = st.selectbox("Escolha um Sticker:", stickers_lista)
        if st.form_submit_button("Enviar Mensagem 🚀") and msg:
            cursor.execute("INSERT INTO chat (usuario, mensagem, sticker) VALUES (?, ?, ?)", (usuario_atual, msg, stk))
            conn.commit()
            st.rerun()
            
    cursor.execute("SELECT usuario, mensagem, sticker FROM chat ORDER BY id DESC LIMIT 15")
    mensagens = cursor.fetchall()
    conn.close()
    
    for m in mensagens:
        st.markdown(f"💬 **{m[0]}**: {m[1]} {m[2]}")
"""

with open("app.py", "w", encoding="utf-8") as f:
    f.write(app_code_v2)
print("File app.py updated with the requested layout.")
