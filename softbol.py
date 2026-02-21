import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN DE ARCHIVOS ---
DATA_DIR = "datos_liga_2026"
if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)

EQUIPOS_FILE = os.path.join(DATA_DIR, "equipos.csv")
JUGADORES_FILE = os.path.join(DATA_DIR, "jugadores.csv")
CONFIG_FILE = os.path.join(DATA_DIR, "config.csv")

if not os.path.exists(CONFIG_FILE):
    pd.DataFrame([{"user": "admin", "pass": "123"}]).to_csv(CONFIG_FILE, index=False)

# --- 2. FUNCIONES DE CARGA ---
def cargar_csv(ruta, columnas):
    if os.path.exists(ruta): return pd.read_csv(ruta)
    return pd.DataFrame(columns=columnas)

# --- 3. INICIALIZACIÓN ---
if 'admin' not in st.session_state: st.session_state.admin = False

cols_db = ["Nombre", "Equipo", "VB", "H", "2B", "3B", "HR", "G", "P", "K", "ERA"]
df_e = cargar_csv(EQUIPOS_FILE, ["Nombre"])
df_j = cargar_csv(JUGADORES_FILE, cols_db)

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.title("🥎 Softbol Liga 2026")
    if not st.session_state.admin:
        with st.expander("🔐 Login Admin"):
            u = st.text_input("Usuario")
            p = st.text_input("Password", type="password")
            if st.button("Entrar"):
                c = pd.read_csv(CONFIG_FILE).iloc[0]
                if u == c['user'] and p == str(c['pass']):
                    st.session_state.admin = True
                    st.rerun()
    else:
        st.success("Modo Admin: ON")
        if st.button("Cerrar Sesión"):
            st.session_state.admin = False
            st.rerun()
    
    st.divider()
    menu = st.radio("Sección:", ["🏆 Líderes Top 10", "📋 Tablas Completas", "🏘️ Equipos", "✍️ Registrar Datos", "💾 Respaldo"])

# --- 5. LÓGICA DE SECCIONES ---

if menu == "🏆 Líderes Top 10":
    st.header("🥇 Cuadro de Honor")
    tab_bat, tab_pitch = st.tabs(["⚾ LÍDERES BATEO", "🎯 LÍDERES PITCHEO"])
    
    with tab_bat:
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

    with tab_pitch:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Juegos Ganados")
            st.table(df_j.nlargest(10, 'G')[['Nombre', 'G']])
        with c2:
            st.subheader("Juegos Perdidos")
            st.table(df_j.nlargest(10, 'P')[['Nombre', 'P']])

elif menu == "📋 Tablas Completas":
    st.header("Estadísticas Generales")
    t1, t2 = st.tabs(["📊 Bateo", "🔥 Pitcheo"])
    with t1:
        df_b = df_j[["Nombre", "Equipo", "VB", "H", "2B", "3B", "HR"]].copy()
        df_b['AVG'] = (df_b['H'] / df_b['VB']).fillna(0.000)
        st.dataframe(df_b.sort_values("AVG", ascending=False), use_container_width=True)
    with t2:
        st.dataframe(df_j[["Nombre", "Equipo", "G", "P"]].sort_values("G", ascending=False), use_container_width=True)

elif menu == "✍️ Registrar Datos":
    if not st.session_state.admin:
        st.error("Inicia sesión para registrar datos.")
    else:
        st.header("Entrada de Datos")
        tipo = st.radio("¿Qué deseas registrar?", ["Bateador", "Pitcher"], horizontal=True)
        
        with st.form("form_registro"):
            nom = st.text_input("Nombre del Jugador")
            eq = st.selectbox("Equipo", df_e["Nombre"])
            
            if tipo == "Bateador":
                col1, col2, col3 = st.columns(3)
                vb = col1.number_input("VB", min_value=0)
                h = col2.number_input("Hits", min_value=0)
                d2 = col3.number_input("2B", min_value=0)
                d3 = col1.number_input("3B", min_value=0)
                hr = col2.number_input("HR", min_value=0)
                # Mantener valores previos de pitcheo si existen
                p_g, p_p = 0, 0
            else:
                col1, col2 = st.columns(2)
                p_g = col1.number_input("Ganados (G)", min_value=0)
                p_p = col2.number_input("Perdidos (P)", min_value=0)
                # Mantener valores previos de bateo en 0
                vb, h, d2, d3, hr = 0, 0, 0, 0, 0

            if st.form_submit_button("Guardar Registro"):
                # Lógica para no duplicar: si existe, sumamos o reemplazamos
                df_j = df_j[df_j['Nombre'] != nom]
                n_fila = pd.DataFrame([{"Nombre": nom, "Equipo": eq, "VB": vb, "H": h, "2B": d2, "3B": d3, "HR": hr, "G": p_g, "P": p_p}])
                df_j = pd.concat([df_j, n_fila], ignore_index=True)
                df_j.to_csv(JUGADORES_FILE, index=False)
                st.success(f"Datos de {nom} actualizados.")
                st.rerun()

elif menu == "🏘️ Equipos":
    if st.session_state.admin:
        nuevo = st.text_input("Nuevo Equipo:")
        if st.button("Agregar"):
            df_e = pd.concat([df_e, pd.DataFrame([{"Nombre": nuevo}])], ignore_index=True)
            df_e.to_csv(EQUIPOS_FILE, index=False)
            st.rerun()
    st.table(df_e)

elif menu == "💾 Respaldo":
    st.header("Centro de Datos")
    st.download_button("📥 Descargar Base de Datos", df_j.to_csv(index=False), "liga_2026.csv")
    archivo = st.file_uploader("📤 Restaurar desde CSV", type="csv")
    if archivo:
        pd.read_csv(archivo).to_csv(JUGADORES_FILE, index=False)
        st.success("Datos cargados.")
        st.rerun()
