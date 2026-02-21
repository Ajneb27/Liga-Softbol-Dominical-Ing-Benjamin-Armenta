import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN DE ARCHIVOS ---
DATA_DIR = "datos_liga"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

CONFIG_FILE = os.path.join(DATA_DIR, "config.csv")
EQUIPOS_FILE = os.path.join(DATA_DIR, "equipos.csv")
JUGADORES_FILE = os.path.join(DATA_DIR, "jugadores.csv")

# --- 2. GESTIÓN DE CREDENCIALES ---
# Si no existe el archivo de configuración, creamos las credenciales iniciales
if not os.path.exists(CONFIG_FILE):
    pd.DataFrame([{"usuario": "admin", "clave": "123"}]).to_csv(CONFIG_FILE, index=False)

def obtener_credenciales():
    df_conf = pd.read_csv(CONFIG_FILE)
    return df_conf.iloc[0]['usuario'], str(df_conf.iloc[0]['clave'])

def actualizar_credenciales(nuevo_u, nueva_c):
    pd.DataFrame([{"usuario": nuevo_u, "clave": nueva_c}]).to_csv(CONFIG_FILE, index=False)

def cargar_datos(ruta, columnas):
    if os.path.exists(ruta):
        return pd.read_csv(ruta)
    return pd.DataFrame(columns=columnas)

# --- 3. ESTADO DE SESIÓN ---
if 'es_admin' not in st.session_state:
    st.session_state.es_admin = False

ADMIN_USER, ADMIN_PASS = obtener_credenciales()
df_e = cargar_datos(EQUIPOS_FILE, ["Nombre"])
df_j = cargar_datos(JUGADORES_FILE, ["Nombre", "Equipo", "VB", "H"])

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.title("🥎 Liga Softbol")
    if not st.session_state.es_admin:
        st.header("🔐 Acceso Admin")
        u_input = st.text_input("Usuario")
        p_input = st.text_input("Contraseña", type="password")
        if st.button("Entrar"):
            if u_input == ADMIN_USER and p_input == ADMIN_PASS:
                st.session_state.es_admin = True
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
    else:
        st.success(f"Conectado como: {ADMIN_USER}")
        if st.button("Cerrar Sesión"):
            st.session_state.es_admin = False
            st.rerun()
    
    st.divider()
    opciones = ["📊 Estadísticas Públicas"]
    if st.session_state.es_admin:
        opciones += ["🏘️ Gestión Equipos", "👤 Registro Jugadores", "🔑 Cambiar Clave", "💾 RESPALDO"]
    
    menu = st.radio("Ir a:", opciones)

# --- 5. SECCIONES ---

if menu == "📊 Estadísticas Públicas":
    st.header("Ranking de Bateo")
    if not df_j.empty:
        df_j['AVG'] = (df_j['H'] / df_j['VB']).fillna(0.000)
        st.dataframe(df_j.sort_values(by="AVG", ascending=False), use_container_width=True)
    else:
        st.info("Aún no hay datos de jugadores.")

elif menu == "🔑 Cambiar Clave":
    st.header("Configuración de Seguridad")
    nuevo_usuario = st.text_input("Nuevo nombre de usuario", value=ADMIN_USER)
    nueva_clave = st.text_input("Nueva contraseña", type="password")
    confirmar = st.text_input("Confirmar contraseña", type="password")
    
    if st.button("Actualizar Credenciales"):
        if nueva_clave == confirmar and nueva_clave != "":
            actualizar_credenciales(nuevo_usuario, nueva_clave)
            st.success("¡Credenciales actualizadas! Se cerrará la sesión por seguridad.")
            st.session_state.es_admin = False
            st.rerun()
        else:
            st.error("Las contraseñas no coinciden o están vacías.")

elif menu == "🏘️ Gestión Equipos":
    # ... (Mismo código de gestión de equipos anterior)
    st.header("Equipos")
    nuevo_eq = st.text_input("Nombre del Equipo")
    if st.button("Guardar Equipo"):
        df_e = pd.concat([df_e, pd.DataFrame([{"Nombre": nuevo_eq}])], ignore_index=True)
        df_e.to_csv(EQUIPOS_FILE, index=False)
        st.success("Guardado")
        st.rerun()

elif menu == "👤 Registro Jugadores":
    # ... (Mismo código de registro de jugadores anterior)
    st.header("Nuevo Jugador")
    with st.form("form_j"):
        n = st.text_input("Nombre")
        eq = st.selectbox("Equipo", df_e["Nombre"])
        v = st.number_input("VB", min_value=0)
        h = st.number_input("H", min_value=0)
        if st.form_submit_button("Registrar"):
            df_j = pd.concat([df_j, pd.DataFrame([{"Nombre": n, "Equipo": eq, "VB": v, "H": h}])], ignore_index=True)
            df_j.to_csv(JUGADORES_FILE, index=False)
            st.success("Registrado")
            st.rerun()

elif menu == "💾 RESPALDO":
    # ... (Sección de respaldo para descargar/subir CSV)
    st.header("Respaldo")
    csv = df_j.to_csv(index=False).encode('utf-8')
    st.download_button("Descargar Respaldo Jugadores", csv, "jugadores.csv", "text/csv")
