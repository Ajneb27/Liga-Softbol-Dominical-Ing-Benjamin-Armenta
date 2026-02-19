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

# --- 2. CARGA DE DATOS SIN CACHÉ ---
def leer_datos(n, cols):
    p = path_archivo(n)
    if os.path.exists(p):
        df = pd.read_csv(p)
        df.columns = df.columns.str.strip()
        for col in df.select_dtypes(['object']).columns:
            df[col] = df[col].astype(str).str.strip()
        for c in cols:
            if c not in df.columns: df[c] = "" if c in ["Score","Password","Jornada"] else 0
        return df[cols]
    return pd.DataFrame(columns=cols)

# Recarga constante para evitar datos fantasmas
st.session_state.jugadores = leer_datos("data_jugadores.csv", COLS_J)
st.session_state.pitchers = leer_datos("data_pitchers.csv", COLS_P)
st.session_state.equipos = leer_datos("data_equipos.csv", ["Nombre"])
st.session_state.calendario = leer_datos("data_calendario.csv", COLS_CAL)
st.session_state.accesos = leer_datos("data_accesos.csv", COLS_ACC)

if 'rol' not in st.session_state: st.session_state.rol = "Invitado"

# --- 3. LOGIN ---
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
            st.session_state.rol = "Invitado"; st.rerun()

    opciones = ["🏠 Inicio", "🏆 LÍDERES", "📊 Standings", "📋 Rosters", "🖼️ Galería"]
    if st.session_state.rol == "Admin": opciones.insert(0, "🏃 Admin General")
    menu = st.sidebar.radio("IR A:", opciones)

# --- 4. ROSTERS (CORREGIDO) ---
if menu == "📋 Rosters":
    st.title("📋 Rosters de Equipos")
    if not st.session_state.equipos.empty:
        lista_equipos = sorted(st.session_state.equipos["Nombre"].unique().tolist())
        eq_sel = st.selectbox("Selecciona un Equipo:", lista_equipos)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"🥖 Bateo: {eq_sel}")
            # Filtro insensible a mayúsculas/espacios
            df_b = st.session_state.jugadores[st.session_state.jugadores["Equipo"].str.upper() == eq_sel.upper()].copy()
            if not df_b.empty:
                df_b['AVG'] = ((df_b['H']+df_b['H2']+df_b['H3']+df_b['HR'])/df_b['VB'].replace(0,1)).fillna(0)
                st.dataframe(df_b[["Nombre","VB","H","H2","H3","HR","AVG"]].sort_values("AVG", ascending=False).style.format({"AVG":"{:.3f}"}).highlight_max(color='#FFD700', subset=["AVG"]), use_container_width=True, hide_index=True)
            else: st.info("No hay bateadores registrados.")

        with col2:
            st.subheader(f"🔥 Pitcheo: {eq_sel}")
            df_p = st.session_state.pitchers[st.session_state.pitchers["Equipo"].str.upper() == eq_sel.upper()].copy()
            if not df_p.empty:
                df_p['EFE'] = ((df_p['CL']*7)/df_p['IP'].replace(0,1)).fillna(0)
                st.dataframe(df_p[["Nombre","JG","JP","IP","K","EFE"]].style.format({"EFE":"{:.2f}"}).highlight_max(color='#FFD700', subset=["JG"]), use_container_width=True, hide_index=True)
            else: st.info("No hay pitchers registrados.")
    else: st.warning("No hay equipos en la base de datos.")

