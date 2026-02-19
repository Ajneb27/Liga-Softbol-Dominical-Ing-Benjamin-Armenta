import streamlit as st
import pandas as pd
import os
import urllib.parse
from datetime import datetime
import qrcode
from io import BytesIO
from fpdf import FPDF

# --- 1. CONFIGURACIÓN DE CARPETA Y RUTAS ---
CARPETA_DATOS = "datos_liga"

# Crear la carpeta si no existe
if not os.path.exists(CARPETA_DATOS):
    os.makedirs(CARPETA_DATOS)

def ruta(archivo):
    return os.path.join(CARPETA_DATOS, archivo)

# --- 2. CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Liga Softbol Pro 2026", layout="wide", page_icon="🥎")

# URL REAL DE TU PÁGINA (Cámbiala por la tuya)
URL_MI_PAGINA = "https://liga-softbol-dominical-ing-benjamin-armenta.streamlit.app" 

def inicializar_configs():
    if not os.path.exists(ruta("config.txt")): 
        with open(ruta("config.txt"), "w") as f: f.write("softbol2026")
    if not os.path.exists(ruta("color_pri.txt")): 
        with open(ruta("color_pri.txt"), "w") as f: f.write("#1a237e")
    if not os.path.exists(ruta("color_sec.txt")): 
        with open(ruta("color_sec.txt"), "w") as f: f.write("#b71c1c")
    if not os.path.exists(ruta("bg_url.txt")): 
        with open(ruta("bg_url.txt"), "w") as f: f.write("https://images.unsplash.com")

def cargar_datos():
    for k in ['bateo', 'pitcheo', 'juegos', 'fotos', 'perfiles', 'mvp', 'playoffs']:
        archivo_csv = ruta(f"data_{k}.csv")
        if os.path.exists(archivo_csv):
            st.session_state[k] = pd.read_csv(archivo_csv)
        else:
            if k == 'bateo': st.session_state[k] = pd.DataFrame(columns=["Nombre", "Equipo", "VB", "H", "2B", "3B", "HR", "RBI"])
            elif k == 'pitcheo': st.session_state[k] = pd.DataFrame(columns=["Nombre", "Equipo", "JG", "JP", "IP", "CL", "CF", "CC"])
            elif k == 'juegos': st.session_state[k] = pd.DataFrame(columns=["Fecha", "Hora", "Local", "Visita", "Campo"])
            else: st.session_state[k] = pd.DataFrame()

def guardar_todo():
    for k in ['bateo', 'pitcheo', 'juegos', 'fotos', 'perfiles', 'mvp', 'playoffs']:
        st.session_state[k].to_csv(ruta(f"data_{k}.csv"), index=False)

inicializar_configs()
cargar_datos()

# --- 3. ESTILO VISUAL (CORREGIDO) ---
color_p = open(ruta("color_pri.txt"), "r").read().strip()
color_s = open(ruta("color_sec.txt"), "r").read().strip()
bg_img = open(ruta("bg_url.txt"), "r").read().strip()

st.markdown(f"""
    <style>
    .stApp {{ background-image: url("{bg_img}"); background-size: cover; background-attachment: fixed; }}
    .block-container {{ background-color: rgba(255, 255, 255, 0.93); padding: 30px; border-radius: 15px; box-shadow: 0px 4px 15px rgba(0,0,0,0.3); }}
    [data-testid="stSidebar"] {{ background-color: {color_p}; }}
    [data-testid="stSidebar"] * {{ color: white !important; }}
    [data-testid="stSidebar"] input {{ color: black !important; }}
    h1, h2, h3 {{ color: {color_s} !important; text-align: center; font-family: 'Arial Black'; }}
    .stButton>button {{ background-color: {color_s}; color: white; border-radius: 8px; font-weight: bold; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. BARRA LATERAL ---
st.sidebar.title("⚾ LIGA SOFTBOL 2026")
pass_admin = open(ruta("config.txt"), "r").read().strip()
pwd = st.sidebar.text_input("Contraseña Admin:", type="password")
es_admin = (pwd == pass_admin)

with st.sidebar:
    st.components.v1.html("""<div align="center"><img src="https://counter1.optistats.ovh" border="0"><p style="color:white; font-size:12px;">Visitas Totales</p></div>""", height=100)

menu = st.sidebar.radio("IR A:", ["🏆 Standings", "📅 Calendario", "🥖 Bateo", "🔥 Pitcheo", "⚙️ CONFIG"])

# --- 5. LÓGICA DE SECCIONES (Resumida) ---
if menu == "🏆 Standings":
    st.header("📊 Tabla de Posiciones")
    if not st.session_state.pitcheo.empty:
        stnd = st.session_state.pitcheo.groupby('Equipo').agg({'JG':'sum','JP':'sum','CF':'sum','CC':'sum'}).reset_index()
        stnd['JJ'] = stnd['JG'] + stnd['JP']
        stnd['PCT'] = (stnd['JG'] / stnd['JJ']).fillna(0).round(3)
        stnd['DIF'] = stnd['CF'] - stnd['CC']
        st.table(stnd.sort_values(by=['PCT', 'DIF'], ascending=False))

elif menu == "🥖 Bateo":
    st.header("📊 Estadísticas de Bateo")
    if not st.session_state.bateo.empty:
        df_f = st.session_state.bateo
        st.dataframe(df_f, use_container_width=True)
    if es_admin:
        with st.form("r_b"):
            n, e = st.text_input("Nombre"), st.text_input("Equipo")
            if st.form_submit_button("Guardar"):
                st.session_state.bateo.loc[len(st.session_state.bateo)] = [n, e, 0, 0, 0, 0, 0, 0]
                guardar_todo(); st.rerun()

elif menu == "⚙️ CONFIG":
    st.header("⚙️ Ajustes de la Liga")
    if es_admin:
        if st.button("🔥 BORRAR DATOS DE CARPETA"):
            for f in os.listdir(CARPETA_DATOS):
                if f.endswith(".csv"):
                    os.remove(os.path.join(CARPETA_DATOS, f))
            st.success("Datos eliminados de la carpeta 'datos_liga'.")
            st.rerun()
