import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN DE LA APP ---
st.set_page_config(
    page_title="LIGA SOFTBOL DOMINICAL ING. BENJAMIN ARMENTA",
    page_icon="⚾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CONFIGURACIÓN DE DATOS ---
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
        df[cols_num] = df[cols_num].apply(pd.to_numeric, errors='coerce').fillna(0).astype(int)
        return df[columnas]
    return pd.DataFrame(columns=columnas)

# Carga de datos
st.session_state.jugadores = cargar_datos("data_jugadores.csv", COLS_J)
st.session_state.pitchers = cargar_datos("data_pitchers.csv", COLS_P)
st.session_state.equipos = pd.read_csv(ruta("data_equipos.csv")) if os.path.exists(ruta("data_equipos.csv")) else pd.DataFrame(columns=["Nombre"])

# --- 3. SEGURIDAD (ADMIN) ---
st.sidebar.title("⚾ MENÚ LIGA 2026")
if 'autenticado' not in st.session_state: st.session_state.autenticado = False

if not st.session_state.autenticado:
    with st.sidebar.form("login"):
        pwd = st.text_input("Contraseña Admin:", type="password")
        if st.form_submit_button("Entrar"):
            if pwd == "softbol2026":
                st.session_state.autenticado = True
                st.rerun()
            else: st.error("Incorrecta")
else:
    st.sidebar.success("🔓 MODO ADMIN")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()

# --- BOTÓN DE DESCARGA EN SIDEBAR ---
st.sidebar.divider()
if not st.session_state.jugadores.empty:
    csv_j = st.session_state.jugadores.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button("📥 Descargar Bateo (CSV)", csv_j, "bateo_2026.csv", "text/csv")

menu = st.sidebar.radio("IR A:", ["🏠 Inicio", "🏆 TOP 10 LÍDERES", "📊 Standings (Posiciones)", "📋 Rosters por Equipo", "🏃 Estadísticas (Admin)", "👥 Equipos"])

# ==========================================
# SECCIÓN: INICIO
# ==========================================
if menu == "🏠 Inicio":
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
        else: st.markdown("<h1 style='text-align: center; font-size: 80px;'>⚾</h1>", unsafe_allow_html=True)
    
    st.markdown("<h1 style='text-align: center;'>LIGA DE SOFTBOL 2026</h1>", unsafe_allow_html=True)
    st.divider()

    col_noticia, col_cal = st.columns(2)
    with col_noticia:
        st.subheader("📢 Noticias y Galería")
        st.info("**Aviso:** Los stats se actualizan cada domingo por la tarde.")
        if os.path.exists("foto1.jpg"): st.image("foto1.jpg", caption="Campo de Juego", use_container_width=True)
        else: st.write("Sube 'foto1.jpg' para verla aquí.")

    with col_cal:
        st.subheader("📅 Próximos Juegos")
        data_cal = {"Fecha": ["Dom 22 Feb", "Dom 22 Feb"], "Hora": ["09:00 AM", "11:30 AM"], "Juego": ["Equipo A vs B", "Equipo C vs D"]}
        st.table(pd.DataFrame(data_cal))

# ==========================================
# SECCIÓN: TOP 10 LÍDERES (RESTAURADA COMPLETA)
# ==========================================
elif menu == "🏆 TOP 10 LÍDERES":
    t_b, t_p = st.tabs(["🥖 Bateo", "🔥 Pitcheo"])
    with t_b:
        df_b = st.session_state.jugadores.copy()
        if not df_b.empty:
            df_b['H_T'] = df_b['H'] + df_b['H2'] + df_b['H3'] + df_b['HR']
            df_b['AVG'] = (df_b['H_T'] / df_b['VB'].replace(0, 1)).fillna(0)
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("🥇 AVG")
                st.table(df_b.sort_values("AVG", ascending=False).head(10)[["Nombre", "AVG"]].style.format({"AVG": "{:.3f}"}))
                st.subheader("🥇 Hits Totales")
                st.table(df_b.sort_values("H_T", ascending=False).head(10)[["Nombre", "H_T"]])
                st.subheader("🥇 Triples (H3)")
                st.table(df_b.sort_values("H3", ascending=False).head(10)[["Nombre", "H3"]])
            with c2:
                st.subheader("🥇 Jonrones (HR)")
                st.table(df_b.sort_values("HR", ascending=False).head(10)[["Nombre", "HR"]])
                st.subheader("🥇 Dobles (H2)")
                st.table(df_b.sort_values("H2", ascending=False).head(10)[["Nombre", "H2"]])
        else: st.info("Sin datos.")

    with t_p:
        df_p = st.session_state.pitchers.copy()
        if not df_p.empty:
            df_p['EFE'] = ((df_p['CL'] * 7) / df_p['IP'].replace(0, 1)).fillna(0)
            cp1, cp2 = st.columns(2)
            with cp1:
                st.subheader("🥇 Efectividad")
                st.table(df_p[df_p['IP'] > 0].sort_values("EFE", ascending=True).head(10)[["Nombre", "EFE"]].style.format({"EFE": "{:.2f}"}))
                st.subheader("🥇 Ganados (JG)")
                st.table(df_p.sort_values("JG", ascending=False).head(10)[["Nombre", "JG"]])
            with cp2:
                st.subheader("🥇 Perdidos (JP)")
                st.table(df_p.sort_values("JP", ascending=False).head(10)[["Nombre", "JP"]])
                st.subheader("🥇 Innings (IP)")
                st.table(df_p.sort_values("IP", ascending=False).head(10)[["Nombre", "IP"]])

# ==========================================
# SECCIÓN: STANDINGS (AUTOMÁTICOS)
# ==========================================
elif menu == "📊 Standings (Posiciones)":
    st.header("📊 Tabla de Posiciones")
    if not st.session_state.pitchers.empty:
        std = st.session_state.pitchers.groupby("Equipo")[["JG", "JP"]].sum().reset_index()
        std["PCT"] = (std["JG"] / (std["JG"] + std["JP"]).replace(0, 1)).fillna(0)
        st.dataframe(std.sort_values(by=["JG", "PCT"], ascending=False).style.format({"PCT": "{:.3f}"}), use_container_width=True)
    else: st.info("No hay datos de pitcheo para calcular standings.")

# ==========================================
# SECCIÓN: ROSTER
# ==========================================
elif menu == "📋 Rosters por Equipo":
    if not st.session_state.equipos.empty:
        eq_s = st.selectbox("Equipo:", st.session_state.equipos["Nombre"].tolist())
        df_r = st.session_state.jugadores[st.session_state.jugadores["Equipo"] == eq_s].copy()
        st.subheader("🥖 Bateadores")
        if not df_r.empty:
            df_r['AVG'] = ((df_r['H']+df_r['H2']+df_r['H3']+df_r['HR'])/df_r['VB'].replace(0,1)).fillna(0)
            st.dataframe(df_r[["Nombre", "VB", "H", "H2", "H3", "HR", "AVG"]].style.format({"AVG": "{:.3f}"}), use_container_width=True)
        
        df_rp = st.session_state.pitchers[st.session_state.pitchers["Equipo"] == eq_s].copy()
        st.subheader("🔥 Pitchers")
        if not df_rp.empty:
            st.dataframe(df_rp[["Nombre", "JG", "JP", "IP", "CL"]], use_container_width=True)
    else: st.warning("Crea equipos primero.")

# ==========================================
# SECCIÓN: ESTADÍSTICAS ADMIN (CON ELIMINAR)
# ==========================================
elif menu == "🏃 Estadísticas (Admin)":
    if not st.session_state.autenticado: st.warning("Inicia sesión.")
    else:
        tb_b, tb_p = st.tabs(["🥖 Bateo", "🔥 Pitcheo"])
        with tb_b:
            lista_j = ["-- Nuevo --"] + sorted(st.session_state.jugadores["Nombre"].tolist())
            sel_j = st.selectbox("Bateador:", lista_j)
            v_n, v_eq, v_vb, v_h, v_h2, v_h3, v_hr = "", "", 1, 0, 0, 0, 0
            if sel_j != "-- Nuevo --":
                d = st.session_state.jugadores[st.session_state.jugadores["Nombre"] == sel_j].iloc[0]
                v_n, v_eq, v_vb, v_h, v_h2, v_h3, v_hr = d["Nombre"], d["Equipo"], int(d["VB"]), int(d["H"]), int(d["H2"]), int(d["H3"]), int(d["HR"])
            with st.form("f_b"):
                nom = st.text_input("Nombre", value=v_n)
                eq = st.selectbox("Equipo", st.session_state.equipos["Nombre"].tolist() if not st.session_state.equipos.empty else ["N/A"])
                c1, c2, c3, c4, c5 = st.columns(5)
                vb = c1.number_input("VB", 1, value=v_vb); h = c2.number_input("H", value=v_h)
                h2 = c3.number_input("H2", value=v_h2); h3 = c4.number_input("H3", value=v_h3); hr = c5.number_input("HR", value=v_hr)
                if st.form_submit_button("💾 Guardar"):
                    st.session_state.jugadores = st.session_state.jugadores[st.session_state.jugadores["Nombre"] != sel_j]
                    nueva = pd.DataFrame([{"Nombre": nom, "Equipo": eq, "VB": vb, "H": h, "H2": h2, "H3": h3, "HR": hr}])
                    pd.concat([st.session_state.jugadores, nueva], ignore_index=True).to_csv(ruta("data_jugadores.csv"), index=False)
                    st.rerun()
            if sel_j != "-- Nuevo --" and st.button("🗑️ Eliminar Jugador"):
                st.session_state.jugadores[st.session_state.jugadores["Nombre"] != sel_j].to_csv(ruta("data_jugadores.csv"), index=False)
                st.rerun()

        with tb_p:
            lista_p = ["-- Nuevo --"] + sorted(st.session_state.pitchers["Nombre"].tolist())
            sel_p = st.selectbox("Pitcher:", lista_p)
            vp_n, vp_eq, vp_jg, vp_jp, vp_ip, vp_cl = "", "", 0, 0, 0, 0
            if sel_p != "-- Nuevo --":
                dp = st.session_state.pitchers[st.session_state.pitchers["Nombre"] == sel_p].iloc[0]
                vp_n, vp_eq, vp_jg, vp_jp, vp_ip, vp_cl = dp["Nombre"], dp["Equipo"], int(dp["JG"]), int(dp["JP"]), int(dp["IP"]), int(dp["CL"])
            with st.form("f_p"):
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
            if sel_p != "-- Nuevo --" and st.button("🗑️ Eliminar Pitcher"):
                st.session_state.pitchers[st.session_state.pitchers["Nombre"] != sel_p].to_csv(ruta("data_pitchers.csv"), index=False)
                st.rerun()

# ==========================================
# SECCIÓN: EQUIPOS
# ==========================================
elif menu == "👥 Equipos":
    st.header("👥 Equipos")
    if st.session_state.autenticado:
        n_e = st.text_input("Nombre Equipo")
        if st.button("Registrar"):
            pd.concat([st.session_state.equipos, pd.DataFrame([{"Nombre": n_e}])], ignore_index=True).to_csv(ruta("data_equipos.csv"), index=False)
            st.rerun()
        if not st.session_state.equipos.empty:
            eq_del = st.selectbox("Eliminar equipo:", st.session_state.equipos["Nombre"].tolist())
            if st.button("🗑️ Borrar Equipo Seleccionado"):
                st.session_state.equipos[st.session_state.equipos["Nombre"] != eq_del].to_csv(ruta("data_equipos.csv"), index=False)
                st.rerun()
    st.table(st.session_state.equipos)
