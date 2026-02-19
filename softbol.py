import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="LIGA SOFTBOL", page_icon="⚾", layout="wide")
st.markdown("<style>th{background-color:#D32F2F!important;color:white!important;}h1,h2{color:#B71C1C;}</style>", unsafe_allow_html=True)

DATOS_DIR = "datos_liga"
if not os.path.exists(DATOS_DIR): os.makedirs(DATOS_DIR)

def path_archivo(n): return os.path.join(DATOS_DIR, n)

# --- 2. CARGA DE DATOS DIRECTA ---
def obtener_df(nombre, columnas):
    p = path_archivo(nombre)
    if os.path.exists(p):
        df = pd.read_csv(p)
        df.columns = df.columns.str.strip()
        # Limpieza de espacios para que el Roster no falle
        for col in df.select_dtypes(['object']).columns:
            df[col] = df[col].astype(str).str.strip()
        return df
    return pd.DataFrame(columns=columnas)

# --- 3. LOGIN ---
if 'rol' not in st.session_state: st.session_state.rol = "Invitado"

with st.sidebar:
    st.title("🥎 LIGA DOMINICAL")
    if st.session_state.rol == "Invitado":
        pwd = st.text_input("Clave Admin:", type="password")
        if st.button("ENTRAR"):
            if pwd == "softbol2026": st.session_state.rol = "Admin"; st.rerun()
    else:
        if st.button("SALIR"): st.session_state.rol = "Invitado"; st.rerun()
    
    menu = st.radio("MENÚ:", ["🏠 Inicio", "🏆 LÍDERES", "📊 Standings", "📋 Rosters", "🏃 Admin General"])

# --- 4. SECCIÓN ROSTERS (LECTURA FORZADA) ---
if menu == "📋 Rosters":
    st.title("📋 Rosters de Equipos")
    df_e = obtener_df("data_equipos.csv", ["Nombre"])
    df_j = obtener_df("data_jugadores.csv", ["Nombre","Equipo","VB","H","H2","H3","HR"])
    df_p = obtener_df("data_pitchers.csv", ["Nombre","Equipo","JG","JP","IP","CL","K"])

    if not df_e.empty:
        lista_e = sorted(df_e["Nombre"].unique().tolist())
        eq_sel = st.selectbox("Selecciona Equipo:", lista_e)
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader(f"🥖 Bateadores")
            # Filtro exacto ignorando mayúsculas/minúsculas
            db = df_j[df_j["Equipo"].str.upper() == eq_sel.upper()].copy()
            if not db.empty:
                db["AVG"] = ((db["H"]+db["H2"]+db["H3"]+db["HR"])/db["VB"].replace(0,1)).fillna(0)
                st.dataframe(db[["Nombre","VB","H","H2","H3","HR","AVG"]].style.format({"AVG": "{:.3f}"}), use_container_width=True, hide_index=True)
            else: st.info("No hay bateadores.")
            
        with c2:
            st.subheader(f"🔥 Pitchers")
            dp = df_p[df_p["Equipo"].str.upper() == eq_sel.upper()].copy()
            if not dp.empty:
                st.dataframe(dp[["Nombre","JG","JP","IP","K"]], use_container_width=True, hide_index=True)
            else: st.info("No hay pitchers.")
    else: st.warning("No hay equipos registrados.")

# --- 5. ADMIN GENERAL (EDICIÓN DIRECTA) ---
elif menu == "🏃 Admin General":
    if st.session_state.rol != "Admin": st.error("Acceso Denegado")
    else:
        st.title("⚙️ Panel de Edición")
        st.warning("⚠️ IMPORTANTE: Después de editar o eliminar, presiona el botón GUARDAR debajo de la tabla.")
        
        t1, t2, t3, t4 = st.tabs(["Equipos", "Bateadores", "Pitchers", "Calendario"])
        
        with t1:
            df_e = obtener_df("data_equipos.csv", ["Nombre"])
            ed_e = st.data_editor(df_e, num_rows="dynamic", use_container_width=True, key="edit_eq")
            if st.button("💾 GUARDAR EQUIPOS"):
                ed_e.to_csv(path_archivo("data_equipos.csv"), index=False); st.success("Guardado"); st.rerun()

        with t2:
            df_j = obtener_df("data_jugadores.csv", ["Nombre","Equipo","VB","H","H2","H3","HR"])
            ed_j = st.data_editor(df_j, num_rows="dynamic", use_container_width=True, key="edit_bat")
            if st.button("💾 GUARDAR BATEADORES"):
                ed_j.to_csv(path_archivo("data_jugadores.csv"), index=False); st.success("Guardado"); st.rerun()

        with t3:
            df_p = obtener_df("data_pitchers.csv", ["Nombre","Equipo","JG","JP","IP","CL","K"])
            ed_p = st.data_editor(df_p, num_rows="dynamic", use_container_width=True, key="edit_pit")
            if st.button("💾 GUARDAR PITCHERS"):
                ed_p.to_csv(path_archivo("data_pitchers.csv"), index=False); st.success("Guardado"); st.rerun()

        with t4:
            df_c = obtener_df("data_calendario.csv", ["Jornada","Fecha","Hora","Campo","Local","Visitante","Score"])
            ed_c = st.data_editor(df_c, num_rows="dynamic", use_container_width=True, key="edit_cal")
            if st.button("💾 GUARDAR CALENDARIO"):
                ed_c.to_csv(path_archivo("data_calendario.csv"), index=False); st.success("Guardado"); st.rerun()

# --- 6. INICIO Y LÍDERES ---
elif menu == "🏠 Inicio":
    st.title("⚾ LIGA DOMINICAL 2026")
    df_c = obtener_df("data_calendario.csv", ["Jornada","Fecha","Hora","Campo","Local","Visitante","Score"])
    st.dataframe(df_c, use_container_width=True, hide_index=True)

elif menu == "🏆 LÍDERES":
    st.title("🥇 Cuadro de Honor")
    df_j = obtener_df("data_jugadores.csv", ["Nombre","Equipo","VB","H","H2","H3","HR"])
    if not df_j.empty:
        df_j["AVG"] = ((df_j["H"]+df_j["H2"]+df_j["H3"]+df_j["HR"]) / df_j["VB"].replace(0,1)).fillna(0)
        st.table(df_j.sort_values("AVG", ascending=False).head(5)[["Nombre", "Equipo", "AVG"]])
