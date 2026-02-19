import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="LIGA SOFTBOL", page_icon="⚾", layout="wide")
st.markdown("<style>th{background-color:#D32F2F!important;color:white!important;}h1,h2{color:#B71C1C;}</style>", unsafe_allow_html=True)

DATOS_DIR = "datos_liga"
if not os.path.exists(DATOS_DIR): os.makedirs(DATOS_DIR)

def path_archivo(n): return os.path.join(DATOS_DIR, n)

# --- 2. FUNCIONES DE GUARDADO Y CARGA DIRECTA ---
def cargar(archivo):
    p = path_archivo(archivo)
    if os.path.exists(p):
        df = pd.read_csv(p)
        df.columns = df.columns.str.strip()
        return df
    return pd.DataFrame()

def guardar(df, archivo):
    df.to_csv(path_archivo(archivo), index=False)

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

# --- 4. ZONA ADMIN (FORMULARIOS DE ALTA Y BAJA DIRECTA) ---
if menu == "⚙️ Admin General":
    if st.session_state.rol != "Admin":
        st.error("Acceso Denegado")
    else:
        st.title("⚙️ Panel de Control Directo")
        
        tab1, tab2, tab3 = st.tabs(["🏆 Equipos", "🥖 Jugadores", "📅 Calendario"])

        with tab1:
            st.subheader("Registrar o Eliminar Equipos")
            df_e = cargar("data_equipos.csv")
            
            with st.form("f_equipos"):
                n_e = st.text_input("Nombre del nuevo equipo:")
                if st.form_submit_button("➕ AGREGAR EQUIPO"):
                    if n_e:
                        nuevo_e = pd.DataFrame([{"Nombre": n_e.strip()}])
                        df_res = pd.concat([df_e, nuevo_e], ignore_index=True).drop_duplicates()
                        guardar(df_res, "data_equipos.csv")
                        st.success("Equipo guardado"); st.rerun()
            
            if not df_e.empty:
                st.write("---")
                e_borrar = st.selectbox("Selecciona equipo para ELIMINAR:", df_e["Nombre"].tolist())
                if st.button("🗑️ ELIMINAR EQUIPO SELECCIONADO"):
                    df_res = df_e[df_e["Nombre"] != e_borrar]
                    guardar(df_res, "data_equipos.csv")
                    st.warning(f"Equipo {e_borrar} eliminado"); st.rerun()
                st.table(df_e)

        with tab2:
            st.subheader("Gestión de Jugadores")
            df_j = cargar("data_jugadores.csv")
            df_e = cargar("data_equipos.csv")
            
            if df_e.empty:
                st.warning("⚠️ Primero debes crear un equipo en la pestaña anterior.")
            else:
                with st.form("f_jugadores"):
                    nom_j = st.text_input("Nombre del Jugador:")
                    eq_j = st.selectbox("Asignar a Equipo:", df_e["Nombre"].tolist())
                    c1, c2, c3, c4 = st.columns(4)
                    vb = c1.number_input("VB", 0); h = c2.number_input("H", 0)
                    h2 = c3.number_input("H2", 0); hr = c4.number_input("HR", 0)
                    if st.form_submit_button("💾 GUARDAR JUGADOR"):
                        nuevo_j = pd.DataFrame([{"Nombre": nom_j, "Equipo": eq_j, "VB": vb, "H": h, "H2": h2, "H3": 0, "HR": hr}])
                        df_res = pd.concat([df_j, nuevo_j], ignore_index=True)
                        guardar(df_res, "data_jugadores.csv")
                        st.success("Jugador guardado"); st.rerun()
                
                if not df_j.empty:
                    st.write("---")
                    j_borrar = st.selectbox("Selecciona jugador para ELIMINAR:", df_j["Nombre"].tolist())
                    if st.button("🗑️ ELIMINAR JUGADOR"):
                        df_res = df_j[df_j["Nombre"] != j_borrar]
                        guardar(df_res, "data_jugadores.csv")
                        st.rerun()
                    st.dataframe(df_j, use_container_width=True)

        with tab3:
            st.subheader("Calendario (Edición Rápida)")
            df_c = cargar("data_calendario.csv")
            if df_c.empty:
                df_c = pd.DataFrame(columns=["Jornada", "Fecha", "Local", "Visitante", "Score"])
            
            ed_cal = st.data_editor(df_c, num_rows="dynamic", use_container_width=True)
            if st.button("💾 GUARDAR TODO EL CALENDARIO"):
                guardar(ed_cal, "data_calendario.csv")
                st.success("Calendario actualizado"); st.rerun()

# --- 5. ROSTERS (LECTURA LÍMPIA) ---
elif menu == "📋 Rosters":
    st.title("📋 Rosters")
    df_e = cargar("data_equipos.csv")
    df_j = cargar("data_jugadores.csv")

    if not df_e.empty:
        eq_sel = st.selectbox("Selecciona Equipo:", df_e["Nombre"].tolist())
        db = df_j[df_j["Equipo"] == eq_sel].copy()
        if not db.empty:
            db["AVG"] = (db["H"] / db["VB"].replace(0,1)).fillna(0)
            st.dataframe(db[["Nombre", "VB", "H", "H2", "HR", "AVG"]].sort_values("AVG", ascending=False), use_container_width=True, hide_index=True)
        else: st.info("No hay jugadores en este equipo.")
    else: st.warning("No hay equipos registrados.")

elif menu == "🏠 Inicio":
    st.title("⚾ LIGA DOMINICAL 2026")
    df_c = cargar("data_calendario.csv")
    if not df_c.empty: st.table(df_c)
