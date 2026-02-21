import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. CONFIGURACIÓN DE RUTAS ---
DATA_DIR = "liga_softbol_2026"
if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)

JUGADORES_FILE = os.path.join(DATA_DIR, "jugadores_stats.csv")
EQUIPOS_FILE = os.path.join(DATA_DIR, "equipos_lista.csv")
CONFIG_FILE = os.path.join(DATA_DIR, "config_admin.csv")

ANIO_ACTUAL = 2026 # Año de la temporada actual

# Credenciales por defecto
if not os.path.exists(CONFIG_FILE):
    pd.DataFrame([{"user": "admin", "pass": "123"}]).to_csv(CONFIG_FILE, index=False)

# --- 2. MOTOR DE DATOS ---
def cargar_base_datos():
    columnas_obligatorias = ["Nombre", "Equipo", "VB", "H", "2B", "3B", "HR", "G", "P"]
    if os.path.exists(JUGADORES_FILE):
        try:
            df = pd.read_csv(JUGADORES_FILE)
            for col in columnas_obligatorias:
                if col not in df.columns: df[col] = 0
        except: df = pd.DataFrame(columns=columnas_obligatorias)
    else: df = pd.DataFrame(columns=columnas_obligatorias)
    
    cols_num = ["VB", "H", "2B", "3B", "HR", "G", "P"]
    for c in cols_num:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
    return df

def cargar_equipos():
    if os.path.exists(EQUIPOS_FILE):
        df = pd.read_csv(EQUIPOS_FILE)
        if "Debut" not in df.columns: df["Debut"] = ANIO_ACTUAL
        return df
    return pd.DataFrame(columns=["Nombre", "Debut"])

# --- 3. INICIALIZACIÓN ---
if 'admin_sesion' not in st.session_state: st.session_state.admin_sesion = False

df_j = cargar_base_datos()
df_e = cargar_equipos()

# --- 4. INTERFAZ ---
st.set_page_config(page_title="Liga Softbol 2026", layout="wide")

with st.sidebar:
    st.title("🥎 Softbol Liga 2026")
    if not st.session_state.admin_sesion:
        with st.expander("🔐 Acceso Admin"):
            u = st.text_input("Usuario")
            p = st.text_input("Clave", type="password")
            if st.button("Entrar"):
                c = pd.read_csv(CONFIG_FILE).iloc[0]
                if u == c['user'] and p == str(c['pass']):
                    st.session_state.admin_sesion = True
                    st.rerun()
                else: st.error("Error")
    else:
        if st.button("Cerrar Sesión"):
            st.session_state.admin_sesion = False
            st.rerun()
    
    st.divider()
    menu = st.radio("Secciones:", ["🏆 LÍDERES (TOP 10)", "📋 ROSTERS", "📊 TABLA GENERAL", "🏘️ EQUIPOS", "✍️ REGISTRAR", "🗑️ BORRAR", "💾 RESPALDO"])

# --- 5. SECCIÓN LÍDERES ---
if menu == "🏆 LÍDERES (TOP 10)":
    st.header("🔝 Líderes Departamentales")
    tab_bat, tab_pit = st.tabs(["⚾ BATEO", "🎯 PITCHEO"])
    with tab_bat:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.subheader("Hits (H)"); st.table(df_j.nlargest(10, 'H')[['Nombre', 'H']])
            st.subheader("Home Runs (HR)"); st.table(df_j.nlargest(10, 'HR')[['Nombre', 'HR']])
        with c2:
            st.subheader("Dobles (2B)"); st.table(df_j.nlargest(10, '2B')[['Nombre', '2B']])
        with c3:
            st.subheader("Triples (3B)"); st.table(df_j.nlargest(10, '3B')[['Nombre', '3B']])
    with tab_pit:
        c1, c2 = st.columns(2)
        with c1: st.subheader("Ganados (G)"); st.table(df_j.nlargest(10, 'G')[['Nombre', 'G']])
        with c2: st.subheader("Perdidos (P)"); st.table(df_j.nlargest(10, 'P')[['Nombre', 'P']])

