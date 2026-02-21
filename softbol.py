import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN DE RUTAS ---
DATA_DIR = "liga_softbol_2026_final"
if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)

JUGADORES_FILE = os.path.join(DATA_DIR, "jugadores_stats.csv")
EQUIPOS_FILE = os.path.join(DATA_DIR, "equipos_lista.csv")
ANIO_ACTUAL = 2026 

# --- 2. MOTOR DE DATOS (CON REPARACIÓN DE COLUMNAS) ---
def cargar_base_datos():
    cols_obligatorias = ["Nombre", "Equipo", "VB", "H", "2B", "3B", "HR", "G", "P"]
    if os.path.exists(JUGADORES_FILE):
        try:
            df = pd.read_csv(JUGADORES_FILE)
            for col in cols_obligatorias:
                if col not in df.columns: df[col] = 0
        except: df = pd.DataFrame(columns=cols_obligatorias)
    else: df = pd.DataFrame(columns=cols_obligatorias)
    
    for c in ["VB", "H", "2B", "3B", "HR", "G", "P"]:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
    return df

def cargar_equipos():
    if os.path.exists(EQUIPOS_FILE):
        df = pd.read_csv(EQUIPOS_FILE)
        if df.empty: return pd.DataFrame(columns=["Nombre", "Debut"])
        return df
    return pd.DataFrame(columns=["Nombre", "Debut"])

# --- 3. INICIALIZACIÓN ---
if 'admin_sesion' not in st.session_state: st.session_state.admin_sesion = False
df_j = cargar_base_datos()
df_e = cargar_equipos()

st.set_page_config(page_title="Softbol Pro 2026", layout="wide")

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.title("🥎 Liga Softbol 2026")
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

# --- 5. SECCIÓN ROSTERS (CORREGIDA) ---
if menu == "📋 ROSTERS":
    st.header("👥 Rosters de Equipos")
    if df_e.empty:
        st.warning("⚠️ No hay equipos registrados. Ve a la sección '🏘️ EQUIPOS' para añadir uno primero.")
    else:
        # Selector de equipo basado en la lista real de equipos
        eq_nombres = df_e["Nombre"].unique().tolist()
        eq_sel = st.selectbox("Selecciona un Equipo:", eq_nombres)
        
        # Filtrado estricto
        roster = df_j[df_j["Equipo"] == eq_sel]
        
        if roster.empty:
            st.info(f"El equipo '{eq_sel}' aún no tiene jugadores con estadísticas registradas.")
        else:
            st.subheader(f"Lista de Jugadores: {eq_sel}")
            # Mostrar tabla limpia
            df_mostrar = roster.copy()
            df_mostrar['AVG'] = (df_mostrar['H'] / df_mostrar['VB']).fillna(0.000)
            st.dataframe(df_mostrar[["Nombre", "VB", "H", "2B", "3B", "HR", "AVG", "G", "P"]], use_container_width=True)

# --- 6. SECCIÓN REGISTRAR (ASEGURA VÍNCULO) ---
elif menu == "✍️ REGISTRAR":
    if not st.session_state.admin_sesion: st.warning("Inicia sesión como administrador.")
    elif df_e.empty: st.error("Crea un equipo en '🏘️ EQUIPOS' antes de registrar jugadores.")
    else:
        st.header("✍️ Registro de Estadísticas")
        modo = st.radio("Tipo:", ["Bateo", "Pitcheo"], horizontal=True)
        with st.form("reg_form"):
            nom = st.text_input("Nombre Completo:")
            eq = st.selectbox("Asignar a Equipo:", df_e["Nombre"].unique())
            if modo == "Bateo":
                v1, v2, v3, v4, v5 = st.columns(5)
                vb = v1.number_input("VB", 0); h = v2.number_input("H", 0)
                d2 = v3.number_input("2B", 0); d3 = v4.number_input("3B", 0); hr = v5.number_input("HR", 0)
                g, p = 0, 0
            else:
                p1, p2 = st.columns(2)
                g = p1.number_input("G", 0); p = p2.number_input("P", 0)
                vb, h, d2, d3, hr = 0, 0, 0, 0, 0
            
            if st.form_submit_button("💾 Guardar Jugador"):
                if nom:
                    # Reemplazar si ya existe
                    df_j = df_j[df_j["Nombre"] != nom]
                    nueva = pd.DataFrame([{"Nombre": nom, "Equipo": eq, "VB": vb, "H": h, "2B": d2, "3B": d3, "HR": hr, "G": g, "P": p}])
                    df_final = pd.concat([df_j, nueva], ignore_index=True)
                    df_final.to_csv(JUGADORES_FILE, index=False)
                    st.success(f"¡{nom} guardado en {eq}!")
                    st.rerun()
                else: st.error("Escribe un nombre.")

# --- 7. OTRAS SECCIONES (LÍDERES, EQUIPOS, RESPALDO) ---
elif menu == "🏆 LÍDERES":
    st.header("🔝 Líderes")
    t1, t2 = st.tabs(["⚾ Bateo", "🎯 Pitcheo"])
    with t1:
        c1, c2, c3 = st.columns(3)
        with c1: st.subheader("Hits"); st.table(df_j.nlargest(10, 'H')[['Nombre', 'H']])
        with c2: st.subheader("2B"); st.table(df_j.nlargest(10, '2B')[['Nombre', '2B']])
        with c3: st.subheader("3B"); st.table(df_j.nlargest(10, '3B')[['Nombre', '3B']])
    with t2:
        st.subheader("Ganados"); st.table(df_j.nlargest(10, 'G')[['Nombre', 'G']])

elif menu == "🏘️ EQUIPOS":
    st.header("🏘️ Equipos")
    if st.session_state.admin_sesion:
        with st.form("add_eq"):
            ne = st.text_input("Nombre Equipo:"); de = st.number_input("Debut:", 1980, 2026, 2026)
            if st.form_submit_button("Añadir"):
                df_e = pd.concat([df_e, pd.DataFrame([{"Nombre": ne, "Debut": de}])], ignore_index=True)
                df_e.to_csv(EQUIPOS_FILE, index=False); st.rerun()
    st.table(df_e)

elif menu == "💾 RESPALDO":
    st.download_button("📥 Descargar", df_j.to_csv(index=False), "respaldo.csv")
    f = st.file_uploader("📤 Restaurar", type="csv")
    if f: pd.read_csv(f).to_csv(JUGADORES_FILE, index=False); st.rerun()
