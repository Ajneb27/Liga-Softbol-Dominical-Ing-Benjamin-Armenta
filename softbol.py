import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN DE DATOS Y CARPETAS ---
CARPETA_DATOS = "datos_liga"
if not os.path.exists(CARPETA_DATOS):
    os.makedirs(CARPETA_DATOS)

def ruta(archivo):
    return os.path.join(CARPETA_DATOS, archivo)

# Columnas maestras para asegurar consistencia
COLS_JUGADORES = ["Nombre", "Edad", "Equipo", "VB", "H", "H2", "H3", "HR"]
COLS_PITCHERS = ["Nombre", "Equipo", "JG", "JP", "IP", "CL"]

def inicializar_datos():
    # Inicializar Equipos
    if 'equipos' not in st.session_state:
        if os.path.exists(ruta("data_equipos.csv")):
            df = pd.read_csv(ruta("data_equipos.csv"))
            df.columns = df.columns.str.strip()
            st.session_state.equipos = df
        else:
            st.session_state.equipos = pd.DataFrame(columns=["Nombre"])
    
    # Inicializar Jugadores (Bateo)
    if 'jugadores' not in st.session_state:
        if os.path.exists(ruta("data_jugadores.csv")):
            df = pd.read_csv(ruta("data_jugadores.csv"))
            df.columns = df.columns.str.strip() # Limpia espacios en nombres de columnas
            for col in COLS_JUGADORES:
                if col not in df.columns: df[col] = 0 # Crea columna si falta
            st.session_state.jugadores = df[COLS_JUGADORES] # Fuerza el orden
        else:
            st.session_state.jugadores = pd.DataFrame(columns=COLS_JUGADORES)

    # Inicializar Pitchers
    if 'pitchers' not in st.session_state:
        if os.path.exists(ruta("data_pitchers.csv")):
            df = pd.read_csv(ruta("data_pitchers.csv"))
            df.columns = df.columns.str.strip()
            for col in COLS_PITCHERS:
                if col not in df.columns: df[col] = 0
            st.session_state.pitchers = df[COLS_PITCHERS]
        else:
            st.session_state.pitchers = pd.DataFrame(columns=COLS_PITCHERS)

def guardar_datos():
    st.session_state.equipos.to_csv(ruta("data_equipos.csv"), index=False)
    st.session_state.jugadores.to_csv(ruta("data_jugadores.csv"), index=False)
    st.session_state.pitchers.to_csv(ruta("data_pitchers.csv"), index=False)

inicializar_datos()

# --- 2. BARRA LATERAL (LOGIN) ---
st.sidebar.title("⚾ LIGA SOFTBOL 2026")
with st.sidebar.form("login"):
    pwd = st.text_input("Contraseña Admin:", type="password")
    if st.form_submit_button("Validar Acceso"): pass

# Contraseña por defecto o desde config
pass_m = "softbol2026"
if os.path.exists(ruta("config.txt")):
    pass_m = open(ruta("config.txt"), "r").read().strip()

es_admin = (pwd == pass_m)

menu = st.sidebar.radio("MENÚ:", ["🏠 Inicio", "🏆 TOP 10 LÍDERES", "👥 Equipos", "🏃 Bateo (H1, H2, H3, HR)", "🔥 Pitcheo (JG, JP)"])

# ==========================================
# SECCIÓN: TOP 10 LÍDERES
# ==========================================
if menu == "🏆 TOP 10 LÍDERES":
    st.header("🏆 Cuadro de Honor")
    tab_b, tab_p = st.tabs(["🥖 Líderes de Bateo", "🔥 Líderes de Pitcheo"])

    with tab_b:
        if not st.session_state.jugadores.empty:
            df_b = st.session_state.jugadores.copy()
            # Convertir a número con seguridad
            for c in ['H', 'H2', 'H3', 'HR', 'VB']:
                df_b[c] = pd.to_numeric(df_b[c], errors='coerce').fillna(0)
            
            # Cálculo de AVG (H + H2 + H3 + HR) / VB
            df_b['AVG'] = (df_b['H'] + df_b['H2'] + df_b['H3'] + df_b['HR']) / df_b['VB'].replace(0, 1)
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
            for c in ['CL', 'IP', 'JG']:
                df_p[c] = pd.to_numeric(df_p[c], errors='coerce').fillna(0)
            
            # Efectividad: (Carreras Limpias * 7) / Innings Pitcheados
            df_p['EFE'] = ((df_p['CL'] * 7) / df_p['IP'].replace(0, 1)).round(2)
            
            cp1, cp2 = st.columns(2)
            with cp1:
                st.subheader("🥇 Top 10 Ganados (JG)")
                st.table(df_p.sort_values(by="JG", ascending=False).head(10)[["Nombre", "JG"]])
            with cp2:
                st.subheader("🥇 Top 10 Efectividad (EFE)")
                st.table(df_p[df_p['IP'] > 0].sort_values(by="EFE", ascending=True).head(10)[["Nombre", "EFE"]])
        else: st.info("No hay datos de pitcheo.")

