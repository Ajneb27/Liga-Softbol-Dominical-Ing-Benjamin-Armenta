import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN DE DATOS ---
CARPETA_DATOS = "datos_liga"
if not os.path.exists(CARPETA_DATOS):
    os.makedirs(CARPETA_DATOS)

def ruta(archivo):
    return os.path.join(CARPETA_DATOS, archivo)

def inicializar_datos():
    # Definimos columnas base para asegurar que NUNCA falten
    cols_j = ["Nombre", "Edad", "Equipo", "VB", "H", "H2", "H3", "HR"]
    cols_p = ["Nombre", "Equipo", "JG", "JP", "IP", "CL"]

    if 'equipos' not in st.session_state:
        st.session_state.equipos = pd.read_csv(ruta("data_equipos.csv")) if os.path.exists(ruta("data_equipos.csv")) else pd.DataFrame(columns=["Nombre"])
    
    if 'jugadores' not in st.session_state:
        if os.path.exists(ruta("data_jugadores.csv")):
            df = pd.read_csv(ruta("data_jugadores.csv"))
            # Forzar que existan todas las columnas necesarias
            for col in cols_j:
                if col not in df.columns: df[col] = 0
            st.session_state.jugadores = df
        else:
            st.session_state.jugadores = pd.DataFrame(columns=cols_j)

    if 'pitchers' not in st.session_state:
        if os.path.exists(ruta("data_pitchers.csv")):
            df = pd.read_csv(ruta("data_pitchers.csv"))
            for col in cols_p:
                if col not in df.columns: df[col] = 0
            st.session_state.pitchers = df
        else:
            st.session_state.pitchers = pd.DataFrame(columns=cols_p)

def guardar_datos():
    st.session_state.equipos.to_csv(ruta("data_equipos.csv"), index=False)
    st.session_state.jugadores.to_csv(ruta("data_jugadores.csv"), index=False)
    st.session_state.pitchers.to_csv(ruta("data_pitchers.csv"), index=False)

inicializar_datos()

# --- BARRA LATERAL ---
st.sidebar.title("⚾ LIGA SOFTBOL 2026")
with st.sidebar.form("login"):
    pwd = st.text_input("Contraseña Admin:", type="password")
    log_btn = st.form_submit_button("Validar Acceso")

pass_m = "softbol2026" # Contraseña por defecto
es_admin = (pwd == pass_m)

menu = st.sidebar.radio("MENÚ:", ["🏠 Inicio", "🏆 TOP 10 LÍDERES", "👥 Equipos", "🏃 Bateo (H1, H2, H3, HR)", "🔥 Pitcheo (JG, JP)"])

