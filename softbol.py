import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN Y ESTILOS ---
st.set_page_config(page_title="LIGA DE SOFTBOL DOMINICAL", page_icon="⚾", layout="wide")
st.markdown("<style>th{background-color:#D32F2F!important;color:white!important;text-align:center!important;}.stDataFrame,.stTable{border:2px solid #D32F2F;border-radius:10px;}div.stButton>button:first-child{background-color:#D32F2F;color:white;border-radius:5px;}h1,h2,h3{color:#B71C1C;}</style>",unsafe_allow_html=True)

# --- 2. DIRECTORIOS ---
DATOS_DIR, FOTOS_DIR = "datos_liga", "galeria_liga"
for d in [DATOS_DIR, FOTOS_DIR]:
    if not os.path.exists(d): os.makedirs(d)

def path_archivo(n): return os.path.join(DATOS_DIR, n)

# --- 3. CARGA DE DATOS ---
COLS_J, COLS_P = ["Nombre","Equipo","VB","H","H2","H3","HR"], ["Nombre","Equipo","JG","JP","IP","CL","K"]
COLS_CAL, COLS_ACC = ["Jornada","Fecha","Hora","Campo","Local","Visitante","Score"], ["Equipo","Password"]

def leer_csv(n, cols):
    p = path_archivo(n)
    if os.path.exists(p):
        df = pd.read_csv(p)
        for c in cols:
            if c not in df.columns: df[c] = "" if c in ["Score","Password","Jornada"] else 0
        return df[cols]
    return pd.DataFrame(columns=cols)

# Carga inicial solo si no existe en la sesión para evitar trabas
if 'jugadores' not in st.session_state:
    st.session_state.jugadores = leer_csv("data_jugadores.csv", COLS_J)
    st.session_state.pitchers = leer_csv("data_pitchers.csv", COLS_P)
    st.session_state.equipos = leer_csv("data_equipos.csv", ["Nombre"])
    st.session_state.calendario = leer_csv("data_calendario.csv", COLS_CAL)
    st.session_state.accesos = leer_csv("data_accesos.csv", COLS_ACC)

if 'rol' not in st.session_state: st.session_state.rol = "Invitado"

# --- 4. SIDEBAR (Navegación Unificada) ---
with st.sidebar:
    st.title("🥎 LIGA DOMINICAL")
    if st.session_state.rol == "Invitado":
        with st.form("login"):
            pwd = st.text_input("Clave:", type="password")
            if st.form_submit_button("Entrar"):
                if pwd == "softbol2026": st.session_state.rol = "Admin"; st.rerun()
                elif pwd in st.session_state.accesos["Password"].values:
                    fila = st.session_state.accesos[st.session_state.accesos["Password"]==pwd].iloc[0]
                    st.session_state.rol, st.session_state.eq_gestion = "Delegado", fila["Equipo"]; st.rerun()
                else: st.error("Clave Incorrecta")
    else:
        st.success(f"🔓 {st.session_state.rol}")
        if st.button("Cerrar Sesión"):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()

    opciones = ["🏠 Inicio", "🏆 LÍDERES", "📊 Standings", "📋 Rosters", "🖼️ Galería"]
    if st.session_state.rol == "Admin": opciones.insert(0, "🏃 Admin General")
    menu = st.sidebar.radio("IR A:", opciones)

# --- 5. SECCIONES ---

if menu == "🏃 Admin General" and st.session_state.rol == "Admin":
    st.title("⚙️ Panel de Control")
    t_e, t_b, t_p, t_c = st.tabs(["Equipos", "Bateadores", "Pitchers", "Calendario"])
    
    with t_b:
        sel = st.selectbox("Elegir Jugador:", ["-- Nuevo --"] + sorted(st.session_state.jugadores["Nombre"].tolist()))
        v = ["","",0,0,0,0,0]
        if sel != "-- Nuevo --":
            d = st.session_state.jugadores[st.session_state.jugadores["Nombre"]==sel].iloc[0]
            v = [d["Nombre"],d["Equipo"],int(d["VB"]),int(d["H"]),int(d["H2"]),int(d["H3"]),int(d["HR"])]
        with st.form("fb"):
            nom = st.text_input("Nombre", value=v[0]); eq = st.selectbox("Equipo", st.session_state.equipos["Nombre"].tolist())
            c1,c2,c3,c4,c5 = st.columns(5)
            vb=c1.number_input("VB",value=v[2]); h=c2.number_input("H",value=v[3]); h2=c3.number_input("H2",value=v[4]); h3=c4.number_input("H3",value=v[5]); hr=c5.number_input("HR",value=v[6])
            if st.form_submit_button("Guardar"):
                df = st.session_state.jugadores[st.session_state.jugadores["Nombre"] != sel]
                new_df = pd.concat([df, pd.DataFrame([[nom,eq,vb,h,h2,h3,hr]], columns=COLS_J)], ignore_index=True)
                new_df.to_csv(path_archivo("data_jugadores.csv"), index=False)
                st.session_state.jugadores = new_df; st.success("Guardado"); st.rerun()

    with t_c:
        st.subheader("Editor de Jornadas y Resultados")
        ed_cal = st.data_editor(st.session_state.calendario, num_rows="dynamic", use_container_width=True)
        if st.button("💾 Guardar Todo el Calendario"):
            ed_cal.to_csv(path_archivo("data_calendario.csv"), index=False)
            st.session_state.calendario = ed_cal; st.success("Sincronizado")

