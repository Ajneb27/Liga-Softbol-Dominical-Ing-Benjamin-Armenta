import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="LIGA SOFTBOL", page_icon="⚾", layout="wide")
st.markdown("<style>th{background-color:#D32F2F!important;color:white!important;}h1,h2{color:#B71C1C;}</style>", unsafe_allow_html=True)

DATOS_DIR = "datos_liga"
if not os.path.exists(DATOS_DIR): os.makedirs(DATOS_DIR)

def path_archivo(n): return os.path.join(DATOS_DIR, n)

COLUMNAS_BASE = {
    "data_jugadores.csv": ["Nombre", "Equipo", "VB", "H", "H2", "H3", "HR"],
    "data_pitchers.csv": ["Nombre", "Equipo", "JG", "JP", "IP", "CL", "K"],
    "data_equipos.csv": ["Nombre"],
    "data_calendario.csv": ["Jornada", "Fecha", "Hora", "Campo", "Local", "Visitante", "Score"]
}

# --- 2. CARGA Y REPARACIÓN ---
def cargar_y_reparar(nombre_archivo):
    p = path_archivo(nombre_archivo)
    cols_necesarias = COLUMNAS_BASE[nombre_archivo]
    if os.path.exists(p):
        try:
            df = pd.read_csv(p)
            df.columns = df.columns.str.strip()
            for c in cols_necesarias:
                if c not in df.columns: df[c] = "" if c in ["Nombre", "Equipo", "Local", "Visitante", "Score", "Jornada"] else 0
            for col in df.select_dtypes(['object']).columns: df[col] = df[col].astype(str).str.strip()
            return df[cols_necesarias]
        except: return pd.DataFrame(columns=cols_necesarias)
    return pd.DataFrame(columns=cols_necesarias)

# --- 3. LOGIN ---
if 'rol' not in st.session_state: st.session_state.rol = "Invitado"

with st.sidebar:
    st.title("🥎 LIGA DOMINICAL")
    if st.session_state.rol == "Invitado":
        pwd = st.text_input("Clave Admin:", type="password")
        if st.button("ENTRAR"):
            if pwd == "softbol2026": 
                st.session_state.rol = "Admin"
                st.rerun()
    else:
        if st.button("SALIR"): 
            st.session_state.rol = "Invitado"
            st.rerun()
    
    menu = st.radio("MENÚ:", ["🏠 Inicio", "🏆 LÍDERES", "📊 Standings", "📋 Rosters", "⚙️ Admin General"])

# --- 4. ZONA ADMIN (CON ELIMINACIÓN ACTIVADA) ---
if menu == "⚙️ Admin General":
    if st.session_state.rol != "Admin":
        st.error("Acceso Denegado")
    else:
        st.title("⚙️ Panel de Control")
        st.warning("🗑️ **PARA ELIMINAR:** Selecciona la fila (cuadrito izquierdo) y pulsa la tecla **DELETE** de tu teclado. Luego pulsa **GUARDAR**.")

        t1, t2, t3, t4 = st.tabs(["Equipos", "Bateadores", "Pitchers", "Calendario"])

        with t1:
            df_e = cargar_y_reparar("data_equipos.csv")
            # num_rows="dynamic" permite añadir y eliminar filas
            ed_e = st.data_editor(df_e, num_rows="dynamic", use_container_width=True, key="ed_eq")
            if st.button("💾 GUARDAR EQUIPOS"):
                ed_e.to_csv(path_archivo("data_equipos.csv"), index=False)
                st.success("Cambios guardados"); st.rerun()

        with t2:
            df_j = cargar_y_reparar("data_jugadores.csv")
            ed_j = st.data_editor(df_j, num_rows="dynamic", use_container_width=True, key="ed_bat")
            if st.button("💾 GUARDAR BATEADORES"):
                ed_j.to_csv(path_archivo("data_jugadores.csv"), index=False)
                st.success("Cambios guardados"); st.rerun()

        with t3:
            df_p = cargar_y_reparar("data_pitchers.csv")
            ed_p = st.data_editor(df_p, num_rows="dynamic", use_container_width=True, key="ed_pit")
            if st.button("💾 GUARDAR PITCHERS"):
                ed_p.to_csv(path_archivo("data_pitchers.csv"), index=False)
                st.success("Cambios guardados"); st.rerun()

        with t4:
            df_c = cargar_y_reparar("data_calendario.csv")
            ed_c = st.data_editor(df_c, num_rows="dynamic", use_container_width=True, key="ed_cal")
            if st.button("💾 GUARDAR CALENDARIO"):
                ed_c.to_csv(path_archivo("data_calendario.csv"), index=False)
                st.success("Cambios guardados"); st.rerun()

# --- 5. ROSTERS ---
elif menu == "📋 Rosters":
    st.title("📋 Rosters")
    df_e = cargar_y_reparar("data_equipos.csv")
    df_j = cargar_y_reparar("data_jugadores.csv")
    df_p = cargar_y_reparar("data_pitchers.csv")

    if not df_e.empty:
        lista_e = sorted(df_e["Nombre"].unique().tolist())
        eq_sel = st.selectbox("Selecciona Equipo:", lista_e)
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🥖 Bateadores")
            db = df_j[df_j["Equipo"].str.upper() == eq_sel.upper()].copy()
            if not db.empty:
                for c in ["VB","H","H2","H3","HR"]: db[c] = pd.to_numeric(db[c], errors='coerce').fillna(0)
                db["AVG"] = ((db["H"]+db["H2"]+db["H3"]+db["HR"])/db["VB"].replace(0,1)).fillna(0)
                st.dataframe(db[["Nombre","VB","H","H2","H3","HR","AVG"]].sort_values("AVG", ascending=False).style.format({"AVG":"{:.3f}"}), use_container_width=True, hide_index=True)
            else: st.info(f"No hay jugadores en {eq_sel}")
        with c2:
            st.subheader("🔥 Pitchers")
            dp = df_p[df_p["Equipo"].str.upper() == eq_sel.upper()].copy()
            if not dp.empty:
                st.dataframe(dp[["Nombre","JG","JP","IP","K"]], use_container_width=True, hide_index=True)
            else: st.info(f"No hay pitchers en {eq_sel}")
    else: st.warning("No hay equipos registrados.")

# --- 6. INICIO Y LÍDERES ---
elif menu == "🏠 Inicio":
    st.title("⚾ LIGA DOMINICAL 2026")
    df_c = cargar_y_reparar("data_calendario.csv")
    st.dataframe(df_c, use_container_width=True, hide_index=True)

elif menu == "🏆 LÍDERES":
    st.title("🥇 Líderes")
    df_j = cargar_y_reparar("data_jugadores.csv")
    if not df_j.empty:
        for c in ["VB","H","H2","H3","HR"]: df_j[c] = pd.to_numeric(df_j[c], errors='coerce').fillna(0)
        df_j["AVG"] = ((df_j["H"]+df_j["H2"]+df_j["H3"]+df_j["HR"]) / df_j["VB"].replace(0,1)).fillna(0)
        st.table(df_j.sort_values("AVG", ascending=False).head(5)[["Nombre", "Equipo", "AVG"]].style.format({"AVG": "{:.3f}"}))
