import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN DE ARCHIVOS ---
DATA_DIR = "datos_liga_2026"
if not os.path.exists(DATA_DIR): 
    os.makedirs(DATA_DIR)

EQUIPOS_FILE = os.path.join(DATA_DIR, "equipos.csv")
JUGADORES_FILE = os.path.join(DATA_DIR, "jugadores.csv")
CONFIG_FILE = os.path.join(DATA_DIR, "config.csv")

if not os.path.exists(CONFIG_FILE):
    pd.DataFrame([{"user": "admin", "pass": "123"}]).to_csv(CONFIG_FILE, index=False)

# --- 2. FUNCIONES DE CARGA ---
def cargar_csv(ruta, columnas):
    if os.path.exists(ruta): 
        return pd.read_csv(ruta)
    return pd.DataFrame(columns=columnas)

# --- 3. INICIALIZACIÓN Y LIMPIEZA ---
if 'admin' not in st.session_state: st.session_state.admin = False
if 'menu_actual' not in st.session_state: st.session_state.menu_actual = "🏆 Líderes (Top 10)"
if 'equipo_seleccionado' not in st.session_state: st.session_state.equipo_seleccionado = None

cols_db = ["Nombre", "Equipo", "VB", "H", "2B", "3B", "HR", "G", "P"]
df_e = cargar_csv(EQUIPOS_FILE, ["Nombre"])
df_j = cargar_csv(JUGADORES_FILE, cols_db)

# Conversión numérica para evitar errores de tipos
for col in ["VB", "H", "2B", "3B", "HR", "G", "P"]:
    df_j[col] = pd.to_numeric(df_j[col], errors='coerce').fillna(0)

# --- 4. BARRA LATERAL ---
st.set_page_config(page_title="Liga Softbol 2026", layout="wide")

with st.sidebar:
    st.title("🥎 Softbol Pro 2026")
    if not st.session_state.admin:
        with st.expander("🔐 Admin"):
            u_in = st.text_input("Usuario")
            p_in = st.text_input("Password", type="password")
            if st.button("Entrar"):
                conf = pd.read_csv(CONFIG_FILE).iloc[0]
                if u_in == conf['user'] and p_in == str(conf['pass']):
                    st.session_state.admin = True
                    st.rerun()
    else:
        st.success("Admin Activo")
        if st.button("Cerrar Sesión"):
            st.session_state.admin = False
            st.rerun()
    
    st.divider()
    # Usamos session_state para el menú para permitir "redirecciones"
    opciones = ["🏆 Líderes (Top 10)", "📋 Rosters por Equipo", "📊 Estadísticas Totales", "🏘️ Equipos", "✍️ Registrar Datos", "💾 Respaldo"]
    st.session_state.menu_actual = st.radio("Sección:", opciones, index=opciones.index(st.session_state.menu_actual))

# --- 5. LÓGICA DE SECCIONES ---

# --- SECCIÓN: ROSTERS (NUEVA) ---
if st.session_state.menu_actual == "📋 Rosters por Equipo":
    st.header("👥 Rosters de los Equipos")
    if df_e.empty:
        st.info("No hay equipos registrados.")
    else:
        # Si venimos de registrar un jugador, seleccionamos su equipo automáticamente
        default_index = 0
        if st.session_state.equipo_seleccionado:
            try:
                default_index = list(df_e['Nombre']).index(st.session_state.equipo_seleccionado)
            except: pass
        
        eq_ver = st.selectbox("Selecciona un equipo para ver sus jugadores:", df_e['Nombre'], index=default_index)
        
        roster = df_j[df_j['Equipo'] == eq_ver]
        if roster.empty:
            st.warning(f"El equipo {eq_ver} aún no tiene jugadores registrados.")
        else:
            st.subheader(f"Jugadores de {eq_ver} ({len(roster)})")
            # Mostramos bateo y pitcheo simplificado
            st.dataframe(roster[["Nombre", "VB", "H", "HR", "G", "P"]], use_container_width=True)

# --- SECCIÓN: REGISTRAR (CON REDIRECCIÓN) ---
elif st.session_state.menu_actual == "✍️ Registrar Datos":
    if not st.session_state.admin:
        st.warning("⚠️ Inicia sesión para registrar.")
    else:
        st.header("Entrada de Estadísticas")
        modo = st.radio("Tipo:", ["Bateador", "Pitcher"], horizontal=True)
        
        with st.form("registro_form"):
            nombre_j = st.text_input("Nombre del Jugador")
            equipo_j = st.selectbox("Equipo", df_e["Nombre"])
            
            if modo == "Bateador":
                c1, c2, c3 = st.columns(3)
                vbat = c1.number_input("VB", min_value=0, step=1)
                hits = c2.number_input("Hits", min_value=0, step=1)
                hr = c3.number_input("HR", min_value=0, step=1)
                d2, d3, gan, perd = 0, 0, 0, 0
            else:
                c1, c2 = st.columns(2)
                gan = c1.number_input("Ganados (G)", min_value=0, step=1)
                perd = c2.number_input("Perdidos (P)", min_value=0, step=1)
                vbat, hits, d2, d3, hr = 0, 0, 0, 0, 0

            if st.form_submit_button("💾 Guardar y Ver Roster"):
                if nombre_j:
                    df_j = df_j[df_j['Nombre'] != nombre_j]
                    nueva_data = pd.DataFrame([{"Nombre": nombre_j, "Equipo": equipo_j, "VB": vbat, "H": hits, "2B": d2, "3B": d3, "HR": hr, "G": gan, "P": perd}])
                    df_j = pd.concat([df_j, nueva_data], ignore_index=True)
                    df_j.to_csv(JUGADORES_FILE, index=False)
                    
                    # REDIRECCIÓN:
                    st.session_state.equipo_seleccionado = equipo_j
                    st.session_state.menu_actual = "📋 Rosters por Equipo"
                    st.rerun()

# --- SECCIONES RESTANTES (RESUMIDAS) ---
elif st.session_state.menu_actual == "🏆 Líderes (Top 10)":
    st.header("🥇 Top 10")
    t1, t2 = st.tabs(["⚾ Bateo", "🎯 Pitcheo"])
    with t1: st.table(df_j.nlargest(10, 'H')[['Nombre', 'Equipo', 'H']])
    with t2: st.table(df_j.nlargest(10, 'G')[['Nombre', 'Equipo', 'G']])

elif st.session_state.menu_actual == "📊 Estadísticas Totales":
    st.header("Tablas Completas")
    df_j['AVG'] = (df_j['H'] / df_j['VB']).fillna(0.000)
    st.dataframe(df_j.sort_values("AVG", ascending=False), use_container_width=True)

elif st.session_state.menu_actual == "🏘️ Equipos":
    st.header("Equipos")
    if st.session_state.admin:
        nuevo = st.text_input("Nombre equipo:")
        if st.button("Añadir"):
            df_e = pd.concat([df_e, pd.DataFrame([{"Nombre": nuevo}])], ignore_index=True)
            df_e.to_csv(EQUIPOS_FILE, index=False)
            st.rerun()
    st.table(df_e)

elif st.session_state.menu_actual == "💾 Respaldo":
    st.header("💾 Respaldo")
    st.download_button("📥 Descargar CSV", df_j.to_csv(index=False).encode('utf-8'), "liga.csv")
    subido = st.file_uploader("📤 Restaurar", type="csv")
    if subido:
        pd.read_csv(subido).to_csv(JUGADORES_FILE, index=False)
        st.success("Restaurado.")
        st.rerun()