# --- SECCIÓN: TOP 10 LÍDERES ---
if menu == "🏆 TOP 10 LÍDERES":
    st.header("🏆 Cuadro de Honor")
    tab_b, tab_p = st.tabs(["🥖 Líderes de Bateo", "🔥 Líderes de Pitcheo"])

    with tab_b:
        if not st.session_state.jugadores.empty:
            df_b = st.session_state.jugadores.copy()
            # Asegurar que los datos sean números para poder sumar y dividir
            for c in ['H', 'H2', 'H3', 'HR', 'VB']:
                df_b[c] = pd.to_numeric(df_b[c], errors='coerce').fillna(0)
            
            # Cálculo de AVG: (H+H2+H3+HR) / VB. Usamos .replace(0,1) para evitar error de división por cero
            df_b['AVG'] = ((df_b['H'] + df_b['H2'] + df_b['H3'] + df_b['HR']) / df_b['VB'].replace(0, 1))
            df_b['AVG'] = df_b['AVG'].fillna(0).round(3)
            
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("🥇 Top 10 Average (AVG)")
                st.table(df_b.sort_values(by="AVG", ascending=False).head(10)[["Nombre", "AVG"]])
                st.subheader("🥇 Top 10 Home Runs (HR)")
                st.table(df_b.sort_values(by="HR", ascending=False).head(10)[["Nombre", "HR"]])
            with c2:
                st.subheader("🥇 Top 10 Triples (H3)")
                st.table(df_b.sort_values(by="H3", ascending=False).head(10)[["Nombre", "H3"]])
                st.subheader("🥇 Top 10 Dobles (H2)")
                st.table(df_b.sort_values(by="H2", ascending=False).head(10)[["Nombre", "H2"]])
        else: st.info("No hay datos de bateo.")

    with tab_p:
        if not st.session_state.pitchers.empty:
            df_p = st.session_state.pitchers.copy()
            for c in ['CL', 'IP']:
                df_p[c] = pd.to_numeric(df_p[c], errors='coerce').fillna(0)
            df_p['EFE'] = ((df_p['CL'] * 7) / df_p['IP'].replace(0, 1)).round(2)
            
            cp1, cp2 = st.columns(2)
            with cp1:
                st.subheader("🥇 Top 10 Ganados (JG)")
                st.table(df_p.sort_values(by="JG", ascending=False).head(10)[["Nombre", "JG"]])
            with cp2:
                st.subheader("🥇 Top 10 Efectividad (EFE)")
                st.table(df_p[df_p['IP'] > 0].sort_values(by="EFE", ascending=True).head(10)[["Nombre", "EFE"]])
        else: st.info("No hay datos de pitcheo.")

# --- SECCIÓN: BATEO ---
elif menu == "🏃 Bateo (H1, H2, H3, HR)":
    st.header("🏃 Estadísticas de Bateo")
    if es_admin:
        with st.form("nuevo_b"):
            n_b = st.text_input("Nombre Jugador")
            eq_lista = st.session_state.equipos['Nombre'].tolist() if not st.session_state.equipos.empty else ["Sin equipo"]
            eq_b = st.selectbox("Equipo", eq_lista)
            c1, c2, c3, c4, c5 = st.columns(5)
            vb = c1.number_input("VB", min_value=1, value=1)
            h1 = c2.number_input("H1", 0)
            h2 = c3.number_input("H2", 0)
            h3 = c4.number_input("H3", 0)
            hr = c5.number_input("HR", 0)
            if st.form_submit_button("Guardar Bateador"):
                nueva_fila = pd.DataFrame([{"Nombre": n_b, "Edad": 0, "Equipo": eq_b, "VB": vb, "H": h1, "H2": h2, "H3": h3, "HR": hr}])
                st.session_state.jugadores = pd.concat([st.session_state.jugadores, nueva_fila], ignore_index=True)
                guardar_datos(); st.rerun()
    st.dataframe(st.session_state.jugadores, use_container_width=True)

# --- SECCIÓN: PITCHO ---
elif menu == "🔥 Pitcheo (JG, JP)":
    st.header("🔥 Estadísticas de Pitcheo")
    if es_admin:
        with st.form("nuevo_p"):
            n_p = st.text_input("Nombre Pitcher")
            eq_lista = st.session_state.equipos['Nombre'].tolist() if not st.session_state.equipos.empty else ["Sin equipo"]
            eq_p = st.selectbox("Equipo", eq_lista)
            c1, c2, c3, c4 = st.columns(4)
            jg = c1.number_input("Ganados (JG)", 0)
            jp = c2.number_input("Perdidos (JP)", 0)
            ip = c3.number_input("Innings (IP)", 0.1)
            cl = c4.number_input("CL", 0)
            if st.form_submit_button("Guardar Pitcher"):
                nueva_p = pd.DataFrame([{"Nombre": n_p, "Equipo": eq_p, "JG": jg, "JP": jp, "IP": ip, "CL": cl}])
                st.session_state.pitchers = pd.concat([st.session_state.pitchers, nueva_p], ignore_index=True)
                guardar_datos(); st.rerun()
    st.dataframe(st.session_state.pitchers, use_container_width=True)
