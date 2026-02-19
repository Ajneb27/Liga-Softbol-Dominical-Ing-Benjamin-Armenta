import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="LIGA DE SOFTBOL DOMINICAL", page_icon="⚾", layout="wide")

# Estilo Rojo Deportivo
st.markdown("<style>th {background-color: #D32F2F !important; color: white !important;} .stButton>button {background-color: #D32F2F; color: white;}</style>", unsafe_allow_html=True)

DATOS_DIR = "datos_liga"
FOTOS_DIR = "galeria_liga"
for d in [DATOS_DIR, FOTOS_DIR]:
    if not os.path.exists(d): os.makedirs(d)

def path_archivo(nombre): return os.path.join(DATOS_DIR, nombre)

# --- 2. CARGA DE DATOS ---
def leer_csv(nombre, columnas):
    p = path_archivo(nombre)
    if os.path.exists(p):
        try:
            df = pd.read_csv(p)
            df.columns = df.columns.str.strip()
            for c in columnas:
                if c not in df.columns: df[c] = "" if c == "Score" else 0
            return df[columnas]
        except: return pd.DataFrame(columns=columnas)
    return pd.DataFrame(columns=columnas)

# Variables de estado
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
        csv = st.session_state.jugadores.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Respaldar Bateo", csv, "bateo.csv", "text/csv")
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
    st.subheader("📅 Calendario de Juegos")
    st.dataframe(st.session_state.calendario, use_container_width=True, hide_index=True)

elif menu == "🏆 Líderes":
    t1, t2 = st.tabs(["🥖 Bateo", "🔥 Pitcheo"])
    with t1:
        df = st.session_state.jugadores.copy()
        if not df.empty:
            df['H_T'] = df['H'] + df['H2'] + df['H3'] + df['HR']
            df['AVG'] = (df['H_T'] / df['VB'].replace(0, 1)).fillna(0)
            c1, c2 = st.columns(2)
            c1.subheader("🥇 AVG"); c1.table(df.sort_values("AVG", ascending=False).head(10)[["Nombre", "AVG"]].style.format({"AVG": "{:.3f}"}))
            c2.subheader("🥇 Hits"); c2.table(df.sort_values("H_T", ascending=False).head(10)[["Nombre", "H_T"]])
            c3, c4 = st.columns(2)
            c3.subheader("🥇 HR"); c3.table(df.sort_values("HR", ascending=False).head(10)[["Nombre", "HR"]])
            c4.subheader("🥇 H2"); c4.table(df.sort_values("H2", ascending=False).head(10)[["Nombre", "H2"]])
        else: st.info("Sin datos.")
    with t2:
        dfp = st.session_state.pitchers.copy()
        if not dfp.empty:
            dfp['EFE'] = ((dfp['CL'] * 7) / dfp['IP'].replace(0, 1)).fillna(0)
            cp1, cp2 = st.columns(2)
            cp1.subheader("🥇 EFE"); cp1.table(dfp[dfp['IP']>0].sort_values("EFE").head(10)[["Nombre", "EFE"]].style.format({"EFE": "{:.2f}"}))
            cp2.subheader("🥇 Ganados"); cp2.table(dfp.sort_values("JG", ascending=False).head(10)[["Nombre", "JG"]])

elif menu == "📊 Standings":
    if not st.session_state.pitchers.empty:
        std = st.session_state.pitchers.groupby("Equipo")[["JG", "JP"]].sum().reset_index()
        std["PCT"] = (std["JG"] / (std["JG"] + std["JP"]).replace(0, 1)).fillna(0)
        st.dataframe(std.sort_values(by=["JG", "PCT"], ascending=False).style.format({"PCT": "{:.3f}"}), use_container_width=True, hide_index=True)

elif menu == "📋 Rosters":
    if not st.session_state.equipos.empty:
        eq = st.selectbox("Equipo:", st.session_state.equipos["Nombre"].tolist())
        st.write("🥖 Bateadores"); st.dataframe(st.session_state.jugadores[st.session_state.jugadores["Equipo"] == eq], hide_index=True)
        st.write("🔥 Pitchers"); st.dataframe(st.session_state.pitchers[st.session_state.pitchers["Equipo"] == eq], hide_index=True)