# --- 5. ADMIN GENERAL (GESTIÓN TOTAL) ---
elif menu == "🏃 Admin General" and st.session_state.rol == "Admin":
    t1, t2, t3, t4 = st.tabs(["Bateadores", "Pitchers", "Calendario", "Equipos"])
    
    with t1:
        sel = st.selectbox("Elegir Jugador:", ["-- Nuevo --"] + sorted(st.session_state.jugadores["Nombre"].tolist()))
        v = ["","",0,0,0,0,0]
        if sel != "-- Nuevo --":
            d = st.session_state.jugadores[st.session_state.jugadores["Nombre"]==sel].iloc[0]
            v = [d["Nombre"], d["Equipo"], d["VB"], d["H"], d["H2"], d["H3"], d["HR"]]
        with st.form("f_bat"):
            nom = st.text_input("Nombre", value=v[0]); eq = st.selectbox("Equipo", st.session_state.equipos["Nombre"].tolist(), index=0 if v[1]=="" else st.session_state.equipos["Nombre"].tolist().index(v[1]))
            c1,c2,c3,c4,c5 = st.columns(5)
            vb=c1.number_input("VB", value=int(v[2])); h=c2.number_input("H", value=int(v[3])); h2=c3.number_input("H2", value=int(v[4])); h3=c4.number_input("H3", value=int(v[5])); hr=c5.number_input("HR", value=int(v[6]))
            if st.form_submit_button("Guardar Bateador"):
                df = st.session_state.jugadores[st.session_state.jugadores["Nombre"] != sel]
                pd.concat([df, pd.DataFrame([[nom,eq,vb,h,h2,h3,hr]], columns=COLS_J)], ignore_index=True).to_csv(path_archivo("data_jugadores.csv"), index=False)
                st.success("Guardado"); st.rerun()

    with t2:
        selp = st.selectbox("Elegir Pitcher:", ["-- Nuevo --"] + sorted(st.session_state.pitchers["Nombre"].tolist()))
        vp = ["","",0,0,0,0,0]
        if selp != "-- Nuevo --":
            dp = st.session_state.pitchers[st.session_state.pitchers["Nombre"]==selp].iloc[0]
            vp = [dp["Nombre"], dp["Equipo"], dp["JG"], dp["JP"], dp["IP"], dp["CL"], dp["K"]]
        with st.form("f_pit"):
            nomp = st.text_input("Nombre", value=vp[0]); eqp = st.selectbox("Equipo ", st.session_state.equipos["Nombre"].tolist(), index=0 if vp[1]=="" else st.session_state.equipos["Nombre"].tolist().index(vp[1]))
            c1,c2,c3,c4,c5 = st.columns(5)
            jg=c1.number_input("JG", value=int(vp[2])); jp=c2.number_input("JP", value=int(vp[3])); ip=c3.number_input("IP", value=int(vp[4])); cl=c4.number_input("CL", value=int(vp[5])); k=c5.number_input("K", value=int(vp[6]))
            if st.form_submit_button("Guardar Pitcher"):
                dfp = st.session_state.pitchers[st.session_state.pitchers["Nombre"] != selp]
                pd.concat([dfp, pd.DataFrame([[nomp,eqp,jg,jp,ip,cl,k]], columns=COLS_P)], ignore_index=True).to_csv(path_archivo("data_pitchers.csv"), index=False)
                st.success("Pitcher Guardado"); st.rerun()

# --- LÍDERES, STANDINGS E INICIO (RESTO DEL CÓDIGO) ---
elif menu == "🏠 Inicio":
    st.title("⚾ LIGA DOMINICAL 2026")
    st.table(st.session_state.calendario)

elif menu == "🏆 LÍDERES":
    df = st.session_state.jugadores.copy()
    if not df.empty:
        df['H_T'] = df['H'] + df['H2'] + df['H3'] + df['HR']
        df['AVG'] = (df['H_T'] / df['VB'].replace(0, 1)).fillna(0)
        c1, c2 = st.columns(2)
        c1.subheader("⚾ AVG"); c1.table(df.sort_values("AVG", ascending=False).head(5)[["Nombre","AVG"]].style.format({"AVG": "{:.3f}"}).highlight_max(color='#FFD700', axis=0))
        c2.subheader("⚡ Hits"); c2.table(df.sort_values("H_T", ascending=False).head(5)[["Nombre","H_T"]].style.highlight_max(color='#FFD700', axis=0))

elif menu == "📊 Standings":
    st.title("📊 Posiciones")
    stats = {eq: {"JJ":0, "JG":0, "JP":0} for eq in st.session_state.equipos["Nombre"]}
    for _, f in st.session_state.calendario.iterrows():
        sc = str(f["Score"]).strip()
        if "-" in sc:
            try:
                sl, sv = map(int, sc.split("-")); l, v = str(f["Local"]).strip(), str(f["Visitante"]).strip()
                if l in stats and v in stats:
                    stats[l]["JJ"]+=1; stats[v]["JJ"]+=1
                    if sl > sv: stats[l]["JG"]+=1; stats[v]["JP"]+=1
                    elif sv > sl: stats[v]["JG"]+=1; stats[l]["JP"]+=1
            except: continue
    df_s = pd.DataFrame.from_dict(stats, orient='index').reset_index().rename(columns={'index':'Equipo'})
    df_s["AVG"] = (df_s["JG"] / df_s["JJ"].replace(0,1)).fillna(0)
    st.table(df_s.sort_values(["AVG","JG"], ascending=False).style.format({"AVG":"{:.3f}"}))
