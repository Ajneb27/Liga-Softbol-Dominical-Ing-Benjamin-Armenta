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
COLS_CAL, COLS_ACC = ["Fecha","Hora","Campo","Local","Visitante","Score"], ["Equipo","Password"]

def leer_csv(n, cols):
    p = path_archivo(n)
    if os.path.exists(p):
        try:
            df = pd.read_csv(p)
            df.columns = df.columns.str.strip()
            for c in cols:
                if c not in df.columns: df[c] = "" if c in ["Score","Password"] else 0
            return df[cols]
        except: return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

# Carga de Datos
st.session_state.jugadores = leer_csv("data_jugadores.csv", COLS_J)
st.session_state.pitchers = leer_csv("data_pitchers.csv", COLS_P)
st.session_state.equipos = leer_csv("data_equipos.csv", ["Nombre"])
st.session_state.calendario = leer_csv("data_calendario.csv", COLS_CAL)
st.session_state.accesos = leer_csv("data_accesos.csv", COLS_ACC)

if 'rol' not in st.session_state: st.session_state.rol = "Invitado"

# --- SIDEBAR ---
with st.sidebar:
    st.title("🥎 LIGA DOMINICAL")
    if st.session_state.rol == "Invitado":
        with st.form("login"):
            pwd_in = st.text_input("Clave:", type="password")
            if st.form_submit_button("Entrar"):
                if pwd_in == "softbol2026": st.session_state.rol = "Admin"; st.rerun()
                elif pwd_in in st.session_state.accesos["Password"].values:
                    fila = st.session_state.accesos[st.session_state.accesos["Password"]==pwd_in].iloc[0]
                    st.session_state.rol, st.session_state.eq_gestion = "Delegado", fila["Equipo"]; st.rerun()
                else: st.error("Error")
    else:
        st.success(f"🔓 {st.session_state.rol}")
        if st.button("Salir"): st.session_state.rol = "Invitado"; st.rerun()

menu = st.sidebar.radio("IR A:", ["🏠 Inicio","🏆 LÍDERES","📊 Standings","📋 Rosters","🔍 Buscador","🖼️ Galería"])
if st.session_state.rol == "Admin": menu = st.sidebar.radio("ZONA ADMIN:", ["🏃 Admin General"])

# --- LÍDERES ---
if menu == "🏆 LÍDERES":
    st.title("🥇 Cuadro de Honor")
    t_bateo, t_pitcheo = st.tabs(["🥖 Bateo", "🔥 Pitcheo"])
    with t_bateo:
        dfb = st.session_state.jugadores.copy()
        if not dfb.empty:
            dfb['H_T'] = dfb['H'] + dfb['H2'] + dfb['H3'] + dfb['HR']
            dfb['AVG'] = (dfb['H_T'] / dfb['VB'].replace(0, 1)).fillna(0)
            c1, c2 = st.columns(2)
            c1.subheader("⚾ AVG"); c1.table(dfb.sort_values("AVG", ascending=False).head(5)[["Nombre","AVG"]].style.format({"AVG": "{:.3f}"}).highlight_max(color='#FFD700', axis=0))
            c2.subheader("⚡ Hits"); c2.table(dfb.sort_values("H_T", ascending=False).head(5)[["Nombre","H_T"]].style.highlight_max(color='#FFD700', axis=0))
    with t_pitcheo:
        dfp = st.session_state.pitchers.copy()
        if not dfp.empty:
            dfp['EFE'] = ((dfp['CL'] * 7) / dfp['IP'].replace(0, 1)).fillna(0)
            cp1, cp2 = st.columns(2)
            cp1.subheader("📉 EFE"); cp1.table(dfp[dfp['IP']>0].sort_values("EFE").head(5)[["Nombre","EFE"]].style.format({"EFE": "{:.2f}"}).highlight_min(color='#FFD700', axis=0))
            cp2.subheader("💎 Ganados"); cp2.table(dfp.sort_values("JG", ascending=False).head(5)[["Nombre","JG"]].style.highlight_max(color='#FFD700', axis=0))

