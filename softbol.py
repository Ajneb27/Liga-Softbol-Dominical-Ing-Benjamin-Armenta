import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN DE ARCHIVOS ---
DATA_DIR = "datos_liga_final"
if not os.path.exists(DATA_DIR): 
    os.makedirs(DATA_DIR)

EQUIPOS_FILE = os.path.join(DATA_DIR, "equipos.csv")
JUGADORES_FILE = os.path.join(DATA_DIR, "jugadores.csv")
CONFIG_FILE = os.path.join(DATA_DIR, "config.csv")

# Credenciales iniciales (admin / 123)
if not os.path.exists(CONFIG_FILE):
    pd.DataFrame([{"user": "admin", "pass": "123"}]).to_csv(CONFIG_FILE, index=False)

# --- 2. FUNCIONES DE CARGA ---
def cargar_csv(ruta, columnas):
    if os.path.exists(ruta): 
        return pd.read_csv(ruta)
    return pd.DataFrame(columns=columnas)

# --- 3. INICIALIZACIÓN Y LIMPIEZA DE DATOS (EVITA EL TYPEERROR) ---
if 'admin' not in st.session_state: 
    st.session_state.admin = False

# Definición de columnas base
cols_db = ["Nombre", "Equipo", "VB", "H", "2B", "3B", "HR", "G", "P"]
df_e = cargar_csv(EQUIPOS_FILE, ["Nombre"])
df_j = cargar_csv(JUGADORES_FILE, cols_db)

# CONVERSIÓN CRÍTICA: Asegura que las columnas estadísticas sean números
cols_num = ["VB", "H", "2B", "3B", "HR", "G", "P"]
for col in cols_num:
    if col in df_j.columns:
        df_j[col] = pd.to_numeric(df_j[col], errors='coerce').fillna(0)
    else:
        df_j[col] = 0

# --- 4. BARRA LATERAL ---
st.set_page_config(page_title="Liga Softbol 2026", layout="wide")

with st.sidebar:
    st.title("🥎 Softbol Liga Pro")
    if not st.session_state.admin:
        with st.expander("🔐 Acceso Administrador"):
            u_in = st.text_input("Usuario")
            p_in = st.text_input("Password", type="password")
            if st.button("Entrar"):
                conf = pd.read_csv(CONFIG_FILE).iloc[0]
                if u_in == conf['user'] and p_in == str(conf['pass']):
                    st.session_state.admin = True
                    st.rerun()
                else:
                    st.error("Credenciales Incorrectas")
    else:
        st.success("Sesión: Administrador")
        if st.button("Cerrar Sesión"):
            st.session_state.admin = False
            st.rerun()
    
    st.divider()
    menu = st.radio("Sección:", ["🏆 Líderes (Top 10)", "📋 Estadísticas Totales", "🏘️ Equipos", "✍️ Registrar Datos", "💾 Respaldo"])

# --- 5. LÓGICA DE SECCIONES ---

if menu == "🏆 Líderes (Top 10)":
    st.header("🥇 Los 10 Mejores de la Temporada")
    tab_b, tab_p = st.tabs(["⚾ LÍDERES BATEO", "🎯 LÍDERES PITCHEO"])
    
    with tab_b:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Hits")
            st.table(df_j.nlargest(10, 'H')[['Nombre', 'H']])
            st.subheader("Home Runs")
            st.table(df_j.nlargest(10, 'HR')[['Nombre', 'HR']])
        with c2:
            st.subheader("Dobles (2B)")
            st.table(df_j.nlargest(10, '2B')[['Nombre', '2B']])
            st.subheader("Triples (3B)")
            st.table(df_j.nlargest(10, '3B')[['Nombre', '3B']])

    with tab_p:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Juegos Ganados")
            st.table(df_j.nlargest(10, 'G')[['Nombre', 'G']])
        with c2:
            st.subheader("Juegos Perdidos")
            st.table(df_j.nlargest(10, 'P')[['Nombre', 'P']])

