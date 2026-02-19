import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN DE DATOS ---
CARPETA_DATOS = "datos_liga"
if not os.path.exists(CARPETA_DATOS): os.makedirs(CARPETA_DATOS)

def ruta(archivo): return os.path.join(CARPETA_DATOS, archivo)

# ESTRUCTURA EXACTA DE COLUMNAS (NO CAMBIAR)
COLS_J = ["Nombre", "Equipo", "VB", "H", "H2", "H3", "HR"]
COLS_P = ["Nombre", "Equipo", "JG", "JP", "IP", "CL"] 

def cargar_datos(archivo, columnas):
    path = ruta(archivo)
    if os.path.exists(path):
        df = pd.read_csv(path)
        df.columns = df.columns.str.strip()
        # Asegurar que todas las columnas existan
        for col in columnas:
            if col not in df.columns: df[col] = 0
        # Forzar que sean números
        cols_num = [c for c in columnas if c not in ["Nombre", "Equipo"]]
        df[cols_num] = df[cols_num].apply(pd.to_numeric, errors='coerce').fillna(0)
        return df[columnas]
    return pd.DataFrame(columns=columnas)

# Cargar bases de datos
if 'jugadores' not in st.session_state: st.session_state.jugadores = cargar_datos("data_jugadores.csv", COLS_J)
if 'pitchers' not in st.session_state: st.session_state.pitchers = cargar_datos("data_pitchers.csv", COLS_P)
if 'equipos' not in st.session_state:
    st.session_state.equipos = pd.read_csv(ruta("data_equipos.csv")) if os.path.exists(ruta("data_equipos.csv")) else pd.DataFrame(columns=["Nombre"])

# --- 2. SEGURIDAD (ADMIN) ---
st.sidebar.title("⚾ LIGA SOFTBOL 2026")
if 'autenticado' not in st.session_state: st.session_state.autenticado = False

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
menu = st.sidebar.radio("MENÚ:", ["🏠 Inicio", "🏆 TOP 10 LÍDERES", "📋 Rosters por Equipo", "🏃 Estadísticas (Admin)", "👥 Equipos"])

# ==========================================
# SECCIÓN: TOP 10 LÍDERES (RESTAURADA)
# ==========================================
if menu == "🏆 TOP 10 LÍDERES":
    tab_b, tab_p = st.tabs(["🥖 Bateo", "🔥 Pitcheo"])
    
    with tab_b:
        st.header("🏆 Líderes de Bateo")
        df_l = st.session_state.jugadores.copy()
        if not df_l.empty:
            # Cálculo de Hits Totales y AVG
            df_l['H+'] = df_l['H'] + df_l['H2'] + df_l['H3'] + df_l['HR']
            df_l['AVG'] = (df_l['H+'] / df_l['VB'].replace(0, 1)).fillna(0)
            
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("🥇 Average (AVG)")
                st.table(df_l.sort_values("AVG", ascending=False).head(10)[["Nombre", "AVG"]].style.format({"AVG": "{:.3f}"}))
                st.subheader("🥇 Hits Totales (H+)")
                st.table(df_l.sort_values("H+", ascending=False).head(10)[["Nombre", "H+"]])
            with c2:
                st.subheader("🥇 Jonrones (HR)")
                st.table(df_l.sort_values("HR", ascending=False).head(10)[["Nombre", "HR"]])
                st.subheader("🥇 Dobles (H2)")
                st.table(df_l.sort_values("H2", ascending=False).head(10)[["Nombre", "H2"]])
            
            st.subheader("🥇 Triples (H3)")
            st.table(df_l.sort_values("H3", ascending=False).head(10)[["Nombre", "H3"]])

    with tab_p:
        st.header("🏆 Líderes de Pitcheo")
        df_p = st.session_state.pitchers.copy()
        if not df_p.empty:
            df_p['EFE'] = ((df_p['CL'] * 7) / df_p['IP'].replace(0, 1)).fillna(0)
            cp1, cp2 = st.columns(2)
            with cp1:
                st.subheader("🥇 Efectividad")
                st.table(df_p[df_p['IP'] > 0].sort_values("EFE", ascending=True).head(10)[["Nombre", "EFE"]].style.format({"EFE": "{:.2f}"}))
            with cp2:
                st.subheader("🥇 Ganados (JG)")
                st.table(df_p.sort_values("JG", ascending=False).head(10)[["Nombre", "JG"]])
        else: st.info("Sin datos.")

