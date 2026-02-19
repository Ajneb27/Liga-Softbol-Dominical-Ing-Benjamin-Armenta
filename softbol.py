import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="LIGA DE SOFTBOL DOMINICAL", page_icon="⚾", layout="wide")
st.markdown("<style>th{background-color:#D32F2F!important;color:white!important;text-align:center!important;}.stDataFrame,.stTable{border:2px solid #D32F2F;border-radius:10px;}div.stButton>button:first-child{background-color:#D32F2F;color:white;border-radius:5px;}h1,h2,h3{color:#B71C1C;}</style>",unsafe_allow_html=True)

DATOS_DIR, FOTOS_DIR = "datos_liga", "galeria_liga"
for d in [DATOS_DIR, FOTOS_DIR]:
    if not os.path.exists(d): os.makedirs(d)

def path_archivo(n): return os.path.join(DATOS_DIR, n)

COLS_J = ["Nombre","Equipo","VB","H","H2","H3","HR"]
COLS_P = ["Nombre","Equipo","JG","JP","IP","CL","K"]
COLS_CAL = ["Jornada","Fecha","Hora","Campo","Local","Visitante","Score"]
COLS_ACC = ["Equipo","Password"]

def leer_csv(n, cols):
    p = path_archivo(n)
    if os.path.exists(p):
        try:
            df = pd.read_csv(p)
            df.columns = df.columns.str.strip()
            for c in cols:
                if c not in df.columns: df[c] = "" if c in ["Score","Password","Jornada"] else 0
            return df[cols]
        except: return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

# Carga de Datos en session_state
st.session_state.jugadores = leer_csv("data_jugadores.csv", COLS_J)
st.session_state.pitchers = leer_csv("data_pitchers.csv", COLS_P)
st.session_state.equipos = leer_csv("data_equipos.csv", ["Nombre"])
st.session_state.calendario = leer_csv("data_calendario.csv", COLS_CAL)
st.session_state.accesos = leer_csv("data_accesos.csv", COLS_ACC)

if 'rol' not in st.session_state: st.session_state.rol = "Invitado"
if 'eq_gestion' not in st.session_state: st.session_state.eq_gestion = None

# --- SIDEBAR Y LOGIN ---
with st.sidebar:
    st.title("🥎 LIGA DOMINICAL")
    if st.session_state.rol == "Invitado":
        with st.form("login"):
            pwd_in = st.text_input("Clave de Acceso:", type="password")
            if st.form_submit_button("Entrar"):
                if pwd_in == "softbol2026": 
                    st.session_state.rol = "Admin"; st.rerun()
                elif pwd_in in st.session_state.accesos["Password"].values:
                    fila = st.session_state.accesos[st.session_state.accesos["Password"]==pwd_in].iloc[0]
                    st.session_state.rol, st.session_state.eq_gestion = "Delegado", fila["Equipo"]
                    st.rerun()
                else: st.error("Clave Incorrecta")
    else:
        st.success(f"🔓 Sesión: {st.session_state.rol}")
        if st.button("Cerrar Sesión"):
            st.session_state.rol = "Invitado"; st.session_state.eq_gestion = None; st.rerun()

# --- MENÚ UNIFICADO ---
opciones = ["🏠 Inicio", "🏆 LÍDERES", "📊 Standings", "📋 Rosters", "🖼️ Galería"]
if st.session_state.rol == "Admin":
    opciones.insert(0, "🏃 Admin General")
elif st.session_state.rol == "Delegado":
    opciones.insert(0, "📋 Mi Equipo (Delegado)")

menu = st.sidebar.radio("IR A:", opciones)

# --- 1. ZONA ADMIN GENERAL ---
if menu == "🏃 Admin General" and st.session_state.rol == "Admin":
    t_e, t_b, t_p, t_c, t_k = st.tabs(["Equipos", "Bateadores", "Pitchers", "Calendario", "Claves"])
    
    with t_e:
        with st.form("ae"):
            ne = st.text_input("Nuevo Equipo:"); st.form_submit_button("Agregar") and pd.concat([st.session_state.equipos, pd.DataFrame([[ne]], columns=["Nombre"])], ignore_index=True).to_csv(path_archivo("data_equipos.csv"), index=False) or st.rerun()
        de = st.selectbox("Borrar Equipo:", ["--"] + st.session_state.equipos["Nombre"].tolist())
        if st.button("Eliminar") and de != "--": st.session_state.equipos[st.session_state.equipos["Nombre"] != de].to_csv(path_archivo("data_equipos.csv"), index=False); st.rerun()

    with t_b:
        sel = st.selectbox("Jugador:", ["-- Nuevo --"] + sorted(st.session_state.jugadores["Nombre"].tolist()))
        v = ["","",0,0,0,0,0]
        if sel != "-- Nuevo --":
            d = st.session_state.jugadores[st.session_state.jugadores["Nombre"]==sel].iloc[0]
            v = [d["Nombre"],d["Equipo"],int(d["VB"]),int(d["H"]),int(d["H2"]),int(d["H3"]),int(d["HR"])]
        with st.form("fb"):
            nom = st.text_input("Nombre", v[0]); eq = st.selectbox("Equipo", st.session_state.equipos["Nombre"].tolist())
            c1,c2,c3,c4,c5 = st.columns(5)
            vb=c1.number_input("VB",v[2]); h=c2.number_input("H",v[3]); h2=c3.number_input("H2",v[4]); h3=c4.number_input("H3",v[5]); hr=c5.number_input("HR",v[6])
            if st.form_submit_button("Guardar"):
                df = st.session_state.jugadores[st.session_state.jugadores["Nombre"] != sel]
                pd.concat([df, pd.DataFrame([[nom,eq,vb,h,h2,h3,hr]], columns=COLS_J)], ignore_index=True).to_csv(path_archivo("data_jugadores.csv"), index=False); st.rerun()

    with t_c:
        ed_cal = st.data_editor(st.session_state.calendario, num_rows="dynamic", use_container_width=True)
        if st.button("Guardar Cambios Calendario"): ed_cal.to_csv(path_archivo("data_calendario.csv"), index=False); st.rerun()

