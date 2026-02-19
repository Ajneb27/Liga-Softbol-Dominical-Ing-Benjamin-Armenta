import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN DE CARPETA Y DATOS ---
CARPETA_DATOS = "datos_liga"
if not os.path.exists(CARPETA_DATOS):
    os.makedirs(CARPETA_DATOS)

def ruta(archivo):
    return os.path.join(CARPETA_DATOS, archivo)

# Inicializar bases de datos
if 'equipos' not in st.session_state:
    st.session_state.equipos = pd.read_csv(ruta("data_equipos.csv")) if os.path.exists(ruta("data_equipos.csv")) else pd.DataFrame(columns=["Nombre"])

if 'jugadores' not in st.session_state:
    st.session_state.jugadores = pd.read_csv(ruta("data_jugadores.csv")) if os.path.exists(ruta("data_jugadores.csv")) else pd.DataFrame(columns=["Nombre", "Edad", "Equipo", "H", "H2", "H3", "HR"])

if 'pitchers' not in st.session_state:
    st.session_state.pitchers = pd.read_csv(ruta("data_pitchers.csv")) if os.path.exists(ruta("data_pitchers.csv")) else pd.DataFrame(columns=["Nombre", "Equipo", "JG", "JP", "IP", "CL"])

def guardar_datos():
    st.session_state.equipos.to_csv(ruta("data_equipos.csv"), index=False)
    st.session_state.jugadores.to_csv(ruta("data_jugadores.csv"), index=False)
    st.session_state.pitchers.to_csv(ruta("data_pitchers.csv"), index=False)

# --- 2. SISTEMA DE LOGIN ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

with st.sidebar.form("login_form"):
    st.title("🔐 Acceso Admin")
    clave = st.text_input("Contraseña:", type="password")
    if st.form_submit_button("🔓 ENTRAR"):
        if clave == "softbol2026":
            st.session_state.autenticado = True
            st.sidebar.success("✅ Conectado")
        else:
            st.session_state.autenticado = False
            st.sidebar.error("❌ Error")

menu = st.sidebar.radio("Navegación:", ["🏠 Inicio", "👥 Equipos", "🏃 Jugadores (Bateo)", "🔥 Pitchers (Lanzadores)"])

# ==========================================
# SECCIÓN: PITCHERS (LANZADORES)
# ==========================================
if menu == "🔥 Pitchers (Lanzadores)":
    st.header("🔥 Estadísticas de Pitcheo")
    lista_eq = st.session_state.equipos['Nombre'].tolist()

    if st.session_state.autenticado:
        if not lista_eq:
            st.error("⚠️ Registra un equipo primero.")
        else:
            with st.expander("➕ REGISTRAR / EDITAR PITCHER"):
                with st.form("nuevo_pitcher"):
                    nom_p = st.text_input("Nombre del Lanzador")
                    eq_p = st.selectbox("Equipo:", lista_eq)
                    c1, c2, c3, c4 = st.columns(4)
                    jg = c1.number_input("Ganados (JG)", 0)
                    jp = c2.number_input("Perdidos (JP)", 0)
                    ip = c3.number_input("Innings (IP)", 0.0)
                    cl = c4.number_input("Car. Limpias (CL)", 0)
                    
                    if st.form_submit_button("💾 GUARDAR PITCHER"):
                        nuevo_p = pd.DataFrame([{"Nombre": nom_p, "Equipo": eq_p, "JG": jg, "JP": jp, "IP": ip, "CL": cl}])
                        st.session_state.pitchers = pd.concat([st.session_state.pitchers, nuevo_p], ignore_index=True)
                        guardar_datos()
                        st.success(f"Pitcher {nom_p} guardado")
                        st.rerun()

    # TABLA DE PITCHEO
    if not st.session_state.pitchers.empty:
        df_p = st.session_state.pitchers.copy()
        # Cálculo de Efectividad (ERA) - (CL * 7 / IP)
        df_p['ERA'] = (df_p['CL'] * 7 / df_p['IP']).fillna(0).round(2)
        
        st.subheader("📊 Tabla de Pitcheo")
        st.dataframe(df_p, use_container_width=True)
        
        # LÍDER EN GANADOS
        mejor_p = df_p.loc[df_p['JG'].idxmax()]
        st.info(f"🥇 Líder en Ganados: **{mejor_p['Nombre']}** con **{mejor_p['JG']}** victorias.")

# ==========================================
# SECCIÓN: JUGADORES (BATEO)
# ==========================================
elif menu == "🏃 Jugadores (Bateo)":
    st.header("🏃 Estadísticas de Bateo")
    lista_eq = st.session_state.equipos['Nombre'].tolist()
    
    if st.session_state.autenticado:
        with st.expander("➕ REGISTRAR BATEADOR"):
            with st.form("nuevo_bateo"):
                nb = st.text_input("Nombre")
                eb = st.selectbox("Equipo", lista_eq)
                c1, c2, c3, c4 = st.columns(4)
                h1 = c1.number_input("H1", 0)
                h2 = c2.number_input("H2", 0)
                h3 = c3.number_input("H3", 0)
                hr = c4.number_input("HR", 0)
                if st.form_submit_button("💾 GUARDAR"):
                    nuevo_b = pd.DataFrame([{"Nombre": nb, "Equipo": eb, "H": h1, "H2": h2, "H3": h3, "HR": hr}])
                    st.session_state.jugadores = pd.concat([st.session_state.jugadores, nuevo_b], ignore_index=True)
                    guardar_datos(); st.rerun()

    st.dataframe(st.session_state.jugadores, use_container_width=True)

# (Secciones de Inicio y Equipos se mantienen igual que antes...)
elif menu == "👥 Equipos":
    st.header("👥 Equipos")
    # ... (Aquí va tu código de equipos anterior)
