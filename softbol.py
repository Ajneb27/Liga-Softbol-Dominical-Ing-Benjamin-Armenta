import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN Y ESTILOS ---
st.set_page_config(page_title="Softbol Pro Manager", layout="centered")

DATA_DIR = "db_liga"
EQUIPOS_FILE = f"{DATA_DIR}/equipos.csv"
JUGADORES_FILE = f"{DATA_DIR}/jugadores.csv"

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# --- 2. MOTOR DE DATOS ---
def cargar_datos(archivo, columnas):
    if os.path.exists(archivo):
        return pd.read_csv(archivo)
    return pd.DataFrame(columns=columnas)

def guardar_datos(df, archivo):
    df.to_csv(archivo, index=False)

# Inicializar estados
if 'equipos' not in st.session_state:
    st.session_state.equipos = cargar_datos(EQUIPOS_FILE, ["Nombre"])
if 'jugadores' not in st.session_state:
    st.session_state.jugadores = cargar_datos(JUGADORES_FILE, ["Nombre", "Equipo", "VB", "H"])

# --- 3. INTERFAZ ---
st.title("🥎 Softbol Pro Manager")

menu = st.sidebar.selectbox("Ir a:", ["Panel de Control", "Gestión de Equipos", "Registro de Jugadores"])

if menu == "Panel de Control":
    st.header("📊 Estadísticas de la Liga")
    if not st.session_state.jugadores.empty:
        df = st.session_state.jugadores.copy()
        # Cálculo de Average (H / VB)
        df['AVG'] = (df['H'] / df['VB']).fillna(0.000)
        st.dataframe(df.sort_values(by="AVG", ascending=False), use_container_width=True)
    else:
        st.info("Aún no hay datos de jugadores para mostrar.")

elif menu == "Gestión de Equipos":
    st.header("🏘️ Equipos")
    with st.form("nuevo_equipo"):
        nombre = st.text_input("Nombre del nuevo equipo")
        if st.form_submit_button("Registrar Equipo"):
            if nombre and nombre not in st.session_state.equipos['Nombre'].values:
                nuevo_df = pd.concat([st.session_state.equipos, pd.DataFrame([{"Nombre": nombre}])], ignore_index=True)
                guardar_datos(nuevo_df, EQUIPOS_FILE)
                st.session_state.equipos = nuevo_df
                st.success(f"Equipo '{nombre}' registrado.")
                st.rerun()
    
    st.write("---")
    st.table(st.session_state.equipos)

elif menu == "Registro de Jugadores":
    st.header("👤 Jugadores")
    if st.session_state.equipos.empty:
        st.warning("Primero debes registrar al menos un equipo.")
    else:
        with st.form("nuevo_jugador"):
            nom_j = st.text_input("Nombre completo")
            eq_j = st.selectbox("Equipo", st.session_state.equipos['Nombre'])
            col1, col2 = st.columns(2)
            vb = col1.number_input("Veces al Bate (VB)", min_value=0, step=1)
            h = col2.number_input("Hits (H)", min_value=0, step=1)
            
            if st.form_submit_button("Añadir Jugador"):
                if nom_j:
                    nuevo_j = pd.DataFrame([{"Nombre": nom_j, "Equipo": eq_j, "VB": vb, "H": h}])
                    df_final = pd.concat([st.session_state.jugadores, nuevo_j], ignore_index=True)
                    guardar_datos(df_final, JUGADORES_FILE)
                    st.session_state.jugadores = df_final
                    st.success(f"{nom_j} añadido a {eq_j}")
                    st.rerun()
