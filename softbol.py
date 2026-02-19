import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN DE CARPETA Y DATOS ---
CARPETA_DATOS = "datos_liga"
if not os.path.exists(CARPETA_DATOS):
    os.makedirs(CARPETA_DATOS)

def ruta(archivo):
    return os.path.join(CARPETA_DATOS, archivo)

# Inicializar bases de datos en la memoria
if 'equipos' not in st.session_state:
    st.session_state.equipos = pd.read_csv(ruta("data_equipos.csv")) if os.path.exists(ruta("data_equipos.csv")) else pd.DataFrame(columns=["Nombre"])

if 'jugadores' not in st.session_state:
    st.session_state.jugadores = pd.read_csv(ruta("data_jugadores.csv")) if os.path.exists(ruta("data_jugadores.csv")) else pd.DataFrame(columns=["Nombre", "Edad", "Equipo", "H", "H2", "H3", "HR"])

def guardar_datos():
    st.session_state.equipos.to_csv(ruta("data_equipos.csv"), index=False)
    st.session_state.jugadores.to_csv(ruta("data_jugadores.csv"), index=False)

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

if st.session_state.autenticado:
    if st.sidebar.button("🔒 CERRAR SESIÓN"):
        st.session_state.autenticado = False
        st.rerun()

menu = st.sidebar.radio("Navegación:", ["🏠 Inicio", "👥 Equipos", "🏃 Jugadores (Roster)"])

# ==========================================
# SECCIÓN: EQUIPOS (ALTA Y BORRADO)
# ==========================================
if menu == "👥 Equipos":
    st.header("👥 Gestión de Equipos")
    
    if st.session_state.autenticado:
        with st.form("nuevo_eq"):
            n_eq = st.text_input("Nombre del Nuevo Equipo:")
            if st.form_submit_button("➕ GUARDAR EQUIPO"):
                if n_eq and n_eq not in st.session_state.equipos['Nombre'].values:
                    st.session_state.equipos = pd.concat([st.session_state.equipos, pd.DataFrame([{"Nombre": n_eq}])], ignore_index=True)
                    guardar_datos()
                    st.success(f"Equipo {n_eq} registrado")
                    st.rerun()

        st.divider()
        st.subheader("🗑️ Borrar Equipo")
        if not st.session_state.equipos.empty:
            eq_a_borrar = st.selectbox("Selecciona equipo para eliminar:", st.session_state.equipos['Nombre'])
            if st.button("❌ ELIMINAR EQUIPO SELECCIONADO"):
                st.session_state.equipos = st.session_state.equipos[st.session_state.equipos['Nombre'] != eq_a_borrar]
                # También borramos jugadores de ese equipo
                st.session_state.jugadores = st.session_state.jugadores[st.session_state.jugadores['Equipo'] != eq_a_borrar]
                guardar_datos()
                st.warning(f"Equipo {eq_a_borrar} eliminado.")
                st.rerun()

    st.subheader("Lista de Equipos Registrados")
    st.table(st.session_state.equipos)

# ==========================================
# SECCIÓN: JUGADORES (ALTA, SELECCIÓN Y EDICIÓN)
# ==========================================
elif menu == "🏃 Jugadores (Roster)":
    st.header("🏃 Gestión de Jugadores")
    # LISTA DE EQUIPOS PARA SELECCIONAR (DIRECCIONAMIENTO)
    lista_eq = st.session_state.equipos['Nombre'].tolist()
    
    if st.session_state.autenticado:
        if not lista_eq:
            st.error("⚠️ No hay equipos. Registra uno primero en la sección 'Equipos'.")
        else:
            # FORMULARIO DE ALTA
            with st.expander("➕ REGISTRAR NUEVO JUGADOR"):
                with st.form("nuevo_jug"):
                    nom = st.text_input("Nombre")
                    ed = st.number_input("Edad", 5, 90, 20)
                    eq = st.selectbox("Seleccionar Equipo:", lista_eq) # Aquí se direcciona
                    if st.form_submit_button("💾 GUARDAR JUGADOR"):
                        nuevo_j = pd.DataFrame([{"Nombre": nom, "Edad": ed, "Equipo": eq, "H": 0, "H2": 0, "H3": 0, "HR": 0}])
                        st.session_state.jugadores = pd.concat([st.session_state.jugadores, nuevo_j], ignore_index=True)
                        guardar_datos()
                        st.success("¡Registrado!")
                        st.rerun()

            st.divider()
            # SECCIÓN DE EDICIÓN Y BORRADO DE JUGADORES
            st.subheader("✏️ Editar o Borrar Jugador")
            if not st.session_state.jugadores.empty:
                j_sel = st.selectbox("Seleccionar Jugador para modificar:", st.session_state.jugadores['Nombre'])
                idx = st.session_state.jugadores[st.session_state.jugadores['Nombre'] == j_sel].index[0]
                
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    nuevo_nombre = st.text_input("Cambiar Nombre:", st.session_state.jugadores.at[idx, 'Nombre'])
                    nueva_edad = st.number_input("Cambiar Edad:", 5, 90, int(st.session_state.jugadores.at[idx, 'Edad']))
                with col_e2:
                    nuevo_equipo = st.selectbox("Mover a Equipo:", lista_eq, index=lista_eq.index(st.session_state.jugadores.at[idx, 'Equipo']))
                
                c_btn1, c_btn2 = st.columns(2)
                if c_btn1.button("💾 ACTUALIZAR DATOS"):
                    st.session_state.jugadores.at[idx, 'Nombre'] = nuevo_nombre
                    st.session_state.jugadores.at[idx, 'Edad'] = nueva_edad
                    st.session_state.jugadores.at[idx, 'Equipo'] = nuevo_equipo
                    guardar_datos()
                    st.success("Actualizado")
                    st.rerun()
                
                if c_btn2.button("🗑️ BORRAR JUGADOR"):
                    st.session_state.jugadores = st.session_state.jugadores.drop(idx)
                    guardar_datos()
                    st.warning("Jugador eliminado")
                    st.rerun()

    # VISUALIZACIÓN POR EQUIPO (FILTRO)
    st.subheader("🔍 Ver Roster por Equipo")
    if lista_eq:
        filtro = st.selectbox("Filtrar Tabla:", ["Todos"] + lista_eq)
        if filtro == "Todos":
            st.dataframe(st.session_state.jugadores, use_container_width=True)
        else:
            st.dataframe(st.session_state.jugadores[st.session_state.jugadores['Equipo'] == filtro], use_container_width=True)

# ==========================================
# SECCIÓN: INICIO
# ==========================================
elif menu == "🏠 Inicio":
    st.header("🏆 Liga de Softbol 2026")
    st.write(f"Equipos: {len(st.session_state.equipos)} | Jugadores: {len(st.session_state.jugadores)}")
