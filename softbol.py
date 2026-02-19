import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN ESTRUCTURAL ---
st.set_page_config(page_title="LIGA REINICIO", layout="wide")

DB_DIR = "database"
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

# Definimos las tablas base
ESTRUCTURA = {
    "equipos": ["Nombre"],
    "jugadores": ["Nombre", "Equipo", "VB", "H", "HR"],
    "calendario": ["Fecha", "Local", "Visitante", "Score"]
}

# --- 2. MOTOR DE DATOS (EL CORAZÓN DE LA APP) ---
def cargar_tabla(nombre):
    ruta = os.path.join(DB_DIR, f"{nombre}.csv")
    if os.path.exists(ruta):
        return pd.read_csv(ruta)
    return pd.DataFrame(columns=ESTRUCTURA[nombre])

def guardar_y_refrescar(nombre, df):
    ruta = os.path.join(DB_DIR, f"{nombre}.csv")
    df.to_csv(ruta, index=False)
    st.session_state[nombre] = df
    st.cache_data.clear() # Limpia cualquier memoria vieja
    st.rerun() # Fuerza a la app a mostrar el cambio

# Carga inicial en la memoria de la App
for tabla in ESTRUCTURA:
    if tabla not in st.session_state:
        st.session_state[tabla] = cargar_tabla(tabla)

# --- 3. INTERFAZ VISUAL ---
st.title("⚾ SISTEMA DE GESTIÓN DE LIGA")
st.markdown("---")

menu = st.sidebar.radio("MENÚ PRINCIPAL", ["🏠 Tablero", "👥 Equipos", "🏃 Jugadores", "📅 Calendario"])

# --- SECCIÓN: EQUIPOS ---
if menu == "👥 Equipos":
    st.header("Gestión de Equipos")
    
    # Formulario para agregar
    with st.form("nuevo_equipo", clear_on_submit=True):
        nombre_eq = st.text_input("Nombre del Nuevo Equipo")
        if st.form_submit_button("➕ Registrar Equipo"):
            if nombre_eq:
                nuevo_df = pd.concat([st.session_state.equipos, pd.DataFrame([{"Nombre": nombre_eq}])], ignore_index=True)
                guardar_y_refrescar("equipos", nuevo_df)

    # Tabla y Borrado
    st.subheader("Equipos Registrados")
    if not st.session_state.equipos.empty:
        st.dataframe(st.session_state.equipos, use_container_width=True)
        equipo_a_borrar = st.selectbox("Selecciona para eliminar:", st.session_state.equipos["Nombre"])
        if st.button("🗑️ Eliminar Equipo Seleccionado"):
            df_reducido = st.session_state.equipos[st.session_state.equipos["Nombre"] != equipo_a_borrar]
            guardar_y_refrescar("equipos", df_reducido)

# --- SECCIÓN: JUGADORES ---
elif menu == "🏃 Jugadores":
    st.header("Control de Jugadores")
    
    if st.session_state.equipos.empty:
        st.warning("⚠️ Primero debes registrar al menos un equipo.")
    else:
        with st.form("nuevo_jugador", clear_on_submit=True):
            col1, col2 = st.columns(2)
            n_jug = col1.text_input("Nombre del Jugador")
            e_jug = col2.selectbox("Equipo", st.session_state.equipos["Nombre"])
            if st.form_submit_button("✅ Guardar Jugador"):
                nuevo_j = pd.DataFrame([{"Nombre": n_jug, "Equipo": e_jug, "VB": 0, "H": 0, "HR": 0}])
                df_j_final = pd.concat([st.session_state.jugadores, nuevo_j], ignore_index=True)
                guardar_y_refrescar("jugadores", df_j_final)

        st.subheader("Roster General")
        st.dataframe(st.session_state.jugadores, use_container_width=True, hide_index=True)

# --- SECCIÓN: CALENDARIO ---
elif menu == "📅 Calendario":
    st.header("Calendario y Resultados")
    
    with st.expander("🗓️ Programar Nuevo Juego"):
        with st.form("juego"):
            f = st.date_input("Fecha")
            loc = st.selectbox("Local", st.session_state.equipos["Nombre"], key="loc")
            vis = st.selectbox("Visitante", st.session_state.equipos["Nombre"], key="vis")
            if st.form_submit_button("Programar"):
                nuevo_p = pd.DataFrame([{"Fecha": str(f), "Local": loc, "Visitante": vis, "Score": "0-0"}])
                df_c = pd.concat([st.session_state.calendario, nuevo_p], ignore_index=True)
                guardar_y_refrescar("calendario", df_c)

    st.subheader("Partidos")
    st.dataframe(st.session_state.calendario, use_container_width=True)

# --- SECCIÓN: TABLERO (HOME) ---
elif menu == "🏠 Tablero":
    st.subheader("Resumen de la Liga")
    c1, c2, c3 = st.columns(3)
    c1.metric("Equipos", len(st.session_state.equipos))
    c2.metric("Jugadores", len(st.session_state.jugadores))
    c3.metric("Juegos", len(st.session_state.calendario))
