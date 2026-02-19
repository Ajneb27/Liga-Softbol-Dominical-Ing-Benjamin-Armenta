import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="LIGA SOFTBOL", page_icon="⚾", layout="wide")
st.markdown("<style>th{background-color:#D32F2F!important;color:white!important;}h1,h2{color:#B71C1C;}</style>", unsafe_allow_html=True)

DATOS_DIR = "datos_liga"
if not os.path.exists(DATOS_DIR): os.makedirs(DATOS_DIR)

def path_archivo(n): return os.path.join(DATOS_DIR, n)

# --- 2. CARGA DE DATOS REAL (CADA VEZ QUE SE MUEVE EL MOUSE) ---
def cargar_todas_las_tablas():
    archivos = {
        "jugadores": (["Nombre","Equipo","VB","H","H2","H3","HR"], "data_jugadores.csv"),
        "pitchers": (["Nombre","Equipo","JG","JP","IP","CL","K"], "data_pitchers.csv"),
        "equipos": (["Nombre"], "data_equipos.csv"),
        "calendario": (["Jornada","Fecha","Hora","Campo","Local","Visitante","Score"], "data_calendario.csv")
    }
    for key, (cols, nombre) in archivos.items():
        p = path_archivo(nombre)
        if os.path.exists(p):
            df = pd.read_csv(p)
            df.columns = df.columns.str.strip()
            for c in df.select_dtypes(['object']).columns: df[c] = df[c].astype(str).str.strip()
            st.session_state[key] = df
        else:
            st.session_state[key] = pd.DataFrame(columns=cols)

cargar_todas_las_tablas()

if 'rol' not in st.session_state: st.session_state.rol = "Invitado"

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("🥎 LIGA DOMINICAL")
    if st.session_state.rol == "Invitado":
        pwd = st.text_input("Clave Admin:", type="password")
        if st.button("ENTRAR"):
            if pwd == "softbol2026": st.session_state.rol = "Admin"; st.rerun()
    else:
        if st.button("CERRAR SESIÓN"): st.session_state.rol = "Invitado"; st.rerun()

    menu = st.radio("IR A:", ["🏠 Inicio", "🏆 LÍDERES", "📊 Standings", "📋 Rosters", "🏃 Admin General"])

# --- 4. ZONA ADMIN (RESTRUCTURADA Y FUNCIONAL) ---
if menu == "🏃 Admin General":
    if st.session_state.rol != "Admin": st.error("Acceso Denegado")
    else:
        st.title("⚙️ Panel de Control Administrativo")
        tab_eq, tab_bat, tab_pit, tab_cal = st.tabs(["🏆 Equipos", "🥖 Bateadores", "🔥 Pitchers", "📅 Calendario"])

        with tab_eq:
            st.subheader("Gestión de Equipos")
            with st.form("f_equipos"):
                n_e = st.text_input("Nombre del nuevo equipo:")
                if st.form_submit_button("➕ Agregar Equipo"):
                    if n_e:
                        nuevo = pd.concat([st.session_state.equipos, pd.DataFrame([[n_e.strip()]], columns=["Nombre"])], ignore_index=True)
                        nuevo.to_csv(path_archivo("data_equipos.csv"), index=False)
                        st.success(f"Equipo {n_e} creado"); st.rerun()
            st.write("Equipos actuales:")
            st.dataframe(st.session_state.equipos, use_container_width=True, hide_index=True)

        with tab_bat:
            st.subheader("Gestión de Bateadores")
            with st.form("f_bateo"):
                nb = st.text_input("Nombre del Bateador:")
                eb = st.selectbox("Equipo:", st.session_state.equipos["Nombre"].tolist() if not st.session_state.equipos.empty else ["Crea un equipo primero"])
                c1, c2, c3, c4, c5 = st.columns(5)
                vb, h, h2, h3, hr = c1.number_input("VB",0), c2.number_input("H",0), c3.number_input("H2",0), c4.number_input("H3",0), c5.number_input("HR",0)
                if st.form_submit_button("💾 Guardar Bateador"):
                    nueva_f = pd.DataFrame([[nb, eb, vb, h, h2, h3, hr]], columns=["Nombre","Equipo","VB","H","H2","H3","HR"])
                    pd.concat([st.session_state.jugadores, nueva_f], ignore_index=True).to_csv(path_archivo("data_jugadores.csv"), index=False)
                    st.success("Bateador registrado"); st.rerun()

        with tab_pit:
            st.subheader("Gestión de Pitchers")
            with st.form("f_pitchers"):
                np = st.text_input("Nombre del Pitcher:")
                ep = st.selectbox("Equipo :", st.session_state.equipos["Nombre"].tolist() if not st.session_state.equipos.empty else ["Crea un equipo primero"])
                c1, c2, c3, c4 = st.columns(4)
                jg, jp, ip, k = c1.number_input("JG",0), c2.number_input("JP",0), c3.number_input("IP",0), c4.number_input("K",0)
                if st.form_submit_button("🔥 Guardar Pitcher"):
                    nueva_p = pd.DataFrame([[np, ep, jg, jp, ip, 0, k]], columns=["Nombre","Equipo","JG","JP","IP","CL","K"])
                    pd.concat([st.session_state.pitchers, nueva_p], ignore_index=True).to_csv(path_archivo("data_pitchers.csv"), index=False)
                    st.success("Pitcher registrado"); st.rerun()

        with tab_cal:
            st.subheader("Editor de Calendario")
            ed_cal = st.data_editor(st.session_state.calendario, num_rows="dynamic", use_container_width=True)
            if st.button("💾 Guardar Todo el Calendario"):
                ed_cal.to_csv(path_archivo("data_calendario.csv"), index=False); st.success("Calendario Actualizado")

# --- 5. ROSTERS (CALCULADOS AL INSTANTE) ---
elif menu == "📋 Rosters":
    st.title("📋 Rosters de Equipos")
    if not st.session_state.equipos.empty:
        eq_sel = st.selectbox("Selecciona un Equipo:", sorted(st.session_state.equipos["Nombre"].tolist()))
        
        st.subheader(f"Bateo - {eq_sel}")
        db = st.session_state.jugadores[st.session_state.jugadores["Equipo"].str.upper() == eq_sel.upper()].copy()
        if not db.empty:
            db["AVG"] = ((db["H"] + db["H2"] + db["H3"] + db["HR"]) / db["VB"].replace(0, 1)).fillna(0)
            st.dataframe(db.style.format({"AVG": "{:.3f}"}), use_container_width=True, hide_index=True)
        else: st.info("No hay bateadores.")

        st.subheader(f"Pitcheo - {eq_sel}")
        dp = st.session_state.pitchers[st.session_state.pitchers["Equipo"].str.upper() == eq_sel.upper()].copy()
        if not dp.empty:
            st.dataframe(dp, use_container_width=True, hide_index=True)
        else: st.info("No hay pitchers.")

# --- 6. INICIO Y LÍDERES ---
elif menu == "🏠 Inicio":
    st.title("⚾ LIGA DOMINICAL 2026")
    st.dataframe(st.session_state.calendario, use_container_width=True, hide_index=True)

elif menu == "🏆 LÍDERES":
    st.title("🥇 Cuadro de Honor")
    df = st.session_state.jugadores.copy()
    if not df.empty:
        df["AVG"] = ((df["H"]+df["H2"]+df["H3"]+df["HR"]) / df["VB"].replace(0,1)).fillna(0)
        st.table(df.sort_values("AVG", ascending=False).head(5)[["Nombre", "Equipo", "AVG"]])
