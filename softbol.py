import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN DE DATOS ---
CARPETA_DATOS = "datos_liga"
if not os.path.exists(CARPETA_DATOS): os.makedirs(CARPETA_DATOS)

def ruta(archivo): return os.path.join(CARPETA_DATOS, archivo)

COLS_J = ["Nombre", "Equipo", "VB", "H", "H2", "H3", "HR"]
COLS_P = ["Nombre", "Equipo", "JG", "JP", "IP", "CL"] 

def cargar_datos(archivo, columnas):
    path = ruta(archivo)
    if os.path.exists(path):
        df = pd.read_csv(path)
        df.columns = df.columns.str.strip()
        for col in columnas:
            if col not in df.columns: df[col] = 0
        cols_num = [c for c in columnas if c not in ["Nombre", "Equipo"]]
        df[cols_num] = df[cols_num].apply(pd.to_numeric, errors='coerce').fillna(0).astype(int)
        return df[columnas]
    return pd.DataFrame(columns=columnas)

st.session_state.jugadores = cargar_datos("data_jugadores.csv", COLS_J)
st.session_state.pitchers = cargar_datos("data_pitchers.csv", COLS_P)
st.session_state.equipos = pd.read_csv(ruta("data_equipos.csv")) if os.path.exists(ruta("data_equipos.csv")) else pd.DataFrame(columns=["Nombre"])

# --- 2. SEGURIDAD ---
st.sidebar.title("⚾ LIGA SOFTBOL 2026")
if 'autenticado' not in st.session_state: st.session_state.autenticado = False

if not st.session_state.autenticado:
    with st.sidebar.form("login"):
        pwd = st.text_input("Contraseña Admin:", type="password")
        if st.form_submit_button("Validar Acceso"):
            if pwd == "softbol2026":
                st.session_state.autenticado = True
                st.rerun()
            else: st.error("Clave incorrecta")
else:
    st.sidebar.success("🔓 MODO ADMINISTRADOR")
    if st.sidebar.button("Cerrar Sesión 🔒"):
        st.session_state.autenticado = False
        st.rerun()

menu = st.sidebar.radio("MENÚ:", ["🏠 Inicio", "🏆 TOP 10 LÍDERES", "📋 Rosters por Equipo", "🏃 Estadísticas (Admin)", "👥 Equipos"])

# ==========================================
# SECCIÓN: TOP 10 LÍDERES (RESTAURADA CON TRIPLES)
# ==========================================
if menu == "🏆 TOP 10 LÍDERES":
    t_bateo, t_pitcheo = st.tabs(["🥖 Bateo", "🔥 Pitcheo"])
    
    with t_bateo:
        st.header("🏆 Cuadro de Honor: Bateo")
        df_b = st.session_state.jugadores.copy()
        if not df_b.empty:
            df_b['H_T'] = df_b['H'] + df_b['H2'] + df_b['H3'] + df_b['HR']
            df_b['AVG'] = (df_b['H_T'] / df_b['VB'].replace(0, 1)).fillna(0)
            
            # FILA 1
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("🥇 Average (AVG)")
                st.table(df_b.sort_values("AVG", ascending=False).head(10)[["Nombre", "AVG"]].style.format({"AVG": "{:.3f}"}))
                st.subheader("🥇 Hits Totales (H+)")
                st.table(df_b.sort_values("H_T", ascending=False).head(10)[["Nombre", "H_T"]])
            with c2:
                st.subheader("🥇 Jonrones (HR)")
                st.table(df_b.sort_values("HR", ascending=False).head(10)[["Nombre", "HR"]])
                st.subheader("🥇 Dobles (H2)")
                st.table(df_b.sort_values("H2", ascending=False).head(10)[["Nombre", "H2"]])
            
            # FILA 2 (AQUÍ ESTÁN LOS TRIPLES)
            st.divider()
            st.subheader("🥇 Triples (H3)")
            st.table(df_b.sort_values("H3", ascending=False).head(10)[["Nombre", "H3"]])
        else: st.info("Sin datos.")

    with t_pitcheo:
        st.header("🏆 Cuadro de Honor: Pitcheo")
        df_p = st.session_state.pitchers.copy()
        if not df_p.empty:
            df_p['EFE'] = ((df_p['CL'] * 7) / df_p['IP'].replace(0, 1)).fillna(0)
            cp1, cp2 = st.columns(2)
            with cp1:
                st.subheader("🥇 Efectividad (EFE)")
                st.table(df_p[df_p['IP'] > 0].sort_values("EFE", ascending=True).head(10)[["Nombre", "EFE"]].style.format({"EFE": "{:.2f}"}))
                st.subheader("🥇 Ganados (JG)")
                st.table(df_p.sort_values("JG", ascending=False).head(10)[["Nombre", "JG"]])
            with cp2:
                st.subheader("🥇 Perdidos (JP)")
                st.table(df_p.sort_values("JP", ascending=False).head(10)[["Nombre", "JP"]])
                st.subheader("🥇 Innings (IP)")
                st.table(df_p.sort_values("IP", ascending=False).head(10)[["Nombre", "IP"]])
        else: st.info("Sin datos.")

# El resto de secciones (Estadísticas Admin, Roster, Equipos, Inicio) se mantienen igual que en tu código previo.
# (Para ahorrar espacio, asegúrate de mantener las funciones de guardado y los formularios que ya tenías).
