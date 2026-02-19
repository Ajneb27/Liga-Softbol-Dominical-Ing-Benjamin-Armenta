import streamlit as st
import pandas as pd
import os
import urllib.parse
from datetime import datetime
import qrcode
from io import BytesIO
from fpdf import FPDF

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(page_title="Liga Softbol Pro 2026", layout="wide", page_icon="🥎")

# URL REAL DE TU PÁGINA (CÁMBIALA AQUÍ)
URL_MI_PAGINA = "https://liga-softbol-dominical-ing-benjamin-armenta-2ojzdqfhxt7tfq3z6x.streamlit.app/" 

# Archivos de Datos
ARCHIVOS = ["data_bateo.csv", "data_pitcheo.csv", "data_juegos.csv", "data_fotos.csv", "data_perfiles.csv", "data_mvp.csv", "data_playoffs.csv"]

def inicializar_configs():
    if not os.path.exists("config.txt"): 
        with open("config.txt", "w") as f: f.write("softbol2026")
    if not os.path.exists("color_pri.txt"): 
        with open("color_pri.txt", "w") as f: f.write("#1a237e")
    if not os.path.exists("color_sec.txt"): 
        with open("color_sec.txt", "w") as f: f.write("#b71c1c")
    if not os.path.exists("bg_url.txt"): 
        with open("bg_url.txt", "w") as f: f.write("https://images.unsplash.com")

def cargar_datos():
    for k in ['bateo', 'pitcheo', 'juegos', 'fotos', 'perfiles', 'mvp', 'playoffs']:
        archivo = f"data_{k}.csv"
        if os.path.exists(archivo):
            st.session_state[k] = pd.read_csv(archivo)
        else:
            if k == 'bateo': st.session_state[k] = pd.DataFrame(columns=["Nombre", "Equipo", "VB", "H", "2B", "3B", "HR", "RBI"])
            elif k == 'pitcheo': st.session_state[k] = pd.DataFrame(columns=["Nombre", "Equipo", "JG", "JP", "IP", "CL", "CF", "CC"])
            elif k == 'juegos': st.session_state[k] = pd.DataFrame(columns=["Fecha", "Hora", "Local", "Visita", "Campo"])
            else: st.session_state[k] = pd.DataFrame()

def guardar_todo():
    for k in ['bateo', 'pitcheo', 'juegos', 'fotos', 'perfiles', 'mvp', 'playoffs']:
        st.session_state[k].to_csv(f"data_{k}.csv", index=False)

inicializar_configs()
cargar_datos()

# --- 2. ESTILO VISUAL DINÁMICO ---
color_p = open("color_pri.txt", "r").read().strip()
color_s = open("color_sec.txt", "r").read().strip()
bg_img = open("bg_url.txt", "r").read().strip()

