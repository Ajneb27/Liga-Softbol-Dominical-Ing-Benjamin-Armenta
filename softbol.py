import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. CONFIGURACIÓN DE CARPETA Y RUTAS ---
CARPETA_DATOS = "datos_liga"
if not os.path.exists(CARPETA_DATOS):
    os.makedirs(CARPETA_DATOS)

def ruta(archivo):
    return os.path.join(CARPETA_DATOS, archivo)

# --- 2. CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Liga Softbol Pro 2026", layout="wide", page_icon="🥎")

def inicializar_configs():
    if not os.path.exists(ruta("config.txt")): 
        with open(ruta("config.txt"), "w") as f: f.write("softbol2026")
    if not os.path.exists(ruta("color_pri.txt")): 
        with open(ruta("color_pri.txt"), "w") as f: f.write("#1a237e")
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

inicializar_configs()
cargar_datos()

# --- 3. ESTILO VISUAL ---
color_p = open(ruta("color_pri.txt"), "r").read().strip()
bg_img = open(ruta("bg_url.txt"), "r").read().strip()

st.markdown(f"""
    <style>
    .stApp {{ background-image: url("{bg_img}"); background-size: cover; background-attachment: fixed; }}
    .block-container {{ background-color: rgba(255, 255, 255, 0.94); padding: 30px; border-radius: 15px; box-shadow: 0px 4px 15px rgba(0,0,0,0.3); }}
    [data-testid="stSidebar"] {{ background-color: {color_p}; }}
    [data-testid="stSidebar"] * {{ color: white !important; }}
    [data-testid="stSidebar"] input {{ color: black !important; }}
    h1, h2, h3 {{ color: #b71c1c !important; text-align: center; font-family: 'Arial Black'; }}
    .stButton>button {{ border-radius: 8px; font-weight: bold; width: 100%; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. BARRA LATERAL (LOGIN) ---
st.sidebar.title("⚾ LIGA 2026")
pass_actual = open(ruta("config.txt"), "r").read().strip()
pwd = st.sidebar.text_input("Contraseña Admin:", type="password")
es_admin = (pwd == pass_actual)

menu = st.sidebar.radio("IR A:", ["🏆 Standings", "🥖 Bateo", "🔥 Pitcheo", "📅 Rol", "⚙️ CONFIG"])

# ==========================================
# SECCIÓN: CONFIGURACIÓN (CON VER CLAVE)
# ==========================================
if menu == "⚙️ CONFIG":
    st.header("⚙️ Ajustes y Seguridad")
    if es_admin:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔑 Gestión de Acceso")
            # --- OPCIÓN: VER CONTRASEÑA ---
            if st.checkbox("👁️ Mostrar Contraseña Actual"):
                st.info(f"Tu clave es: **{pass_actual}**")
            
            st.divider()
            nueva_p = st.text_input("Cambiar a Nueva Contraseña", type="password")
            if st.button("Guardar Nueva Clave"):
                with open(ruta("config.txt"), "w") as f: f.write(nueva_p)
                st.success("¡Clave actualizada!")
                st.rerun()

        with col2:
            st.subheader("🎨 Personalización")
            n_cp = st.color_picker("Color Barra Lateral", color_p)
            n_bg = st.text_input("Link Fondo (URL)", bg_img)
            if st.button("Guardar Diseño"):
                with open(ruta("color_pri.txt"), "w") as f: f.write(n_cp)
                with open(ruta("bg_url.txt"), "w") as f: f.write(n_bg)
                st.rerun()
    else:
        st.error("Debes ingresar la contraseña en la barra lateral para ver los ajustes.")

# (Aquí se mantienen las secciones de Bateo, Pitcheo y Standings como antes...)
elif menu == "🏆 Standings":
    st.header("📊 Posiciones de la Liga")
    if not st.session_state.pitcheo.empty:
        st.table(st.session_state.pitcheo)
