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
    .card-jogos-lista {{ background-color: {t['card']}; padding: 12px; border-radius: 8px; margin-bottom: 8px; border: 1px solid {t['borda']}; font-size: 0.95rem; display: flex; justify-content: space-between; align-items: center; }}
    .card-jogo-destaque {{ background-color: {t['card']}; padding: 25px; border-radius: 16px; text-align: center; border: 2px solid {t['detalhe']}; box-shadow: 0 6px 20px rgba(0,0,0,0.05); margin-bottom: 15px; }}
    .badge-ao-vivo {{ background-color: #e63946; color: white; padding: 4px 10px; border-radius: 4px; font-size: 0.85rem; font-weight: bold; }}
    .badge-intervalo {{ background-color: #ca8a04; color: white; padding: 4px 10px; border-radius: 4px; font-size: 0.85rem; font-weight: bold; }}
    .badge-agendado {{ background-color: #0077b6; color: white; padding: 4px 10px; border-radius: 4px; font-size: 0.85rem; font-weight: bold; }}
</style>
''', unsafe_allow_html=True)

# 2. BANCO DE DADOS CORE COMPLETO (v14 - Alinhado com o seu texto)
def conectar_banco():
    return sqlite3.connect('copa_dados_v14.db', check_same_thread=False)

def inicializar_banco():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS usuarios (nome TEXT PRIMARY KEY)')
    cursor.execute('''CREATE TABLE IF NOT EXISTS resultados_reais (
                        jogo_id INTEGER PRIMARY KEY, grupo TEXT, horario TEXT,
                        time1 TEXT, gols1 INTEGER, time2 TEXT, gols2 INTEGER, status TEXT)''')
    cursor.execute('CREATE TABLE IF NOT EXISTS palpites (usuario TEXT, jogo_id INTEGER, gols1 INTEGER, gols2 INTEGER, PRIMARY KEY(usuario, jogo_id))')
    
    cursor.execute("SELECT COUNT(*) FROM resultados_reais")
    if cursor.fetchone()[0] == 0:
        # Inserindo EXATAMENTE o cronograma e os status certos do seu relógio de agora
        jogos = [
            (1, "Grupo E", "Agora", "Alemanha", 3, "Curaçao", 1, "intervalo"),
            (2, "Grupo F", "17:00", "Holanda", 0, "Japão", 0, "agendado"),
            (3, "Grupo E", "20:00", "Costa do Marfim", 0, "Equador", 0, "agendado"),
            (4, "Grupo F", "23:00", "Suécia", 0, "Tunísia", 0, "agendado"),
            # Amanhã
            (5, "Grupo H", "Amanhã 13:00", "Espanha", 0, "Cabo Verde", 0, "agendado"),
            (6, "Grupo G", "Amanhã 16:00", "Bélgica", 0, "Egito", 0, "agendado"),
            (7, "Grupo H", "Amanhã 19:00", "Arábia Saudita", 0, "Uruguai", 0, "agendado")
        ]
        cursor.executemany("INSERT INTO resultados_reais VALUES (?, ?, ?, ?, ?, ?, ?, ?)", jogos)
        conn.commit()
    conn.close()

inicializar_banco()

# 3. LOGIN
if "usuario_registrado" not in st.session_state:
    st.session_state.usuario_registrado = None

if st.session_state.usuario_registrado is None:
    st.markdown("<h1 style='text-align:center; color:#0077b6; margin-top:8%;'>🏆 PORTAL COPA 2026</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        nome_input = st.text_input("Nome do Jogador:", placeholder="Ex: Lucas").strip()
        if st.button("Entrar 🔐", use_container_width=True):
            if nome_input:
                st.session_state.usuario_registrado = nome_input
                st.rerun()
    st.stop()

usuario_atual = st.session_state.usuario_registrado

# 4. DASHBOARD
st.markdown(f'''
<div class="header-painel">
    <div class="logo-site">🏆 PORTAL COPA DE PALPITES</div>
    <div style="font-weight:bold;">👤 Jogador: {usuario_atual}</div>
</div>
''', unsafe_allow_html=True)

st.session_state.tema_escolhido = st.selectbox("🎨 Mudar Cor do Site:", ["Branco", "Preto", "Azul", "Dourado", "Verde e Amarelo"])

aba_jogos, aba_palpites = st.tabs(["⚽ Jogos do Dia (Placar ao Vivo)", "📋 Tabela Palpites"])

with aba_jogos:
    st.markdown('<div class="titulo-secao">🏟️ Partidas de Hoje - Central de Resultados</div>', unsafe_allow_html=True)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT jogo_id, grupo, horario, time1, gols1, time2, gols2, status FROM resultados_reais")
    
    for j in cursor.fetchall():
        j_id, grupo, hora, t1, g1, t2, g2, stat = j
        
        # Define a etiqueta certa baseada no tempo real de agora
        if stat == "intervalo":
            badge = f'<span class="badge-intervalo">🟠 INTERVALO ({g1} x {g2})</span>'
        elif stat == "ao_vivo":
            badge = f'<span class="badge-ao-vivo">🔴 AO VIVO ({g1} x {g2})</span>'
        else:
            badge = f'<span class="badge-agendado">⏰ Horário: {hora}</span>'
            
        st.markdown(f'''
        <div class="card-jogo-destaque">
            <small style="text-transform:uppercase; font-weight:bold;">{grupo}</small>
            <h2 style="margin:10px 0;">{t1} {g1 if stat in ["ao_vivo", "intervalo"] else ""} vs {g2 if stat in ["ao_vivo", "intervalo"] else ""} {t2}</h2>
            {badge}
        </div>
        ''', unsafe_allow_html=True)
        
    # Painel Administrativo Secreto no rodapé para você mudar os placares quando quiser
    st.write("---")
    with st.expander("⚙️ Painel do Organizador (Atualizar Placar do Google/UOL manualmente)"):
        st.write("Como organizador do bolão, mude os placares aqui para atualizar a tela dos seus amigos:")
        cursor.execute("SELECT jogo_id, time1, time2 FROM resultados_reais")
        lista_adm = cursor.fetchall()
        escolha_jogo = st.selectbox("Escolha o jogo para alterar:", [f"#{x[0]} - {x[1]} x {x[2]}" for x in lista_adm])
        id_modificar = int(escolha_jogo.split(" ")[0].replace("#", ""))
        
        g1_new = st.number_input("Gols Time 1:", min_value=0, value=0, key="g1_new")
        g2_new = st.number_input("Gols Time 2:", min_value=0, value=0, key="g2_new")
        status_new = st.selectbox("Mudar Status para:", ["agendado", "ao_vivo", "intervalo", "encerrado"])
        
        if st.button("Atualizar Placar no Site 🔄"):
            cursor.execute("UPDATE resultados_reais SET gols1=?, gols2=?, status=? WHERE jogo_id=?", (g1_new, g2_new, status_new, id_modificar))
            conn.commit()
            st.success("Placar atualizado com sucesso!")
            st.rerun()
    conn.close()

with aba_palpites:
    st.write("### Faça seus Palpites para os próximos jogos")
    # Mostra apenas jogos futuros (esconde a Alemanha porque já começou!)
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT jogo_id, grupo, horario, time1, time2 FROM resultados_reais WHERE status='agendado'")
    for j in cursor.fetchall():
        st.write(f"🔹 **[{j[1]}]** {j[3]} x {j[4]} — Horário: {j[2]}")
    conn.close()