# ==========================================
# SECCIÓN: ESTADÍSTICAS ADMIN (EDITAR/GUARDAR)
# ==========================================
elif menu == "🏃 Estadísticas (Admin)":
    if not es_admin:
        st.warning("Acceso restringido a administradores.")
    else:
        t_b, t_p = st.tabs(["🥖 Bateo", "🔥 Pitcheo"])
        with t_b:
            lista_n = ["-- Nuevo --"] + sorted(st.session_state.jugadores["Nombre"].tolist())
            sel = st.selectbox("Seleccionar Bateador:", lista_n)
            v_n, v_eq, v_vb, v_h, v_h2, v_h3, v_hr = "", "", 1, 0, 0, 0, 0
            if sel != "-- Nuevo --":
                d = st.session_state.jugadores[st.session_state.jugadores["Nombre"] == sel].iloc[0]
                v_n, v_eq, v_vb, v_h, v_h2, v_h3, v_hr = d["Nombre"], d["Equipo"], int(d["VB"]), int(d["H"]), int(d["H2"]), int(d["H3"]), int(d["HR"])
            
            with st.form("f_bateo"):
                nom = st.text_input("Nombre", value=v_n)
                eq = st.selectbox("Equipo", st.session_state.equipos["Nombre"].tolist() if not st.session_state.equipos.empty else ["N/A"])
                c1, c2, c3, c4, c5 = st.columns(5)
                vb = c1.number_input("VB", 1, value=v_vb); h1 = c2.number_input("H1", value=v_h)
                h2_in = c3.number_input("H2", value=v_h2); h3_in = c4.number_input("H3", value=v_h3); hr_in = c5.number_input("HR", value=v_hr)
                if st.form_submit_button("💾 Guardar Bateador"):
                    st.session_state.jugadores = st.session_state.jugadores[st.session_state.jugadores["Nombre"] != sel]
                    nueva = pd.DataFrame([{"Nombre": nom, "Equipo": eq, "VB": vb, "H": h1, "H2": h2_in, "H3": h3_in, "HR": hr_in}])
                    st.session_state.jugadores = pd.concat([st.session_state.jugadores, nueva], ignore_index=True)
                    st.session_state.jugadores.to_csv(ruta("data_jugadores.csv"), index=False)
                    st.rerun()

        with t_p:
            lista_p = ["-- Nuevo --"] + sorted(st.session_state.pitchers["Nombre"].tolist())
            sel_p = st.selectbox("Seleccionar Pitcher:", lista_p)
            vp_n, vp_eq, vp_jg, vp_jp, vp_ip, vp_cl = "", "", 0, 0, 0.0, 0
            if sel_p != "-- Nuevo --":
                dp = st.session_state.pitchers[st.session_state.pitchers["Nombre"] == sel_p].iloc[0]
                vp_n, vp_eq, vp_jg, vp_jp, vp_ip, vp_cl = dp["Nombre"], dp["Equipo"], int(dp["JG"]), int(dp["JP"]), float(dp["IP"]), int(dp["CL"])
            
            with st.form("f_pitcheo"):
                nom_p = st.text_input("Nombre Pitcher", value=vp_n)
                eq_p = st.selectbox("Equipo ", st.session_state.equipos["Nombre"].tolist() if not st.session_state.equipos.empty else ["N/A"])
                c1, c2, c3, c4 = st.columns(4)
                jg = c1.number_input("JG", value=vp_jg); jp = c2.number_input("JP", value=vp_jp)
                ip = c3.number_input("IP", value=vp_ip); cl = c4.number_input("CL", value=vp_cl)
                if st.form_submit_button("🔥 Guardar Pitcher"):
                    st.session_state.pitchers = st.session_state.pitchers[st.session_state.pitchers["Nombre"] != sel_p]
                    nueva_p = pd.DataFrame([{"Nombre": nom_p, "Equipo": eq_p, "JG": jg, "JP": jp, "IP": ip, "CL": cl}])
                    st.session_state.pitchers = pd.concat([st.session_state.pitchers, nueva_p], ignore_index=True)
                    st.session_state.pitchers.to_csv(ruta("data_pitchers.csv"), index=False)
                    st.rerun()

# ==========================================
# SECCIÓN: ROSTER
# ==========================================
elif menu == "📋 Rosters por Equipo":
    st.header("📋 Roster Detallado")
    if not st.session_state.equipos.empty:
        eq_s = st.selectbox("Selecciona Equipo:", st.session_state.equipos["Nombre"].tolist())
        df_r = st.session_state.jugadores[st.session_state.jugadores["Equipo"] == eq_s].copy()
        if not df_r.empty:
            df_r['AVG'] = ((df_r['H']+df_r['H2']+df_r['H3']+df_r['HR'])/df_r['VB'].replace(0,1)).fillna(0)
            st.dataframe(df_r[["Nombre", "VB", "H", "H2", "H3", "HR", "AVG"]].style.format({"AVG": "{:.3f}"}), use_container_width=True)
        
        df_rp = st.session_state.pitchers[st.session_state.pitchers["Equipo"] == eq_s].copy()
        if not df_rp.empty:
            df_rp['EFE'] = ((df_rp['CL'] * 7) / df_rp['IP'].replace(0, 1)).fillna(0)
            st.dataframe(df_rp[["Nombre", "JG", "JP", "IP", "CL", "EFE"]].style.format({"EFE": "{:.2f}"}), use_container_width=True)
    else: st.warning("No hay equipos registrados.")

elif menu == "👥 Equipos":
    st.header("👥 Equipos")
    if es_admin:
        n_e = st.text_input("Nombre Equipo")
        if st.button("Registrar"):
            st.session_state.equipos = pd.concat([st.session_state.equipos, pd.DataFrame([{"Nombre": n_e}])], ignore_index=True)
            st.session_state.equipos.to_csv(ruta("data_equipos.csv"), index=False)
            st.rerun()
    st.table(st.session_state.equipos)
