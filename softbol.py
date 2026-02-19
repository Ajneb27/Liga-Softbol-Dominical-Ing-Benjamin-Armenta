import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN Y ESTILOS ---
st.set_page_config(page_title="LIGA SOFTBOL 2026", page_icon="⚾", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #fdfdfd; }
    th { background-color: #D32F2F !important; color: white !important; }
    div.stButton > button { background-color: #D32F2F; color: white; border-radius: 8px; width: 100%; }
    h1, h2, h3 { color: #B71C1C; font-family: 'Arial Black'; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. BASE DE DATOS LOCAL (CSV) ---
DATOS_DIR, FOTOS_DIR = "datos_liga", "galeria_liga"
for d in [DATOS_DIR, FOTOS_DIR]:
    if not os.path.exists(d): os.makedirs(d)

COLS = {
    "jugadores": ["Nombre", "Equipo", "VB", "H", "H2", "H3", "HR"],
    "pitchers": ["Nombre", "Equipo", "JG", "JP", "IP", "CL"],
    "calendario": ["Fecha", "Hora", "Campo", "Local", "Visitante", "Score"],
    "equipos": ["Nombre"],
    "accesos": ["Equipo", "Password"]
}

def gestionar_datos(archivo, df_nuevo=None):
    p = os.path.join(DATOS_DIR, f"data_{archivo}.csv")
    if df_nuevo is not None:
        df_nuevo.to_csv(p, index=False)
        st.session_state[archivo] = df_nuevo
        return df_nuevo
    if archivo not in st.session_state:
        if os.path.exists(p):
            df = pd.read_csv(p)
            for c in COLS[archivo]:
                if c not in df.columns: df[c] = 0 if c not in ["Score", "Password"] else ""
            st.session_state[archivo] = df[COLS[archivo]]
        else:
            st.session_state[archivo] = pd.DataFrame(columns=COLS[archivo])
    return st.session_state[archivo]

# Carga inicial forzada
for tabla in COLS.keys(): gestionar_datos(tabla)

# --- 3. LOGIN Y ROLES ---
if 'rol' not in st.session_state: st.session_state.rol = "Invitado"
if 'eq_gestion' not in st.session_state: st.session_state.eq_gestion = None

with st.sidebar:
    st.title("🥎 MENÚ LIGA")
    if st.session_state.rol == "Invitado":
        with st.form("login"):
            pwd = st.text_input("Contraseña:", type="password")
            if st.form_submit_button("Entrar"):
                if pwd == "softbol2026": 
                    st.session_state.rol = "Admin"; st.rerun()
                elif pwd in st.session_state.accesos["Password"].values:
                    f = st.session_state.accesos[st.session_state.accesos["Password"] == pwd].iloc[0]
                    st.session_state.rol = "Delegado"; st.session_state.eq_gestion = f["Equipo"]; st.rerun()
                else: st.error("Clave Incorrecta")
    else:
        st.info(f"Sesión: {st.session_state.rol}")
        if st.button("Cerrar Sesión"):
            st.session_state.rol = "Invitado"; st.session_state.eq_gestion = None; st.rerun()

menu = st.sidebar.radio("Ir a:", ["🏠 Inicio", "🏆 Líderes", "📊 Standings", "📋 Rosters", "🔍 Buscador"] + 
                       (["🏃 Admin General"] if st.session_state.rol == "Admin" else []) +
                       (["📋 Mi Roster"] if st.session_state.rol == "Delegado" else []))

# --- 4. SECCIONES ---

if menu == "🏠 Inicio":
    st.markdown("<h1 style='text-align:center;'>⚾ LIGA DOMINICAL 2026 ⚾</h1>", unsafe_allow_html=True)
    fots = sorted([f for f in os.listdir(FOTOS_DIR) if f.lower().endswith(('.png', '.jpg'))], reverse=True)
    if fots:
        c = st.columns(3)
        for i, f in enumerate(fots[:3]): c[i].image(os.path.join(FOTOS_DIR, f), use_container_width=True)
    st.subheader("📅 Calendario")
    st.dataframe(st.session_state.calendario, use_container_width=True, hide_index=True)

elif menu == "📊 Standings":
    st.header("📊 Posiciones")
    cal = st.session_state.calendario.copy()
    cal = cal[cal['Score'].str.contains('-', na=False)]
    res = []
    for eq in st.session_state.equipos["Nombre"]:
        jg = jp = 0
        part = cal[(cal['Local'] == eq) | (cal['Visitante'] == eq)]
        for _, f in part.iterrows():
            try:
                sl, sv = map(int, f['Score'].split('-'))
                if (f['Local'] == eq and sl > sv) or (f['Visitante'] == eq and sv > sl): jg += 1
                else: jp += 1
            except: continue
        pct = jg/(jg+jp) if (jg+jp)>0 else 0
        res.append({"Equipo": eq, "JJ": jg+jp, "JG": jg, "JP": jp, "PCT": pct})
    st.table(pd.DataFrame(res).sort_values("PCT", ascending=False).style.format({"PCT": "{:.3f}"}))

elif menu == "📋 Mi Roster":
    eq = st.session_state.eq_gestion
    st.subheader(f"Gestión de Roster: {eq}")
    with st.expander("➕ Alta de Jugador"):
        nj = st.text_input("Nombre completo:")
        if st.button("Registrar"):
            df = pd.concat([st.session_state.jugadores, pd.DataFrame([[nj, eq, 0,0,0,0,0]], columns=COLS["jugadores"])], ignore_index=True)
            gestionar_datos("jugadores", df); st.rerun()
    
    baja = st.selectbox("Baja de Jugador:", ["--"] + st.session_state.jugadores[st.session_state.jugadores["Equipo"]==eq]["Nombre"].tolist())
    if st.button("🗑️ Eliminar Permanente") and baja != "--":
        df = st.session_state.jugadores[st.session_state.jugadores["Nombre"] != baja]
        gestionar_datos("jugadores", df); st.rerun()

elif menu == "🏃 Admin General":
    t1, t2, t3, t4 = st.tabs(["Equipos", "Stats", "Calendario", "Fotos"])
    with t1:
        ne = st.text_input("Nombre del Equipo:")
        if st.button("Añadir Equipo"):
            df = pd.concat([st.session_state.equipos, pd.DataFrame([[ne]], columns=["Nombre"])], ignore_index=True)
            gestionar_datos("equipos", df); st.rerun()
        be = st.selectbox("Eliminar Equipo:", ["--"] + st.session_state.equipos["Nombre"].tolist())
        if st.button("Borrar Equipo") and be != "--":
            gestionar_datos("equipos", st.session_state.equipos[st.session_state.equipos["Nombre"] != be]); st.rerun()

    with t2:
        sel = st.selectbox("Jugador:", ["--"] + sorted(st.session_state.jugadores["Nombre"].tolist()))
        if sel != "--":
            row = st.session_state.jugadores[st.session_state.jugadores["Nombre"] == sel].iloc[0]
            with st.form("ed"):
                c = st.columns(3)
                v1 = c[0].number_input("VB", value=int(row["VB"]))
                v2 = c[1].number_input("H", value=int(row["H"]))
                v3 = c[2].number_input("HR", value=int(row["HR"]))
                if st.form_submit_button("Actualizar Stats"):
                    st.session_state.jugadores.loc[st.session_state.jugadores["Nombre"]==sel, ["VB","H","HR"]] = [v1, v2, v3]
                    gestionar_datos("jugadores", st.session_state.jugadores); st.success("Guardado"); st.rerun()

    with t3:
        st.write("Editar Scores")
        idx = st.selectbox("Partido:", st.session_state.calendario.index, format_func=lambda x: f"{st.session_state.calendario.loc[x, 'Local']} vs {st.session_state.calendario.loc[x, 'Visitante']}")
        sc = st.text_input("Score:", st.session_state.calendario.loc[idx, "Score"])
        if st.button("Guardar Resultado"):
            st.session_state.calendario.at[idx, "Score"] = sc
            gestionar_datos("calendario", st.session_state.calendario); st.rerun()

    with t4:
        img = st.file_uploader("Subir foto de jornada", type=["jpg", "png"])
        if img:
            with open(os.path.join(FOTOS_DIR, img.name), "wb") as f: f.write(img.getbuffer())
            st.success("Foto guardada en galería")

elif menu == "🔍 Buscador":
    b = st.text_input("Nombre del jugador:")
    if b: st.dataframe(st.session_state.jugadores[st.session_state.jugadores["Nombre"].str.contains(b, case=False)], use_container_width=True)
