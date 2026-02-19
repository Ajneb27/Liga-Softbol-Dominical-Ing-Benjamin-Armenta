import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN DE CARPETAS Y DATOS ---
CARPETA_DATOS = "datos_liga"
if not os.path.exists(CARPETA_DATOS):
    os.makedirs(CARPETA_DATOS)

def ruta(archivo):
    return os.path.join(CARPETA_DATOS, archivo)

# Inicializar bases de datos
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

menu = st.sidebar.radio("MENÚ:", ["🏠 Inicio", "👥 Equipos (Alta/Editar)", "🏃 Jugadores (Alta/Editar)", "📊 Consulta por Equipo"])

# ==========================================
# SECCIÓN: EQUIPOS (ALTA Y EDICIÓN)
# ==========================================
if menu == "👥 Equipos (Alta/Editar)":
    st.header("👥 Gestión de Equipos")
    
    if es_admin:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("➕ Nuevo Equipo")
            with st.form("nuevo_eq"):
                n_eq = st.text_input("Nombre")
                if st.form_submit_button("Guardar"):
                    if n_eq and n_eq not in st.session_state.equipos['Nombre'].values:
                        st.session_state.equipos = pd.concat([st.session_state.equipos, pd.DataFrame([{"Nombre": n_eq}])], ignore_index=True)
                        guardar_datos(); st.success("Guardado")
        
        with col2:
            st.subheader("✏️ Editar/Borrar Equipo")
            if not st.session_state.equipos.empty:
                eq_edit = st.selectbox("Selecciona equipo:", st.session_state.equipos['Nombre'])
                nuevo_nom = st.text_input("Nuevo nombre:", value=eq_edit)
                c_edit1, c_edit2 = st.columns(2)
                if c_edit1.button("Actualizar Nombre"):
                    st.session_state.equipos.loc[st.session_state.equipos['Nombre'] == eq_edit, 'Nombre'] = nuevo_nom
                    # Actualizar también a los jugadores de ese equipo
                    st.session_state.jugadores.loc[st.session_state.jugadores['Equipo'] == eq_edit, 'Equipo'] = nuevo_nom
                    guardar_datos(); st.rerun()
                if c_edit2.button("🗑️ Borrar Equipo"):
                    st.session_state.equipos = st.session_state.equipos[st.session_state.equipos['Nombre'] != eq_edit]
                    guardar_datos(); st.rerun()

    st.subheader("Equipos en la Liga")
    st.table(st.session_state.equipos)

# ==========================================
# SECCIÓN: JUGADORES (ALTA Y EDICIÓN/TRANSFERENCIA)
# ==========================================
elif menu == "🏃 Jugadores (Alta/Editar)":
    st.header("🏃 Gestión de Jugadores")
    
    lista_eq = st.session_state.equipos['Nombre'].tolist()
    
    if es_admin:
        st.subheader("➕ Registrar Nuevo Jugador")
        with st.form("nuevo_j"):
            c1, c2, c3 = st.columns(3)
            nj = c1.text_input("Nombre")
            edj = c2.number_input("Edad", 5, 90, 20)
            eqj = c3.selectbox("Equipo", lista_eq)
            if st.form_submit_button("Registrar"):
                st.session_state.jugadores = pd.concat([st.session_state.jugadores, pd.DataFrame([{"Nombre": nj, "Edad": edj, "Equipo": eqj, "H": 0, "HR": 0}])], ignore_index=True)
                guardar_datos(); st.success(f"{nj} registrado")

        st.divider()
        st.subheader("✏️ Editar o Transferir Jugador")
        if not st.session_state.jugadores.empty:
            j_edit = st.selectbox("Selecciona jugador para editar:", st.session_state.jugadores['Nombre'])
            # Obtener datos actuales
            datos_act = st.session_state.jugadores[st.session_state.jugadores['Nombre'] == j_edit].iloc[0]
            
            with st.form("edit_j"):
                ce1, ce2, ce3 = st.columns(3)
                nuevo_nj = ce1.text_input("Editar Nombre", value=datos_act['Nombre'])
                nuevo_ed = ce2.number_input("Editar Edad", 5, 90, int(datos_act['Edad']))
                nuevo_eq = ce3.selectbox("Transferir a Equipo", lista_eq, index=lista_equipos.index(datos_act['Equipo']) if datos_act['Equipo'] in lista_eq else 0)
                
                if st.form_submit_button("Guardar Cambios del Jugador"):
                    idx = st.session_state.jugadores[st.session_state.jugadores['Nombre'] == j_edit].index[0]
                    st.session_state.jugadores.at[idx, 'Nombre'] = nuevo_nj
                    st.session_state.jugadores.at[idx, 'Edad'] = nuevo_ed
                    st.session_state.jugadores.at[idx, 'Equipo'] = nuevo_eq
                    guardar_datos(); st.success("Datos actualizados"); st.rerun()

    st.subheader("Lista Completa de Jugadores")
    st.dataframe(st.session_state.jugadores, use_container_width=True)

# ==========================================
# SECCIÓN: CONSULTA (ROSTER POR EQUIPO)
# ==========================================
elif menu == "📊 Consulta por Equipo":
    st.header("📊 Roster por Equipo")
    lista_eq = st.session_state.equipos['Nombre'].tolist()
    if lista_eq:
        f_eq = st.selectbox("Selecciona Equipo:", lista_eq)
        roster = st.session_state.jugadores[st.session_state.jugadores['Equipo'] == f_eq]
        st.write(f"Total de jugadores: {len(roster)}")
        st.dataframe(roster[["Nombre", "Edad", "H", "HR"]], use_container_width=True)
