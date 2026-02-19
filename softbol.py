import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN DE DATOS ---
CARPETA_DATOS = "datos_liga"
if not os.path.exists(CARPETA_DATOS):
    os.makedirs(CARPETA_DATOS)

def ruta(archivo):
    return os.path.join(CARPETA_DATOS, archivo)

# Inicializar base de datos con todas las categorías de bases
def inicializar_datos():
    if 'equipos' not in st.session_state:
        st.session_state.equipos = pd.read_csv(ruta("data_equipos.csv")) if os.path.exists(ruta("data_equipos.csv")) else pd.DataFrame(columns=["Nombre"])

    if 'jugadores' not in st.session_state:
        if os.path.exists(ruta("data_jugadores.csv")):
            df = pd.read_csv(ruta("data_jugadores.csv"))
            # Asegurar que existan todas las columnas de hits
            for col in ["H", "H2", "H3", "HR"]:
                if col not in df.columns: df[col] = 0
            st.session_state.jugadores = df
        else:
            st.session_state.jugadores = pd.DataFrame(columns=["Nombre", "Edad", "Equipo", "H", "H2", "H3", "HR"])

def guardar_datos():
    st.session_state.equipos.to_csv(ruta("data_equipos.csv"), index=False)
    st.session_state.jugadores.to_csv(ruta("data_jugadores.csv"), index=False)

inicializar_datos()

# --- 2. BARRA LATERAL (LOGIN) ---
st.sidebar.title("⚾ LIGA SOFTBOL 2026")
with st.sidebar.form("login_form"):
    pwd_input = st.text_input("Contraseña Admin:", type="password")
    if st.form_submit_button("Entrar"): pass

pass_maestra = open(ruta("config.txt"), "r").read().strip() if os.path.exists(ruta("config.txt")) else "softbol2026"
es_admin = (pwd_input == pass_maestra)

menu = st.sidebar.radio("MENÚ:", ["🏠 Inicio", "👥 Equipos", "🏃 Jugadores y Stats", "📊 Consulta por Equipo"])

# ==========================================
# SECCIÓN: JUGADORES (H, H2, H3, HR)
# ==========================================
if menu == "🏃 Jugadores y Stats":
    st.header("🏃 Gestión de Jugadores y Estadísticas")
    lista_eq = st.session_state.equipos['Nombre'].tolist()
    
    if es_admin:
        with st.expander("➕ Registrar Nuevo Jugador"):
            with st.form("nuevo_j"):
                c1, c2, c3 = st.columns(3)
                nj = c1.text_input("Nombre Completo")
                edj = c2.number_input("Edad", 5, 90, 20)
                eqj = c3.selectbox("Equipo", lista_eq if lista_eq else ["Sin equipos"])
                if st.form_submit_button("Registrar"):
                    if nj and lista_eq:
                        nuevo = pd.DataFrame([{"Nombre": nj, "Edad": edj, "Equipo": eqj, "H": 0, "H2": 0, "H3": 0, "HR": 0}])
                        st.session_state.jugadores = pd.concat([st.session_state.jugadores, nuevo], ignore_index=True)
                        guardar_datos(); st.rerun()

        st.divider()
        st.subheader("✏️ Actualizar Estadísticas (H, H2, H3, HR)")
        if not st.session_state.jugadores.empty:
            j_sel = st.selectbox("Selecciona Jugador:", st.session_state.jugadores['Nombre'])
            idx = st.session_state.jugadores[st.session_state.jugadores['Nombre'] == j_sel].index[0]
            datos_j = st.session_state.jugadores.iloc[idx]
            
            with st.form("edit_stats_pro"):
                c1, c2, c3 = st.columns(3)
                enom = c1.text_input("Nombre", value=str(datos_j['Nombre']))
                eedad = c2.number_input("Edad", 5, 90, int(datos_j['Edad']))
                eequipo = c3.selectbox("Equipo", lista_eq, index=lista_eq.index(datos_j['Equipo']) if datos_j['Equipo'] in lista_eq else 0)
                
                st.write("--- **Ingreso de Hits por tipo** ---")
                c4, c5, c6, c7 = st.columns(4)
                eh = c4.number_input("Sencillos (H)", 0, value=int(datos_j['H']))
                eh2 = c5.number_input("Dobles (H2)", 0, value=int(datos_j['H2']))
                eh3 = c6.number_input("Triples (H3)", 0, value=int(datos_j['H3']))
                ehr = c7.number_input("Jonrones (HR)", 0, value=int(datos_j['HR']))
                
                if st.form_submit_button("Guardar Cambios"):
                    st.session_state.jugadores.at[idx, 'Nombre'] = enom
                    st.session_state.jugadores.at[idx, 'Edad'] = eedad
                    st.session_state.jugadores.at[idx, 'Equipo'] = eequipo
                    st.session_state.jugadores.at[idx, 'H'] = eh
                    st.session_state.jugadores.at[idx, 'H2'] = eh2
                    st.session_state.jugadores.at[idx, 'H3'] = eh3
                    st.session_state.jugadores.at[idx, 'HR'] = ehr
                    guardar_datos(); st.success("¡Estadísticas actualizadas!"); st.rerun()

    # Tabla General con cálculo de Hits Totales
    st.subheader("Roster de la Liga")
    df_visual = st.session_state.jugadores.copy()
    df_visual["Hits Totales"] = df_visual["H"] + df_visual["H2"] + df_visual["H3"] + df_visual["HR"]
    st.dataframe(df_visual[["Nombre", "Equipo", "H", "H2", "H3", "HR", "Hits Totales"]], use_container_width=True)

# ==========================================
# SECCIÓN: CONSULTA POR EQUIPO
# ==========================================
elif menu == "📊 Consulta por Equipo":
    st.header("📊 Consulta por Equipo")
    lista_eq = st.session_state.equipos['Nombre'].tolist()
    if lista_eq:
        f_eq = st.selectbox("Selecciona Equipo:", lista_eq)
        res = st.session_state.jugadores[st.session_state.jugadores['Equipo'] == f_eq].copy()
        res["Hits Totales"] = res["H"] + res["H2"] + res["H3"] + res["HR"]
        st.dataframe(res[["Nombre", "H", "H2", "H3", "HR", "Hits Totales"]], use_container_width=True)
