import streamlit as st
import pandas as pd
import os

# --- 1. AJUSTES DE SEGURIDAD ---
ADMIN_USER = "admin"
ADMIN_PASS = "123"

# --- 2. GESTIÓN DE ARCHIVOS ---
DATA_DIR = "datos_liga"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

EQUIPOS_FILE = os.path.join(DATA_DIR, "equipos.csv")
JUGADORES_FILE = os.path.join(DATA_DIR, "jugadores.csv")

def cargar_datos(ruta, columnas):
    if os.path.exists(ruta):
        return pd.read_csv(ruta)
    return pd.DataFrame(columns=columnas)

# --- 3. INICIALIZACIÓN ---
if 'es_admin' not in st.session_state:
    st.session_state.es_admin = False

df_e = cargar_datos(EQUIPOS_FILE, ["Nombre"])
df_j = cargar_datos(JUGADORES_FILE, ["Nombre", "Equipo", "VB", "H"])

# --- 4. BARRA LATERAL (LOGIN) ---
with st.sidebar:
    if not st.session_state.es_admin:
        st.header("🔐 Acceso Admin")
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        if st.button("Entrar"):
            if u == ADMIN_USER and p == ADMIN_PASS:
                st.session_state.es_admin = True
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
    else:
        st.success(f"Sesión activa: {ADMIN_USER}")
        if st.button("Cerrar Sesión"):
            st.session_state.es_admin = False
            st.rerun()
    
    st.divider()
    menu = st.radio("Secciones:", ["📊 Estadísticas Públicas", "🏘️ Gestión Equipos", "👤 Registro Jugadores", "💾 RESPALDO"])

# --- 5. LÓGICA DE VISIBILIDAD ---

# ESTA SECCIÓN ES PÚBLICA (Todos pueden verla)
if menu == "📊 Estadísticas Públicas":
    st.title("🥎 Estadísticas de la Liga")
    if not df_j.empty:
        df_j['AVG'] = (df_j['H'] / df_j['VB']).fillna(0.000)
        st.dataframe(df_j.sort_values(by="AVG", ascending=False), use_container_width=True)
    else:
        st.info("No hay datos cargados todavía.")

# LAS SIGUIENTES SECCIONES REQUIEREN SER ADMIN
elif menu in ["🏘️ Gestión Equipos", "👤 Registro Jugadores", "💾 RESPALDO"]:
    if not st.session_state.es_admin:
        st.warning("⚠️ Debes iniciar sesión como administrador para ver esta sección.")
    else:
        if menu == "🏘️ Gestión Equipos":
            st.header("Gestionar Equipos")
            nuevo_eq = st.text_input("Nombre del Equipo")
            if st.button("Guardar"):
                df_e = pd.concat([df_e, pd.DataFrame([{"Nombre": nuevo_eq}])], ignore_index=True)
                df_e.to_csv(EQUIPOS_FILE, index=False)
                st.success("Guardado")
                st.rerun()

        elif menu == "👤 Registro Jugadores":
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
            st.header("Respaldo Anti-Borrado")
            csv = df_j.to_csv(index=False).encode('utf-8')
            st.download_button("Descargar Respaldo CSV", csv, "liga_respaldo.csv", "text/csv")
            archivo = st.file_uploader("Subir Respaldo para restaurar", type="csv")
            if archivo:
                pd.read_csv(archivo).to_csv(JUGADORES_FILE, index=False)
                st.success("¡Datos restaurados!")
