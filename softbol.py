import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN DE RUTAS ---
DATA_DIR = "liga_softbol_2026_final"
if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)

JUGADORES_FILE = os.path.join(DATA_DIR, "jugadores_stats.csv")
EQUIPOS_FILE = os.path.join(DATA_DIR, "equipos_lista.csv")
ANIO_ACTUAL = 2026 

# --- 2. MOTOR DE DATOS (PROTECCIÓN TOTAL DE COLUMNAS) ---
def cargar_base_datos():
    # LISTA MAESTRA: Si falta alguna, el sistema la crea con 0
    cols_obligatorias = ["Nombre", "Equipo", "VB", "H", "2B", "3B", "HR", "G", "P"]
    if os.path.exists(JUGADORES_FILE):
        try:
            df = pd.read_csv(JUGADORES_FILE)
            for col in cols_obligatorias:
                if col not in df.columns: df[col] = 0
        except: df = pd.DataFrame(columns=cols_obligatorias)
    else: df = pd.DataFrame(columns=cols_obligatorias)
    
    # Asegurar que los cálculos de "nlargest" no fallen (conversión numérica)
    for c in ["VB", "H", "2B", "3B", "HR", "G", "P"]:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
    return df

def cargar_equipos():
    if os.path.exists(EQUIPOS_FILE):
        return pd.read_csv(EQUIPOS_FILE)
    return pd.DataFrame(columns=["Nombre", "Debut"])

# --- 3. INICIALIZACIÓN ---
if 'admin_sesion' not in st.session_state: st.session_state.admin_sesion = False
df_j = cargar_base_datos()
df_e = cargar_equipos()

st.set_page_config(page_title="Liga Softbol 2026", layout="wide")

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.title("🥎 Softbol Pro 2026")
    if not st.session_state.admin_sesion:
        with st.expander("🔐 Login Admin"):
            u = st.text_input("Usuario"); p = st.text_input("Clave", type="password")
            if st.button("Entrar"):
                if u == "admin" and p == "123":
                    st.session_state.admin_sesion = True
                    st.rerun()
    else:
        if st.button("Cerrar Sesión"):
            st.session_state.admin_sesion = False
            st.rerun()
    
    st.divider()
    menu = st.radio("Menú:", ["🏆 LÍDERES", "📋 ROSTERS", "📜 HISTORIAL JUGADOR", "🏘️ EQUIPOS", "✍️ REGISTRAR", "💾 RESPALDO"])

# --- 5. SECCIÓN LÍDERES (TODOS LOS DEPARTAMENTOS) ---
if menu == "🏆 LÍDERES":
    st.header("🔝 Líderes Departamentales (Top 10)")
    tab_bat, tab_pit = st.tabs(["⚾ DEPARTAMENTOS BATEO", "🎯 DEPARTAMENTOS PITCHEO"])
    
    with tab_bat:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Hits (H)")
            st.table(df_j.nlargest(10, 'H')[['Nombre', 'H']])
            st.subheader("Dobles (2B)")
            st.table(df_j.nlargest(10, '2B')[['Nombre', '2B']])
        with col2:
            st.subheader("Home Runs (HR)")
            st.table(df_j.nlargest(10, 'HR')[['Nombre', 'HR']])
            st.subheader("Triples (3B)")
            st.table(df_j.nlargest(10, '3B')[['Nombre', '3B']])

    with tab_pit:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Juegos Ganados (G)")
            st.table(df_j.nlargest(10, 'G')[['Nombre', 'G']])
        with col2:
            st.subheader("Juegos Perdidos (P)")
            st.table(df_j.nlargest(10, 'P')[['Nombre', 'P']])

# --- 6. SECCIÓN ROSTERS ---
elif menu == "📋 ROSTERS":
    st.header("👥 Rosters por Equipo")
    if df_e.empty: st.warning("No hay equipos. Agrégalos en '🏘️ EQUIPOS'.")
    else:
        eq_sel = st.selectbox("Equipo:", df_e["Nombre"].unique())
        roster = df_j[df_j["Equipo"] == eq_sel]
        st.dataframe(roster, use_container_width=True)

# --- 7. SECCIÓN HISTORIAL ---
elif menu == "📜 HISTORIAL JUGADOR":
    st.header("📜 Ficha del Jugador")
    if df_j.empty: st.info("No hay datos.")
    else:
        j_sel = st.selectbox("Buscar Jugador:", sorted(df_j["Nombre"].unique()))
        datos = df_j[df_j["Nombre"] == j_sel].iloc
        c1, c2 = st.columns(2)
        c1.metric("Hits", int(datos['H']))
        c1.metric("HR", int(datos['HR']))
        c2.metric("Ganados", int(datos['G']))
        c2.metric("Perdidos", int(datos['P']))

# --- 8. SECCIÓN REGISTRAR (INCLUYE TODO) ---
elif menu == "✍️ REGISTRAR":
    if not st.session_state.admin_sesion: st.warning("Inicia sesión.")
    elif df_e.empty: st.error("Crea un equipo primero.")
    else:
        st.header("✍️ Anotar Estadísticas")
        tipo = st.radio("Tipo:", ["Bateo", "Pitcheo"], horizontal=True)
        with st.form("reg_master"):
            nom = st.text_input("Nombre:")
            eq = st.selectbox("Equipo:", df_e["Nombre"].unique())
            if tipo == "Bateo":
                c1, c2, c3, c4, c5 = st.columns(5)
                vb = c1.number_input("VB", 0); h = c2.number_input("H", 0)
                d2 = c3.number_input("2B", 0); d3 = c4.number_input("3B", 0); hr = c5.number_input("HR", 0)
                g, p = 0, 0
            else:
                p1, p2 = st.columns(2)
                g = p1.number_input("G", 0); p = p2.number_input("P", 0)
                vb, h, d2, d3, hr = 0, 0, 0, 0, 0
            
            if st.form_submit_button("💾 Guardar"):
                df_j = df_j[df_j["Nombre"] != nom]
                nueva = pd.DataFrame([{"Nombre": nom, "Equipo": eq, "VB": vb, "H": h, "2B": d2, "3B": d3, "HR": hr, "G": g, "P": p}])
                pd.concat([df_j, nueva], ignore_index=True).to_csv(JUGADORES_FILE, index=False)
                st.success("Guardado."); st.rerun()

# --- 9. EQUIPOS Y RESPALDO ---
elif menu == "🏘️ EQUIPOS":
    if st.session_state.admin_sesion:
        with st.form("eq"):
            ne = st.text_input("Equipo:"); de = st.number_input("Debut:", 1980, 2026, 2026)
            if st.form_submit_button("Añadir"):
                df_e = pd.concat([df_e, pd.DataFrame([{"Nombre": ne, "Debut": de}])], ignore_index=True)
                df_e.to_csv(EQUIPOS_FILE, index=False); st.rerun()
    st.table(df_e)

elif menu == "💾 RESPALDO":
    st.download_button("📥 Descargar CSV", df_j.to_csv(index=False), "liga.csv")
    f = st.file_uploader("📤 Restaurar", type="csv")
    if f: pd.read_csv(f).to_csv(JUGADORES_FILE, index=False); st.rerun()
