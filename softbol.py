import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="LIGA SOFTBOL", page_icon="⚾", layout="wide")
st.markdown("<style>th{background-color:#D32F2F!important;color:white!important;}h1,h2{color:#B71C1C;}</style>", unsafe_allow_html=True)

DATOS_DIR, FOTOS_DIR = "datos_liga", "galeria_liga"
for d in [DATOS_DIR, FOTOS_DIR]:
    if not os.path.exists(d): os.makedirs(d)

def path_archivo(n): return os.path.join(DATOS_DIR, n)

COLS_J = ["Nombre","Equipo","VB","H","H2","H3","HR"]
COLS_P = ["Nombre","Equipo","JG","JP","IP","CL","K"]
COLS_CAL = ["Jornada","Fecha","Hora","Campo","Local","Visitante","Score"]
COLS_ACC = ["Equipo","Password"]

@st.cache_data
def leer_datos(n, cols):
    p = path_archivo(n)
    if os.path.exists(p):
        df = pd.read_csv(p)
        df.columns = df.columns.str.strip()
        for c in cols:
            if c not in df.columns: df[c] = "" if c in ["Score","Password","Jornada"] else 0
        return df[cols]
    return pd.DataFrame(columns=cols)

# Inicializar sesión una sola vez
if 'rol' not in st.session_state:
    st.session_state.rol = "Invitado"
    st.session_state.jugadores = leer_datos("data_jugadores.csv", COLS_J)
    st.session_state.pitchers = leer_datos("data_pitchers.csv", COLS_P)
    st.session_state.equipos = leer_datos("data_equipos.csv", ["Nombre"])
    st.session_state.calendario = leer_datos("data_calendario.csv", COLS_CAL)
    st.session_state.accesos = leer_csv_acc = leer_datos("data_accesos.csv", COLS_ACC)

# --- 2. LOGIN Y SALIDA ---
with st.sidebar:
    st.title("🥎 LIGA DOMINICAL")
    if st.session_state.rol == "Invitado":
        with st.form("login"):
            pwd = st.text_input("Clave:", type="password")
            if st.form_submit_button("ENTRAR"):
                if pwd == "softbol2026": st.session_state.rol = "Admin"; st.rerun()
                elif pwd in st.session_state.accesos["Password"].values:
                    fila = st.session_state.accesos[st.session_state.accesos["Password"]==pwd].iloc[0]
                    st.session_state.rol, st.session_state.eq_gestion = "Delegado", fila["Equipo"]; st.rerun()
                else: st.error("Clave Incorrecta")
    else:
        st.success(f"🔓 {st.session_state.rol}")
        if st.button("CERRAR SESIÓN"):
            st.cache_data.clear()
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()

    opciones = ["🏠 Inicio", "🏆 LÍDERES", "📊 Standings", "📋 Rosters", "🖼️ Galería"]
    if st.session_state.rol == "Admin": opciones.insert(0, "🏃 Admin General")
    menu = st.radio("IR A:", opciones)

# --- 3. SECCIONES ---

if menu == "🏃 Admin General":
    st.title("⚙️ Administración")
    tab1, tab2 = st.tabs(["Bateadores", "Calendario"])
    with tab1:
        sel = st.selectbox("Jugador:", ["-- Nuevo --"] + sorted(st.session_state.jugadores["Nombre"].tolist()))
        dn, de, dvb, dh, dh2, dh3, dhr = "", "", 0, 0, 0, 0, 0
        if sel != "-- Nuevo --":
            d = st.session_state.jugadores[st.session_state.jugadores["Nombre"] == sel].iloc[0]
            dn, de, dvb, dh, dh2, dh3, dhr = d["Nombre"], d["Equipo"], int(d["VB"]), int(d["H"]), int(d["H2"]), int(d["H3"]), int(d["HR"])
        with st.form("f_bat"):
            n_nom = st.text_input("Nombre", value=dn)
            n_eq = st.selectbox("Equipo", st.session_state.equipos["Nombre"].tolist())
            c1,c2,c3,c4,c5 = st.columns(5)
            n_vb, n_h = c1.number_input("VB", value=dvb), c2.number_input("H", value=dh)
            n_h2, n_h3, n_hr = c3.number_input("H2", value=dh2), c4.number_input("H3", value=dh3), c5.number_input("HR", value=dhr)
            if st.form_submit_button("Guardar"):
                df_r = st.session_state.jugadores[st.session_state.jugadores["Nombre"] != sel]
                nuevo = pd.DataFrame([[n_nom, n_eq, n_vb, n_h, n_h2, n_h3, n_hr]], columns=COLS_J)
                res = pd.concat([df_r, nuevo], ignore_index=True)
                res.to_csv(path_archivo("data_jugadores.csv"), index=False)
                st.session_state.jugadores = res; st.cache_data.clear(); st.success("Guardado"); st.rerun()

