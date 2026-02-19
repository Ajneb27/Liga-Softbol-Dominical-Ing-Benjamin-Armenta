import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="LIGA DE SOFTBOL DOMINICAL", page_icon="⚾", layout="wide")

# Diseño en Rojo
st.markdown("<style>th {background-color: #D32F2F !important; color: white !important;} .stButton>button {background-color: #D32F2F; color: white;}</style>", unsafe_allow_html=True)

# Carpetas
DATOS_DIR = "datos_liga"
FOTOS_DIR = "galeria_liga"
for d in [DATOS_DIR, FOTOS_DIR]:
    if not os.path.exists(d): os.makedirs(d)

def path_archivo(nombre): return os.path.join(DATOS_DIR, nombre)

# --- 2. FUNCIONES DE DATOS ---
def leer_csv(nombre, columnas):
    p = path_archivo(nombre)
    if os.path.exists(p):
        try:
            df = pd.read_csv(p)
            for c in columnas:
                if c not in df.columns: df[c] = 0
            return df[columnas]
        except: return pd.DataFrame(columns=columnas)
    return pd.DataFrame(columns=columnas)

# Cargar todo al inicio
st.session_state.jugadores = leer_csv("data_jugadores.csv", ["Nombre", "Equipo", "VB", "H", "H2", "H3", "HR"])
st.session_state.pitchers = leer_csv("data_pitchers.csv", ["Nombre", "Equipo", "JG", "JP", "IP", "CL"])
st.session_state.equipos = leer_csv("data_equipos.csv", ["Nombre"])
st.session_state.calendario = leer_csv("data_calendario.csv", ["Fecha", "Hora", "Campo", "Local", "Visitante", "Score"])

# --- 3. SEGURIDAD ---
if 'admin' not in st.session_state: st.session_state.admin = False

with st.sidebar:
    st.title("🥎 LIGA DOMINICAL")
    if not st.session_state.admin:
        with st.form("login"):
            p = st.text_input("Contraseña:", type="password")
            if st.form_submit_button("Entrar"):
                if p == "softbol2026": 
                    st.session_state.admin = True
                    st.rerun()
                else: st.error("Error")
    else:
        st.success("MODO ADMIN")
        # Respaldos
        st.divider()
        csv = st.session_state.jugadores.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Bajar CSV", csv, "liga_stats.csv", "text/csv")
        if st.button("Cerrar Sesión"):
            st.session_state.admin = False
            st.rerun()

menu = st.sidebar.radio("MENÚ:", ["🏠 Inicio", "🏆 Líderes", "📊 Standings", "📋 Rosters", "🏃 Admin"])

# --- 4. SECCIONES ---
if menu == "🏠 Inicio":
    st.markdown("<h1 style='text-align: center; color: #D32F2F;'>⚾ LIGA DE SOFTBOL DOMINICAL</h1>", unsafe_allow_html=True)
    st.divider()
    fotos = os.listdir(FOTOS_DIR)
    if fotos:
        cols = st.columns(3)
        for i, f in enumerate(fotos[:3]):
            with cols[i%3]: st.image(os.path.join(FOTOS_DIR, f), use_container_width=True)
    st.subheader("📅 Calendario")
    st.dataframe(st.session_state.calendario, use_container_width=True, hide_index=True)

elif menu == "🏆 Líderes":
    t1, t2 = st.tabs(["Bateo", "Pitcheo"])
    with t1:
        df = st.session_state.jugadores.copy()
        if not df.empty:
            df['AVG'] = ((df['H']+df['H2']+df['H3']+df['HR']) / df['VB'].replace(0,1)).fillna(0)
            st.subheader("Mejores AVG")
            st.table(df.sort_values("AVG", ascending=False).head(5)[["Nombre", "AVG"]].style.format({"AVG": "{:.3f}"}))
        else: st.info("Vació")
    with t2:
        dfp = st.session_state.pitchers.copy()
        if not dfp.empty:
            dfp['EFE'] = ((dfp['CL'] * 7) / dfp['IP'].replace(0, 1)).fillna(0)
            st.subheader("Mejor EFE")
            st.table(dfp[dfp['IP']>0].sort_values("EFE").head(5)[["Nombre", "EFE"]].style.format({"EFE": "{:.2f}"}))
        else: st.info("Vacío")

elif menu == "📊 Standings":
    if not st.session_state.pitchers.empty:
        std = st.session_state.pitchers.groupby("Equipo")[["JG", "JP"]].sum().reset_index()
        st.dataframe(std.sort_values("JG", ascending=False), use_container_width=True, hide_index=True)
    else: st.info("No hay datos")

elif menu == "📋 Rosters":
    if not st.session_state.equipos.empty:
        eq = st.selectbox("Equipo", st.session_state.equipos["Nombre"].tolist())
        st.write("Bateadores:")
        st.dataframe(st.session_state.jugadores[st.session_state.jugadores["Equipo"]==eq], hide_index=True)
        st.write("Pitchers:")
        st.dataframe(st.session_state.pitchers[st.session_state.pitchers["Equipo"]==eq], hide_index=True)

elif menu == "🏃 Admin":
    if not st.session_state.admin: st.warning("Entra como admin")
    else:
        # Registro de Equipos
        with st.expander("Equipos"):
            n_eq = st.text_input("Nuevo Equipo")
            if st.button("Añadir"):
                nueva_fila = pd.DataFrame([{"Nombre": n_eq}])
                st.session_state.equipos = pd.concat([st.session_state.equipos, nueva_fila], ignore_index=True)
                st.session_state.equipos.to_csv(path_archivo("data_equipos.csv"), index=False)
                st.rerun()
        
        # Registro de Bateo
        with st.expander("Bateo"):
            with st.form("f1"):
                nom = st.text_input("Nombre")
                eq = st.selectbox("Equipo", st.session_state.equipos["Nombre"].tolist() if not st.session_state.equipos.empty else ["-"])
                vb = st.number_input("VB", 0); h = st.number_input("H", 0)
                h2 = st.number_input("H2", 0); h3 = st.number_input("H3", 0); hr = st.number_input("HR", 0)
                if st.form_submit_button("Guardar"):
                    df = st.session_state.jugadores[st.session_state.jugadores["Nombre"] != nom]
                    nueva = pd.DataFrame([[nom, eq, vb, h, h2, h3, hr]], columns=["Nombre", "Equipo", "VB", "H", "H2", "H3", "HR"])
                    pd.concat([df, nueva], ignore_index=True).to_csv(path_archivo("data_jugadores.csv"), index=False)
                    st.rerun()

        # Registro de Pitcheo
        with st.expander("Pitcheo"):
            with st.form("f2"):
                nom_p = st.text_input("Nombre P")
                eq_p = st.selectbox("Equipo ", st.session_state.equipos["Nombre"].tolist() if not st.session_state.equipos.empty else ["-"])
                jg = st.number_input("JG", 0); jp = st.number_input("JP", 0); ip = st.number_input("IP", 0); cl = st.number_input("CL", 0)
                if st.form_submit_button("Guardar Pitcher"):
                    dfp = st.session_state.pitchers[st.session_state.pitchers["Nombre"] != nom_p]
                    nueva_p = pd.DataFrame([[nom_p, eq_p, jg, jp, ip, cl]], columns=["Nombre", "Equipo", "JG", "JP", "IP", "CL"])
                    pd.concat([dfp, nueva_p], ignore_index=True).to_csv(path_archivo("data_pitchers.csv"), index=False)
                    st.rerun()
