import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN Y ESTILOS ---
st.set_page_config(page_title="LIGA DE SOFTBOL DOMINICAL", page_icon="⚾", layout="wide")
st.markdown("<style>th{background-color:#D32F2F!important;color:white!important;text-align:center!important;}.stDataFrame,.stTable{border:2px solid #D32F2F;border-radius:10px;}div.stButton>button:first-child{background-color:#D32F2F;color:white;border-radius:5px;}h1,h2,h3{color:#B71C1C;}</style>",unsafe_allow_html=True)

# --- 2. DIRECTORIOS Y DATOS ---
DATOS_DIR, FOTOS_DIR = "datos_liga", "galeria_liga"
for d in [DATOS_DIR, FOTOS_DIR]:
    if not os.path.exists(d): os.makedirs(d)

def path_archivo(n): return os.path.join(DATOS_DIR, n)

COLS_J, COLS_P = ["Nombre","Equipo","VB","H","H2","H3","HR"], ["Nombre","Equipo","JG","JP","IP","CL","K"]
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

# Carga de datos
st.session_state.jugadores = leer_csv("data_jugadores.csv", COLS_J)
st.session_state.pitchers = leer_csv("data_pitchers.csv", COLS_P)
st.session_state.equipos = leer_csv("data_equipos.csv", ["Nombre"])
st.session_state.calendario = leer_csv("data_calendario.csv", COLS_CAL)
st.session_state.accesos = leer_csv("data_accesos.csv", COLS_ACC)

if 'rol' not in st.session_state: st.session_state.rol = "Invitado"

# --- 3. SIDEBAR Y LOGIN ---
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
                else: st.error("Clave Incorrecta")
    else:
        st.success(f"🔓 {st.session_state.rol}")
        if st.button("Cerrar Sesión"): st.session_state.rol = "Invitado"; st.rerun()

menu = st.sidebar.radio("IR A:", ["🏠 Inicio","🏆 LÍDERES","📊 Standings","📋 Rosters","🔍 Buscador","🖼️ Galería"])
if st.session_state.rol == "Admin": menu = st.sidebar.radio("ZONA ADMIN:", ["🏃 Admin General"])

# --- 4. SECCIONES ---

if menu == "🏠 Inicio":
    st.markdown("<h1 style='text-align:center;'>⚾ LIGA DE SOFTBOL DOMINICAL ⚾</h1>", unsafe_allow_html=True)
    st.subheader("📅 Calendario de Juegos")
    st.table(st.session_state.calendario)

elif menu == "🏆 LÍDERES":
    t1, t2 = st.tabs(["🥖 Bateo", "🔥 Pitcheo"])
    with t1:
        df = st.session_state.jugadores.copy()
        if not df.empty:
            df['H_T'] = df['H']+df['H2']+df['H3']+df['HR']
            df['AVG'] = (df['H_T']/df['VB'].replace(0,1)).fillna(0)
            c1, c2 = st.columns(2)
            c1.subheader("🥇 Promedio (AVG)"); c1.table(df.sort_values("AVG", ascending=False).head(5)[["Nombre","AVG"]].style.format({"AVG":"{:.3f}"}))
            c2.subheader("🥇 Jonrones (HR)"); c2.table(df.sort_values("HR", ascending=False).head(5)[["Nombre","HR"]])
    with t2:
        dfp = st.session_state.pitchers.copy()
        if not dfp.empty:
            dfp['EFE'] = ((dfp['CL']*7)/dfp['IP'].replace(0,1)).fillna(0)
            cp1, cp2 = st.columns(2)
            cp1.subheader("🥇 Ganados"); cp1.table(dfp.sort_values("JG", ascending=False).head(5)[["Nombre","JG"]])
            cp2.subheader("🥇 EFE"); cp2.table(dfp[dfp['IP']>0].sort_values("EFE").head(5)[["Nombre","EFE"]].style.format({"EFE":"{:.2f}"}))

elif menu == "📊 Standings":
    st.title("📊 Tabla de Posiciones")
    st.info("Nota: Los resultados se calculan del Calendario (formato Score: '10-5')")
    stats = {eq: {"JJ":0, "JG":0, "JP":0, "JE":0} for eq in st.session_state.equipos["Nombre"]}
    for _, f in st.session_state.calendario.iterrows():
        sc = str(f["Score"]).strip()
        if "-" in sc:
            try:
                sl, sv = map(int, sc.split("-"))
                l, v = f["Local"], f["Visitante"]
                if l in stats and v in stats:
                    stats[l]["JJ"]+=1; stats[v]["JJ"]+=1
                    if sl > sv: stats[l]["JG"]+=1; stats[v]["JP"]+=1
                    elif sv > sl: stats[v]["JG"]+=1; stats[l]["JP"]+=1
                    else: stats[l]["JE"]+=1; stats[v]["JE"]+=1
            except: continue
    df_s = pd.DataFrame.from_dict(stats, orient='index').reset_index().rename(columns={'index':'Equipo'})
    df_s["AVG"] = (df_s["JG"] / df_s["JJ"].replace(0,1)).fillna(0)
    st.table(df_s.sort_values(["AVG","JG"], ascending=False).style.format({"AVG":"{:.3f}"}))

elif menu == "🏃 Admin General":
    tab_e, tab_b, tab_p, tab_c, tab_k = st.tabs(["Equipos", "Bateo", "Pitcheo", "Calendario", "🔑 Claves"])
    with tab_b:
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
    with tab_k:
        with st.form("f_k"):
            eq_k, pk = st.selectbox("Equipo:", st.session_state.equipos["Nombre"].tolist()), st.text_input("Clave:")
            if st.form_submit_button("🔒 Asignar"):
                df = st.session_state.accesos[st.session_state.accesos["Equipo"] != eq_k]
                pd.concat([df, pd.DataFrame([[eq_k,pk]], columns=COLS_ACC)], ignore_index=True).to_csv(path_archivo("data_accesos.csv"), index=False); st.rerun()
        st.table(st.session_state.accesos)

elif menu == "📋 Rosters":
    eq = st.selectbox("Equipo:", st.session_state.equipos["Nombre"].tolist())
    st.dataframe(st.session_state.jugadores[st.session_state.jugadores["Equipo"]==eq], use_container_width=True, hide_index=True)

elif menu == "🖼️ Galería":
    st.subheader("📸 Fotos"); fotos = os.listdir(FOTOS_DIR)
    cols = st.columns(3)
    for i, f in enumerate(fotos):
        with cols[i%3]: st.image(os.path.join(FOTOS_DIR, f))

