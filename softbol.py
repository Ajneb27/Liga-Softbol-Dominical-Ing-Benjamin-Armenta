import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="LIGA SOFTBOL", page_icon="⚾", layout="wide")

DATOS_DIR = "datos_liga"
if not os.path.exists(DATOS_DIR): os.makedirs(DATOS_DIR)

def path_archivo(n): return os.path.join(DATOS_DIR, n)

# --- 2. CARGA DE DATOS (LECTURA DIRECTA DE DISCO) ---
def cargar(nombre, columnas):
    p = path_archivo(nombre)
    if os.path.exists(p):
        return pd.read_csv(p)
    return pd.DataFrame(columns=columnas)

# --- 3. LOGIN ---
if 'rol' not in st.session_state: st.session_state.rol = "Invitado"

with st.sidebar:
    st.title("🥎 LIGA DOMINICAL")
    if st.session_state.rol == "Invitado":
        pwd = st.text_input("Contraseña Admin:", type="password")
        if st.button("ENTRAR"):
            if pwd == "softbol2026": 
                st.session_state.rol = "Admin"
                st.rerun()
    else:
        if st.button("SALIR"): 
            st.session_state.rol = "Invitado"
            st.rerun()
    
    menu = st.radio("MENÚ:", ["🏠 Inicio", "🏆 LÍDERES", "📊 Standings", "📋 Rosters", "⚙️ Admin General"])

# --- 4. ZONA ADMIN (EDICIÓN Y ELIMINACIÓN) ---
if menu == "⚙️ Admin General":
    if st.session_state.rol != "Admin":
        st.error("Acceso Denegado")
    else:
        st.title("⚙️ Panel de Control")
        st.info("💡 **Para Borrar:** Selecciona la fila y presiona 'Delete'. **Para Guardar:** Presiona el botón de abajo.")

        tab1, tab2, tab3, tab4 = st.tabs(["Equipos", "Bateadores", "Pitchers", "Calendario"])

        with tab1:
            df_e = cargar("data_equipos.csv", ["Nombre"])
            ed_e = st.data_editor(df_e, num_rows="dynamic", use_container_width=True, key="ed_eq")
            if st.button("💾 GUARDAR EQUIPOS"):
                ed_e.to_csv(path_archivo("data_equipos.csv"), index=False)
                st.success("Equipos Guardados"); st.rerun()

        with tab2:
            df_j = cargar("data_jugadores.csv", ["Nombre","Equipo","VB","H","H2","H3","HR"])
            ed_j = st.data_editor(df_j, num_rows="dynamic", use_container_width=True, key="ed_bat")
            if st.button("💾 GUARDAR BATEADORES"):
                ed_j.to_csv(path_archivo("data_jugadores.csv"), index=False)
                st.success("Bateadores Guardados"); st.rerun()

        with tab3:
            df_p = cargar("data_pitchers.csv", ["Nombre","Equipo","JG","JP","IP","CL","K"])
            ed_p = st.data_editor(df_p, num_rows="dynamic", use_container_width=True, key="ed_pit")
            if st.button("💾 GUARDAR PITCHERS"):
                ed_p.to_csv(path_archivo("data_pitchers.csv"), index=False)
                st.success("Pitchers Guardados"); st.rerun()

        with tab4:
            df_c = cargar("data_calendario.csv", ["Jornada","Fecha","Hora","Campo","Local","Visitante","Score"])
            ed_c = st.data_editor(df_c, num_rows="dynamic", use_container_width=True, key="ed_cal")
            if st.button("💾 GUARDAR CALENDARIO"):
                ed_c.to_csv(path_archivo("data_calendario.csv"), index=False)
                st.success("Calendario Guardado"); st.rerun()

# --- 5. ROSTERS (FILTRO AUTOMÁTICO) ---
elif menu == "📋 Rosters":
    st.title("📋 Rosters")
    df_e = cargar("data_equipos.csv", ["Nombre"])
    df_j = cargar("data_jugadores.csv", ["Nombre","Equipo","VB","H","H2","H3","HR"])
    df_p = cargar("data_pitchers.csv", ["Nombre","Equipo","JG","JP","IP","CL","K"])

    if not df_e.empty:
        # Limpieza de datos para que el filtro no falle
        df_j["Equipo"] = df_j["Equipo"].astype(str).str.strip()
        df_p["Equipo"] = df_p["Equipo"].astype(str).str.strip()
        
        lista_equipos = sorted(df_e["Nombre"].astype(str).str.strip().unique().tolist())
        equipo = st.selectbox("Selecciona Equipo:", lista_equipos)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🥖 Bateadores")
            # Filtro exacto
            filtro_b = df_j[df_j["Equipo"] == equipo].copy()
            if not filtro_b.empty:
                filtro_b["AVG"] = ((filtro_b["H"]+filtro_b["H2"]+filtro_b["H3"]+filtro_b["HR"])/filtro_b["VB"].replace(0,1)).fillna(0)
                st.dataframe(filtro_b[["Nombre","VB","H","H2","H3","HR","AVG"]].sort_values("AVG", ascending=False), use_container_width=True, hide_index=True)
            else: st.info("No hay bateadores.")
            
        with col2:
            st.subheader("🔥 Pitchers")
            filtro_p = df_p[df_p["Equipo"] == equipo].copy()
            if not filtro_p.empty:
                st.dataframe(filtro_p[["Nombre","JG","JP","IP","K"]], use_container_width=True, hide_index=True)
            else: st.info("No hay pitchers.")
    else: st.warning("No hay equipos registrados.")

# --- 6. INICIO Y LÍDERES ---
elif menu == "🏠 Inicio":
    st.title("⚾ LIGA DOMINICAL 2026")
    df_c = cargar("data_calendario.csv", ["Jornada","Fecha","Hora","Campo","Local","Visitante","Score"])
    st.table(df_c)

elif menu == "🏆 LÍDERES":
    st.title("🥇 Líderes")
    df_j = cargar("data_jugadores.csv", ["Nombre","Equipo","VB","H","H2","H3","HR"])
    if not df_j.empty:
        df_j["AVG"] = ((df_j["H"]+df_j["H2"]+df_j["H3"]+df_j["HR"]) / df_j["VB"].replace(0,1)).fillna(0)
        st.table(df_j.sort_values("AVG", ascending=False).head(5)[["Nombre", "Equipo", "AVG"]])