# --- 6. SECCIÓN EQUIPOS (CON AÑO DE DEBUT) ---
elif menu == "🏘️ EQUIPOS":
    st.header("🏘️ Gestión de Equipos")
    if st.session_state.admin_sesion:
        with st.form("nuevo_equipo"):
            ne = st.text_input("Nombre del equipo:")
            debut = st.number_input("Año de debut en la liga:", min_value=1980, max_value=ANIO_ACTUAL, value=ANIO_ACTUAL)
            if st.form_submit_button("Añadir Equipo"):
                if ne and ne not in df_e['Nombre'].values:
                    nuevo = pd.DataFrame([{"Nombre": ne, "Debut": debut}])
                    df_e = pd.concat([df_e, nuevo], ignore_index=True)
                    df_e.to_csv(EQUIPOS_FILE, index=False)
                    st.success(f"Equipo {ne} añadido.")
                    st.rerun()

    st.subheader("Lista de Equipos y Trayectoria")
    if not df_e.empty:
        df_mostrar = df_e.copy()
        # Cálculo de temporadas: Año Actual - Debut + 1 (para incluir la actual)
        df_mostrar["Temporadas"] = ANIO_ACTUAL - df_mostrar["Debut"] + 1
        st.dataframe(df_mostrar, use_container_width=True)

# --- 7. SECCIÓN REGISTRAR ---
elif menu == "✍️ REGISTRAR":
    if not st.session_state.admin_sesion: st.warning("Inicia sesión")
    elif df_e.empty: st.error("Crea un equipo primero")
    else:
        st.header("Registrar Estadísticas")
        modo = st.radio("Tipo:", ["Bateo", "Pitcheo"], horizontal=True)
        with st.form("reg_2026"):
            nom = st.text_input("Nombre del Jugador")
            eq = st.selectbox("Equipo", df_e["Nombre"])
            col1, col2, col3 = st.columns(3)
            if modo == "Bateo":
                vb = col1.number_input("VB", min_value=0); h = col2.number_input("H", min_value=0); d2 = col3.number_input("2B", min_value=0)
                d3 = col1.number_input("3B", min_value=0); hr = col2.number_input("HR", min_value=0); g, p = 0, 0
            else:
                g = col1.number_input("G", min_value=0); p = col2.number_input("P", min_value=0)
                vb, h, d2, d3, hr = 0, 0, 0, 0, 0
            if st.form_submit_button("💾 GUARDAR"):
                df_j = df_j[df_j["Nombre"] != nom]
                nueva = pd.DataFrame([{"Nombre": nom, "Equipo": eq, "VB": vb, "H": h, "2B": d2, "3B": d3, "HR": hr, "G": g, "P": p}])
                df_j = pd.concat([df_j, nueva], ignore_index=True)
                df_j.to_csv(JUGADORES_FILE, index=False)
                st.success("Datos actualizados")
                st.rerun()

# --- 8. RESTO DE SECCIONES (RESPALDO, ROSTERS, BORRAR) ---
elif menu == "📋 ROSTERS":
    eq_sel = st.selectbox("Selecciona Equipo:", df_e["Nombre"].unique()) if not df_e.empty else None
    if eq_sel: st.dataframe(df_j[df_j["Equipo"] == eq_sel], use_container_width=True)

elif menu == "💾 RESPALDO":
    st.download_button("📥 Descargar Respaldo", df_j.to_csv(index=False).encode('utf-8'), "respaldo_liga.csv")
    f = st.file_uploader("📤 Restaurar CSV", type="csv")
    if f:
        pd.read_csv(f).to_csv(JUGADORES_FILE, index=False); st.rerun()

elif menu == "🗑️ BORRAR":
    if st.session_state.admin_sesion:
        j_del = st.selectbox("Borrar Jugador:", df_j["Nombre"].unique())
        if st.button("Eliminar"):
            df_j = df_j[df_j["Nombre"] != j_del]
            df_j.to_csv(JUGADORES_FILE, index=False); st.rerun()
