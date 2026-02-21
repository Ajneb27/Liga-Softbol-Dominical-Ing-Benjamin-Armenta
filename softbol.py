import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Liga Softbol - Admin", layout="centered")

# Credenciales (En producción, usa st.secrets)
ADMIN_USER = "admin"
ADMIN_PASSWORD = "123" 

DATA_DIR = "db_liga"
EQUIPOS_FILE = f"{DATA_DIR}/equipos.csv"
JUGADORES_FILE = f"{DATA_DIR}/jugadores.csv"

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# --- 2. FUNCIONES DE DATOS ---
def cargar_datos(archivo, columnas):
    if os.path.exists(archivo):
        return pd.read_csv(archivo)
    return pd.DataFrame(columns=columnas)

def guardar_datos(df, archivo):
    df.to_csv(archivo, index=False)

# Inicializar sesión y datos
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if 'equipos' not in st.session_state:
    st.session_state.equipos = cargar_datos(EQUIPOS_FILE, ["Nombre"])
if 'jugadores' not in st.session_state:
    st.session_state.jugadores = cargar_datos(JUGADORES_FILE, ["Nombre", "Equipo", "VB", "H"])

# --- 3. LÓGICA DE LOGIN ---
def login():
    st.title("🔐 Acceso al Sistema")
    with st.form("login_form"):
        usuario = st.text_input("Usuario")
        clave = st.text_input("Contraseña", type="password")
        if st.form_submit_button("Entrar"):
            if usuario == ADMIN_USER and clave == ADMIN_PASSWORD:
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Credenciales incorrectas")

def logout():
    st.session_state.autenticado = False
    st.rerun()

# --- 4. CUERPO PRINCIPAL ---
if not st.session_state.autenticado:
    login()
else:
    # Barra lateral con Logout
    with st.sidebar:
        st.write(f"👤 Usuario: **{ADMIN_USER}**")
        if st.button("Cerrar Sesión"):
            logout()
        st.divider()
        menu = st.radio("Menú", ["Estadísticas", "Equipos", "Jugadores"])

    st.title("🥎 Panel Administrativo")

    if menu == "Estadísticas":
        st.header("📊 Tabla de Posiciones")
        df = st.session_state.jugadores.copy()
        df['AVG'] = (df['H'] / df['VB']).fillna(0.000)
        st.dataframe(df.sort_values(by="AVG", ascending=False), use_container_width=True)

    elif menu == "Equipos":
        st.header("🏘️ Gestión de Equipos")
        with st.form("add_equipo"):
            n_eq = st.text_input("Nombre del Equipo")
            if st.form_submit_button("Guardar"):
                if n_eq:
                    nuevo_df = pd.concat([st.session_state.equipos, pd.DataFrame([{"Nombre": n_eq}])], ignore_index=True)
                    guardar_datos(nuevo_df, EQUIPOS_FILE)
                    st.session_state.equipos = nuevo_df
                    st.success("Registrado")
                    st.rerun()

    elif menu == "Jugadores":
        st.header("👤 Registro de Jugadores")
        if st.session_state.equipos.empty:
            st.warning("Crea un equipo primero.")
        else:
            with st.form("add_jugador"):
                nombre = st.text_input("Nombre")
                eq = st.selectbox("Equipo", st.session_state.equipos['Nombre'])
                v_bate = st.number_input("VB", min_value=0)
                hits = st.number_input("H", min_value=0)
                if st.form_submit_button("Agregar"):
                    n_j = pd.DataFrame([{"Nombre": nombre, "Equipo": eq, "VB": v_bate, "H": hits}])
                    st.session_state.jugadores = pd.concat([st.session_state.jugadores, n_j], ignore_index=True)
                    guardar_datos(st.session_state.jugadores, JUGADORES_FILE)
                    st.success("Añadido")
                    st.rerun()
