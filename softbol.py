import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN DE RUTAS Y CARPETAS ---
DATA_DIR = "liga_softbol_2026"
if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)

JUGADORES_FILE = os.path.join(DATA_DIR, "jugadores_stats.csv")
EQUIPOS_FILE = os.path.join(DATA_DIR, "equipos_lista.csv")
CONFIG_FILE = os.path.join(DATA_DIR, "config_admin.csv")

# Credenciales por defecto
if not os.path.exists(CONFIG_FILE):
    pd.DataFrame([{"user": "admin", "pass": "123"}]).to_csv(CONFIG_FILE, index=False)

# --- 2. MOTOR DE DATOS (PROTECCIÓN TOTAL) ---
def cargar_base_datos():
    # Definimos TODAS las columnas que solicitaste
    columnas_obligatorias = ["Nombre", "Equipo", "VB", "H", "2B", "3B", "HR", "G", "P"]
    
    if os.path.exists(JUGADORES_FILE):
        try:
            df = pd.read_csv(JUGADORES_FILE)
            # Si faltan columnas por algún error, las agregamos con 0
            for col in columnas_obligatorias:
                if col not in df.columns: df[col] = 0
        except:
            df = pd.DataFrame(columns=columnas_obligatorias)
    else:
        df = pd.DataFrame(columns=columnas_obligatorias)
    
    # CONVERSIÓN NUMÉRICA: Evita que los líderes desaparezcan por errores de tipo
    cols_num = ["VB", "H", "2B", "3B", "HR", "G", "P"]
    for c in cols_num:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
    
    return df

# --- 3. INICIALIZACIÓN ---
if 'admin_sesion' not in st.session_state: st.session_state.admin_sesion = False

df_j = cargar_base_datos()
df_e = pd.read_csv(EQUIPOS_FILE) if os.path.exists(EQUIPOS_FILE) else pd.DataFrame(columns=["Nombre"])

# --- 4. INTERFAZ ---
st.set_page_config(page_title="Liga Softbol 2026", layout="wide")

with st.sidebar:
    st.title("🥎 Menú Liga Pro")
    if not st.session_state.admin_sesion:
        with st.expander("🔐 Acceso Admin"):
            u = st.text_input("Usuario")
            p = st.text_input("Clave", type="password")
            if st.button("Entrar"):
                c = pd.read_csv(CONFIG_FILE).iloc[0]
                if u == c['user'] and p == str(c['pass']):
                    st.session_state.admin_sesion = True
                    st.rerun()
                else: st.error("Error")
    else:
        if st.button("Cerrar Sesión"):
            st.session_state.admin_sesion = False
            st.rerun()
    
    st.divider()
    menu = st.radio("Secciones:", ["🏆 LÍDERES (TOP 10)", "📋 ROSTERS", "📊 TABLA GENERAL", "🏘️ EQUIPOS", "✍️ REGISTRAR", "🗑️ BORRAR", "💾 RESPALDO"])

# --- 5. LÓGICA DE DEPARTAMENTOS (ESTADÍSTICAS) ---

if menu == "🏆 LÍDERES (TOP 10)":
    st.header("🔝 Líderes Departamentales")
    tab_bat, tab_pit = st.tabs(["⚾ BATEO", "🎯 PITCHEO"])
    
    with tab_bat:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.subheader("Hits (H)")
            st.table(df_j.nlargest(10, 'H')[['Nombre', 'H']])
            st.subheader("Home Runs (HR)")
            st.table(df_j.nlargest(10, 'HR')[['Nombre', 'HR']])
        with c2:
            st.subheader("Dobles (2B)")
            st.table(df_j.nlargest(10, '2B')[['Nombre', '2B']])
        with c3:
            st.subheader("Triples (3B)")
            st.table(df_j.nlargest(10, '3B')[['Nombre', '3B']])

    with tab_pit:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Juegos Ganados (G)")
            st.table(df_j.nlargest(10, 'G')[['Nombre', 'Equipo', 'G']])
        with c2:
            st.subheader("Juegos Perdidos (P)")
            st.table(df_j.nlargest(10, 'P')[['Nombre', 'Equipo', 'P']])

elif menu == "📋 ROSTERS":
    st.header("👥 Rosters de Equipos")
    if df_e.empty: st.info("No hay equipos creados.")
    else:
        eq_sel = st.selectbox("Selecciona Equipo:", df_e["Nombre"].unique())
        st.dataframe(df_j[df_j["Equipo"] == eq_sel], use_container_width=True)

elif menu == "✍️ REGISTRAR":
    if not st.session_state.admin_sesion: st.warning("Inicia sesión")
    elif df_e.empty: st.error("Crea un equipo primero")
    else:
        st.header("Registrar Estadísticas")
        modo = st.radio("Tipo:", ["Bateo", "Pitcheo"], horizontal=True)
        with st.form("reg_2026"):
            nom = st.text_input("Nombre del Jugador")
            eq = st.selectbox("Equipo", df_e["Nombre"])
            col1, col2, col3 = st.columns(3)
            
            if modo == "Bateo":
                vb = col1.number_input("VB", min_value=0)
                h = col2.number_input("H", min_value=0)
                d2 = col3.number_input("2B", min_value=0)
                d3 = col1.number_input("3B", min_value=0)
                hr = col2.number_input("HR", min_value=0)
                g, p = 0, 0
            else:
                g = col1.number_input("Ganados (G)", min_value=0)
                p = col2.number_input("Perdidos (P)", min_value=0)
                vb, h, d2, d3, hr = 0, 0, 0, 0, 0
            
            if st.form_submit_button("💾 GUARDAR"):
                # Evitar duplicados: borrar si ya existe y poner el nuevo
                df_j = df_j[df_j["Nombre"] != nom]
                nueva = pd.DataFrame([{"Nombre": nom, "Equipo": eq, "VB": vb, "H": h, "2B": d2, "3B": d3, "HR": hr, "G": g, "P": p}])
                df_j = pd.concat([df_j, nueva], ignore_index=True)
                df_j.to_csv(JUGADORES_FILE, index=False)
                st.success("Actualizado y Redireccionado")
                st.rerun()

elif menu == "💾 RESPALDO":
    st.header("💾 Centro de Datos")
    st.download_button("📥 Descargar CSV Actual", df_j.to_csv(index=False).encode('utf-8'), "liga_backup.csv")
    f = st.file_uploader("📤 Restaurar desde Respaldo", type="csv")
    if f:
        pd.read_csv(f).to_csv(JUGADORES_FILE, index=False)
        st.success("Sincronizado correctamente.")
        st.rerun()

# --- SECCIONES EXTRAS (BORRAR Y EQUIPOS) ---
elif menu == "🏘️ EQUIPOS":
    if st.session_state.admin_sesion:
        ne = st.text_input("Nombre de equipo:")
        if st.button("Añadir"):
            df_e = pd.concat([df_e, pd.DataFrame([{"Nombre": ne}])], ignore_index=True)
            df_e.to_csv(EQUIPOS_FILE, index=False); st.rerun()
    st.table(df_e)

elif menu == "🗑️ BORRAR":
    if st.session_state.admin_sesion:
        j_del = st.selectbox("Borrar Jugador:", df_j["Nombre"].unique())
        if st.button("Eliminar"):
            df_j = df_j[df_j["Nombre"] != j_del]
            df_j.to_csv(JUGADORES_FILE, index=False); st.rerun()
