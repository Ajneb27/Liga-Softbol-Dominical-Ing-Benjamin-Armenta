import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN DE DATOS ---
CARPETA_DATOS = "datos_liga"
if not os.path.exists(CARPETA_DATOS): os.makedirs(CARPETA_DATOS)

def ruta(archivo): return os.path.join(CARPETA_DATOS, archivo)

COLS_J = ["Nombre", "Equipo", "VB", "H", "H2", "H3", "HR"]
COLS_P = ["Nombre", "Equipo", "JG", "JP", "IP", "CL"] 

def cargar_datos(archivo, columnas):
    path = ruta(archivo)
    if os.path.exists(path):
        df = pd.read_csv(path)
        df.columns = df.columns.str.strip()
        for col in columnas:
            if col not in df.columns: df[col] = 0
        cols_num = [c for c in columnas if c not in ["Nombre", "Equipo"]]
        df[cols_num] = df[cols_num].apply(pd.to_numeric, errors='coerce').fillna(0)
        return df[columnas]
    return pd.DataFrame(columns=columnas)

# Carga constante para asegurar que siempre haya datos frescos
st.session_state.jugadores = cargar_datos("data_jugadores.csv", COLS_J)
st.session_state.pitchers = cargar_datos("data_pitchers.csv", COLS_P)
st.session_state.equipos = pd.read_csv(ruta("data_equipos.csv")) if os.path.exists(ruta("data_equipos.csv")) else pd.DataFrame(columns=["Nombre"])

# --- 2. SEGURIDAD ---
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

menu = st.sidebar.radio("MENÚ:", ["🏠 Inicio", "🏆 TOP 10 LÍDERES", "📋 Rosters por Equipo", "🏃 Estadísticas (Admin)", "👥 Equipos"])

# ==========================================
# SECCIÓN: ROSTERS POR EQUIPO (CORREGIDA)
# ==========================================
if menu == "📋 Rosters por Equipo":
    st.header("📋 Roster Detallado por Equipo")
    
    if not st.session_state.equipos.empty:
        # Añadimos una key para forzar la actualización al cambiar
        eq_s = st.selectbox("Selecciona un Equipo para ver su Roster:", 
                            st.session_state.equipos["Nombre"].tolist(),
                            key="selector_roster")
        
        # FILTRADO DE BATEADORES
        df_r = st.session_state.jugadores[st.session_state.jugadores["Equipo"] == eq_s].copy()
        
        st.subheader(f"🥖 Bateadores de {eq_s}")
        if not df_r.empty:
            # Cálculo de AVG en milésimas
            df_r['H_T'] = df_r['H'] + df_r['H2'] + df_r['H3'] + df_r['HR']
            df_r['AVG'] = (df_r['H_T'] / df_r['VB'].replace(0, 1)).fillna(0)
            
            # Mostramos columnas clave
            st.dataframe(df_r[["Nombre", "VB", "H", "H2", "H3", "HR", "AVG"]].style.format({"AVG": "{:.3f}"}), 
                         use_container_width=True)
        else:
            st.info(f"No hay bateadores registrados en {eq_s}.")

        # FILTRADO DE PITCHERS
        st.subheader(f"🔥 Pitchers de {eq_s}")
        df_rp = st.session_state.pitchers[st.session_state.pitchers["Equipo"] == eq_s].copy()
        if not df_rp.empty:
            df_rp['EFE'] = ((df_rp['CL'] * 7) / df_rp['IP'].replace(0, 1)).fillna(0)
            st.dataframe(df_rp[["Nombre", "JG", "JP", "IP", "CL", "EFE"]].style.format({"EFE": "{:.2f}"}), 
                         use_container_width=True)
        else:
            st.info(f"No hay pitchers registrados en {eq_s}.")
    else:
        st.warning("No hay equipos registrados todavía.")

# ==========================================
# SECCIÓN: TOP 10 LÍDERES
# ==========================================
elif menu == "🏆 TOP 10 LÍDERES":
    t_b, t_p = st.tabs(["🥖 Bateo", "🔥 Pitcheo"])
    with t_b:
        df_b = st.session_state.jugadores.copy()
        if not df_b.empty:
            df_b['HT'] = df_b['H'] + df_b['H2'] + df_b['H3'] + df_b['HR']
            df_b['AVG'] = (df_b['HT'] / df_b['VB'].replace(0, 1)).fillna(0)
            c1, c2 = st.columns(2)
            c1.table(df_b.sort_values("AVG", ascending=False).head(10)[["Nombre", "AVG"]].style.format({"AVG": "{:.3f}"}))
            c2.table(df_b.sort_values("HR", ascending=False).head(10)[["Nombre", "HR"]])
    with t_p:
        df_p = st.session_state.pitchers.copy()
        if not df_p.empty:
            df_p['EFE'] = ((df_p['CL'] * 7) / df_p['IP'].replace(0, 1)).fillna(0)
            c1, c2 = st.columns(2)
            c1.table(df_p[df_p['IP'] > 0].sort_values("EFE", ascending=True).head(10)[["Nombre", "EFE"]].style.format({"EFE": "{:.2f}"}))
            c2.table(df_p.sort_values("JG", ascending=False).head(10)[["Nombre", "JG"]])