# --- 2. LÍDERES ---
elif menu == "🏆 LÍDERES":
    t1, t2 = st.tabs(["🥖 Bateo", "🔥 Pitcheo"])
    with t1:
        dfb = st.session_state.jugadores.copy()
        if not dfb.empty:
            dfb['H_T'] = dfb['H'] + dfb['H2'] + dfb['H3'] + dfb['HR']
            dfb['AVG'] = (dfb['H_T'] / dfb['VB'].replace(0, 1)).fillna(0)
            c1, c2 = st.columns(2)
            c1.subheader("⚾ AVG"); c1.table(dfb.sort_values("AVG", ascending=False).head(5)[["Nombre","AVG"]].style.format({"AVG": "{:.3f}"}).highlight_max(color='#FFD700', axis=0))
            c2.subheader("⚡ Hits"); c2.table(dfb.sort_values("H_T", ascending=False).head(5)[["Nombre","H_T"]].style.highlight_max(color='#FFD700', axis=0))
            c3, c4, c5 = st.columns(3)
            c3.subheader("🚀 HR"); c3.table(dfb.sort_values("HR", ascending=False).head(5)[["Nombre","HR"]].style.highlight_max(color='#FFD700', axis=0))
            c4.subheader("🥈 H2"); c4.table(dfb.sort_values("H2", ascending=False).head(5)[["Nombre","H2"]].style.highlight_max(color='#FFD700', axis=0))
            c5.subheader("🥉 H3"); c5.table(dfb.sort_values("H3", ascending=False).head(5)[["Nombre","H3"]].style.highlight_max(color='#FFD700', axis=0))

    with t2:
        dfp = st.session_state.pitchers.copy()
        if not dfp.empty:
            dfp['EFE'] = ((dfp['CL'] * 7) / dfp['IP'].replace(0, 1)).fillna(0)
            cp1, cp2 = st.columns(2)
            cp1.subheader("📉 EFE"); cp1.table(dfp[dfp['IP']>0].sort_values("EFE").head(5)[["Nombre","EFE"]].style.format({"EFE": "{:.2f}"}).highlight_min(color='#FFD700', axis=0))
            cp2.subheader("💎 JG"); cp2.table(dfp.sort_values("JG", ascending=False).head(5)[["Nombre","JG"]].style.highlight_max(color='#FFD700', axis=0))

# --- 3. STANDINGS ---
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

# --- 4. GALERÍA (CON SUBIDA DE FOTOS) ---
elif menu == "🖼️ Galería":
    st.title("📸 Galería")
    if st.session_state.rol == "Admin":
        with st.expander("⬆️ SUBIR FOTO"):
            archivo = st.file_uploader("Imagen:", type=['png', 'jpg', 'jpeg'])
            if st.button("Guardar") and archivo:
                with open(os.path.join(FOTOS_DIR, archivo.name), "wb") as f: f.write(archivo.getbuffer())
                st.success("Subida"); st.rerun()
    fotos = os.listdir(FOTOS_DIR)
    cols = st.columns(3)
    for i, f in enumerate(fotos):
        with cols[i%3]: st.image(os.path.join(FOTOS_DIR, f))

# --- 5. INICIO Y ROSTERS ---
elif menu == "🏠 Inicio":
    st.markdown("<h1 style='text-align:center;'>⚾ LIGA DOMINICAL 2026</h1>", unsafe_allow_html=True)
    st.subheader("📅 Calendario")
    st.dataframe(st.session_state.calendario, use_container_width=True, hide_index=True)

elif menu == "📋 Rosters":
    eq_sel = st.selectbox("Equipo:", st.session_state.equipos["Nombre"].tolist())
    st.subheader("🥖 Bateadores")
    dfb_eq = st.session_state.jugadores[st.session_state.jugadores["Equipo"] == eq_sel].copy()
    if not dfb_eq.empty:
        dfb_eq['AVG'] = ((dfb_eq['H']+dfb_eq['H2']+dfb_eq['H3']+dfb_eq['HR']) / dfb_eq['VB'].replace(0,1)).fillna(0)
        st.dataframe(dfb_eq.style.format({"AVG":"{:.3f}"}).highlight_max(color='#FFD700', subset=["AVG"]), use_container_width=True, hide_index=True)
    st.subheader("🔥 Pitchers")
    dfp_eq = st.session_state.pitchers[st.session_state.pitchers["Equipo"] == eq_sel].copy()
    if not dfp_eq.empty:
        st.dataframe(dfp_eq, use_container_width=True, hide_index=True)
