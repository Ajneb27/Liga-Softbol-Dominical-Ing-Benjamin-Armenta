import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="LIGA DE SOFTBOL DOMINICAL", page_icon="⚾", layout="wide")

st.markdown("""
    <style>
    th { background-color: #D32F2F !important; color: white !important; text-align: center !important; }
    .stDataFrame, .stTable { border: 2px solid #D32F2F; border-radius: 10px; }
    div.stButton > button:first-child { background-color: #D32F2F; color: white; border-radius: 5px; width: 100%; }
    h1, h2, h3 { color: #B71C1C; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #f0f2f6; border-radius: 5px; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE DIRECTORIOS Y ARCHIVOS ---
DATOS_DIR, FOTOS_DIR = "datos_liga", "galeria_liga"
for d in [DATOS_DIR, FOTOS_DIR]:
    if not os.path.exists(d): os.makedirs(d)

def path_archivo(nombre): return os.path.join(DATOS_DIR, nombre)

COLS_J = ["Nombre", "Equipo", "VB", "H", "H2", "H3", "HR"]
COLS_P = ["Nombre", "Equipo", "JG", "JP", "IP", "CL"]
COLS_CAL = ["Fecha", "Hora", "Campo", "Local", "Visitante", "Score"]
COLS_ACC = ["Equipo", "Password"]

def leer_csv(nombre, columnas):
    p = path_archivo(nombre)
    if os.path.exists(p):
        try:
            df = pd.read_csv(p)
            for c in columnas:
                if c not in df.columns: df[c] = "" if c in ["Score", "Password"] else 0
            return df[columnas]
        except: return pd.DataFrame(columns=columnas)
    return pd.DataFrame(columns=columnas)

# Carga inicial en session_state
if 'jugadores' not in st.session_state:
    st.session_state.jugadores = leer_csv("data_jugadores.csv", COLS_J)
    st.session_state.pitchers = leer_csv("data_pitchers.csv", COLS_P)
    st.session_state.equipos = leer_csv("data_equipos.csv", ["Nombre"])
    st.session_state.calendario = leer_csv("data_calendario.csv", COLS_CAL)
    st.session_state.accesos = leer_csv("data_accesos.csv", COLS_ACC)

# --- 3. SEGURIDAD ---
if 'rol' not in st.session_state: st.session_state.rol = "Invitado"
if 'eq_gestion' not in st.session_state: st.session_state.eq_gestion = None

with st.sidebar:
    st.title("🥎 LIGA DOMINICAL")
    if st.session_state.rol == "Invitado":
        with st.form("login"):
            pwd_in = st.text_input("Contraseña:", type="password")
            if st.form_submit_button("Entrar"):
                if pwd_in == "softbol2026": 
                    st.session_state.rol = "Admin"; st.rerun()
                elif pwd_in in st.session_state.accesos["Password"].values:
                    fila = st.session_state.accesos[st.session_state.accesos["Password"] == pwd_in].iloc[0]
                    st.session_state.rol = "Delegado"; st.session_state.eq_gestion = fila["Equipo"]; st.rerun()
                else: st.error("Clave Incorrecta")
    else:
        st.success(f"🔓 {st.session_state.rol}: {st.session_state.eq_gestion if st.session_state.eq_gestion else ''}")
        if st.button("Cerrar Sesión"):
            st.session_state.rol = "Invitado"; st.session_state.eq_gestion = None; st.rerun()

# --- 4. MENÚ PRINCIPAL ---
opciones = ["🏠 Inicio", "🏆 LÍDERES", "📊 Standings", "📋 Rosters", "🔍 Buscador"]
if st.session_state.rol == "Admin": opciones.append("🏃 Admin General")
if st.session_state.rol == "Delegado": opciones.append("📋 Mi Roster")

menu = st.sidebar.radio("IR A:", opciones)

# --- 5. LÓGICA DE SECCIONES ---

if menu == "🏠 Inicio":
    st.markdown("<h1 style='text-align: center;'>⚾ LIGA DE SOFTBOL ⚾</h1>", unsafe_allow_html=True)
    fotos = sorted([f for f in os.listdir(FOTOS_DIR) if f.endswith(('.png', '.jpg', '.jpeg'))], reverse=True)
    if fotos:
        st.subheader("📸 Galería")
        cols = st.columns(3)
        for i, f in enumerate(fotos[:3]):
            cols[i%3].image(os.path.join(FOTOS_DIR, f), use_container_width=True)
    st.subheader("📅 Próximos Encuentros")
    st.dataframe(st.session_state.calendario, use_container_width=True, hide_index=True)

elif menu == "🏆 LÍDERES":
    t1, t2 = st.tabs(["🥖 Bateo", "🔥 Pitcheo"])
    with t1:
        df = st.session_state.jugadores.copy()
        if not df.empty:
            df['H_T'] = df['H'] + df['H2'] + df['H3'] + df['HR']
            df['AVG'] = (df['H_T'] / df['VB'].replace(0, 1)).fillna(0)
            c1, c2 = st.columns(2)
            c1.subheader("🥇 AVG"); c1.table(df.sort_values("AVG", ascending=False).head(5)[["Nombre", "AVG"]].style.format({"AVG": "{:.3f}"}))
            c2.subheader("🥇 HR"); c2.table(df.sort_values("HR", ascending=False).head(5)[["Nombre", "HR"]])
    with t2:
        dfp = st.session_state.pitchers.copy()
        if not dfp.empty:
            dfp['ERA'] = ((dfp['CL'] * 7) / dfp['IP'].replace(0, 1)).fillna(0)
            cp1, cp2 = st.columns(2)
            cp1.subheader("🥇 ERA"); cp1.table(dfp[dfp['IP']>0].sort_values("ERA").head(5)[["Nombre", "ERA"]].style.format({"ERA": "{:.2f}"}))
            cp2.subheader("🥇 Ganados"); cp2.table(dfp.sort_values("JG", ascending=False).head(5)[["Nombre", "JG"]])

elif menu == "📊 Standings":
    st.header("📊 Tabla de Posiciones")
    cal = st.session_state.calendario.copy()
    cal = cal[cal['Score'].str.contains('-', na=False)]
    stats = []
    for eq in st.session_state.equipos["Nombre"]:
        jg, jp = 0, 0
        partidos = cal[(cal['Local'] == eq) | (cal['Visitante'] == eq)]
        for _, f in partidos.iterrows():
            try:
                s_l, s_v = map(int, f['Score'].split('-'))
                if (f['Local'] == eq and s_l > s_v) or (f['Visitante'] == eq and s_v > s_l): jg += 1
                else: jp += 1
            except: continue
        jj = jg + jp
        pct = jg / jj if jj > 0 else 0
        stats.append({"Equipo": eq, "JJ": jj, "JG": jg, "JP": jp, "PCT": pct})
    st.table(pd.DataFrame(stats).sort_values("PCT", ascending=False).style.format({"PCT": "{:.3f}"}))

elif menu == "🔍 Buscador":
    q = st.text_input("Buscar jugador:")
    if q:
        st.dataframe(st.session_state.jugadores[st.session_state.jugadores["Nombre"].str.contains(q, case=False)], use_container_width=True)

elif menu == "📋 Mi Roster":
    eq = st.session_state.eq_gestion
    st.header(f"Gestión de {eq}")
    with st.expander("➕ Nuevo Jugador"):
        with st.form("add_j"):
            nom = st.text_input("Nombre:")
            if st.form_submit_button("Guardar"):
                df_n = pd.concat([st.session_state.jugadores, pd.DataFrame([[nom, eq, 0,0,0,0,0]], columns=COLS_J)], ignore_index=True)
                df_n.to_csv(path_archivo("data_jugadores.csv"), index=False); st.rerun()
    
    eliminar = st.selectbox("Eliminar Jugador:", ["--"] + st.session_state.jugadores[st.session_state.jugadores["Equipo"]==eq]["Nombre"].tolist())
    if st.button("Confirmar Baja") and eliminar != "--":
        st.session_state.jugadores[st.session_state.jugadores["Nombre"] != eliminar].to_csv(path_archivo("data_jugadores.csv"), index=False); st.rerun()

elif menu == "🏃 Admin General":
    t_e, t_b, t_c, t_f = st.tabs(["Equipos", "Bateo/Stats", "Calendario", "Fotos"])
    
    with t_e:
        n_eq = st.text_input("Nuevo Equipo:")
        if st.button("Añadir"):
            pd.concat([st.session_state.equipos, pd.DataFrame([[n_eq]], columns=["Nombre"])], ignore_index=True).to_csv(path_archivo("data_equipos.csv"), index=False); st.rerun()
        borrar_e = st.selectbox("Borrar Equipo:", ["--"] + st.session_state.equipos["Nombre"].tolist())
        if st.button("Eliminar") and borrar_e != "--":
            st.session_state.equipos[st.session_state.equipos["Nombre"] != borrar_e].to_csv(path_archivo("data_equipos.csv"), index=False); st.rerun()

    with t_b:
        sel = st.selectbox("Jugador:", ["--"] + sorted(st.session_state.jugadores["Nombre"].tolist()))
        if sel != "--":
            d = st.session_state.jugadores[st.session_state.jugadores["Nombre"] == sel].iloc[0]
            with st.form("edit_b"):
                v_vb = st.number_input("VB", value=int(d["VB"]))
                v_h = st.number_input("H", value=int(d["H"]))
                v_hr = st.number_input("HR", value=int(d["HR"]))
                if st.form_submit_button("Actualizar"):
                    st.session_state.jugadores.loc[st.session_state.jugadores["Nombre"]==sel, ["VB","H","HR"]] = [v_vb, v_h, v_hr]
                    st.session_state.jugadores.to_csv(path_archivo("data_jugadores.csv"), index=False); st.rerun()

    with t_c:
        idx = st.selectbox("Partido:", st.session_state.calendario.index, format_func=lambda x: f"{st.session_state.calendario.loc[x, 'Local']} vs {st.session_state.calendario.loc[x, 'Visitante']}")
        n_score = st.text_input("Score (10-5):", value=st.session_state.calendario.loc[idx, "Score"])
        if st.button("Guardar Marcador"):
            st.session_state.calendario.at[idx, "Score"] = n_score
            st.session_state.calendario.to_csv(path_archivo("data_calendario.csv"), index=False); st.success("OK"); st.rerun()

    with t_f:
        f_subir = st.file_uploader("Subir foto:", type=["jpg","png"])
        if f_subir:
            with open(os.path.join(FOTOS_DIR, f_subir.name), "wb") as f: f.write(f_subir.getbuffer())
            st.success("Foto subida")