st.markdown(f"""
    <style>
    .stApp {{ background-image: url("{bg_img}"); background-size: cover; background-attachment: fixed; }}
    .block-container {{ background-color: rgba(255, 255, 255, 0.93); padding: 30px; border-radius: 15px; }}
    [data-testid="stSidebar"] {{ background-color: {color_p}; }}
    [data-testid="stSidebar"] * {{ color: white !important; }}
    h1, h2, h3 {{ color: {color_s} !important; text-align: center; }}
    .stButton>button {{ background-color: {color_s}; color: white; border-radius: 8px; width: 100%; }}
    .juego-hoy {{ background-color: #fff9c4; border: 2px solid #f44336; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNCIÓN PARA GENERAR PDF ---
def crear_pdf(df, titulo):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, titulo.upper(), ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("Arial", "B", 10)
    pdf.set_fill_color(230, 230, 230)
    for col in df.columns:
        pdf.cell(24, 10, str(col), border=1, align="C", fill=True)
    pdf.ln()
    pdf.set_font("Arial", "", 9)
    for i in range(len(df)):
        for col in df.columns:
            pdf.cell(24, 10, str(df.iloc[i][col]), border=1, align="C")
        pdf.ln()
    return pdf.output()

# --- 4. PANEL LATERAL ---
st.sidebar.title("⚾ LIGA SOFTBOL 2026")
pass_admin = open("config.txt", "r").read().strip()
pwd = st.sidebar.text_input("Contraseña Admin:", type="password")
es_admin = (pwd == pass_admin)

# Contador de Visitas
st.sidebar.components.v1.html("""<div align="center"><img src="https://counter1.optistats.ovh" border="0"><p style="color:white; font-size:12px;">Visitas Totales</p></div>""", height=80)

menu = st.sidebar.radio("IR A:", ["🏆 Standings", "📅 Calendario", "🥖 Bateo", "🔥 Pitcheo", "👤 Perfiles", "🔥 PLAYOFFS", "🌟 MVP", "📲 QR/Lineup", "⚙️ CONFIG"])

# --- 5. SECCIONES ---

if menu == "🏆 Standings":
    st.header("📊 Tabla de Posiciones General")
    if not st.session_state.pitcheo.empty:
        stnd = st.session_state.pitcheo.groupby('Equipo').agg({'JG':'sum','JP':'sum','CF':'sum','CC':'sum'}).reset_index()
        stnd['JJ'] = stnd['JG'] + stnd['JP']
        stnd['PCT'] = (stnd['JG'] / stnd['JJ']).fillna(0).round(3)
        stnd['DIF'] = stnd['CF'] - stnd['CC']
        st.table(stnd.sort_values(by=['PCT', 'DIF'], ascending=False))

elif menu == "🥖 Bateo":
    st.header("📊 Estadísticas de Bateo")
    if not st.session_state.bateo.empty:
        df_b = st.session_state.bateo.copy()
        df_b['AVG'] = ((df_b['H'] + df_b['2B'] + df_b['3B'] + df_b['HR']) / df_b['VB']).fillna(0).round(3)
        
        eq_sel = st.selectbox("🎯 Filtrar Equipo para PDF:", ["TODOS"] + sorted(list(df_b['Equipo'].unique())))
        df_f = df_b if eq_sel == "TODOS" else df_b[df_b['Equipo'] == eq_sel]
        st.dataframe(df_f, use_container_width=True)
        
        pdf_bateo = crear_pdf(df_f, f"Bateo - {eq_sel}")
        st.download_button(f"📄 Descargar PDF de {eq_sel} para WhatsApp", data=pdf_bateo, file_name=f"bateo_{eq_sel}.pdf", mime="application/pdf")

    if es_admin:
        with st.expander("➕ Registrar Bateador"):
            with st.form("r_b"):
                n, e, v, h, hr = st.text_input("Nombre"), st.text_input("Equipo"), st.number_input("VB",1), st.number_input("H",0), st.number_input("HR",0)
                if st.form_submit_button("Guardar"):
                    st.session_state.bateo.loc[len(st.session_state.bateo)] = [n, e, v, h, 0, 0, hr, 0]
                    guardar_todo(); st.rerun()

elif menu == "📅 Calendario":
    st.header("🗓️ Rol de Juegos")
    hoy = datetime.now().strftime("%d/%m/%Y")
    for _, r in st.session_state.juegos.iterrows():
        if r['Fecha'] == hoy: st.markdown(f"<div class='juego-hoy'>🚨 JUEGO HOY: {r['Local']} vs {r['Visita']} | {r['Hora']}</div>", unsafe_allow_html=True)
    st.dataframe(st.session_state.juegos, use_container_width=True)
    if es_admin:
        with st.form("f_j"):
            f, h, l, v, c = st.date_input("Fecha"), st.time_input("Hora"), st.text_input("Local"), st.text_input("Visita"), st.text_input("Campo")
            if st.form_submit_button("Agendar"):
                st.session_state.juegos.loc[len(st.session_state.juegos)] = [f.strftime("%d/%m/%Y"), h.strftime("%H:%M"), l, v, c]
                guardar_todo(); st.rerun()

elif menu == "⚙️ CONFIG":
    st.header("⚙️ Ajustes de la Liga")
    if es_admin:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🎨 Diseño")
            ncp = st.color_picker("Barra Lateral", color_p)
            ncs = st.color_picker("Botones/Títulos", color_s)
            nbg = st.text_input("Link Fondo (URL)", bg_img)
            if st.button("Guardar Diseño"):
                with open("color_pri.txt", "w") as f: f.write(ncp)
                with open("color_sec.txt", "w") as f: f.write(ncs)
                with open("bg_url.txt", "w") as f: f.write(nbg)
                st.rerun()
        with c2:
            st.subheader("🚨 Reset")
            if st.checkbox("BORRAR TODO"):
                if st.button("🔥 RESET"):
                    for a in ARCHIVOS: 
                        if os.path.exists(a): os.remove(a)
                    st.rerun()

