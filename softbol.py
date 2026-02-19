import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN DE CARPETA ---
CARPETA_DATOS = "datos_liga"
if not os.path.exists(CARPETA_DATOS):
    os.makedirs(CARPETA_DATOS)

def ruta(archivo):
    return os.path.join(CARPETA_DATOS, archivo)

# --- 2. FUNCIÓN DE LIMPIEZA FORZADA (ESTO ARREGLA EL ERROR) ---
def cargar_datos_limpios():
    cols = ["Nombre", "Edad", "Equipo", "H", "H2", "H3", "HR"]
    path_jugadores = ruta("data_jugadores.csv")
    
    if os.path.exists(path_jugadores):
        try:
            df = pd.read_csv(path_jugadores)
            # Si detecta que faltan H2 o H3, las crea con ceros
            for c in cols:
                if c not in df.columns:
                    df[c] = 0
            return df
        except:
            return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

# Inicializar datos en la sesión
if 'jugadores' not in st.session_state:
    st.session_state.jugadores = cargar_datos_limpios()

if 'equipos' not in st.session_state:
    st.session_state.equipos = pd.read_csv(ruta("data_equipos.csv")) if os.path.exists(ruta("data_equipos.csv")) else pd.DataFrame(columns=["Nombre"])

def guardar_datos():
    st.session_state.equipos.to_csv(ruta("data_equipos.csv"), index=False)
    st.session_state.jugadores.to_csv(ruta("data_jugadores.csv"), index=False)

# --- 3. BARRA LATERAL (LOGIN) ---
st.sidebar.title("⚾ LIGA SOFTBOL 2026")
pwd = st.sidebar.text_input("Contraseña Admin:", type="password")
pass_maestra = open(ruta("config.txt"), "r").read().strip() if os.path.exists(ruta("config.txt")) else "softbol2026"
es_admin = (pwd == pass_maestra)

menu = st.sidebar.radio("MENÚ:", ["🏠 Inicio", "👥 Equipos", "🏃 Jugadores y Stats", "⚙️ MANTENIMIENTO"])

# ==========================================
# SECCIÓN: MANTENIMIENTO (PARA BORRAR SI NADA FUNCIONA)
# ==========================================
if menu == "⚙️ MANTENIMIENTO":
    st.header("⚙️ Herramientas de Reparación")
    if es_admin:
        st.warning("Usa este botón solo si el error rojo persiste.")
        if st.button("🔥 REPARAR BASE DE DATOS (RESET)"):
            if os.path.exists(ruta("data_jugadores.csv")):
                os.remove(ruta("data_jugadores.csv"))
            st.session_state.jugadores = pd.DataFrame(columns=["Nombre", "Edad", "Equipo", "H", "H2", "H3", "HR"])
            guardar_datos()
            st.success("¡Base de datos reparada! Ya puedes registrar H2 y H3.")
            st.rerun()
    else:
        st.error("Ingresa la clave para reparar.")

# ==========================================
# SECCIÓN: JUGADORES (H, H2, H3, HR)
# ==========================================
elif menu == "🏃 Jugadores y Stats":
    st.header("🏃 Estadísticas de Jugadores")
    lista_eq = st.session_state.equipos['Nombre'].tolist()
    
    if es_admin:
        with st.expander("➕ Nuevo Jugador"):
            with st.form("f_n"):
                n, ed = st.text_input("Nombre"), st.number_input("Edad", 5, 90, 20)
                eq = st.selectbox("Equipo", lista_eq if lista_eq else ["Sin equipos"])
                if st.form_submit_button("Guardar"):
                    nuevo = pd.DataFrame([{"Nombre": n, "Edad": ed, "Equipo": eq, "H": 0, "H2": 0, "H3": 0, "HR": 0}])
                    st.session_state.jugadores = pd.concat([st.session_state.jugadores, nuevo], ignore_index=True)
                    guardar_datos(); st.rerun()

        if not st.session_state.jugadores.empty:
            st.subheader("✏️ Editar Stats")
            j_sel = st.selectbox("Elegir Jugador:", st.session_state.jugadores['Nombre'])
            idx = st.session_state.jugadores[st.session_state.jugadores['Nombre'] == j_sel].index[0]
            d = st.session_state.jugadores.iloc[idx]
            
            with st.form("f_ed"):
                c1, c2, c3, c4 = st.columns(4)
                h1 = c1.number_input("H", value=int(d.get('H', 0)))
                h2 = c2.number_input("H2", value=int(d.get('H2', 0)))
                h3 = c3.number_input("H3", value=int(d.get('H3', 0)))
                hr = c4.number_input("HR", value=int(d.get('HR', 0)))
                if st.form_submit_button("Actualizar"):
                    st.session_state.jugadores.at[idx, 'H'] = h1
                    st.session_state.jugadores.at[idx, 'H2'] = h2
                    st.session_state.jugadores.at[idx, 'H3'] = h3
                    st.session_state.jugadores.at[idx, 'HR'] = hr
                    guardar_datos(); st.success("¡Actualizado!"); st.rerun()

    st.dataframe(st.session_state.jugadores, use_container_width=True)