elif menu == "🏆 LÍDERES":
    st.title("🥇 Cuadro de Honor")
    df = st.session_state.jugadores.copy()
    if not df.empty:
        df['H_T'] = df['H'] + df['H2'] + df['H3'] + df['HR']
        df['AVG'] = (df['H_T'] / df['VB'].replace(0, 1)).fillna(0)
        c1, c2 = st.columns(2)
        c1.subheader("⚾ AVG"); c1.table(df.sort_values("AVG", ascending=False).head(5)[["Nombre","AVG"]].style.format({"AVG": "{:.3f}"}).highlight_max(color='#FFD700', axis=0))
        c2.subheader("⚡ Hits"); c2.table(df.sort_values("H_T", ascending=False).head(5)[["Nombre","H_T"]].style.highlight_max(color='#FFD700', axis=0))
        c3, c4, c5 = st.columns(3)
        c3.subheader("🚀 HR"); c3.table(df.sort_values("HR", ascending=False).head(5)[["Nombre","HR"]].style.highlight_max(color='#FFD700', axis=0))
        c4.subheader("🥈 H2"); c4.table(df.sort_values("H2", ascending=False).head(5)[["Nombre","H2"]].style.highlight_max(color='#FFD700', axis=0))
        c5.subheader("🥉 H3"); c5.table(df.sort_values("H3", ascending=False).head(5)[["Nombre","H3"]].style.highlight_max(color='#FFD700', axis=0))

elif menu == "📋 Rosters":
    st.title("📋 Rosters por Equipo")
    if not st.session_state.equipos.empty:
        eq = st.selectbox("Seleccionar Equipo:", st.session_state.equipos["Nombre"].tolist())
        
        # Bateadores
        st.subheader(f"🥖 Bateadores - {eq}")
        db = st.session_state.jugadores[st.session_state.jugadores["Equipo"] == eq].copy()
        if not db.empty:
            db['AVG'] = ((db['H']+db['H2']+db['H3']+db['HR'])/db['VB'].replace(0,1)).fillna(0)
            st.dataframe(db[["Nombre","VB","H","H2","H3","HR","AVG"]].style.format({"AVG":"{:.3f}"}).highlight_max(color='#FFD700', subset=["AVG"]), use_container_width=True, hide_index=True)
        
        # Pitchers
        st.subheader(f"🔥 Pitchers - {eq}")
        dp = st.session_state.pitchers[st.session_state.pitchers["Equipo"] == eq].copy()
        if not dp.empty:
            st.dataframe(dp, use_container_width=True, hide_index=True)
    else: st.warning("No hay equipos registrados.")

elif menu == "📊 Standings":
    st.title("📊 Posiciones")
    stats = {eq: {"JJ":0, "JG":0, "JP":0} for eq in st.session_state.equipos["Nombre"]}
    for _, f in st.session_state.calendario.iterrows():
        sc = str(f["Score"]).strip()
        if "-" in sc:
            try:
                sl, sv = map(int, sc.split("-")); l, v = f["Local"], f["Visitante"]
                if l in stats and v in stats:
                    stats[l]["JJ"]+=1; stats[v]["JJ"]+=1
                    if sl > sv: stats[l]["JG"]+=1; stats[v]["JP"]+=1
                    elif sv > sl: stats[v]["JG"]+=1; stats[l]["JP"]+=1
            except: continue
    df_s = pd.DataFrame.from_dict(stats, orient='index').reset_index().rename(columns={'index':'Equipo'})
    df_s["AVG"] = (df_s["JG"] / df_s["JJ"].replace(0,1)).fillna(0)
    st.table(df_s.sort_values(["AVG","JG"], ascending=False).style.format({"AVG":"{:.3f}"}).highlight_max(subset=["AVG"], color='#FFD700', axis=0))

elif menu == "🏠 Inicio":
    st.title("⚾ LIGA DOMINICAL 2026")
    st.table(st.session_state.calendario)
