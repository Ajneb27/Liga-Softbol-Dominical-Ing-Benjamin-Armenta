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
COLS_P = ["Nombre","Equipo","JG","JP","IP","CL","K"] # Añadí 'K' para Ponches
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

# --- SIDEBAR Y LOGIN ---
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

# --- SECCIÓN LÍDERES ACTUALIZADA ---
if menu == "🏆 LÍDERES":
    st.title("🥇 Cuadro de Honor")
    t_bateo, t_pitcheo = st.tabs(["🥖 Departamentos de Bateo", "🔥 Departamentos de Pitcheo"])
    
    with t_bateo:
        dfb = st.session_state.jugadores.copy()
        if not dfb.empty:
            dfb['H_T'] = dfb['H'] + dfb['H2'] + dfb['H3'] + dfb['HR']
            dfb['AVG'] = (dfb['H_T'] / dfb['VB'].replace(0, 1)).fillna(0)
            
            c1, c2 = st.columns(2)
            c1.subheader("⚾ Promedio (AVG)")
            c1.table(dfb.sort_values("AVG", ascending=False).head(5)[["Nombre","Equipo","AVG"]].style.format({"AVG": "{:.3f}"}))
            c2.subheader("⚡ Hits Totales")
            c2.table(dfb.sort_values("H_T", ascending=False).head(5)[["Nombre","Equipo","H_T"]])
            
            c3, c4, c5 = st.columns(3)
            c3.subheader("🚀 Jonrones (HR)")
            c3.table(dfb.sort_values("HR", ascending=False).head(5)[["Nombre","HR"]])
            c4.subheader("🥈 Dobles (H2)")
            c4.table(dfb.sort_values("H2", ascending=False).head(5)[["Nombre","H2"]])
            c5.subheader("🥉 Triples (H3)")
            c5.table(dfb.sort_values("H3", ascending=False).head(5)[["Nombre","H3"]])
        else: st.warning("No hay datos de bateo.")

    with t_pitcheo:
        dfp = st.session_state.pitchers.copy()
        if not dfp.empty:
            dfp['EFE'] = ((dfp['CL'] * 7) / dfp['IP'].replace(0, 1)).fillna(0)
            
            cp1, cp2 = st.columns(2)
            cp1.subheader("📉 Efectividad (EFE)")
            cp1.table(dfp[dfp['IP']>0].sort_values("EFE").head(5)[["Nombre","Equipo","EFE"]].style.format({"EFE": "{:.2f}"}))
            cp2.subheader("💎 Juegos Ganados (JG)")
            cp2.table(dfp.sort_values("JG", ascending=False).head(5)[["Nombre","Equipo","JG"]])
            
            cp3, cp4 = st.columns(2)
            cp3.subheader("🔥 Ponches (K)")
            cp3.table(dfp.sort_values("K", ascending=False).head(5)[["Nombre","K"]])
            cp4.subheader("🕒 Innings (IP)")
            cp4.table(dfp.sort_values("IP", ascending=False).head(5)[["Nombre","IP"]])
        else: st.warning("No hay datos de pitcheo.")

# --- RESTO DE SECCIONES (Sigue igual) ---
elif menu == "🏠 Inicio":
    st.markdown("<h1 style='text-align:center;'>⚾ LIGA DOMINICAL</h1>", unsafe_allow_html=True)
    st.subheader("📅 Calendario"); st.table(st.session_state.calendario)

elif menu == "📋 Rosters":
    eq = st.selectbox("Equipo:", st.session_state.equipos["Nombre"].tolist())
    st.dataframe(st.session_state.jugadores[st.session_state.jugadores["Equipo"]==eq], use_container_width=True, hide_index=True)

elif menu == "🏃 Admin General":
    # Lógica de admin que ya tenías...
    st.write("Panel de Administración")
