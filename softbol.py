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

# --- 2. SEGURIDAD (LOGIN / LOGOUT) ---
st.sidebar.title("⚾ LIGA SOFTBOL 2026")

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    with st.sidebar.form("login"):
        pwd = st.text_input("Contraseña Admin:", type="password")
        if st.form_submit_button("Validar Acceso"):
            if pwd == "softbol2026":
                st.session_state.autenticado = True
                st.rerun()
            else: st.error("Clave incorrecta")
else:
    st.sidebar.success("🔓 MODO ADMINISTRADOR")
    if st.sidebar.button("Cerrar Sesión 🔒"):
        st.session_state.autenticado = False
        st.rerun()

es_admin = st.session_state.autenticado
menu = st.sidebar.radio("MENÚ:", ["🏠 Inicio", "🏆 TOP 10 LÍDERES", "📋 Rosters por Equipo", "🏃 Bateo (Admin)", "👥 Equipos"])

# ==========================================
# SECCIÓN: ROSTERS POR EQUIPO (NUEVA)
# ==========================================
if menu == "📋 Rosters por Equipo":
    st.header("📋 Roster Detallado por Equipo")
    
    if not st.session_state.equipos.empty:
        equipo_sel = st.selectbox("Selecciona un Equipo:", st.session_state.equipos["Nombre"].tolist())
        
        # Filtrar jugadores del equipo seleccionado
        df_roster = st.session_state.jugadores[st.session_state.jugadores["Equipo"] == equipo_sel].copy()
        
        if not df_roster.empty:
            # Calcular AVG para el roster
            hits = df_roster['H'] + df_roster['H2'] + df_roster['H3'] + df_roster['HR']
            df_roster['AVG'] = (hits / df_roster['VB'].replace(0, 1)).fillna(0)
            
            st.subheader(f"Jugadores de {equipo_sel}")
            # Mostrar tabla formateada con milésimas
            st.dataframe(
                df_roster[["Nombre", "VB", "H", "H2", "H3", "HR", "AVG"]].style.format({"AVG": "{:.3f}"}),
                use_container_width=True
            )
            
            # Resumen rápido del equipo
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Jugadores", len(df_roster))
            c2.metric("Total HR Equipo", int(df_roster["HR"].sum()))
            c3.metric("AVG Colectivo", f"{(df_roster['AVG'].mean()):.3f}")
        else:
            st.info(f"Aún no hay jugadores registrados en el equipo {equipo_sel}.")
    else:
        st.warning("Primero debes registrar equipos en la sección '👥 Equipos'.")

# ==========================================
# SECCIÓN: TOP 10 LÍDERES
# ==========================================
elif menu == "🏆 TOP 10 LÍDERES":
    st.header("🏆 Líderes de la Liga (Milésimas)")
    df_l = st.session_state.jugadores.copy()
    if not df_l.empty:
        hits = df_l['H'] + df_l['H2'] + df_l['H3'] + df_l['HR']
        df_l['AVG'] = (hits / df_l['VB'].replace(0, 1)).fillna(0)
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🥇 Promedio (AVG)")
            res_avg = df_l.sort_values("AVG", ascending=False).head(10)[["Nombre", "AVG"]]
            st.table(res_avg.style.format({"AVG": "{:.3f}"}))
        with c2:
            st.subheader("🥇 Jonrones (HR)")
            st.table(df_l.sort_values("HR", ascending=False).head(10)[["Nombre", "HR"]])
    else: st.info("No hay datos cargados.")

# ==========================================
# SECCIÓN: BATEO (ADMIN)
# ==========================================
elif menu == "🏃 Bateo (Admin)":
    st.header("🏃 Gestión de Estadísticas")
    if es_admin:
        with st.expander("🛠️ EDITAR / REGISTRAR JUGADOR", expanded=True):
            lista_n = ["-- Nuevo --"] + sorted(st.session_state.jugadores["Nombre"].tolist())
            sel = st.selectbox("Buscar jugador:", lista_n)
            
            v_n, v_eq, v_vb, v_h, v_h2, v_h3, v_hr = "", "", 1, 0, 0, 0, 0
            if sel != "-- Nuevo --":
                d = st.session_state.jugadores[st.session_state.jugadores["Nombre"] == sel].iloc[0]
                v_n, v_eq, v_vb, v_h, v_h2, v_h3, v_hr = d["Nombre"], d["Equipo"], int(d["VB"]), int(d["H"]), int(d["H2"]), int(d["H3"]), int(d["HR"])

            with st.form("f_bateo"):
                nom = st.text_input("Nombre", value=v_n)
                eq = st.selectbox("Equipo", st.session_state.equipos["Nombre"].tolist() if not st.session_state.equipos.empty else ["N/A"])
                col1, col2, col3, col4, col5 = st.columns(5)
                vb = col1.number_input("VB", min_value=1, value=v_vb)
                h = col2.number_input("H1", value=v_h); h2 = col3.number_input("H2", value=v_h2)
                h3 = col4.number_input("H3", value=v_h3); hr = col5.number_input("HR", value=v_hr)
                
                if st.form_submit_button("💾 GUARDAR"):
                    if sel != "-- Nuevo --":
                        st.session_state.jugadores = st.session_state.jugadores[st.session_state.jugadores["Nombre"] != sel]
                    nueva = pd.DataFrame([{"Nombre": nom, "Edad": 0, "Equipo": eq, "VB": vb, "H": h, "H2": h2, "H3": h3, "HR": hr}])
                    st.session_state.jugadores = pd.concat([st.session_state.jugadores, nueva], ignore_index=True)
                    st.session_state.jugadores.to_csv(ruta("data_jugadores.csv"), index=False)
                    st.rerun()

        with st.expander("🗑️ BORRAR JUGADOR"):
            b_sel = st.selectbox("Selecciona para borrar:", st.session_state.jugadores["Nombre"].tolist())
            if st.button("BORRAR ❌"):
                st.session_state.jugadores = st.session_state.jugadores[st.session_state.jugadores["Nombre"] != b_sel]
                st.session_state.jugadores.to_csv(ruta("data_jugadores.csv"), index=False)
                st.rerun()
    else:
        st.warning("Inicia sesión como Admin para modificar datos.")
    st.dataframe(st.session_state.jugadores)

# ==========================================
# SECCIÓN: EQUIPOS E INICIO
# ==========================================
elif menu == "👥 Equipos":
    st.header("👥 Equipos")
    if es_admin:
        n_e = st.text_input("Nombre Equipo")
        if st.button("Registrar"):
            st.session_state.equipos = pd.concat([st.session_state.equipos, pd.DataFrame([{"Nombre": n_e}])], ignore_index=True)
            st.session_state.equipos.to_csv(ruta("data_equipos.csv"), index=False)
            st.rerun()
    st.table(st.session_state.equipos)

elif menu == "🏠 Inicio":
    st.title("⚾ Liga de Softbol 2026")
    st.write("Bienvenido al sistema oficial de estadísticas. Usa el menú lateral para navegar.")
