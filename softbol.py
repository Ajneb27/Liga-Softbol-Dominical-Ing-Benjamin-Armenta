import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN DE ARCHIVOS ---
DATA_DIR = "datos_liga_final"
if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)

EQUIPOS_FILE = os.path.join(DATA_DIR, "equipos.csv")
JUGADORES_FILE = os.path.join(DATA_DIR, "jugadores.csv")
CONFIG_FILE = os.path.join(DATA_DIR, "config.csv")

if not os.path.exists(CONFIG_FILE):
    pd.DataFrame([{"user": "admin", "pass": "123"}]).to_csv(CONFIG_FILE, index=False)

# --- 2. FUNCIONES DE CARGA Y LIMPIEZA ---
def cargar_datos():
    cols = ["Nombre", "Equipo", "VB", "H", "2B", "3B", "HR", "G", "P"]
    if os.path.exists(JUGADORES_FILE):
        df = pd.read_csv(JUGADORES_FILE)
        # Verificar que todas las columnas existan
        for c in cols:
            if c not in df.columns: df[c] = 0
    else:
        df = pd.DataFrame(columns=cols)
    
    # Forzar conversión a números para que no se borren los departamentos
    for col in ["VB", "H", "2B", "3B", "HR", "G", "P"]:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

# --- 3. INICIALIZACIÓN ---
if 'admin' not in st.session_state: st.session_state.admin = False
df_j = cargar_datos()
df_e = pd.read_csv(EQUIPOS_FILE) if os.path.exists(EQUIPOS_FILE) else pd.DataFrame(columns=["Nombre"])

# --- 4. INTERFAZ ---
st.set_page_config(page_title="Liga Softbol Pro", layout="wide")

with st.sidebar:
    st.title("🥎 Menú Principal")
    if not st.session_state.admin:
        with st.expander("🔐 Admin"):
            u = st.text_input("Usuario")
            p = st.text_input("Password", type="password")
            if st.button("Entrar"):
                conf = pd.read_csv(CONFIG_FILE).iloc[0]
                if u == conf['user'] and p == str(conf['pass']):
                    st.session_state.admin = True
                    st.rerun()
    else:
        if st.button("Cerrar Sesión"):
            st.session_state.admin = False
            st.rerun()
    
    st.divider()
    menu = st.radio("Ir a:", ["🏆 Líderes (Top 10)", "📋 Rosters", "📊 Estadísticas Totales", "🏘️ Equipos", "✍️ Registrar", "💾 Respaldo"])

# --- 5. DEPARTAMENTOS DE BATEO Y PITCHEO ---

if menu == "🏆 Líderes (Top 10)":
    st.header("🔝 Líderes Departamentales")
    tab_b, tab_p = st.tabs(["⚾ DEPARTAMENTOS BATEO", "🎯 DEPARTAMENTOS PITCHEO"])
    
    with tab_b:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Hits")
            st.table(df_j.nlargest(10, 'H')[['Nombre', 'Equipo', 'H']])
            st.subheader("Home Runs")
            st.table(df_j.nlargest(10, 'HR')[['Nombre', 'Equipo', 'HR']])
        with col2:
            st.subheader("Dobles (2B)")
            st.table(df_j.nlargest(10, '2B')[['Nombre', 'Equipo', '2B']])
            st.subheader("Triples (3B)")
            st.table(df_j.nlargest(10, '3B')[['Nombre', 'Equipo', '3B']])

    with tab_p:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Juegos Ganados")
            st.table(df_j.nlargest(10, 'G')[['Nombre', 'Equipo', 'G']])
        with col2:
            st.subheader("Juegos Perdidos")
            st.table(df_j.nlargest(10, 'P')[['Nombre', 'Equipo', 'P']])

elif menu == "📋 Rosters":
    st.header("👥 Rosters por Equipo")
    eq_sel = st.selectbox("Selecciona Equipo:", df_e["Nombre"])
    st.dataframe(df_j[df_j["Equipo"] == eq_sel], use_container_width=True)

elif menu == "📊 Estadísticas Totales":
    st.header("Tablas Completas")
    t1, t2 = st.tabs(["Bateo", "Pitcheo"])
    with t1:
        df_j['AVG'] = (df_j['H'] / df_j['VB']).fillna(0.000)
        st.dataframe(df_j[["Nombre", "Equipo", "VB", "H", "AVG", "HR"]].sort_values("AVG", ascending=False))
    with t2:
        st.dataframe(df_j[["Nombre", "Equipo", "G", "P"]].sort_values("G", ascending=False))

elif menu == "✍️ Registrar":
    if not st.session_state.admin: st.warning("Inicia sesión")
    else:
        st.header("Registrar Estadísticas")
        tipo = st.radio("Tipo:", ["Bateador", "Pitcher"], horizontal=True)
        with st.form("reg"):
            nom = st.text_input("Nombre")
            eq = st.selectbox("Equipo", df_e["Nombre"])
            v1, v2, v3 = st.columns(3)
            if tipo == "Bateador":
                vb = v1.number_input("VB", min_value=0)
                h = v2.number_input("H", min_value=0)
                hr = v3.number_input("HR", min_value=0)
                g, p = 0, 0
            else:
                g = v1.number_input("G", min_value=0)
                p = v2.number_input("P", min_value=0)
                vb, h, hr = 0, 0, 0
            
            if st.form_submit_button("Guardar"):
                df_j = df_j[df_j["Nombre"] != nom]
                nueva = pd.DataFrame([{"Nombre": nom, "Equipo": eq, "VB": vb, "H": h, "2B": 0, "3B": 0, "HR": hr, "G": g, "P": p}])
                df_j = pd.concat([df_j, nueva], ignore_index=True)
                df_j.to_csv(JUGADORES_FILE, index=False)
                st.success("Guardado y redireccionado")
                st.rerun()

elif menu == "🏘️ Equipos":
    if st.session_state.admin:
        n_eq = st.text_input("Nuevo Equipo")
        if st.button("Añadir"):
            df_e = pd.concat([df_e, pd.DataFrame([{"Nombre": n_eq}])], ignore_index=True)
            df_e.to_csv(EQUIPOS_FILE, index=False)
            st.rerun()
    st.table(df_e)

elif menu == "💾 Respaldo":
    st.download_button("Descargar CSV", df_j.to_csv(index=False), "liga.csv")
    f = st.file_uploader("Subir CSV", type="csv")
    if f:
        pd.read_csv(f).to_csv(JUGADORES_FILE, index=False)
        st.rerun()
