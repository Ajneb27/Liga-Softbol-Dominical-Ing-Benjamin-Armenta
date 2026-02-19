import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN DE DATOS ---
CARPETA_DATOS = "datos_liga"
if not os.path.exists(CARPETA_DATOS):
    os.makedirs(CARPETA_DATOS)

def ruta(archivo):
    return os.path.join(CARPETA_DATOS, archivo)

# --- FUNCIÓN CLAVE: REPARA EL ERROR DE COLUMNAS FALTANTES ---
def reparar_columnas(df):
    columnas_necesarias = ["Nombre", "Edad", "Equipo", "H", "H2", "H3", "HR"]
    for col in columnas_necesarias:
        if col not in df.columns:
            df[col] = 0  # Si no existe, la crea con ceros
    return df

def inicializar_datos():
    if 'equipos' not in st.session_state:
        if os.path.exists(ruta("data_equipos.csv")):
            st.session_state.equipos = pd.read_csv(ruta("data_equipos.csv"))
        else:
            st.session_state.equipos = pd.DataFrame(columns=["Nombre"])

    if 'jugadores' not in st.session_state:
        if os.path.exists(ruta("data_jugadores.csv")):
            df_temp = pd.read_csv(ruta("data_jugadores.csv"))
            # REPARAMOS ANTES DE CARGAR
            st.session_state.jugadores = reparar_columnas(df_temp)
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

menu = st.sidebar.radio("IR A:", ["🏠 Inicio", "👥 Equipos", "🏃 Jugadores y Stats", "📊 Consulta por Equipo"])

# ==========================================
# SECCIÓN: JUGADORES (YA NO DARÁ ERROR)
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
        st.subheader("✏️ Actualizar Estadísticas (H2=Dobles, H3=Triples)")
        if not st.session_state.jugadores.empty:
            j_sel = st.selectbox("Selecciona Jugador:", st.session_state.jugadores['Nombre'])
            # Usamos loc para evitar errores de índice
            datos_j = st.session_state.jugadores[st.session_state.jugadores['Nombre'] == j_sel].iloc[0]
            idx_j = st.session_state.jugadores[st.session_state.jugadores['Nombre'] == j_sel].index[0]
            
            with st.form("edit_stats_pro"):
                c1, c2, c3 = st.columns(3)
                enom = c1.text_input("Nombre", value=str(datos_j['Nombre']))
                eedad = c2.number_input("Edad", 5, 90, int(datos_j['Edad']))
                eequipo = c3.selectbox("Equipo", lista_eq, index=lista_eq.index(datos_j['Equipo']) if datos_j['Equipo'] in lista_eq else 0)
                
                st.write("--- **Bateo Acumulado** ---")
                c4, c5, c6, c7 = st.columns(4)
                eh = c4.number_input("Sencillos (H)", 0, value=int(datos_j['H']))
                eh2 = c5.number_input("Dobles (H2)", 0, value=int(datos_j['H2']))
                eh3 = c6.number_input("Triples (H3)", 0, value=int(datos_j['H3']))
                ehr = c7.number_input("Jonrones (HR)", 0, value=int(datos_j['HR']))
                
                if st.form_submit_button("Guardar Cambios"):
                    st.session_state.jugadores.at[idx_j, 'Nombre'] = enom
                    st.session_state.jugadores.at[idx_j, 'Edad'] = eedad
                    st.session_state.jugadores.at[idx_j, 'Equipo'] = eequipo
                    st.session_state.jugadores.at[idx_j, 'H'] = eh
                    st.session_state.jugadores.at[idx_j, 'H2'] = eh2
                    st.session_state.jugadores.at[idx_j, 'H3'] = eh3
                    st.session_state.jugadores.at[idx_j, 'HR'] = ehr
                    guardar_datos(); st.success("¡Estadísticas actualizadas!"); st.rerun()

    st.subheader("Roster General")
    df_v = st.session_state.jugadores.copy()
    df_v["Hits Totales"] = df_v["H"] + df_v["H2"] + df_v["H3"] + df_v["HR"]
    st.dataframe(df_v[["Nombre", "Equipo", "H", "H2", "H3", "HR", "Hits Totales"]], use_container_width=True)

elif menu == "📊 Consulta por Equipo":
    st.header("📊 Consulta por Equipo")
    lista_eq = st.session_state.equipos['Nombre'].tolist()
    if lista_eq:
        f_eq = st.selectbox("Selecciona Equipo:", lista_eq)
        res = st.session_state.jugadores[st.session_state.jugadores['Equipo'] == f_eq].copy()
        res["Hits Totales"] = res["H"] + res["H2"] + res["H3"] + res["HR"]
        st.dataframe(res[["Nombre", "H", "H2", "H3", "HR", "Hits Totales"]], use_container_width=True)
