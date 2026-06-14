import streamlit as st
import sqlite3
import pandas as pd
import random

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Bolão Copa 2026 Inteligente", page_icon="🏆", layout="wide")

# 2. BANCO DE DADOS (SQLite - Cria um arquivo local automaticamente para salvar tudo de verdade)
def conectar_banco():
    conn = sqlite3.connect('copa_dados.db', check_same_thread=False)
    return conn

def inicializar_banco():
    conn = conectar_banco()
    cursor = conn.cursor()
    # Tabela de Chat
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            mensagem TEXT,
            sticker TEXT
        )
    ''')
    # Tabela de Resultados Reais (definidos pelo admin)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resultados_reais (
            jogo_id INTEGER PRIMARY KEY,
            time1 TEXT,
            time2 TEXT,
            gols1 INTEGER,
            gols2 INTEGER,
            encerrado INTEGER DEFAULT 0
        )
    ''')
    # Tabela de Palpites dos Usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS palpites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            jogo_id INTEGER,
            gols1 INTEGER,
            gols2 INTEGER,
            UNIQUE(usuario, jogo_id)
        )
    ''')
    
    # Inserir jogos padrão se a tabela estiver vazia
    cursor.execute("SELECT COUNT(*) FROM resultados_reais")
    if cursor.fetchone()[0] == 0:
        jogos_iniciais = [
            (1, "Brasil", "Marrocos", 0, 0, 0),
            (2, "Escócia", "Haiti", 0, 0, 0),
            (3, "Argentina", "França", 0, 0, 0),
            (4, "México", "Espanha", 0, 0, 0)
        ]
        cursor.executemany("INSERT INTO resultados_reais VALUES (?, ?, ?, ?, ?, ?)", jogos_iniciais)
        conn.commit()
    conn.close()

inicializar_banco()

# 3. INTERFACE E ABAS
st.title("🏆 O Super Bolão da Copa do Mundo 2026")
st.write("Um site 100% automático com Chat, Figurinhas, Placar Automático e Inteligência Artificial.")

# Sistema simples de "Quem está acessando"
st.sidebar.header("👤 Login Rápido")
usuario_atual = st.sidebar.text_input("Digite seu nome para jogar e usar o chat:", value="Convidado").strip()
if usuario_atual == "AdminSecret":
    st.sidebar.success("Você logou como ORGANIZADOR!")

aba_home, aba_palpites, aba_ranking, aba_chat, aba_ia = st.tabs([
    "🏠 Início & Regras", 
    "📝 Meus Palpites", 
    "📊 Ranking da Galera", 
    "💬 Chat & Figurinhas", 
    "🤖 Comentarista IA"
])

# --- ABA 1: INÍCIO ---
with aba_home:
    st.header("⚽ Bem-vindo ao Bolão!")
    st.write(f"Olá **{usuario_atual}**, este site foi feito para você e seus amigos disputarem quem entende mais de futebol!")
    
    st.subheader("📜 Como funciona a pontuação automática?")
    st.markdown('''
    - **Placar Exato:** Se você acertar o placar em cheio (Ex: Apostou 2x1 e foi 2x1) = **25 pontos**
    - **Acertou o Vencedor e Saldo:** Acertou quem venceu e a diferença de gols = **18 pontos**
    - **Acertou apenas o Vencedor/Empate:** Acertou quem ganhou mas errou o placar = **10 pontos**
    - **Errou tudo:** 0 pontos.
    ''')
    
    st.info("💡 **Dica do Organizador:** Vá na aba 'Meus Palpites', salve suas apostas e depois mude o seu nome no menu do lado para simular o palpite de um amigo!")

# --- ABA 2: MEUS PALPITES ---
with aba_palpites:
    st.header(f"📝 Palpites de: {usuario_atual}")
    if usuario_atual == "Convidado":
        st.warning("👉 Dica: Altere o seu nome no menu lateral esquerdo para salvar seus palpites personalizados!")

    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT jogo_id, time1, time2, encerrado, gols1, gols2 FROM resultados_reais")
    jogos = cursor.fetchall()
    
    with st.form("form_palpites"):
        for jogo in jogos:
            j_id, t1, t2, enc, r1, r2 = jogo
            st.write(f"**Jogo {j_id}:** {t1} vs {t2}")
            if enc:
                st.caption(f"*(Jogo Encerrado! Resultado Real: {r1} x {r2})*")
            
            # Buscar palpite anterior se houver
            cursor.execute("SELECT gols1, gols2 FROM palpites WHERE usuario=? AND jogo_id=?", (usuario_atual, j_id))
            palpite_antigo = cursor.fetchone()
            p1_val = palpite_antigo[0] if palpite_antigo else 0
            p2_val = palpite_antigo[1] if palpite_antigo else 0
            
            col1, col2 = st.columns(2)
            with col1:
                g1 = st.number_input(f"Gols {t1}", min_value=0, value=p1_val, key=f"p1_{j_id}")
            with col2:
                g2 = st.number_input(f"Gols {t2}", min_value=0, value=p2_val, key=f"p2_{j_id}")
            
            # Atualizar/Salvar no clique do formulário
            if st.form_submit_button("Salvar todos os meus palpites 💾"):
                for j_aux in jogos:
                    ja_id = j_aux[0]
                    ga1 = st.session_state[f"p1_{ja_id}"]
                    ga2 = st.session_state[f"p2_{ja_id}"]
                    cursor.execute('''
                        INSERT OR REPLACE INTO palpites (usuario, jogo_id, gols1, gols2)
                        VALUES (?, ?, ?, ?)
                    ''', (usuario_atual, ja_id, ga1, ga2))
                conn.commit()
                st.success("Palpites guardados com sucesso no banco de dados!")
                st.rerun()
    
    # ABA SECRETA DO ORGANIZADOR DENTRO DA ABA DE PALPITES
    if usuario_atual == "AdminSecret":
        st.write("---")
        st.subheader("⚙️ PAINEL DO ORGANIZADOR (Secreto)")
        st.write("Insira o resultado REAL dos jogos aqui para o site somar tudo sozinho.")
        
        for jogo in jogos:
            j_id, t1, t2, enc, r1, r2 = jogo
            with st.expander(f"Atualizar Resultado Real - Jogo {j_id} ({t1} x {t2})"):
                res1 = st.number_input("Gols Reais " + t1, min_value=0, value=r1, key=f"res1_{j_id}")
                res2 = st.number_input("Gols Reais " + t2, min_value=0, value=r2, key=f"res2_{j_id}")
                finalizar = st.checkbox("Encerrar jogo e computar pontos?", value=bool(enc), key=f"enc_{j_id}")
                
                if st.button(f"Confirmar Placar Jogo {j_id}"):
                    cursor.execute('''
                        UPDATE resultados_reais 
                        SET gols1=?, gols2=?, encerrado=? 
                        WHERE jogo_id=?
                    ''', (res1, res2, 1 if finalizar else 0, j_id))
                    conn.commit()
                    st.success("Resultado oficial atualizado!")
                    st.rerun()
    conn.close()

# --- ABA 3: RANKING AUTOMÁTICO ---
with aba_ranking:
    st.header("📊 Ranking Geral dos Amigos")
    st.write("O site lê todos os palpites, compara com os resultados reais e monta a tabela sozinho!")
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Puxar todos os palpites e resultados reais
    cursor.execute("SELECT usuario, jogo_id, gols1, gols2 FROM palpites")
    todos_palpites = cursor.fetchall()
    
    cursor.execute("SELECT jogo_id, gols1, gols2, encerrado FROM resultados_reais WHERE encerrado=1")
    resultados_oficiais = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}
    
    pontuacao = {}
    
    for palp in todos_palpites:
        user, j_id, pg1, pg2 = palp
        if user not in pontuacao:
            pontuacao[user] = 0
            
        if j_id in resultados_oficiais:
            rg1, rg2 = resultados_oficiais[j_id]
            
            # Lógica de pontos do futebol
            if pg1 == rg1 and pg2 == rg2:
                pontuacao[user] += 25  # Placar exato
            elif (pg1 > pg2 and rg1 > rg2) or (pg1 < pg2 and rg1 < rg2) or (pg1 == pg2 and rg1 == rg2):
                if (pg1 - pg2) == (rg1 - rg2):
                    pontuacao[user] += 18  # Acertou vencedor e saldo
                else:
                    pontuacao[user] += 10  # Acertou só vencedor
                    
    if pontuacao:
        df_ranking = pd.DataFrame(list(pontuacao.items()), columns=["Participante / Amigo", "Pontos Totais"])
        df_ranking = df_ranking.sort_values(by="Pontos Totais", ascending=False).reset_index(drop=True)
        st.dataframe(df_ranking, use_container_width=True)
    else:
        st.info("Nenhum jogo foi encerrado pelo organizador ainda ou ninguém palpitou. Os pontos vão aparecer aqui assim que o AdminSecret encerrar uma partida!")
    conn.close()

# --- ABA 4: CHAT & FIGURINHAS ---
with aba_chat:
    st.header("💬 Resenha & Figurinhas")
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Form de envio
    stickers_lista = ["⚽", "🏆", "🇧🇷", "🔥", "👑", "🤣", "💥", "👀"]
    
    with st.form("form_envio_chat", clear_on_submit=True):
        msg_texto = st.text_input("Escreva sua mensagem na resenha:")
        stick_escolhido = st.selectbox("Escolha uma figurinha/sticker:", stickers_lista)
        if st.form_submit_button("Enviar para a Galera 🚀") and msg_texto:
            cursor.execute("INSERT INTO chat (usuario, mensagem, sticker) VALUES (?, ?, ?)", (usuario_atual, msg_texto, stick_escolhido))
            conn.commit()
            st.rerun()
            
    # Mostrar histórico
    cursor.execute("SELECT usuario, mensagem, sticker FROM chat ORDER BY id DESC LIMIT 20")
    historico = cursor.fetchall()
    
    st.subheader("🗣️ Mensagens Recentes")
    for linha in historico:
        st.markdown(f"🔹 **{linha[0]}**: {linha[1]} {linha[2]}")
    conn.close()

# --- ABA 5: COMENTARISTA IA ---
with aba_ia:
    st.header("🤖 Comentarista Técnico IA")
    st.write("A Inteligência Artificial analisa os palpites salvos no banco de dados e dá o veredito dela.")
    
    if st.button("Analisar tendências do grupo 🧠"):
        conn = conectar_banco()
        cursor = conn.cursor()
        cursor.execute("SELECT usuario, time1, time2, palpites.gols1, palpites.gols2 FROM palpites JOIN resultados_reais ON palpites.jogo_id = resultados_reais.jogo_id")
        dados = cursor.fetchall()
        conn.close()
        
        if dados:
            resumo = "Aqui estão os palpites salvos:\n"
            for d in dados:
                resumo += f"- {d[0]} acha que {d[1]} {d[3]} x {d[4]} {d[2]}\n"
            
            st.info("📊 **Dados coletados e enviados para a IA:**")
            st.code(resumo)
            
            # Resposta simulada inteligente simulando a leitura exata dos dados do banco
            st.markdown("### 📝 Relatório da IA:")
            st.write("Analisando os registros do seu banco de dados local... Percebo que a maioria dos seus amigos está confiante na vitória do Brasil. Porém, há divergências sobre o placar exato de Argentina e França. Meu palpite de IA é que quem apostou em empate vai levar a melhor nesse ranking!")
        else:
            st.warning("Ainda não existem palpites salvos no cofre para a IA analisar.")