# --- ROSTERS (BATEADORES + PITCHERS) ---
elif menu == "📋 Rosters":
    if not st.session_state.equipos.empty:
        eq_sel = st.selectbox("Seleccionar Equipo:", st.session_state.equipos["Nombre"].tolist())
        
        # Bateadores del equipo
        st.subheader(f"🥖 Bateadores - {eq_sel}")
        dfb_eq = st.session_state.jugadores[st.session_state.jugadores["Equipo"] == eq_sel].copy()
        if not dfb_eq.empty:
            dfb_eq['AVG'] = ((dfb_eq['H']+dfb_eq['H2']+dfb_eq['H3']+dfb_eq['HR']) / dfb_eq['VB'].replace(0,1)).fillna(0)
            st.dataframe(dfb_eq[["Nombre","VB","H","H2","H3","HR","AVG"]].style.format({"AVG":"{:.3f}"}).highlight_max(color='#FFD700', subset=["AVG","HR"]), use_container_width=True, hide_index=True)
        else: st.info("No hay bateadores registrados.")

        # Pitchers del equipo
        st.subheader(f"🔥 Pitchers - {eq_sel}")
        dfp_eq = st.session_state.pitchers[st.session_state.pitchers["Equipo"] == eq_sel].copy()
        if not dfp_eq.empty:
            dfp_eq['EFE'] = ((dfp_eq['CL']*7)/dfp_eq['IP'].replace(0,1)).fillna(0)
            st.dataframe(dfp_eq[["Nombre","JG","JP","IP","CL","K","EFE"]].style.format({"EFE":"{:.2f}"}).highlight_max(color='#FFD700', subset=["JG","K"]).highlight_min(color='#FFD700', subset=["EFE"]), use_container_width=True, hide_index=True)
        else: st.info("No hay pitchers registrados.")
    else: st.warning("Cree equipos en la zona Admin primero.")

# --- STANDINGS ---
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

# --- ADMIN GENERAL ---
elif menu == "🏃 Admin General" and st.session_state.rol == "Admin":
    t_e, t_b, t_p, t_c, t_k = st.tabs(["Equipos", "Bateo", "Pitcheo", "Calendario", "🔑 Claves"])
    with t_b:
        sel = st.selectbox("Jugador:", ["-- Nuevo --"] + sorted(st.session_state.jugadores["Nombre"].tolist()))
        v = ["","",0,0,0,0,0]
        if sel != "-- Nuevo --":
            d = st.session_state.jugadores[st.session_state.jugadores["Nombre"]==sel].iloc[0]
            v = [d["Nombre"],d["Equipo"],int(d["VB"]),int(d["H"]),int(d["H2"]),int(d["H3"]),int(d["HR"])]
        with st.form("f_b"):
            nom = st.text_input("Nombre", v[0]); eq = st.selectbox("Equipo", st.session_state.equipos["Nombre"].tolist())
            c1,c2,c3,c4,c5 = st.columns(5)
            vb=c1.number_input("VB",v[2]); h=c2.number_input("H",v[3]); h2=c3.number_input("H2",v[4]); h3=c4.number_input("H3",v[5]); hr=c5.number_input("HR",v[6])
            if st.form_submit_button("Guardar"):
                df = st.session_state.jugadores[st.session_state.jugadores["Nombre"] != sel]
                pd.concat([df, pd.DataFrame([[nom,eq,vb,h,h2,h3,hr]], columns=COLS_J)], ignore_index=True).to_csv(path_archivo("data_jugadores.csv"), index=False); st.rerun()

elif menu == "🏠 Inicio":
    st.markdown("<h1 style='text-align:center;'>⚾ LIGA DOMINICAL</h1>", unsafe_allow_html=True)
    st.table(st.session_state.calendario)
