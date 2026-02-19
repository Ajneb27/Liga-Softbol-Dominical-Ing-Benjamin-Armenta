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

# --- 🏆 SECCIÓN LÍDERES (RESTAURADA) ---
if menu == "🏆 LÍDERES":
    st.title("🥇 Cuadro de Honor 2026")
    t1, t2 = st.tabs(["🥖 Departamentos de Bateo", "🔥 Departamentos de Pitcheo"])
    with t1:
        dfb = st.session_state.jugadores.copy()
        if not dfb.empty:
            dfb['H_T'] = dfb['H'] + dfb['H2'] + dfb['H3'] + dfb['HR']
            dfb['AVG'] = (dfb['H_T'] / dfb['VB'].replace(0, 1)).fillna(0)
            c1, c2 = st.columns(2)
            c1.subheader("⚾ Promedio (AVG)"); c1.table(dfb.sort_values("AVG", ascending=False).head(5)[["Nombre","AVG"]].style.format({"AVG": "{:.3f}"}).highlight_max(color='#FFD700', axis=0))
            c2.subheader("⚡ Hits Totales"); c2.table(dfb.sort_values("H_T", ascending=False).head(5)[["Nombre","H_T"]].style.highlight_max(color='#FFD700', axis=0))
            c3, c4, c5 = st.columns(3)
            c3.subheader("🚀 Jonrones (HR)"); c3.table(dfb.sort_values("HR", ascending=False).head(5)[["Nombre","HR"]].style.highlight_max(color='#FFD700', axis=0))
            c4.subheader("🥈 Dobles (H2)"); c4.table(dfb.sort_values("H2", ascending=False).head(5)[["Nombre","H2"]].style.highlight_max(color='#FFD700', axis=0))
            c5.subheader("🥉 Triples (H3)"); c5.table(dfb.sort_values("H3", ascending=False).head(5)[["Nombre","H3"]].style.highlight_max(color='#FFD700', axis=0))
    with t2:
        dfp = st.session_state.pitchers.copy()
        if not dfp.empty:
            dfp['EFE'] = ((dfp['CL'] * 7) / dfp['IP'].replace(0, 1)).fillna(0)
            cp1, cp2 = st.columns(2)
            cp1.subheader("📉 Efectividad (EFE)"); cp1.table(dfp[dfp['IP']>0].sort_values("EFE").head(5)[["Nombre","EFE"]].style.format({"EFE": "{:.2f}"}).highlight_min(color='#FFD700', axis=0))
            cp2.subheader("💎 Ganados (JG)"); cp2.table(dfp.sort_values("JG", ascending=False).head(5)[["Nombre","JG"]].style.highlight_max(color='#FFD700', axis=0))
            cp3, cp4 = st.columns(2)
            cp3.subheader("🔥 Ponches (K)"); cp3.table(dfp.sort_values("K", ascending=False).head(5)[["Nombre","K"]].style.highlight_max(color='#FFD700', axis=0))
            cp4.subheader("🕒 Innings (IP)"); cp4.table(dfp.sort_values("IP", ascending=False).head(5)[["Nombre","IP"]].style.highlight_max(color='#FFD700', axis=0))

