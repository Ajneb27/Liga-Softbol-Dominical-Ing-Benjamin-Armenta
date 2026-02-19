import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN DE DATOS ---
CARPETA_DATOS = "datos_liga"
if not os.path.exists(CARPETA_DATOS): os.makedirs(CARPETA_DATOS)

def ruta(archivo): return os.path.join(CARPETA_DATOS, archivo)

COLS_J = ["Nombre", "Edad", "Equipo", "VB", "H", "H2", "H3", "HR"]

def cargar_jugadores():
    if os.path.exists(ruta("data_jugadores.csv")):
        df = pd.read_csv(ruta("data_jugadores.csv"))
        df.columns = df.columns.str.strip()
        for col in COLS_J:
            if col not in df.columns: df[col] = 0
        for c in ["VB", "H", "H2", "H3", "HR"]:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
        return df[COLS_J]
    return pd.DataFrame(columns=COLS_J)

if 'jugadores' not in st.session_state: st.session_state.jugadores = cargar_jugadores()
if 'equipos' not in st.session_state:
    st.session_state.equipos = pd.read_csv(ruta("data_equipos.csv")) if os.path.exists(ruta("data_equipos.csv")) else pd.DataFrame(columns=["Nombre"])

# --- 2. SEGURIDAD (LOGIN) ---
st.sidebar.title("⚾ LIGA SOFTBOL 2026")
with st.sidebar.form("login"):
    pwd = st.text_input("Contraseña Admin:", type="password")
    submit_login = st.form_submit_button("Validar Acceso")

# Tu clave de administrador
CLAVE_ADMIN = "softbol2026" 
es_admin = (pwd == CLAVE_ADMIN)

if es_admin:
    st.sidebar.success("🔓 MODO ADMINISTRADOR")
else:
    st.sidebar.info("🔒 MODO LECTURA")

menu = st.sidebar.radio("MENÚ:", ["🏆 TOP 10 LÍDERES", "🏃 Bateo", "👥 Equipos"])

# ==========================================
# SECCIÓN: TOP 10 LÍDERES (PÚBLICO)
# ==========================================
if menu == "🏆 TOP 10 LÍDERES":
    st.header("🏆 Líderes de la Liga (Milésimas)")
    df_l = st.session_state.jugadores.copy()
    if not df_l.empty:
        # Cálculo de AVG automático
        hits = df_l['H'] + df_l['H2'] + df_l['H3'] + df_l['HR']
        df_l['AVG'] = (hits / df_l['VB'].replace(0, 1)).fillna(0)
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🥇 Promedio (AVG)")
            res_avg = df_l.sort_values("AVG", ascending=False).head(10)[["Nombre", "AVG"]]
            st.table(res_avg.style.format({"AVG": "{:.3f}"}))
            st.subheader("🥇 Jonrones (HR)")
            st.table(df_l.sort_values("HR", ascending=False).head(10)[["Nombre", "HR"]])
        with c2:
            st.subheader("🥇 Triples (H3)")
            st.table(df_l.sort_values("H3", ascending=False).head(10)[["Nombre", "H3"]])
            st.subheader("🥇 Dobles (H2)")
            st.table(df_l.sort_values("H2", ascending=False).head(10)[["Nombre", "H2"]])
    else: st.info("No hay datos cargados.")

# ==========================================
# SECCIÓN: BATEO (EDICIÓN RESTRINGIDA)
# ==========================================
elif menu == "🏃 Bateo":
    st.header("🏃 Estadísticas de Bateo")
    
    # SOLO EL ADMIN PUEDE VER EL FORMULARIO
    if es_admin:
        with st.expander("🛠️ PANEL DE EDICIÓN Y REGISTRO", expanded=True):
            lista_nombres = ["-- Nuevo Registro --"] + sorted(st.session_state.jugadores["Nombre"].tolist())
            seleccion = st.selectbox("Selecciona un jugador para EDITAR o deja en 'Nuevo':", lista_nombres)
            
            v_nom, v_eq, v_vb, v_h, v_h2, v_h3, v_hr = "", "", 1, 0, 0, 0, 0
            if seleccion != "-- Nuevo Registro --":
                fila = st.session_state.jugadores[st.session_state.jugadores["Nombre"] == seleccion].iloc[0]
                v_nom, v_eq, v_vb, v_h, v_h2, v_h3, v_hr = fila["Nombre"], fila["Equipo"], int(fila["VB"]), int(fila["H"]), int(fila["H2"]), int(fila["H3"]), int(fila["HR"])

            with st.form("form_bateo"):
                nom = st.text_input("Nombre Completo", value=v_nom)
                eq = st.selectbox("Equipo", st.session_state.equipos["Nombre"].tolist() if not st.session_state.equipos.empty else ["N/A"])
                col1, col2, col3, col4, col5 = st.columns(5)
                vb = col1.number_input("VB", min_value=1, value=v_vb)
                h = col2.number_input("H1", value=v_h); h2 = col3.number_input("H2", value=v_h2)
                h3 = col4.number_input("H3", value=v_h3); hr = col5.number_input("HR", value=v_hr)
                
                if st.form_submit_button("💾 ACTUALIZAR / GUARDAR"):
                    if not nom: st.error("El nombre es necesario.")
                    else:
                        # Si editamos, quitamos el registro previo para no duplicar
                        if seleccion != "-- Nuevo Registro --":
                            st.session_state.jugadores = st.session_state.jugadores[st.session_state.jugadores["Nombre"] != seleccion]
                        
                        nueva_fila = pd.DataFrame([{"Nombre": nom, "Edad": 0, "Equipo": eq, "VB": vb, "H": h, "H2": h2, "H3": h3, "HR": hr}])
                        st.session_state.jugadores = pd.concat([st.session_state.jugadores, nueva_fila], ignore_index=True)
                        st.session_state.jugadores.to_csv(ruta("data_jugadores.csv"), index=False)
                        st.success("¡Datos actualizados!"); st.rerun()

        if not st.session_state.jugadores.empty:
            with st.expander("🗑️ ZONA DE ELIMINACIÓN"):
                borrar_sel = st.selectbox("Selecciona jugador a BORRAR:", st.session_state.jugadores["Nombre"].tolist())
                if st.button("BORRAR PERMANENTEMENTE ❌"):
                    st.session_state.jugadores = st.session_state.jugadores[st.session_state.jugadores["Nombre"] != borrar_sel]
                    st.session_state.jugadores.to_csv(ruta("data_jugadores.csv"), index=False)
                    st.rerun()
    else:
        st.warning("⚠️ Acceso restringido. Solo el administrador puede editar o borrar jugadores.")

    st.subheader("📋 Tabla General")
    st.dataframe(st.session_state.jugadores, use_container_width=True)

# ==========================================
# SECCIÓN: EQUIPOS (RESTRINGIDA)
# ==========================================
elif menu == "👥 Equipos":
    st.header("👥 Equipos de la Liga")
    if es_admin:
        with st.form("nuevo_e"):
            n_e = st.text_input("Nombre del Nuevo Equipo")
            if st.form_submit_button("Registrar Equipo"):
                st.session_state.equipos = pd.concat([st.session_state.equipos, pd.DataFrame([{"Nombre": n_e}])], ignore_index=True)
                st.session_state.equipos.to_csv(ruta("data_equipos.csv"), index=False)
                st.rerun()
    
    st.table(st.session_state.equipos)
