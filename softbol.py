import streamlit as st
import pandas as pd
import os
import urllib.parse

# --- 1. CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="LIGA DE SOFTBOL DOMINICAL", page_icon="⚾", layout="wide")

st.markdown("""
    <style>
    th { background-color: #D32F2F !important; color: white !important; text-align: center !important; }
    .stDataFrame, .stTable { border: 2px solid #D32F2F; border-radius: 10px; }
    div.stButton > button:first-child { background-color: #D32F2F; color: white; border-radius: 5px; }
    h1, h2, h3 { color: #B71C1C; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE DIRECTORIOS ---
DATOS_DIR, FOTOS_DIR = "datos_liga", "galeria_liga"
for d in [DATOS_DIR, FOTOS_DIR]:
    if not os.path.exists(d): os.makedirs(d)

def path_archivo(nombre): return os.path.join(DATOS_DIR, nombre)

# --- 3. FUNCIONES DE CARGA ---
COLS_J = ["Nombre", "Equipo", "VB", "H", "H2", "H3", "HR"]
COLS_P = ["Nombre", "Equipo", "JG", "JP", "IP", "CL"]
COLS_CAL = ["Fecha", "Hora", "Campo", "Local", "Visitante", "Score"]
COLS_ACC = ["Equipo", "Password"]

def leer_csv(nombre, columnas):
    p = path_archivo(nombre)
    if os.path.exists(p):
        try:
            df = pd.read_csv(p)
            df.columns = df.columns.str.strip()
            for c in columnas:
                if c not in df.columns: df[c] = "" if c in ["Score", "Password"] else 0
            return df[columnas]
        except: return pd.DataFrame(columns=columnas)
    return pd.DataFrame(columns=columnas)

# Carga global
st.session_state.jugadores = leer_csv("data_jugadores.csv", COLS_J)
st.session_state.pitchers = leer_csv("data_pitchers.csv", COLS_P)
st.session_state.equipos = leer_csv("data_equipos.csv", ["Nombre"])
st.session_state.calendario = leer_csv("data_calendario.csv", COLS_CAL)
st.session_state.accesos = leer_csv("data_accesos.csv", COLS_ACC)

# --- 4. SEGURIDAD Y ROLES ---
if 'rol' not in st.session_state: st.session_state.rol = "Invitado"
if 'eq_gestion' not in st.session_state: st.session_state.eq_gestion = None

with st.sidebar:
    st.title("🥎 LIGA DOMINICAL")
    if st.session_state.rol == "Invitado":
        with st.form("login"):
            pwd_in = st.text_input("Contraseña de Acceso:", type="password")
            if st.form_submit_button("Entrar"):
                if pwd_in == "softbol2026": 
                    st.session_state.rol = "Admin"; st.rerun()
                elif pwd_in in st.session_state.accesos["Password"].values:
                    fila = st.session_state.accesos[st.session_state.accesos["Password"] == pwd_in].iloc[0]
                    st.session_state.rol = "Delegado"
                    st.session_state.eq_gestion = fila["Equipo"]
                    st.rerun()
                else: st.error("Clave Incorrecta")
    else:
        st.success(f"🔓 Sesión: {st.session_state.rol}")
        if st.session_state.eq_gestion: st.info(f"Equipo: {st.session_state.eq_gestion}")
        if st.button("Cerrar Sesión"):
            st.session_state.rol = "Invitado"; st.session_state.eq_gestion = None; st.rerun()

menu = st.sidebar.radio("IR A:", ["🏠 Inicio", "🏆 LÍDERES", "📊 Standings", "📋 Rosters", "🔍 Buscador", "🖼️ Galería"])
if st.session_state.rol == "Admin": menu = st.sidebar.radio("ZONA ADMIN:", ["🏃 Admin General"])
if st.session_state.rol == "Delegado": menu = st.sidebar.radio("ZONA DELEGADO:", ["📋 Mi Roster (Delegado)"])

# ==========================================
# 🏠 INICIO
# ==========================================
if menu == "🏠 Inicio":
    st.markdown("<h1 style='text-align: center; color: #D32F2F;'>⚾ LIGA DE SOFTBOL DOMINICAL ⚾</h1>", unsafe_allow_html=True)
    st.divider()
    fotos = sorted(os.listdir(FOTOS_DIR), reverse=True)
    if fotos:
        st.subheader("📸 Galería Reciente")
        cols_gal = st.columns(3)
        for i, f in enumerate(fotos[:3]):
            with cols_gal[i]: st.image(os.path.join(FOTOS_DIR, f), use_container_width=True)
    st.subheader("📅 Programación de Juegos")
    st.dataframe(st.session_state.calendario, use_container_width=True, hide_index=True)

# ==========================================
# 🏆 LÍDERES (TODOS LOS DEPARTAMENTOS)
# ==========================================
elif menu == "🏆 LÍDERES":
    t1, t2 = st.tabs(["🥖 Bateo", "🔥 Pitcheo"])
    with t1:
        df = st.session_state.jugadores.copy()
        if not df.empty:
            df['H_T'] = df['H'] + df['H2'] + df['H3'] + df['HR']
            df['AVG'] = (df['H_T'] / df['VB'].replace(0, 1)).fillna(0)
            c1, c2 = st.columns(2)
            c1.subheader("🥇 AVG"); c1.table(df.sort_values("AVG", ascending=False).head(10)[["Nombre", "AVG"]].style.format({"AVG": "{:.3f}"}))
            c2.subheader("🥇 Hits Totales"); c2.table(df.sort_values("H_T", ascending=False).head(10)[["Nombre", "H_T"]])
            c3, c4 = st.columns(2)
            c3.subheader("🥇 Jonrones (HR)"); c3.table(df.sort_values("HR", ascending=False).head(10)[["Nombre", "HR"]])
            c4.subheader("🥇 Dobles (H2)"); c4.table(df.sort_values("H2", ascending=False).head(10)[["Nombre", "H2"]])
        else: st.info("Sin datos.")
    with t2:
        dfp = st.session_state.pitchers.copy()
        if not dfp.empty:
            dfp['EFE'] = ((dfp['CL'] * 7) / dfp['IP'].replace(0, 1)).fillna(0)
            cp1, cp2 = st.columns(2)
            cp1.subheader("🥇 EFE"); cp1.table(dfp[dfp['IP']>0].sort_values("EFE").head(10)[["Nombre", "EFE"]].style.format({"EFE": "{:.2f}"}))
            cp2.subheader("🥇 Ganados"); cp2.table(dfp.sort_values("JG", ascending=False).head(10)[["Nombre", "JG"]])
            cp3, cp4 = st.columns(2)
            cp3.subheader("🥇 Perdidos"); cp3.table(dfp.sort_values("JP", ascending=False).head(10)[["Nombre", "JP"]])
            cp4.subheader("🥇 Innings"); cp4.table(dfp.sort_values("IP", ascending=False).head(10)[["Nombre", "IP"]])
        else: st.info("Sin datos.")

# ==========================================
# 📋 ROSTERS (BATEO + PITCHEO)
# ==========================================
elif menu == "📋 Rosters":
    if not st.session_state.equipos.empty:
        eq_v = st.selectbox("Selecciona Equipo:", st.session_state.equipos["Nombre"].tolist())
        st.subheader("🥖 Bateadores")
        db = st.session_state.jugadores[st.session_state.jugadores["Equipo"] == eq_v].copy()
        if not db.empty:
            db['AVG'] = ((db['H']+db['H2']+db['H3']+db['HR'])/db['VB'].replace(0,1)).fillna(0)
            st.dataframe(db[["Nombre", "VB", "H", "H2", "H3", "HR", "AVG"]].style.format({"AVG": "{:.3f}"}), use_container_width=True, hide_index=True)
        st.subheader("🔥 Pitchers")
        dp = st.session_state.pitchers[st.session_state.pitchers["Equipo"] == eq_v].copy()
        if not dp.empty:
            dp['EFE'] = ((dp['CL'] * 7) / dp['IP'].replace(0, 1)).fillna(0)
            st.dataframe(dp[["Nombre", "JG", "JP", "IP", "CL", "EFE"]].style.format({"EFE": "{:.2f}"}), use_container_width=True, hide_index=True)
    else: st.warning("No hay equipos registrados.")

# ==========================================
# 🔍 BUSCADOR
# ==========================================
elif menu == "🔍 Buscador":
    st.header("🔍 Buscar Jugador")
    q = st.text_input("Escribe el nombre:")
    if q:
        res = st.session_state.jugadores[st.session_state.jugadores["Nombre"].str.contains(q, case=False)]
        st.dataframe(res, hide_index=True)

# ==========================================
# 🖼️ GALERÍA
# ==========================================
elif menu == "🖼️ Galería":
    st.header("📸 Galería de la Liga")
    if st.session_state.rol == "Admin":
        subida = st.file_uploader("Subir Fotos:", accept_multiple_files=True)
        if st.button("Guardar Fotos"):
            for img in subida:
                with open(os.path.join(FOTOS_DIR, img.name), "wb") as f: f.write(img.getbuffer())
            st.rerun()
    fotos = os.listdir(FOTOS_DIR)
    cols = st.columns(4)
    for i, f in enumerate(fotos):
        with cols[i % 4]:
            st.image(os.path.join(FOTOS_DIR, f), use_container_width=True)
            if st.session_state.rol == "Admin" and st.button(f"Borrar {i}"):
                os.remove(os.path.join(FOTOS_DIR, f)); st.rerun()

# ==========================================
# 📋 MI ROSTER (DELEGADO)
# ==========================================
elif menu == "📋 Mi Roster (Delegado)":
    mi_eq = st.session_state.eq_gestion
    st.header(f"➕ Registro: {mi_eq}")
    with st.form("alta_del"):
        nom_n = st.text_input("Nombre del Jugador")
        if st.form_submit_button("✅ Registrar"):
            if nom_n:
                nueva = pd.DataFrame([[nom_n, mi_eq, 0, 0, 0, 0, 0]], columns=COLS_J)
                pd.concat([st.session_state.jugadores, nueva], ignore_index=True).to_csv(path_archivo("data_jugadores.csv"), index=False)
                st.success("Añadido."); st.rerun()

# ==========================================
# 🏃 ADMIN GENERAL
# ==========================================
elif menu == "🏃 Admin General":
    if st.session_state.rol != "Admin": st.warning("Acceso Denegado")
    else:
        tab_e, tab_b, tab_p, tab_c, tab_k = st.tabs(["Equipos", "Bateo", "Pitcheo", "Calendario", "🔑 Claves"])
        with tab_e:
            n_e = st.text_input("Nuevo Equipo")
            if st.button("Registrar"):
                pd.concat([st.session_state.equipos, pd.DataFrame([{"Nombre": n_e}])], ignore_index=True).to_csv(path_archivo("data_equipos.csv"), index=False); st.rerun()
        with tab_b:
            sel = st.selectbox("Jugador:", ["-- Nuevo --"] + sorted(st.session_state.jugadores["Nombre"].tolist()))
            with st.form("f_b"):
                nom = st.text_input("Nombre", value="" if sel=="-- Nuevo --" else sel)
                eq = st.selectbox("Equipo", st.session_state.equipos["Nombre"].tolist())
                c1, c2, c3, c4, c5 = st.columns(5)
                vb, h, h2, h3, hr = c1.number_input("VB"), c2.number_input("H"), c3.number_input("H2"), c4.number_input("H3"), c5.number_input("HR")
                if st.form_submit_button("Guardar"):
                    df = st.session_state.jugadores[st.session_state.jugadores["Nombre"] != sel]
                    pd.concat([df, pd.DataFrame([[nom, eq, vb, h, h2, h3, hr]], columns=COLS_J)], ignore_index=True).to_csv(path_archivo("data_jugadores.csv"), index=False); st.rerun()
            if sel != "-- Nuevo --" and st.button("🗑️ Eliminar Jugador"):
                st.session_state.jugadores[st.session_state.jugadores["Nombre"]!=sel].to_csv(path_archivo("data_jugadores.csv"), index=False); st.rerun()
        with tab_p:
            selp = st.selectbox("Pitcher:", ["-- Nuevo --"] + sorted(st.session_state.pitchers["Nombre"].tolist()))
            with st.form("f_p"):
                nomp = st.text_input("Nombre P", value="" if selp=="-- Nuevo --" else selp)
                eqp = st.selectbox("Equipo ", st.session_state.equipos["Nombre"].tolist())
                pc1, pc2, pc3, pc4 = st.columns(4)
                jg, jp, ip, cl = pc1.number_input("JG"), pc2.number_input("JP"), pc3.number_input("IP"), pc4.number_input("CL")
                if st.form_submit_button("Guardar P"):
                    dfp = st.session_state.pitchers[st.session_state.pitchers["Nombre"] != selp]
                    pd.concat([dfp, pd.DataFrame([[nomp, eqp, jg, jp, ip, cl]], columns=COLS_P)], ignore_index=True).to_csv(path_archivo("data_pitchers.csv"), index=False); st.rerun()
        with tab_k:
            with st.form("f_k"):
                eq_k = st.selectbox("Equipo clave:", st.session_state.equipos["Nombre"].tolist())
                pass_k = st.text_input("Clave:")
                if st.form_submit_button("🔒 Asignar"):
                    df_acc = st.session_state.accesos[st.session_state.accesos["Equipo"] != eq_k]
                    pd.concat([df_acc, pd.DataFrame([[eq_k, pass_k]], columns=COLS_ACC)], ignore_index=True).to_csv(path_archivo("data_accesos.csv"), index=False); st.rerun()
            st.dataframe(st.session_state.accesos, hide_index=True)
        with tab_c:
            with st.form("f_cal"):
                f, h, cp = st.text_input("Fecha"), st.text_input("Hora"), st.text_input("Campo")
                loc, vis = st.selectbox("Local", st.session_state.equipos["Nombre"]), st.selectbox("Visitante", st.session_state.equipos["Nombre"])
                sc = st.text_input("Score")
                if st.form_submit_button("📅 Guardar Juego"):
                    pd.concat([st.session_state.calendario, pd.DataFrame([[f, h, cp, loc, vis, sc]], columns=COLS_CAL)], ignore_index=True).to_csv(path_archivo("data_calendario.csv"), index=False); st.rerun()

# --- STANDINGS ---
elif menu == "📊 Standings":
    if not st.session_state.pitchers.empty:
        std = st.session_state.pitchers.groupby("Equipo")[["JG", "JP"]].sum().reset_index()
        st.dataframe(std.sort_values("JG", ascending=False), use_container_width=True, hide_index=True)
