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

# --- 2. SISTEMA DE LOGIN VISUAL ---
st.sidebar.title("🔐 ACCESO A LA LIGA")

# Usamos un estado de sesión para mantener la puerta abierta una vez que entras
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

# Formulario de entrada
with st.sidebar.form("login_form"):
    clave = st.text_input("Contraseña Maestra:", type="password")
    boton_entrar = st.form_submit_button("🔓 ABRIR PANEL DE CONTROL")

if boton_entrar:
    if clave == "softbol2026":
        st.session_state.autenticado = True
        st.sidebar.success("✅ ¡ADMINISTRADOR CONECTADO!")
    else:
        st.session_state.autenticado = False
        st.sidebar.error("❌ CLAVE INCORRECTA")

# Botón para salir (Cierra la sesión)
if st.session_state.autenticado:
    if st.sidebar.button("🔒 CERRAR SESIÓN"):
        st.session_state.autenticado = False
        st.rerun()

st.sidebar.markdown("---")
menu = st.sidebar.radio("Navegación:", ["🏠 Inicio", "👥 Equipos", "🏃 Jugadores"])

# ==========================================
# SECCIÓN: EQUIPOS (ALTA)
# ==========================================
if menu == "👥 Equipos":
    st.header("👥 Gestión de Equipos")
    
    if st.session_state.autenticado:
        st.success("🛠️ PANEL DE EDICIÓN ACTIVO")
        with st.form("nuevo_eq"):
            n_eq = st.text_input("Escribe el nombre del equipo:")
            if st.form_submit_button("➕ GUARDAR EQUIPO"):
                if n_eq and n_eq not in st.session_state.equipos['Nombre'].values:
                    st.session_state.equipos = pd.concat([st.session_state.equipos, pd.DataFrame([{"Nombre": n_eq}])], ignore_index=True)
                    guardar_datos()
                    st.success(f"¡Equipo {n_eq} registrado con éxito!")
                    st.rerun()
    else:
        st.info("📢 Registra la clave en la barra lateral para agregar equipos.")

    st.subheader("Equipos en la Liga")
    st.table(st.session_state.equipos)

# ==========================================
# SECCIÓN: JUGADORES (ALTA)
# ==========================================
elif menu == "🏃 Jugadores":
    st.header("🏃 Registro de Jugadores")
    lista_eq = st.session_state.equipos['Nombre'].tolist()
    
    if st.session_state.autenticado:
        st.success("🛠️ PANEL DE EDICIÓN ACTIVO")
        if not lista_eq:
            st.error("⚠️ No puedes registrar jugadores si no hay equipos. Ve a la sección 'Equipos' primero.")
        else:
            with st.form("nuevo_jug"):
                nom = st.text_input("Nombre del Jugador")
                ed = st.number_input("Edad", 5, 90, 20)
                eq = st.selectbox("Asignar a Equipo:", lista_eq)
                if st.form_submit_button("💾 GUARDAR JUGADOR"):
                    if nom:
                        nuevo_j = pd.DataFrame([{"Nombre": nom, "Edad": ed, "Equipo": eq, "H": 0, "H2": 0, "H3": 0, "HR": 0}])
                        st.session_state.jugadores = pd.concat([st.session_state.jugadores, nuevo_j], ignore_index=True)
                        guardar_datos()
                        st.success(f"¡{nom} registrado!")
                        st.rerun()
    else:
        st.info("📢 Registra la clave en la barra lateral para agregar jugadores.")

    st.subheader("Lista de Jugadores")
    st.dataframe(st.session_state.jugadores, use_container_width=True)

# ==========================================
# SECCIÓN: INICIO
# ==========================================
elif menu == "🏠 Inicio":
    st.header("🏆 Liga de Softbol 2026")
    if st.session_state.autenticado:
        st.balloons() # Celebra que entraste
        st.success("🌟 Bienvenido, Administrador. Tienes acceso total.")
    else:
        st.write("Bienvenido. Ingresa tu clave para gestionar la liga.")
