import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="LIGA SOFTBOL", page_icon="⚾", layout="wide")

# Estilos rápidos
st.markdown("<style>th{background-color:#D32F2F!important;color:white!important;}h1,h2{color:#B71C1C;}</style>", unsafe_allow_html=True)

DATOS_DIR, FOTOS_DIR = "datos_liga", "galeria_liga"
for d in [DATOS_DIR, FOTOS_DIR]:
    if not os.path.exists(d): os.makedirs(d)

def path_archivo(n): return os.path.join(DATOS_DIR, n)

# --- 2. CARGA DE DATOS (SOLO UNA VEZ) ---
COLS_J, COLS_P = ["Nombre","Equipo","VB","H","H2","H3","HR"], ["Nombre","Equipo","JG","JP","IP","CL","K"]
COLS_CAL = ["Jornada","Fecha","Hora","Campo","Local","Visitante","Score"]
COLS_ACC = ["Equipo","Password"]

@st.cache_data
def leer_datos(n, cols):
    p = path_archivo(n)
    if os.path.exists(p):
        df = pd.read_csv(p)
        for c in cols:
            if c not in df.columns: df[c] = "" if c in ["Score","Password","Jornada"] else 0
        return df[cols]
    return pd.DataFrame(columns=cols)

# Inicializar sesión
if 'rol' not in st.session_state:
    st.session_state.rol = "Invitado"
    st.session_state.jugadores = leer_datos("data_jugadores.csv", COLS_J)
    st.session_state.pitchers = leer_datos("data_pitchers.csv", COLS_P)
    st.session_state.equipos = leer_datos("data_equipos.csv", ["Nombre"])
    st.session_state.calendario = leer_datos("data_calendario.csv", COLS_CAL)
    st.session_state.accesos = leer_datos("data_accesos.csv", COLS_ACC)

# --- 3. LOGIN Y SALIDA ---
with st.sidebar:
    st.title("🥎 LIGA DOMINICAL")
    if st.session_state.rol == "Invitado":
        with st.form("login"):
            pwd = st.text_input("Clave:", type="password")
            if st.form_submit_button("ENTRAR"):
                if pwd == "softbol2026": 
                    st.session_state.rol = "Admin"
                    st.rerun()
                elif pwd in st.session_state.accesos["Password"].values:
                    fila = st.session_state.accesos[st.session_state.accesos["Password"]==pwd].iloc[0]
                    st.session_state.rol, st.session_state.eq_gestion = "Delegado", fila["Equipo"]
                    st.rerun()
                else: st.error("Clave Incorrecta")
    else:
        st.success(f"🔓 {st.session_state.rol}")
        if st.button("CERRAR SESIÓN"):
            st.cache_data.clear() # Limpia basura
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()

    # Navegación
    opciones = ["🏠 Inicio", "🏆 LÍDERES", "📊 Standings", "📋 Rosters", "🖼️ Galería"]
    if st.session_state.rol == "Admin": opciones.insert(0, "🏃 Admin General")
    menu = st.radio("IR A:", opciones)

# --- 4. FUNCIONES DE GUARDADO ---
def guardar(df, nombre, key_ss):
    df.to_csv(path_archivo(nombre), index=False)
    st.session_state[key_ss] = df
    st.cache_data.clear()

# --- 5. SECCIONES ---
if menu == "🏃 Admin General" and st.session_state.rol == "Admin":
    st.title("⚙️ Administración")
    tab1, tab2, tab3 = st.tabs(["Bateadores", "Calendario", "Equipos"])
    
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
                guardar(pd.concat([df_r, nuevo], ignore_index=True), "data_jugadores.csv", "jugadores")
                st.success("Sincronizado"); st.rerun()

    with tab2:
        ed_cal = st.data_editor(st.session_state.calendario, num_rows="dynamic", use_container_width=True)
        if st.button("Guardar Calendario"):
            guardar(ed_cal, "data_calendario.csv", "calendario")
            st.success("Calendario Guardado")

elif menu == "🏆 LÍDERES":
    st.title("🥇 Líderes")
    df = st.session_state.jugadores.copy()
    if not df.empty:
        df['H_T'] = df['H'] + df['H2'] + df['H3'] + df['HR']
        df['AVG'] = (df['H_T'] / df['VB'].replace(0, 1)).fillna(0)
        c1, c2 = st.columns(2)
        c1.subheader("⚾ AVG"); c1.table(df.sort_values("AVG", ascending=False).head(5)[["Nombre","AVG"]].style.format({"AVG": "{:.3f}"}).highlight_max(color='#FFD700', axis=0))
        c2.subheader("🚀 Jonrones"); c2.table(df.sort_values("HR", ascending=False).head(5)[["Nombre","HR"]].style.highlight_max(color='#FFD700', axis=0))
        st.subheader("⚡ Hits Totales"); st.table(df.sort_values("H_T", ascending=False).head(5)[["Nombre","H_T"]].style.highlight_max(color='#FFD700', axis=0))

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
    st.title("⚾ LIGA DOMINICAL")
    st.dataframe(st.session_state.calendario, use_container_width=True, hide_index=True)

elif menu == "🖼️ Galería":
    st.title("📸 Galería")
    if st.session_state.rol == "Admin":
        arch = st.file_uploader("Subir foto:", type=['jpg','png','jpeg'])
        if arch and st.button("Guardar Foto"):
            with open(os.path.join(FOTOS_DIR, arch.name), "wb") as f: f.write(arch.getbuffer())
            st.rerun()
    fotos = os.listdir(FOTOS_DIR)
    cols = st.columns(3)
    for i, f in enumerate(fotos):
        with cols[i%3]: st.image(os.path.join(FOTOS_DIR, f))