# --- 🏃 ADMIN GENERAL (GESTIÓN TOTAL) ---
elif menu == "🏃 Admin General" and st.session_state.rol == "Admin":
    t_e, t_b, t_p, t_c, t_k = st.tabs(["Equipos", "Bateadores", "Pitchers", "Calendario", "Claves"])
    with t_e:
        st.subheader("Equipos")
        with st.form("ae"):
            ne = st.text_input("Nuevo Equipo:")
            if st.form_submit_button("Agregar"):
                pd.concat([st.session_state.equipos, pd.DataFrame([[ne]], columns=["Nombre"])], ignore_index=True).to_csv(path_archivo("data_equipos.csv"), index=False); st.rerun()
        de = st.selectbox("Eliminar:", ["--"] + st.session_state.equipos["Nombre"].tolist())
        if st.button("Borrar Equipo") and de != "--":
            st.session_state.equipos[st.session_state.equipos["Nombre"] != de].to_csv(path_archivo("data_equipos.csv"), index=False); st.rerun()
    with t_b:
        sel = st.selectbox("Jugador:", ["-- Nuevo --"] + sorted(st.session_state.jugadores["Nombre"].tolist()), key="admin_b")
        v = ["","",0,0,0,0,0]
        if sel != "-- Nuevo --":
            d = st.session_state.jugadores[st.session_state.jugadores["Nombre"]==sel].iloc[0]
            v = [d["Nombre"],d["Equipo"],int(d["VB"]),int(d["H"]),int(d["H2"]),int(d["H3"]),int(d["HR"])]
        with st.form("fb"):
            nom = st.text_input("Nombre", value=v[0]); eq = st.selectbox("Equipo", st.session_state.equipos["Nombre"].tolist())
            c1,c2,c3,c4,c5 = st.columns(5)
            vb=c1.number_input("VB",v[2]); h=c2.number_input("H",v[3]); h2=c3.number_input("H2",v[4]); h3=c4.number_input("H3",v[5]); hr=c5.number_input("HR",v[6])
            if st.form_submit_button("Guardar"):
                df = st.session_state.jugadores[st.session_state.jugadores["Nombre"] != sel]
                pd.concat([df, pd.DataFrame([[nom,eq,vb,h,h2,h3,hr]], columns=COLS_J)], ignore_index=True).to_csv(path_archivo("data_jugadores.csv"), index=False); st.rerun()
        if sel != "-- Nuevo --" and st.button("Eliminar Bateador"):
            st.session_state.jugadores[st.session_state.jugadores["Nombre"] != sel].to_csv(path_archivo("data_jugadores.csv"), index=False); st.rerun()
    with t_p:
        selp = st.selectbox("Pitcher:", ["-- Nuevo --"] + sorted(st.session_state.pitchers["Nombre"].tolist()))
        vp = ["","",0,0,0,0,0]
        if selp != "-- Nuevo --":
            dp = st.session_state.pitchers[st.session_state.pitchers["Nombre"]==selp].iloc[0]
            vp = [dp["Nombre"],dp["Equipo"],int(dp["JG"]),int(dp["JP"]),int(dp["IP"]),int(dp["CL"]),int(dp["K"])]
        with st.form("fp"):
            nomp = st.text_input("Nombre", value=vp[0]); eqp = st.selectbox("Equipo", st.session_state.equipos["Nombre"].tolist(), key="eqp")
            c1,c2,c3,c4,c5 = st.columns(5)
            jg=c1.number_input("JG",vp[2]); jp=c2.number_input("JP",vp[3]); ip=c3.number_input("IP",vp[4]); cl=c4.number_input("CL",vp[5]); k=c5.number_input("K",vp[6])
            if st.form_submit_button("Guardar Pitcher"):
                dfp = st.session_state.pitchers[st.session_state.pitchers["Nombre"] != selp]
                pd.concat([dfp, pd.DataFrame([[nomp,eqp,jg,jp,ip,cl,k]], columns=COLS_P)], ignore_index=True).to_csv(path_archivo("data_pitchers.csv"), index=False); st.rerun()
        if selp != "-- Nuevo --" and st.button("Eliminar Pitcher"):
            st.session_state.pitchers[st.session_state.pitchers["Nombre"] != selp].to_csv(path_archivo("data_pitchers.csv"), index=False); st.rerun()

# --- 📊 STANDINGS ---
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

# --- 📋 ROSTERS ---
elif menu == "📋 Rosters":
    if not st.session_state.equipos.empty:
        eq_sel = st.selectbox("Equipo:", st.session_state.equipos["Nombre"].tolist())
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Bateadores")
            dfb_eq = st.session_state.jugadores[st.session_state.jugadores["Equipo"] == eq_sel].copy()
            if not dfb_eq.empty:
                dfb_eq['AVG'] = ((dfb_eq['H']+dfb_eq['H2']+dfb_eq['H3']+dfb_eq['HR']) / dfb_eq['VB'].replace(0,1)).fillna(0)
                st.dataframe(dfb_eq.style.format({"AVG":"{:.3f}"}).highlight_max(color='#FFD700', subset=["AVG"]), use_container_width=True, hide_index=True)
        with c2:
            st.subheader("Pitchers")
            dfp_eq = st.session_state.pitchers[st.session_state.pitchers["Equipo"] == eq_sel].copy()
            if not dfp_eq.empty:
                dfp_eq['EFE'] = ((dfp_eq['CL']*7)/dfp_eq['IP'].replace(0,1)).fillna(0)
                st.dataframe(dfp_eq.style.format({"EFE":"{:.2f}"}).highlight_max(color='#FFD700', subset=["JG"]), use_container_width=True, hide_index=True)

elif menu == "🏠 Inicio":
    st.markdown("<h1 style='text-align:center;'>⚾ LIGA DOMINICAL 2026</h1>", unsafe_allow_html=True)
    st.table(st.session_state.calendario)
