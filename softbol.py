import streamlit as st
import pandas as pd
import os
import urllib.parse

# --- 1. CONFIGURACIÓN VISUAL ---
st.set_page_config(
    page_title="LIGA DE SOFTBOL DOMINICAL",
    page_icon="⚾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilo CSS para color ROJO
st.markdown("""
    <style>
    th { background-color: #D32F2F !important; color: white !important; text-align: center !important; }
    .stDataFrame, .stTable { border: 2px solid #D32F2F; border-radius: 10px; }
    div.stButton > button:first-child { background-color: #D32F2F; color: white; }
    h1, h2, h3 { color: #B71C1C; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE CARPETAS Y DATOS ---
CARPETA_DATOS = "datos_liga"
CARPETA_FOTOS = "galeria_liga"
for c in [CARPETA_DATOS, CARPETA_FOTOS]:
    if not os.path.exists(c): os.makedirs(c)

def ruta(archivo): return os.path.join(CARPETA_DATOS, archivo)

COLS_J = ["Nombre", "Equipo", "VB", "H", "H2", "H3", "HR"]
COLS_P = ["Nombre", "Equipo", "JG", "JP", "IP", "CL"]
COLS_CAL = ["Fecha", "Hora", "Campo", "Local", "Visitante", "Score"]

def cargar_datos(archivo, columnas):
    path = ruta(archivo)
    if os.path.exists(path):
        try:
            df = pd.read_csv(path)
            df.columns = df.columns.str.strip()
            for col in columnas:
                if col not in df.columns: df[col] = "" if col == "Score" else 0
            return df[columnas]
        except:
            return pd.DataFrame(columns=columnas)
    return pd.DataFrame(columns=columnas)

# Carga de datos en el estado de la sesión
st.session_state.jugadores = cargar_datos("data_jugadores.csv", COLS_J)
st.session_state.pitchers = cargar_datos("data_pitchers.csv", COLS_P)
st.session_state.equipos = pd.read_csv(ruta("data_equipos.csv")) if os.path.exists(ruta("data_equipos.csv")) else pd.DataFrame(columns=["Nombre"])
st.session_state.calendario = cargar_datos("data_calendario.csv", COLS_CAL)

# --- 3. SEGURIDAD Y RESPALDOS ---
if 'autenticado' not in st.session_state: st.session_state.autenticado = False

with st.sidebar:
    st.title("🥎 LIGA DOMINICAL")
    if not st.session_state.autenticado:
        with st.form("login"):
            pwd = st.text_input("Contraseña Admin:", type="password")
            if st.form_submit_button("Entrar"):
                if pwd == "softbol2026": 
                    st.session_state.autenticado = True
                    st.rerun()
                else: st.error("Incorrecta")
    else:
        st.success("🔓 MODO ADMIN")
        st.divider()
        st.subheader("💾 Respaldos (Solo Admin)")
        csv_j = st.session_state.jugadores.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Bateadores (CSV)", csv_j, "respaldo_jugadores.csv", "text/csv", use_container_width=True)
        st.divider()
        if st.button("Cerrar Sesión"):
            st.session_state.autenticado = False
            st.rerun()

menu = st.sidebar.radio("IR A:", ["🏠 Inicio", "🏆 LÍDERES", "📊 Standings", "📋 Rosters", "📅 Programación (Admin)", "🖼️ Galería", "🏃 Estadísticas (Admin)", "👥 Equipos"])

# ==========================================
# SECCIONES DE LA APLICACIÓN
# ==========================================

if menu == "🏠 Inicio":
    st.markdown("<h1 style='text-align: center;'>⚾ LIGA DE SOFTBOL DOMINICAL ⚾</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Ing. Benjamin Armenta - 2026</p>", unsafe_allow_html=True)
    st.divider()
    fotos = sorted(os.listdir(CARPETA_FOTOS), reverse=True)
    if fotos:
        cols_gal = st.columns(3)
        for i, f in enumerate(fotos[:3]):
            with cols_gal[i]: st.image(os.path.join(CARPETA_FOTOS, f), use_container_width=True)
    st.subheader("📅 Próximos Juegos")
    st.dataframe(st.session_state.calendario, use_container_width=True, hide_index=True)

elif menu == "🏆 LÍDERES":
    t1, t2 = st.tabs(["🥖 Bateo", "🔥 Pitcheo"])
    with t1:
        df = st.session_state.jugadores.copy()
        if not df.empty:
            df['H_T'] = df['H'] + df['H2'] + df['H3'] + df['HR']
            df['AVG'] = (df['H_T'] / df['VB'].replace(0, 1)).fillna(0)
            c1, c2 = st.columns(2)
            c1.subheader("🥇 AVG"); c1.table(df.sort_values("AVG", ascending=False).head(10)[["Nombre", "AVG"]].style.format({"AVG": "{:.3f}"}))
            c2.subheader("🥇 HR"); c2.table(df.sort_values("HR", ascending=False).head(10)[["Nombre", "HR"]])
            st.subheader("🥇 Hits Totales"); st.table(df.sort_values("H_T", ascending=False).head(10)[["Nombre", "H_T"]])
        else: st.info("No hay datos registrados.")
    with t2:
        dfp = st.session_state.pitchers.copy()
        if not dfp.empty:
            dfp['EFE'] = ((dfp['CL'] * 7) / dfp['IP'].replace(0, 1)).fillna(0)
            cp1, cp2 = st.columns(2)
            cp1.subheader("🥇 EFE"); cp1.table(dfp[dfp['IP']>0].sort_values("EFE").head(10)[["Nombre", "EFE"]].style.format({"EFE": "{:.2f}"}))
            cp2.subheader("🥇 JG"); cp2.table(dfp.sort_values("JG", ascending=False).head(10)[["Nombre", "JG"]])
        else: st.info("No hay datos.")

elif menu == "📊 Standings":
    st.header("📊 Tabla de Posiciones")
    if not st.session_state.pitchers.empty:
        std = st.session_state.pitchers.groupby("Equipo")[["JG", "JP"]].sum().reset_index()
        std["PCT"] = (std["JG"] / (std["JG"] + std["JP"]).replace(0, 1)).fillna(0)
        st.dataframe(std.sort_values(by=["JG", "PCT"], ascending=False).style.format({"PCT": "{:.3f}"}), use_container_width=True, hide_index=True)
    else: st.info("Sin datos de pitcheo.")

elif menu == "📋 Rosters":
    if not st.session_state.equipos.empty:
        eq = st.selectbox("Selecciona Equipo:", st.session_state.equipos["Nombre"].tolist())
        st.subheader("🥖 Bateadores")
        db = st.session_state.jugadores[st.session_state.jugadores["Equipo"] == eq]
        st.dataframe(db, use_container_width=True, hide_index=True)
        st.subheader("🔥 Pitchers")
        dp = st.session_state.pitchers[st.session_state.pitchers["Equipo"] == eq]
        st.dataframe(dp, use_container_width=True, hide_index=True)
    else: st.warning("Crea equipos primero.")

elif menu == "📅 Programación (Admin)":
    if not st.session_state.autenticado: st.warning("Inicia sesión como administrador.")
    else:
        with st.form("f_cal"):
            c1, c2, c3 = st.columns(3)
            f, h, cp = c1.text_input("Fecha"), c2.text_input("Hora"), c3.text_input("Campo")
            l = st.selectbox("Local", st.session_state.equipos["Nombre"]) if not st.session_state.equipos.empty else "N/A"
            v = st.selectbox("Visitante", st.session_state.equipos["Nombre"]) if not st.session_state.equipos.empty else "N/A"
            sc = st.text_input("Score")
            if st.form_submit_button("Guardar Juego"):
                nuevo = pd.DataFrame([[f, h, cp, l, v, sc]], columns=COLS_CAL)
                st.session_state.calendario = pd.concat([st.session_state.calendario, nuevo], ignore_index=True)
                st.session_state.calendario.to_csv(ruta("data_calendario.csv"), index=False)
                st.rerun()

elif menu == "🖼️ Galería":
    if st.session_state.autenticado:
        sub = st.file_uploader("Subir Fotos:", accept_multiple_files=True)
        if st.button("Guardar"):
            for img in sub:
                with open(os.path.join(CARPETA_FOTOS, img.name), "wb") as f: f.write(img.getbuffer())
            st.rerun()
    fotos = os.listdir(CARPETA_FOTOS)
    cols = st.columns(4)
    for i, f in enumerate(fotos):
        with cols[i % 4]: st.image(os.path.join(CARPETA_FOTOS, f), use_container_width=True)

elif menu == "🏃 Estadísticas (Admin)":
    if not st.session_state.autenticado: st.warning("Inicia sesión.")
    else:
        t1, t2 = st.tabs(["Bateo", "Pitcheo"])
        with t1:
            sel = st.selectbox("Jugador:", ["-- Nuevo --"] + sorted(st.session_state.jugadores["Nombre"].tolist()))
            v_n, v_eq, v_vb, v_h, v_h2, v_h3, v_hr = "", "", 1, 0, 0, 0, 0
            if sel != "-- Nuevo --":
                d = st.session_state.jugadores[st.session_state.jugadores["Nombre"] == sel].iloc[0]
                v_n, v_eq, v_vb, v_h, v_h2, v_h3, v_hr = d["Nombre"], d["Equipo"], int(d["VB"]), int(d["H"]), int(d["H2"]), int(d["H3"]), int(d["HR"])
            with st.form("f_j"):
                nom = st.text_input("Nombre", value=v_n)
                eq = st.selectbox("Equipo", st.session_state.equipos["Nombre"]) if not st.session_state.equipos.empty else "N/A"
                c1, c2, c3, c4, c5 = st.columns(5)
                vb, h, h2, h3, hr = c1.number_input("VB", value=v_vb), c2.number_input("H", value=v_h), c3.number_input("H2", value=v_h2), c4.number_input("H3", value=v_h3), c5.number_input("HR", value=v_hr)
                if st.form_submit_button("Guardar"):
                    df = st.session_state.jugadores[st.session_state.jugadores["Nombre"] != sel]
                    nuevo = pd.DataFrame([[nom, eq, vb, h, h2, h3, hr]], columns=COLS_J)
                    pd.concat([df, nuevo], ignore_index=True).to_csv(ruta("data_jugadores.csv"), index=False)
                    st.rerun()

        with t2:
            selp = st.selectbox("Pitcher:", ["-- Nuevo --"] + sorted(st.session_state.pitchers["Nombre"].tolist()))
            vp_n, vp_eq, vp_jg, vp_jp, vp_ip, vp_cl = "", "", 0, 0, 0, 0
            if selp != "-- Nuevo --":
                dp = st.session_state.pitchers[st.session_state.pitchers["Nombre"] == selp].iloc[0]
                vp_n, vp_eq, vp_jg, vp_jp, vp_ip, vp_cl = dp["Nombre"], dp["Equipo"], int(dp["JG"]), int(dp["JP"]), int(dp["IP"]), int(dp["CL"])
            with st.form("f_p"):
                nom_p = st.text_input("Nombre", value=vp_n)
                eq_p = st.selectbox("Equipo ", st.session_state.equipos["Nombre"]) if not st.session_state.equipos.empty else "N/A"
                c1, c2, c3, c4 = st.columns(4)
                jg, jp, ip, cl = c1.number_input("JG", value=vp_jg), c2.number_input("JP", value=vp_jp), c3.number_input("IP", value=vp_ip), c4.number_input("CL", value=vp_cl)
                if st.form_submit_button("Guardar Pitcher"):
                    dfp = st.session_state.pitchers[st.session_state.pitchers["Nombre"] != selp]
                    nuevo_p = pd.DataFrame([[nom_p, eq_p, jg, jp, ip, cl]], columns=COLS_P)
                    pd.concat([dfp, nuevo_p], ignore_index=True).to_csv(ruta("data_pitchers.csv"), index=False)
                    st.rerun()

elif menu == "👥 Equipos":
    if st.session_state.autenticado:
        n_e = st.text_input("Nombre Equipo")
        if st.button("Registrar"):
            pd.concat([st.session_state.equipos, pd.DataFrame([{"Nombre": n_e}])], ignore_index=True).to_csv(ruta("data_equipos.csv"), index=False); st.rerun()
    st.table(st.session_state.equipos)