elif menu == "🏃 Admin":
    if not st.session_state.admin: st.warning("Inicia sesión.")
    else:
        tab_e, tab_b, tab_p, tab_c = st.tabs(["Equipos", "Bateo", "Pitcheo", "Calendario"])
        
        with tab_e:
            c_a, c_b = st.columns(2)
            with c_a:
                n_eq = st.text_input("Nombre del Equipo")
                if st.button("Registrar"):
                    pd.concat([st.session_state.equipos, pd.DataFrame([{"Nombre": n_eq}])], ignore_index=True).to_csv(path_archivo("data_equipos.csv"), index=False); st.rerun()
            with c_b:
                e_borrar = st.selectbox("Borrar Equipo:", st.session_state.equipos["Nombre"].tolist())
                if st.button("🗑️ Borrar"):
                    st.session_state.equipos = st.session_state.equipos[st.session_state.equipos["Nombre"] != e_borrar]
                    st.session_state.equipos.to_csv(path_archivo("data_equipos.csv"), index=False); st.rerun()

        with tab_b:
            sel_j = st.selectbox("Jugador:", ["-- Nuevo --"] + sorted(st.session_state.jugadores["Nombre"].tolist()))
            with st.form("f_b"):
                nom = st.text_input("Nombre", value="" if sel_j == "-- Nuevo --" else sel_j)
                eq = st.selectbox("Equipo", st.session_state.equipos["Nombre"].tolist())
                v1, v2, v3, v4, v5 = st.columns(5)
                vb = v1.number_input("VB", 0); h = v2.number_input("H", 0); h2 = v3.number_input("H2", 0); h3 = v4.number_input("H3", 0); hr = v5.number_input("HR", 0)
                if st.form_submit_button("Guardar"):
                    df = st.session_state.jugadores[st.session_state.jugadores["Nombre"] != sel_j]
                    pd.concat([df, pd.DataFrame([[nom, eq, vb, h, h2, h3, hr]], columns=["Nombre", "Equipo", "VB", "H", "H2", "H3", "HR"])], ignore_index=True).to_csv(path_archivo("data_jugadores.csv"), index=False); st.rerun()
            if sel_j != "-- Nuevo --" and st.button("🗑️ Eliminar Jugador"):
                st.session_state.jugadores[st.session_state.jugadores["Nombre"] != sel_j].to_csv(path_archivo("data_jugadores.csv"), index=False); st.rerun()

        with tab_p:
            sel_p = st.selectbox("Pitcher:", ["-- Nuevo --"] + sorted(st.session_state.pitchers["Nombre"].tolist()))
            with st.form("f_p"):
                nom_p = st.text_input("Nombre P", value="" if sel_p == "-- Nuevo --" else sel_p)
                eq_p = st.selectbox("Equipo  ", st.session_state.equipos["Nombre"].tolist())
                p1, p2, p3, p4 = st.columns(4)
                jg, jp, ip, cl = p1.number_input("JG", 0), p2.number_input("JP", 0), p3.number_input("IP", 0), p4.number_input("CL", 0)
                if st.form_submit_button("Guardar"):
                    dfp = st.session_state.pitchers[st.session_state.pitchers["Nombre"] != sel_p]
                    pd.concat([dfp, pd.DataFrame([[nom_p, eq_p, jg, jp, ip, cl]], columns=["Nombre", "Equipo", "JG", "JP", "IP", "CL"])], ignore_index=True).to_csv(path_archivo("data_pitchers.csv"), index=False); st.rerun()
            if sel_p != "-- Nuevo --" and st.button("🗑️ Eliminar Pitcher"):
                st.session_state.pitchers[st.session_state.pitchers["Nombre"] != sel_p].to_csv(path_archivo("data_pitchers.csv"), index=False); st.rerun()

        with tab_c:
            st.subheader("Gestionar Calendario")
            with st.form("f_cal"):
                f, h, cp = st.text_input("Fecha"), st.text_input("Hora"), st.text_input("Campo")
                loc = st.selectbox("Local", st.session_state.equipos["Nombre"].tolist())
                vis = st.selectbox("Visitante", st.session_state.equipos["Nombre"].tolist())
                sc = st.text_input("Score (Final)")
                if st.form_submit_button("Añadir Juego"):
                    pd.concat([st.session_state.calendario, pd.DataFrame([[f, h, cp, loc, vis, sc]], columns=["Fecha", "Hora", "Campo", "Local", "Visitante", "Score"])], ignore_index=True).to_csv(path_archivo("data_calendario.csv"), index=False); st.rerun()
            if not st.session_state.calendario.empty:
                if st.button("🗑️ Borrar Último Juego"):
                    st.session_state.calendario.drop(st.session_state.calendario.index[-1]).to_csv(path_archivo("data_calendario.csv"), index=False); st.rerun()
