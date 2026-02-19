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

# Leer clave (por defecto softbol2026)
pass_maestra = open(ruta("config.txt"), "r").read().strip() if os.path.exists(ruta("config.txt")) else "softbol2026"
es_admin = (pwd_input == pass_maestra)

menu = st.sidebar.radio("MENÚ:", ["🏠 Inicio", "👥 Equipos (Alta/Editar)", "🏃 Jugadores (Alta/Editar)", "📊 Consulta por Equipo"])

# ==========================================
# SECCIÓN: EQUIPOS
# ==========================================
if menu == "👥 Equipos (Alta/Editar)":
    st.header("👥 Gestión de Equipos")
    if es_admin:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("➕ Nuevo Equipo")
            with st.form("nuevo_eq"):
                n_eq = st.text_input("Nombre del Equipo")
                if st.form_submit_button("Guardar"):
                    if n_eq and n_eq not in st.session_state.equipos['Nombre'].values:
                        st.session_state.equipos = pd.concat([st.session_state.equipos, pd.DataFrame([{"Nombre": n_eq}])], ignore_index=True)
                        guardar_datos()
                        st.success("Equipo Guardado")
                        st.rerun()
        with col2:
            st.subheader("✏️ Editar/Borrar")
            if not st.session_state.equipos.empty:
                eq_sel = st.selectbox("Selecciona Equipo:", st.session_state.equipos['Nombre'])
                nuevo_n = st.text_input("Cambiar nombre a:", value=eq_sel)
                c_b1, c_b2 = st.columns(2)
                if c_b1.button("Actualizar"):
                    st.session_state.equipos.loc[st.session_state.equipos['Nombre'] == eq_sel, 'Nombre'] = nuevo_n
                    st.session_state.jugadores.loc[st.session_state.jugadores['Equipo'] == eq_sel, 'Equipo'] = nuevo_n
                    guardar_datos(); st.rerun()
                if c_b2.button("🗑️ Borrar"):
                    st.session_state.equipos = st.session_state.equipos[st.session_state.equipos['Nombre'] != eq_sel]
                    guardar_datos(); st.rerun()
    st.table(st.session_state.equipos)

# ==========================================
# SECCIÓN: JUGADORES (CORREGIDA)
# ==========================================
elif menu == "🏃 Jugadores (Alta/Editar)":
    st.header("🏃 Gestión de Jugadores")
    lista_eq = st.session_state.equipos['Nombre'].tolist()
    
    if es_admin:
        st.subheader("➕ Registrar Nuevo Jugador")
        with st.form("nuevo_j"):
            c1, c2, c3 = st.columns(3)
            nj = c1.text_input("Nombre del Jugador")
            edj = c2.number_input("Edad", 5, 90, 20)
            eqj = c3.selectbox("Equipo", lista_eq if lista_eq else ["Sin equipos"])
            if st.form_submit_button("Registrar Jugador"):
                if nj and lista_eq:
                    nuevo_reg = pd.DataFrame([{"Nombre": nj, "Edad": edj, "Equipo": eqj, "H": 0, "HR": 0}])
                    st.session_state.jugadores = pd.concat([st.session_state.jugadores, nuevo_reg], ignore_index=True)
                    guardar_datos(); st.success("Registrado")
                    st.rerun()

        st.divider()
        st.subheader("✏️ Editar Jugador y Estadísticas")
        if not st.session_state.jugadores.empty:
            j_a_editar = st.selectbox("Selecciona Jugador:", st.session_state.jugadores['Nombre'])
            # Extraer datos actuales
            datos_j = st.session_state.jugadores[st.session_state.jugadores['Nombre'] == j_a_editar].iloc[0]
            
            with st.form("edit_j_completo"):
                ce1, ce2, ce3 = st.columns(3)
                edit_nom = ce1.text_input("Nombre", value=datos_j['Nombre'])
                edit_edad = ce2.number_input("Edad", 5, 90, int(datos_j['Edad']))
                # CORRECCIÓN DE LA VARIABLE lista_eq
                idx_eq = lista_eq.index(datos_j['Equipo']) if datos_j['Equipo'] in lista_eq else 0
                edit_eq = ce3.selectbox("Equipo (Transferencia)", lista_eq, index=idx_eq)
                
                ce4, ce5 = st.columns(2)
                edit_h = ce4.number_input("Hits (H)", min_value=0, value=int(datos_j['H']))
                edit_hr = ce5.number_input("Home Runs (HR)", min_value=0, value=int(datos_j['HR']))
                
                if st.form_submit_button("Guardar Todos los Cambios"):
                    idx_real = st.session_state.jugadores[st.session_state.jugadores['Nombre'] == j_a_editar].index[0]
                    st.session_state.jugadores.at[idx_real, 'Nombre'] = edit_nom
                    st.session_state.jugadores.at[idx_real, 'Edad'] = edit_edad
                    st.session_state.jugadores.at[idx_real, 'Equipo'] = edit_eq
                    st.session_state.jugadores.at[idx_real, 'H'] = edit_h
                    st.session_state.jugadores.at[idx_real, 'HR'] = edit_hr
                    guardar_datos(); st.success("Cambios guardados"); st.rerun()

    st.subheader("Roster General")
    st.dataframe(st.session_state.jugadores, use_container_width=True)

# ==========================================
# SECCIÓN: CONSULTA
# ==========================================
elif menu == "📊 Consulta por Equipo":
    st.header("📊 Consulta de Rosters")
    lista_eq = st.session_state.equipos['Nombre'].tolist()
    if lista_eq:
        f_eq = st.selectbox("Ver Equipo:", lista_eq)
        res = st.session_state.jugadores[st.session_state.jugadores['Equipo'] == f_eq]
        st.write(f"Jugadores en el equipo: {len(res)}")
        st.dataframe(res, use_container_width=True)