elif menu == "🏆 LÍDERES":
    st.title("🥇 Líderes Individuales")
    dfb = st.session_state.jugadores.copy()
    if not dfb.empty:
        dfb['H_T'] = dfb['H'] + dfb['H2'] + dfb['H3'] + dfb['HR']
        dfb['AVG'] = (dfb['H_T'] / dfb['VB'].replace(0, 1)).fillna(0)
        c1, c2 = st.columns(2)
        c1.subheader("⚾ Promedio (AVG)"); c1.table(dfb.sort_values("AVG", ascending=False).head(5)[["Nombre","AVG"]].style.format({"AVG": "{:.3f}"}).highlight_max(color='#FFD700', axis=0))
        c2.subheader("⚡ Hits"); c2.table(dfb.sort_values("H_T", ascending=False).head(5)[["Nombre","H_T"]].style.highlight_max(color='#FFD700', axis=0))
        c3, c4, c5 = st.columns(3)
        c3.subheader("🚀 HR"); c3.table(dfb.sort_values("HR", ascending=False).head(5)[["Nombre","HR"]].style.highlight_max(color='#FFD700', axis=0))
        c4.subheader("🥈 H2"); c4.table(dfb.sort_values("H2", ascending=False).head(5)[["Nombre","H2"]].style.highlight_max(color='#FFD700', axis=0))
        c5.subheader("🥉 H3"); c5.table(dfb.sort_values("H3", ascending=False).head(5)[["Nombre","H3"]].style.highlight_max(color='#FFD700', axis=0))

elif menu == "📊 Standings":
    st.title("📊 Posiciones")
    stats = {eq: {"JJ":0, "JG":0, "JP":0, "JE":0} for eq in st.session_state.equipos["Nombre"]}
    for _, f in st.session_state.calendario.iterrows():
        sc = str(f["Score"]).strip()
        if "-" in sc:
            try:
                sl, sv = map(int, sc.split("-")); l, v = f["Local"], f["Visitante"]
                if l in stats and v in stats:
                    stats[l]["JJ"]+=1; stats[v]["JJ"]+=1
                    if sl > sv: stats[l]["JG"]+=1; stats[v]["JP"]+=1
                    elif sv > sl: stats[v]["JG"]+=1; stats[l]["JP"]+=1
                    else: stats[l]["JE"]+=1; stats[v]["JE"]+=1
            except: continue
    df_s = pd.DataFrame.from_dict(stats, orient='index').reset_index().rename(columns={'index':'Equipo'})
    df_s["AVG"] = (df_s["JG"] / df_s["JJ"].replace(0,1)).fillna(0)
    st.table(df_s.sort_values(["AVG","JG"], ascending=False).style.format({"AVG":"{:.3f}"}).highlight_max(subset=["AVG"], color='#FFD700', axis=0))

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

elif menu == "🏠 Inicio":
    st.title("⚾ LIGA DOMINICAL 2026")
    st.table(st.session_state.calendario)

elif menu == "📋 Rosters":
    eq = st.selectbox("Equipo:", st.session_state.equipos["Nombre"].tolist())
    dfb_eq = st.session_state.jugadores[st.session_state.jugadores["Equipo"] == eq].copy()
    if not dfb_eq.empty:
        dfb_eq['AVG'] = ((dfb_eq['H']+dfb_eq['H2']+dfb_eq['H3']+dfb_eq['HR'])/dfb_eq['VB'].replace(0,1)).fillna(0)
        st.dataframe(dfb_eq.style.format({"AVG":"{:.3f}"}), use_container_width=True, hide_index=True)
