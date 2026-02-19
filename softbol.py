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
def leer_csv(nombre, columnas):
    p = path_archivo(nombre)
    if os.path.exists(p):
        df = pd.read_csv(p)
        df.columns = df.columns.str.strip()
        return df
    return pd.DataFrame(columns=columnas)

# Variables de Sesión
if 'rol' not in st.session_state: st.session_state.rol = "Invitado"

# Carga forzada de datos frescos
jugadores = leer_csv("data_jugadores.csv", ["Nombre","Equipo","VB","H","H2","H3","HR"])
pitchers = leer_csv("data_pitchers.csv", ["Nombre","Equipo","JG","JP","IP","CL","K"])
equipos = leer_csv("data_equipos.csv", ["Nombre"])
calendario = leer_csv("data_calendario.csv", ["Jornada","Fecha","Hora","Campo","Local","Visitante","Score"])

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

# --- 4. ZONA ADMIN (GUARDAR Y ELIMINAR DIRECTO) ---
if menu == "🏃 Admin General":
    if st.session_state.rol != "Admin": st.error("Acceso Denegado")
    else:
        st.title("⚙️ Gestión Maestra")
        st.info("📌 **Para EDITAR:** Haz clic en la celda. **Para ELIMINAR:** Selecciona la fila y presiona 'Delete' o el icono de basura. **Para GUARDAR:** Presiona el botón rojo debajo de la tabla.")
        
        t_eq, t_bat, t_pit, t_cal = st.tabs(["🏆 Equipos", "🥖 Bateadores", "🔥 Pitchers", "📅 Calendario"])

        with t_eq:
            st.subheader("Equipos Registrados")
            # num_rows="dynamic" permite añadir (+) y eliminar celdas
            ed_eq = st.data_editor(equipos, num_rows="dynamic", use_container_width=True, key="ed_equipos")
            if st.button("💾 GUARDAR CAMBIOS EN EQUIPOS"):
                ed_eq.to_csv(path_archivo("data_equipos.csv"), index=False)
                st.success("Equipos actualizados correctamente"); st.rerun()

        with t_bat:
            st.subheader("Estadísticas de Bateo")
            ed_bat = st.data_editor(jugadores, num_rows="dynamic", use_container_width=True, key="ed_bateo")
            if st.button("💾 GUARDAR CAMBIOS EN BATEADORES"):
                ed_bat.to_csv(path_archivo("data_jugadores.csv"), index=False)
                st.success("Bateadores actualizados correctamente"); st.rerun()

        with t_pit:
            st.subheader("Estadísticas de Pitcheo")
            ed_pit = st.data_editor(pitchers, num_rows="dynamic", use_container_width=True, key="ed_pitcheo")
            if st.button("💾 GUARDAR CAMBIOS EN PITCHERS"):
                ed_pit.to_csv(path_archivo("data_pitchers.csv"), index=False)
                st.success("Pitchers actualizados correctamente"); st.rerun()

        with t_cal:
            st.subheader("Calendario de Jornadas")
            ed_cal = st.data_editor(calendario, num_rows="dynamic", use_container_width=True, key="ed_calendario")
            if st.button("💾 GUARDAR CAMBIOS EN CALENDARIO"):
                ed_cal.to_csv(path_archivo("data_calendario.csv"), index=False)
                st.success("Calendario actualizado correctamente"); st.rerun()

# --- 5. ROSTERS (LECTURA LIMPIA) ---
elif menu == "📋 Rosters":
    st.title("📋 Rosters")
    if not equipos.empty:
        lista_nombres = sorted(equipos["Nombre"].astype(str).unique().tolist())
        eq_sel = st.selectbox("Selecciona Equipo:", lista_nombres)
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Bateadores")
            db = jugadores[jugadores["Equipo"].astype(str).str.strip() == eq_sel].copy()
            if not db.empty:
                db["AVG"] = ((db["H"]+db["H2"]+db["H3"]+db["HR"])/db["VB"].replace(0,1)).fillna(0)
                st.dataframe(db.style.format({"AVG": "{:.3f}"}), use_container_width=True, hide_index=True)
            else: st.info("No hay bateadores.")
        with c2:
            st.subheader("Pitchers")
            dp = pitchers[pitchers["Equipo"].astype(str).str.strip() == eq_sel].copy()
            st.dataframe(dp, use_container_width=True, hide_index=True)
    else: st.warning("No hay equipos registrados.")

# --- 6. INICIO Y LÍDERES ---
elif menu == "🏠 Inicio":
    st.title("⚾ LIGA DOMINICAL 2026")
    st.dataframe(calendario, use_container_width=True, hide_index=True)

elif menu == "🏆 LÍDERES":
    st.title("🥇 Cuadro de Honor")
    if not jugadores.empty:
        df = jugadores.copy()
        df["AVG"] = ((df["H"]+df["H2"]+df["H3"]+df["HR"]) / df["VB"].replace(0,1)).fillna(0)
        st.table(df.sort_values("AVG", ascending=False).head(5)[["Nombre", "Equipo", "AVG"]])
