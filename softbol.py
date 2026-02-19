import streamlit as st
import pandas as pd
import os

# --- CONFIGURACIÓN DE CARPETA ---
CARPETA_DATOS = "datos_liga"
if not os.path.exists(CARPETA_DATOS):
    os.makedirs(CARPETA_DATOS)

def ruta(archivo):
    return os.path.join(CARPETA_DATOS, archivo)

# --- REPARADOR DE COLUMNAS ---
def cargar_datos_seguros():
    cols = ["Nombre", "Edad", "Equipo", "H", "H2", "H3", "HR"]
    if os.path.exists(ruta("data_jugadores.csv")):
        df = pd.read_csv(ruta("data_jugadores.csv"))
        for c in cols:
            if c not in df.columns: df[c] = 0
        return df
    return pd.DataFrame(columns=cols)

# Inicializar
if 'jugadores' not in st.session_state: st.session_state.jugadores = cargar_datos_seguros()
if 'equipos' not in st.session_state: 
    st.session_state.equipos = pd.read_csv(ruta("data_equipos.csv")) if os.path.exists(ruta("data_equipos.csv")) else pd.DataFrame(columns=["Nombre"])

def guardar_datos():
    st.session_state.equipos.to_csv(ruta("data_equipos.csv"), index=False)
    st.session_state.jugadores.to_csv(ruta("data_jugadores.csv"), index=False)

# --- BARRA LATERAL ---
st.sidebar.title("⚾ LIGA SOFTBOL 2026")
pwd = st.sidebar.text_input("Contraseña Admin:", type="password")
pass_m = open(ruta("config.txt"), "r").read().strip() if os.path.exists(ruta("config.txt")) else "softbol2026"
es_admin = (pwd == pass_m)

if es_admin:
    st.sidebar.success("✅ Modo Editor Activo")
else:
    st.sidebar.warning("🔒 Modo Lectura")

menu = st.sidebar.radio("MENÚ:", ["🏠 Inicio", "👥 Equipos", "🏃 Jugadores y Stats"])

# ==========================================
# SECCIÓN: INICIO (PARA QUE NO SE VEA VACÍO)
# ==========================================
if menu == "🏠 Inicio":
    st.header("🏆 Bienvenidos a la Liga de Softbol 2026")
    st.write("Utiliza el menú de la izquierda para navegar.")
    col1, col2 = st.columns(2)
    col1.metric("Equipos Registrados", len(st.session_state.equipos))
    col2.metric("Jugadores Totales", len(st.session_state.jugadores))
    st.info("💡 Si eres administrador, ingresa tu clave en la barra lateral para registrar o editar datos.")

# ==========================================
# SECCIÓN: EQUIPOS
# ==========================================
elif menu == "👥 Equipos":
    st.header("👥 Gestión de Equipos")
    if es_admin:
        with st.form("f_eq"):
            n_eq = st.text_input("Nombre del Nuevo Equipo")
            if st.form_submit_button("Guardar Equipo"):
                if n_eq and n_eq not in st.session_state.equipos['Nombre'].values:
                    st.session_state.equipos = pd.concat([st.session_state.equipos, pd.DataFrame([{"Nombre": n_eq}])], ignore_index=True)
                    guardar_datos(); st.success(f"Equipo {n_eq} listo."); st.rerun()
    
    st.subheader("Lista de Equipos")
    st.table(st.session_state.equipos)

# ==========================================
# SECCIÓN: JUGADORES
# ==========================================
elif menu == "🏃 Jugadores y Stats":
    st.header("🏃 Estadísticas de Jugadores")
    lista_eq = st.session_state.equipos['Nombre'].tolist()
    
    if es_admin:
        with st.expander("➕ Registrar Nuevo Jugador"):
            if not lista_eq:
                st.error("⚠️ Primero debes registrar un equipo en la sección 'Equipos'.")
            else:
                with st.form("f_j"):
                    n, ed = st.text_input("Nombre"), st.number_input("Edad", 5, 90, 20)
                    eq = st.selectbox("Equipo", lista_eq)
                    if st.form_submit_button("Registrar"):
                        nuevo = pd.DataFrame([{"Nombre": n, "Edad": ed, "Equipo": eq, "H": 0, "H2": 0, "H3": 0, "HR": 0}])
                        st.session_state.jugadores = pd.concat([st.session_state.jugadores, nuevo], ignore_index=True)
                        guardar_datos(); st.rerun()

    st.subheader("Roster de la Liga")
    st.dataframe(st.session_state.jugadores, use_container_width=True)
