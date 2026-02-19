import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN DE CARPETAS Y DATOS ---
CARPETA_DATOS = "datos_liga"
if not os.path.exists(CARPETA_DATOS):
    os.makedirs(CARPETA_DATOS)

def ruta(archivo):
    return os.path.join(CARPETA_DATOS, archivo)

# Inicializar bases de datos en la sesión
if 'equipos' not in st.session_state:
    st.session_state.equipos = pd.read_csv(ruta("data_equipos.csv")) if os.path.exists(ruta("data_equipos.csv")) else pd.DataFrame(columns=["Nombre"])

if 'jugadores' not in st.session_state:
    st.session_state.jugadores = pd.read_csv(ruta("data_jugadores.csv")) if os.path.exists(ruta("data_jugadores.csv")) else pd.DataFrame(columns=["Nombre", "Edad", "Equipo", "H", "HR"])

def guardar_datos():
    st.session_state.equipos.to_csv(ruta("data_equipos.csv"), index=False)
    st.session_state.jugadores.to_csv(ruta("data_jugadores.csv"), index=False)

# --- 2. BARRA LATERAL (LOGIN) ---
st.sidebar.title("⚾ LIGA SOFTBOL 2026")
with st.sidebar.form("login_form"):
    pwd_input = st.text_input("Contraseña Admin:", type="password")
    if st.form_submit_button("Entrar"): pass

pass_maestra = open(ruta("config.txt"), "r").read().strip() if os.path.exists(ruta("config.txt")) else "softbol2026"
es_admin = (pwd_input == pass_maestra)

menu = st.sidebar.radio("MENÚ:", ["🏠 Inicio", "👥 Registro de Equipos", "🏃 Registro de Jugadores", "📊 Estadísticas por Equipo"])

# ==========================================
# SECCIÓN: REGISTRO DE EQUIPOS
# ==========================================
if menu == "👥 Registro de Equipos":
    st.header("👥 Gestión de Equipos")
    if es_admin:
        with st.form("nuevo_equipo"):
            n_eq = st.text_input("Nombre del Equipo (ej. Tomateros)")
            if st.form_submit_button("Guardar Equipo"):
                if n_eq and n_eq not in st.session_state.equipos['Nombre'].values:
                    st.session_state.equipos = pd.concat([st.session_state.equipos, pd.DataFrame([{"Nombre": n_eq}])], ignore_index=True)
                    guardar_datos()
                    st.success(f"Equipo {n_eq} listo.")
                else: st.error("Nombre inválido o ya existe.")
    
    st.subheader("Lista de Equipos")
    st.dataframe(st.session_state.equipos, use_container_width=True)

# ==========================================
# SECCIÓN: REGISTRO DE JUGADORES (EDAD Y EQUIPO VINCULADO)
# ==========================================
elif menu == "🏃 Registro de Jugadores":
    st.header("🏃 Alta de Jugadores")
    
    lista_equipos = st.session_state.equipos['Nombre'].tolist()
    
    if not lista_equipos:
        st.warning("⚠️ Primero debes registrar al menos un equipo en la sección anterior.")
    elif es_admin:
        with st.form("nuevo_jugador"):
            nom_j = st.text_input("Nombre del Jugador")
            edad_j = st.number_input("Edad", min_value=5, max_value=90, step=1)
            # Aquí es donde se direcciona al equipo correcto
            eq_j = st.selectbox("Asignar a Equipo:", lista_equipos)
            
            if st.form_submit_button("Registrar Jugador"):
                if nom_j:
                    nuevo_j = pd.DataFrame([{"Nombre": nom_j, "Edad": edad_j, "Equipo": eq_j, "H": 0, "HR": 0}])
                    st.session_state.jugadores = pd.concat([st.session_state.jugadores, nuevo_j], ignore_index=True)
                    guardar_datos()
                    st.success(f"¡{nom_j} ha sido asignado a {eq_j}!")
                else: st.error("El nombre no puede estar vacío.")

    st.subheader("Todos los Jugadores Registrados")
    st.dataframe(st.session_state.jugadores, use_container_width=True)

# ==========================================
# SECCIÓN: ESTADÍSTICAS POR EQUIPO (DIRECCIONAMIENTO)
# ==========================================
elif menu == "📊 Estadísticas por Equipo":
    st.header("📊 Consulta por Equipo")
    lista_equipos = st.session_state.equipos['Nombre'].tolist()
    
    if not lista_equipos:
        st.info("No hay datos para mostrar.")
    else:
        filtro_eq = st.selectbox("Selecciona un equipo para ver su roster:", lista_equipos)
        
        # Filtrado inteligente
        roster = st.session_state.jugadores[st.session_state.jugadores['Equipo'] == filtro_eq]
        
        if roster.empty:
            st.warning(f"No hay jugadores en el equipo {filtro_eq}.")
        else:
            st.subheader(f"Roster de {filtro_eq}")
            st.write(f"Total de jugadores: {len(roster)}")
            st.dataframe(roster[["Nombre", "Edad", "H", "HR"]], use_container_width=True)