elif menu == "📋 Estadísticas Totales":
    st.header("Tablas Generales")
    t1, t2 = st.tabs(["📊 Tabla de Bateo", "🔥 Tabla de Pitcheo"])
    
    with t1:
        df_bat = df_j[["Nombre", "Equipo", "VB", "H", "2B", "3B", "HR"]].copy()
        df_bat['AVG'] = (df_bat['H'] / df_bat['VB']).fillna(0.000)
        st.dataframe(df_bat.sort_values("AVG", ascending=False), use_container_width=True)
    
    with t2:
        df_pit = df_j[["Nombre", "Equipo", "G", "P"]].copy()
        st.dataframe(df_pit.sort_values("G", ascending=False), use_container_width=True)

elif menu == "✍️ Registrar Datos":
    if not st.session_state.admin:
        st.warning("⚠️ Inicia sesión como administrador para registrar o editar datos.")
    elif df_e.empty:
        st.error("Primero debes agregar equipos en la sección '🏘️ Equipos'.")
    else:
        st.header("Entrada de Estadísticas")
        modo = st.radio("Tipo de Jugador:", ["Bateador", "Pitcher"], horizontal=True)
        
        with st.form("registro_form"):
            nombre_j = st.text_input("Nombre del Jugador")
            equipo_j = st.selectbox("Equipo", df_e["Nombre"])
            
            # Buscar si el jugador ya existe para cargar sus datos previos (opcional)
            jugador_prev = df_j[df_j['Nombre'] == nombre_j]
            
            if modo == "Bateador":
                col1, col2, col3 = st.columns(3)
                vbat = col1.number_input("VB", min_value=0, step=1)
                hits = col2.number_input("Hits", min_value=0, step=1)
                d2 = col3.number_input("2B", min_value=0, step=1)
                d3 = col1.number_input("3B", min_value=0, step=1)
                hr = col2.number_input("HR", min_value=0, step=1)
                # Mantiene lo de pitcheo en 0 o lo que ya tenía
                gan, perd = 0, 0
            else:
                col1, col2 = st.columns(2)
                gan = col1.number_input("Ganados (G)", min_value=0, step=1)
                perd = col2.number_input("Perdidos (P)", min_value=0, step=1)
                # Mantiene lo de bateo en 0 o lo que ya tenía
                vbat, hits, d2, d3, hr = 0, 0, 0, 0, 0

            if st.form_submit_button("💾 Guardar / Actualizar"):
                if nombre_j:
                    # Si ya existe, lo borramos para insertar la versión actualizada
                    df_j = df_j[df_j['Nombre'] != nombre_j]
                    
                    nueva_data = pd.DataFrame([{
                        "Nombre": nombre_j, "Equipo": equipo_j, 
                        "VB": vbat, "H": hits, "2B": d2, "3B": d3, "HR": hr,
                        "G": gan, "P": perd
                    }])
                    
                    df_j = pd.concat([df_j, nueva_data], ignore_index=True)
                    df_j.to_csv(JUGADORES_FILE, index=False)
                    st.success(f"¡Datos de {nombre_j} sincronizados!")
                    st.rerun()
                else:
                    st.error("El nombre es obligatorio.")

elif menu == "🏘️ Equipos":
    st.header("Gestión de Equipos")
    if st.session_state.admin:
        nuevo_eq = st.text_input("Nombre del nuevo equipo:")
        if st.button("Añadir Equipo"):
            if nuevo_eq and nuevo_eq not in df_e['Nombre'].values:
                df_e = pd.concat([df_e, pd.DataFrame([{"Nombre": nuevo_eq}])], ignore_index=True)
                df_e.to_csv(EQUIPOS_FILE, index=False)
                st.rerun()
    st.write("### Equipos Actuales")
    st.table(df_e)

elif menu == "💾 Respaldo":
    st.header("💾 Centro de Seguridad de Datos")
    st.info("Dado que Streamlit Cloud puede reiniciar los archivos, descarga tu respaldo después de cada jornada.")
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("1. Descargar")
        csv_data = df_j.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar CSV Jugadores", csv_data, "respaldo_liga.csv", "text/csv")
        
    with c2:
        st.subheader("2. Restaurar")
        archivo = st.file_uploader("Sube el archivo CSV para recuperar datos", type="csv")
        if archivo:
            df_res = pd.read_csv(archivo)
            df_res.to_csv(JUGADORES_FILE, index=False)
            st.success("¡Datos restaurados correctamente!")
            st.rerun()