# ==========================================
# SECCIÓN: ESTADÍSTICAS ADMIN
# ==========================================
elif menu == "🏃 Estadísticas (Admin)":
    if not st.session_state.autenticado:
        st.warning("Acceso solo para administradores.")
    else:
        tb_b, tb_p = st.tabs(["🥖 Bateo", "🔥 Pitcheo"])
        with tb_b:
            lista_j = ["-- Nuevo --"] + sorted(st.session_state.jugadores["Nombre"].tolist())
            sel_j = st.selectbox("Editar Bateador:", lista_j)
            v_n, v_eq, v_vb, v_h, v_h2, v_h3, v_hr = "", "", 1, 0, 0, 0, 0
            if sel_j != "-- Nuevo --":
                d = st.session_state.jugadores[st.session_state.jugadores["Nombre"] == sel_j].iloc[0]
                v_n, v_eq, v_vb, v_h, v_h2, v_h3, v_hr = d["Nombre"], d["Equipo"], int(d["VB"]), int(d["H"]), int(d["H2"]), int(d["H3"]), int(d["HR"])
            with st.form("form_b"):
                nom = st.text_input("Nombre", value=v_n)
                eq = st.selectbox("Equipo", st.session_state.equipos["Nombre"].tolist() if not st.session_state.equipos.empty else ["N/A"])
                c1, c2, c3, c4, c5 = st.columns(5)
                vb = c1.number_input("VB", 1, value=v_vb); h1 = c2.number_input("H1", value=v_h)
                h2 = c3.number_input("H2", value=v_h2); h3 = c4.number_input("H3", value=v_h3); hr = c5.number_input("HR", value=v_hr)
                if st.form_submit_button("💾 Guardar"):
                    st.session_state.jugadores = st.session_state.jugadores[st.session_state.jugadores["Nombre"] != sel_j]
                    nueva = pd.DataFrame([{"Nombre": nom, "Equipo": eq, "VB": vb, "H": h1, "H2": h2, "H3": h3, "HR": hr}])
                    pd.concat([st.session_state.jugadores, nueva], ignore_index=True).to_csv(ruta("data_jugadores.csv"), index=False)
                    st.rerun()

        with tb_p:
            lista_p = ["-- Nuevo --"] + sorted(st.session_state.pitchers["Nombre"].tolist())
            sel_p = st.selectbox("Editar Pitcher:", lista_p)
            vp_n, vp_eq, vp_jg, vp_jp, vp_ip, vp_cl = "", "", 0, 0, 0.0, 0
            if sel_p != "-- Nuevo --":
                dp = st.session_state.pitchers[st.session_state.pitchers["Nombre"] == sel_p].iloc[0]
                vp_n, vp_eq, vp_jg, vp_jp, vp_ip, vp_cl = dp["Nombre"], dp["Equipo"], int(dp["JG"]), int(dp["JP"]), float(dp["IP"]), int(dp["CL"])
            with st.form("form_p"):
                nom_p = st.text_input("Nombre Pitcher", value=vp_n)
                eq_p = st.selectbox("Equipo ", st.session_state.equipos["Nombre"].tolist() if not st.session_state.equipos.empty else ["N/A"])
                c1, c2, c3, c4 = st.columns(4)
                jg = c1.number_input("JG", value=vp_jg); jp = c2.number_input("JP", value=vp_jp)
                ip = c3.number_input("IP", value=vp_ip); cl = c4.number_input("CL", value=vp_cl)
                if st.form_submit_button("🔥 Guardar"):
                    st.session_state.pitchers = st.session_state.pitchers[st.session_state.pitchers["Nombre"] != sel_p]
                    nueva_p = pd.DataFrame([{"Nombre": nom_p, "Equipo": eq_p, "JG": jg, "JP": jp, "IP": ip, "CL": cl}])
                    pd.concat([st.session_state.pitchers, nueva_p], ignore_index=True).to_csv(ruta("data_pitchers.csv"), index=False)
                    st.rerun()

elif menu == "👥 Equipos":
    if es_admin:
        n_e = st.text_input("Nombre Equipo")
        if st.button("Registrar"):
            new_eq = pd.concat([st.session_state.equipos, pd.DataFrame([{"Nombre": n_e}])], ignore_index=True)
            new_eq.to_csv(ruta("data_equipos.csv"), index=False)
            st.rerun()
    st.table(st.session_state.equipos)

elif menu == "🏠 Inicio":
    st.title("⚾ Liga de Softbol 2026")
    st.write("Consulta rosters y líderes oficiales de la temporada.")
