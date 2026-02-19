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

# --- 2. CARGA DE DATOS SIN CACHÉ PARA EVITAR ERRORES ---
def leer_datos(n, cols):
    p = path_archivo(n)
    if os.path.exists(p):
        df = pd.read_csv(p)
        df.columns = df.columns.str.strip()
        # Normalización de texto: elimina espacios al inicio y final
        for col in df.select_dtypes(['object']).columns:
            df[col] = df[col].astype(str).str.strip()
        return df
    return pd.DataFrame(columns=cols)

# Recarga forzada en cada interacción
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

# --- 4. SECCIÓN ROSTERS (NORMALIZADA) ---
if menu == "📋 Rosters":
    st.title("📋 Rosters de Equipos")
    if not st.session_state.equipos.empty:
        lista_e = sorted(st.session_state.equipos["Nombre"].unique().tolist())
        eq_sel = st.selectbox("Selecciona Equipo para ver Roster:", lista_e)
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader(f"🥖 Bateo: {eq_sel}")
            # Filtro robusto: ignora mayúsculas/minúsculas y espacios
            df_b = st.session_state.jugadores[st.session_state.jugadores["Equipo"].str.lower() == eq_sel.lower()].copy()
            if not df_b.empty:
                # Asegurar que las estadísticas sean números
                for c in ["VB","H","H2","H3","HR"]: df_b[c] = pd.to_numeric(df_b[c], errors='coerce').fillna(0)
                df_b['AVG'] = ((df_b['H']+df_b['H2']+df_b['H3']+df_b['HR'])/df_b['VB'].replace(0,1)).fillna(0)
                st.dataframe(df_b[["Nombre","VB","H","H2","H3","HR","AVG"]].sort_values("AVG", ascending=False).style.format({"AVG":"{:.3f}"}).highlight_max(color='#FFD700', subset=["AVG"]), use_container_width=True, hide_index=True)
            else: st.info("No hay bateadores en este equipo.")

        with c2:
            st.subheader(f"🔥 Pitcheo: {eq_sel}")
            df_p = st.session_state.pitchers[st.session_state.pitchers["Equipo"].str.lower() == eq_sel.lower()].copy()
            if not df_p.empty:
                for c in ["JG","JP","IP","CL","K"]: df_p[c] = pd.to_numeric(df_p[c], errors='coerce').fillna(0)
                df_p['EFE'] = ((df_p['CL']*7)/df_p['IP'].replace(0,1)).fillna(0)
                st.dataframe(df_p[["Nombre","JG","JP","IP","K","EFE"]].style.format({"EFE":"{:.2f}"}).highlight_max(color='#FFD700', subset=["JG"]), use_container_width=True, hide_index=True)
            else: st.info("No hay pitchers en este equipo.")
    else: st.warning("No hay equipos registrados. Agrégalos en la Zona Admin.")

# --- 5. ADMIN GENERAL (FORMULARIOS CORREGIDOS) ---
elif menu == "🏃 Admin General" and st.session_state.rol == "Admin":
    t1, t2, t3 = st.tabs(["Bateadores", "Pitchers", "Equipos"])
    with t1:
        sel = st.selectbox("Jugador:", ["-- Nuevo --"] + sorted(st.session_state.jugadores["Nombre"].tolist()))
        # Valores por defecto para el formulario
        v = ["","",0,0,0,0,0]
        if sel != "-- Nuevo --":
            d = st.session_state.jugadores[st.session_state.jugadores["Nombre"]==sel].iloc[0]
            v = [d["Nombre"], d["Equipo"], d["VB"], d["H"], d["H2"], d["H3"], d["HR"]]
        
        with st.form("f_bat"):
            nom = st.text_input("Nombre Completo", value=v[0])
            lista_eq = st.session_state.equipos["Nombre"].tolist()
            eq = st.selectbox("Equipo", lista_eq, index=lista_eq.index(v[1]) if v[1] in lista_eq else 0)
            c1,c2,c3,c4,c5 = st.columns(5)
            vb=c1.number_input("VB", value=int(v[2])); h=c2.number_input("H", value=int(v[3]))
            h2=c3.number_input("H2", value=int(v[4])); h3=c4.number_input("H3", value=int(v[5])); hr=c5.number_input("HR", value=int(v[6]))
            if st.form_submit_button("💾 Guardar Jugador"):
                df_temp = st.session_state.jugadores[st.session_state.jugadores["Nombre"] != sel]
                nuevo_j = pd.DataFrame([[nom.strip(), eq, vb, h, h2, h3, hr]], columns=COLS_J)
                pd.concat([df_temp, nuevo_j], ignore_index=True).to_csv(path_archivo("data_jugadores.csv"), index=False)
                st.success("Guardado"); st.rerun()

    with t3:
        st.subheader("Registrar Equipo")
        n_eq = st.text_input("Nombre del Equipo:")
        if st.button("➕ Añadir Equipo") and n_eq:
            pd.concat([st.session_state.equipos, pd.DataFrame([[n_eq.strip()]], columns=["Nombre"])], ignore_index=True).to_csv(path_archivo("data_equipos.csv"), index=False)
            st.success(f"Equipo {n_eq} añadido"); st.rerun()

# --- 6. INICIO Y LÍDERES ---
elif menu == "🏠 Inicio":
    st.title("⚾ LIGA DOMINICAL 2026")
    st.subheader("📅 Calendario Actual")
    st.table(st.session_state.calendario)

elif menu == "🏆 LÍDERES":
    st.title("🥇 Líderes de la Liga")
    df = st.session_state.jugadores.copy()
    if not df.empty:
        for c in ["VB","H","H2","H3","HR"]: df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
        df['H_T'] = df['H'] + df['H2'] + df['H3'] + df['HR']
        df['AVG'] = (df['H_T'] / df['VB'].replace(0, 1)).fillna(0)
        c1, c2 = st.columns(2)
        c1.subheader("⚾ AVG"); c1.table(df.sort_values("AVG", ascending=False).head(5)[["Nombre","AVG"]].style.format({"AVG": "{:.3f}"}).highlight_max(color='#FFD700', axis=0))
        c2.subheader("⚡ Hits"); c2.table(df.sort_values("H_T", ascending=False).head(5)[["Nombre","H_T"]].style.highlight_max(color='#FFD700', axis=0))
