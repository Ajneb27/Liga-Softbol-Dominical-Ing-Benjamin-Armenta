import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="LIGA SOFTBOL", page_icon="⚾", layout="wide")
st.markdown("<style>th{background-color:#D32F2F!important;color:white!important;}h1,h2{color:#B71C1C;}</style>", unsafe_allow_html=True)

DATOS_DIR = "datos_liga"
if not os.path.exists(DATOS_DIR): os.makedirs(DATOS_DIR)

def path_archivo(n): return os.path.join(DATOS_DIR, n)

# --- 2. CARGA DE DATOS ---
def cargar_datos():
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
            for c in df.select_dtypes(['object']).columns: df[c] = df[col].astype(str).str.strip() if 'col' in locals() else df[c].astype(str).str.strip()
            st.session_state[key] = df
        else:
            st.session_state[key] = pd.DataFrame(columns=cols)

cargar_datos()
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

# --- 4. ZONA ADMIN (EDICIÓN TOTAL) ---
if menu == "🏃 Admin General":
    if st.session_state.rol != "Admin": st.error("Acceso Denegado")
    else:
        st.title("⚙️ Editor de la Liga")
        t_eq, t_bat, t_pit, t_cal = st.tabs(["🏆 Equipos", "🥖 Bateadores", "🔥 Pitchers", "📅 Calendario"])

        with t_eq:
            st.subheader("Gestión de Equipos")
            # ELIMINAR O EDITAR EQUIPO
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                with st.form("add_eq"):
                    n_e = st.text_input("Nombre de nuevo equipo:")
                    if st.form_submit_button("➕ Agregar"):
                        if n_e:
                            df = pd.concat([st.session_state.equipos, pd.DataFrame([[n_e.strip()]], columns=["Nombre"])], ignore_index=True)
                            df.to_csv(path_archivo("data_equipos.csv"), index=False); st.rerun()
            with col_e2:
                eq_del = st.selectbox("Eliminar Equipo:", ["--"] + st.session_state.equipos["Nombre"].tolist())
                if st.button("🗑️ Borrar Equipo") and eq_del != "--":
                    df = st.session_state.equipos[st.session_state.equipos["Nombre"] != eq_del]
                    df.to_csv(path_archivo("data_equipos.csv"), index=False); st.rerun()

        with t_bat:
            st.subheader("Editor de Bateadores")
            sel_b = st.selectbox("Seleccionar Bateador para Editar:", ["-- Nuevo --"] + sorted(st.session_state.jugadores["Nombre"].tolist()))
            # Cargar datos si existe
            v = ["","",0,0,0,0,0]
            if sel_b != "-- Nuevo --":
                d = st.session_state.jugadores[st.session_state.jugadores["Nombre"] == sel_b].iloc[0]
                v = [d["Nombre"], d["Equipo"], d["VB"], d["H"], d["H2"], d["H3"], d["HR"]]
            
            with st.form("edit_bat"):
                nom = st.text_input("Nombre:", value=v[0])
                eq = st.selectbox("Equipo:", st.session_state.equipos["Nombre"].tolist(), index=0 if v[1]=="" else st.session_state.equipos["Nombre"].tolist().index(v[1]) if v[1] in st.session_state.equipos["Nombre"].tolist() else 0)
                c1, c2, c3, c4, c5 = st.columns(5)
                vb, h, h2, h3, hr = c1.number_input("VB", value=int(v[2])), c2.number_input("H", value=int(v[3])), c3.number_input("H2", value=int(v[4])), c4.number_input("H3", value=int(v[5])), c5.number_input("HR", value=int(v[6]))
                if st.form_submit_button("💾 Guardar Cambios"):
                    df = st.session_state.jugadores[st.session_state.jugadores["Nombre"] != sel_b]
                    nuevo = pd.concat([df, pd.DataFrame([[nom, eq, vb, h, h2, h3, hr]], columns=["Nombre","Equipo","VB","H","H2","H3","HR"])], ignore_index=True)
                    nuevo.to_csv(path_archivo("data_jugadores.csv"), index=False); st.success("¡Actualizado!"); st.rerun()

        with t_pit:
            st.subheader("Editor de Pitchers")
            sel_p = st.selectbox("Seleccionar Pitcher para Editar:", ["-- Nuevo --"] + sorted(st.session_state.pitchers["Nombre"].tolist()))
            vp = ["","",0,0,0,0,0]
            if sel_p != "-- Nuevo --":
                d = st.session_state.pitchers[st.session_state.pitchers["Nombre"] == sel_p].iloc[0]
                vp = [d["Nombre"], d["Equipo"], d["JG"], d["JP"], d["IP"], d["CL"], d["K"]]
            
            with st.form("edit_pit"):
                nomp = st.text_input("Nombre Pitcher:", value=vp[0])
                eqp = st.selectbox("Equipo Pitcher:", st.session_state.equipos["Nombre"].tolist(), index=0 if vp[1]=="" else st.session_state.equipos["Nombre"].tolist().index(vp[1]) if vp[1] in st.session_state.equipos["Nombre"].tolist() else 0)
                c1, c2, c3, c4 = st.columns(4)
                jg, jp, ip, k = c1.number_input("JG", value=int(vp[2])), c2.number_input("JP", value=int(vp[3])), c3.number_input("IP", value=int(vp[4])), c4.number_input("K", value=int(vp[6]))
                if st.form_submit_button("🔥 Guardar Cambios Pitcher"):
                    df = st.session_state.pitchers[st.session_state.pitchers["Nombre"] != sel_p]
                    nuevo = pd.concat([df, pd.DataFrame([[nomp, eqp, jg, jp, ip, 0, k]], columns=["Nombre","Equipo","JG","JP","IP","CL","K"])], ignore_index=True)
                    nuevo.to_csv(path_archivo("data_pitchers.csv"), index=False); st.success("¡Actualizado!"); st.rerun()

        with t_cal:
            st.subheader("Editor de Calendario")
            ed_cal = st.data_editor(st.session_state.calendario, num_rows="dynamic", use_container_width=True)
            if st.button("💾 Guardar Calendario Completo"):
                ed_cal.to_csv(path_archivo("data_calendario.csv"), index=False); st.success("Sincronizado")

# --- 5. SECCIONES PÚBLICAS (ROSTERS, LÍDERES) ---
elif menu == "📋 Rosters":
    st.title("📋 Rosters")
    if not st.session_state.equipos.empty:
        eq_sel = st.selectbox("Equipo:", sorted(st.session_state.equipos["Nombre"].tolist()))
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Bateo")
            db = st.session_state.jugadores[st.session_state.jugadores["Equipo"] == eq_sel]
            if not db.empty:
                db["AVG"] = ((db["H"]+db["H2"]+db["H3"]+db["HR"])/db["VB"].replace(0,1)).fillna(0)
                st.dataframe(db.style.format({"AVG": "{:.3f}"}), hide_index=True)
        with c2:
            st.subheader("Pitcheo")
            dp = st.session_state.pitchers[st.session_state.pitchers["Equipo"] == eq_sel]
            st.dataframe(dp, hide_index=True)

elif menu == "🏠 Inicio":
    st.title("⚾ LIGA DOMINICAL 2026")
    st.dataframe(st.session_state.calendario, use_container_width=True, hide_index=True)
