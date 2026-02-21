import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN DE DIRECTORIOS ---
DATA_DIR = "datos_liga_2026"
if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)

EQUIPOS_FILE = os.path.join(DATA_DIR, "equipos.csv")
JUGADORES_FILE = os.path.join(DATA_DIR, "jugadores.csv")
CONFIG_FILE = os.path.join(DATA_DIR, "config.csv")

if not os.path.exists(CONFIG_FILE):
    pd.DataFrame([{"user": "admin", "pass": "123"}]).to_csv(CONFIG_FILE, index=False)

# --- 2. FUNCIONES DE CARGA SEGURA ---
def cargar_datos_jugadores():
    cols = ["Nombre", "Equipo", "VB", "H", "2B", "3B", "HR", "G", "P"]
    if os.path.exists(JUGADORES_FILE):
        df = pd.read_csv(JUGADORES_FILE)
        for c in cols:
            if c not in df.columns: df[c] = 0
    else:
        df = pd.DataFrame(columns=cols)
    
    # Asegurar que los números sean números
    for col in ["VB", "H", "2B", "3B", "HR", "G", "P"]:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

def cargar_equipos():
    if os.path.exists(EQUIPOS_FILE):
        return pd.read_csv(EQUIPOS_FILE)
    return pd.DataFrame(columns=["Nombre"])

# --- 3. INICIALIZACIÓN ---
if 'admin' not in st.session_state: st.session_state.admin = False

df_j = cargar_datos_jugadores()
df_e = cargar_equipos()

# --- 4. INTERFAZ ---
st.set_page_config(page_title="Liga Softbol 2026", layout="wide")

with st.sidebar:
    st.title("🥎 Softbol Liga Pro")
    if not st.session_state.admin:
        with st.expander("🔐 Admin"):
            u = st.text_input("Usuario")
            p = st.text_input("Password", type="password")
            if st.button("Entrar"):
                conf = pd.read_csv(CONFIG_FILE).iloc[0]
                if u == conf['user'] and p == str(conf['pass']):
                    st.session_state.admin = True
                    st.rerun()
                else: st.error("Error")
    else:
        if st.button("Cerrar Sesión"):
            st.session_state.admin = False
            st.rerun()
    
    st.divider()
    menu = st.radio("Sección:", ["🏆 Líderes", "📋 Rosters por Equipo", "📊 Estadísticas", "🏘️ Equipos", "✍️ Registrar", "🗑️ Borrar", "💾 Respaldo"])

# --- 5. LÓGICA DE SECCIONES ---

if menu == "🏆 Líderes":
    st.header("🔝 Líderes")
    t1, t2 = st.tabs(["⚾ BATEO", "🎯 PITCHEO"])
    with t1:
        c1, c2 = st.columns(2)
        with c1: 
            st.subheader("Hits"); st.table(df_j.nlargest(10, 'H')[['Nombre', 'Equipo', 'H']])
        with c2: 
            st.subheader("Home Runs"); st.table(df_j.nlargest(10, 'HR')[['Nombre', 'Equipo', 'HR']])
    with t2:
        st.subheader("Juegos Ganados"); st.table(df_j.nlargest(10, 'G')[['Nombre', 'Equipo', 'G']])

elif menu == "📋 Rosters por Equipo":
    st.header("👥 Rosters")
    if df_e.empty:
        st.warning("No hay equipos registrados. Ve a la sección '🏘️ Equipos' para añadir uno.")
    else:
        eq_sel = st.selectbox("Selecciona Equipo:", df_e["Nombre"].unique())
        roster = df_j[df_j["Equipo"] == eq_sel]
        if roster.empty:
            st.info(f"El equipo {eq_sel} no tiene jugadores registrados todavía.")
        else:
            st.subheader(f"Jugadores de {eq_sel}")
            st.dataframe(roster, use_container_width=True)

elif menu == "✍️ Registrar":
    if not st.session_state.admin: st.warning("Inicia sesión")
    elif df_e.empty: st.error("Crea un equipo primero")
    else:
        st.header("Registrar Estadísticas")
        tipo = st.radio("Modo:", ["Bateo", "Pitcheo"], horizontal=True)
        with st.form("reg_form"):
            nom = st.text_input("Nombre")
            eq = st.selectbox("Equipo", df_e["Nombre"])
            v1, v2, v3 = st.columns(3)
            if tipo == "Bateo":
                vb = v1.number_input("VB", min_value=0); h = v2.number_input("H", min_value=0); hr = v3.number_input("HR", min_value=0)
                g, p = 0, 0
            else:
                g = v1.number_input("G", min_value=0); p = v2.number_input("P", min_value=0)
                vb, h, hr = 0, 0, 0
            
            if st.form_submit_button("Guardar"):
                df_j = df_j[df_j["Nombre"] != nom]
                nueva = pd.DataFrame([{"Nombre": nom, "Equipo": eq, "VB": vb, "H": h, "2B": 0, "3B": 0, "HR": hr, "G": g, "P": p}])
                df_j = pd.concat([df_j, nueva], ignore_index=True)
                df_j.to_csv(JUGADORES_FILE, index=False)
                st.success("¡Guardado!")
                st.rerun()

elif menu == "🏘️ Equipos":
    st.header("Gestión de Equipos")
    if st.session_state.admin:
        n_eq = st.text_input("Nombre del nuevo equipo")
        if st.button("Añadir Equipo"):
            if n_eq and n_eq not in df_e['Nombre'].values:
                df_e = pd.concat([df_e, pd.DataFrame([{"Nombre": n_eq}])], ignore_index=True)
                df_e.to_csv(EQUIPOS_FILE, index=False)
                st.rerun()
    st.table(df_e)

elif menu == "🗑️ Borrar":
    if st.session_state.admin:
        st.header("Eliminar")
        # Borrar Jugador
        j_del = st.selectbox("Borrar Jugador:", df_j["Nombre"].unique())
        if st.button("Eliminar Jugador"):
            df_j = df_j[df_j["Nombre"] != j_del]
            df_j.to_csv(JUGADORES_FILE, index=False)
            st.rerun()
        # Borrar Equipo
        e_del = st.selectbox("Borrar Equipo:", df_e["Nombre"].unique())
        if st.button("Eliminar Equipo"):
            df_e = df_e[df_e["Nombre"] != e_del]
            df_j = df_j[df_j["Equipo"] != e_del]
            df_e.to_csv(EQUIPOS_FILE, index=False)
            df_j.to_csv(JUGADORES_FILE, index=False)
            st.rerun()

elif menu == "💾 Respaldo":
    st.download_button("📥 Descargar CSV", df_j.to_csv(index=False), "respaldo.csv")
    f = st.file_uploader("📤 Restaurar CSV", type="csv")
    if f:
        pd.read_csv(f).to_csv(JUGADORES_FILE, index=False)
        st.rerun()