# ==========================================
# SECCIÓN: BATEO (H, H2, H3, HR)
# ==========================================
elif menu == "🏃 Bateo (H1, H2, H3, HR)":
    st.header("🏃 Estadísticas de Bateo")
    if es_admin:
        with st.form("nuevo_b"):
            n_b = st.text_input("Nombre Jugador")
            lista_eq = st.session_state.equipos['Nombre'].tolist() if not st.session_state.equipos.empty else ["Invitado"]
            eq_b = st.selectbox("Equipo", lista_eq)
            c1, c2, c3, c4, c5 = st.columns(5)
            vb = c1.number_input("VB (Vueltas)", min_value=1, value=1)
            h1 = c2.number_input("H1 (Sencillos)", 0)
            h2 = c3.number_input("H2", 0)
            h3 = c4.number_input("H3", 0)
            hr = c5.number_input("HR", 0)
            if st.form_submit_button("Guardar Bateador"):
                nuevo_j = pd.DataFrame([{"Nombre": n_b, "Edad": 0, "Equipo": eq_b, "VB": vb, "H": h1, "H2": h2, "H3": h3, "HR": hr}])
                st.session_state.jugadores = pd.concat([st.session_state.jugadores, nuevo_j], ignore_index=True)
                guardar_datos(); st.success("¡Guardado!"); st.rerun()
    st.dataframe(st.session_state.jugadores, use_container_width=True)

# ==========================================
# SECCIÓN: PITCHO (JG, JP)
# ==========================================
elif menu == "🔥 Pitcheo (JG, JP)":
    st.header("🔥 Estadísticas de Pitcheo")
    if es_admin:
        with st.form("nuevo_p"):
            n_p = st.text_input("Nombre Pitcher")
            lista_eq = st.session_state.equipos['Nombre'].tolist() if not st.session_state.equipos.empty else ["Invitado"]
            eq_p = st.selectbox("Equipo", lista_eq)
            c1, c2, c3, c4 = st.columns(4)
            jg = c1.number_input("Ganados (JG)", 0)
            jp = c2.number_input("Perdidos (JP)", 0)
            ip = c3.number_input("Innings (IP)", 0.1)
            cl = c4.number_input("CL (Carreras L.)", 0)
            if st.form_submit_button("Guardar Pitcher"):
                nuevo_p = pd.DataFrame([{"Nombre": n_p, "Equipo": eq_p, "JG": jg, "JP": jp, "IP": ip, "CL": cl}])
                st.session_state.pitchers = pd.concat([st.session_state.pitchers, nuevo_p], ignore_index=True)
                guardar_datos(); st.success("¡Guardado!"); st.rerun()
    st.dataframe(st.session_state.pitchers, use_container_width=True)

# ==========================================
# SECCIÓN: EQUIPOS
# ==========================================
elif menu == "👥 Equipos":
    st.header("👥 Gestión de Equipos")
    if es_admin:
        with st.form("nuevo_e"):
            n_e = st.text_input("Nombre del Equipo")
            if st.form_submit_button("Registrar Equipo"):
                st.session_state.equipos = pd.concat([st.session_state.equipos, pd.DataFrame([{"Nombre": n_e}])], ignore_index=True)
                guardar_datos(); st.rerun()
    st.table(st.session_state.equipos)

elif menu == "🏠 Inicio":
    st.title("Bienvenido a la Liga de Softbol 2026")
    st.write("Selecciona una opción en el menú de la izquierda para comenzar.")
