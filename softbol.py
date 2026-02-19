import streamlit as st
import pandas as pd
import os
import urllib.parse

# --- 1. CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="LIGA DE SOFTBOL DOMINICAL", page_icon="⚾", layout="wide")

st.markdown("""
    <style>
    th { background-color: #D32F2F !important; color: white !important; text-align: center !important; }
    .stDataFrame, .stTable { border: 2px solid #D32F2F; border-radius: 10px; }
    div.stButton > button:first-child { background-color: #D32F2F; color: white; border-radius: 5px; }
    h1, h2, h3 { color: #B71C1C; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE DATOS ---
CARPETA_DATOS, CARPETA_FOTOS = "datos_liga", "galeria_liga"
for c in [CARPETA_DATOS, CARPETA_FOTOS]:
    if not os.path.exists(c): os.makedirs(c)

def path_archivo(nombre): return os.path.join(CARPETA_DATOS, nombre)

COLS_J = ["Nombre", "Equipo", "VB", "H", "H2", "H3", "HR"]
COLS_P = ["Nombre", "Equipo", "JG", "JP", "IP", "CL"]
COLS_CAL = ["Fecha", "Hora", "Campo", "Local", "Visitante", "Score"]

def leer_csv(nombre, columnas):
    p = path_archivo(nombre)
    if os.path.exists(p):
        try:
            df = pd.read_csv(p)
            df.columns = df.columns.str.strip()
            for c in columnas:
                if c not in df.columns: df[c] = "" if c == "Score" else 0
            return df[columnas]
        except: return pd.DataFrame(columns=columnas)
    return pd.DataFrame(columns=columnas)

# Carga global de datos
st.session_state.jugadores = leer_csv("data_jugadores.csv", COLS_J)
st.session_state.pitchers = leer_csv("data_pitchers.csv", COLS_P)
st.session_state.equipos = leer_csv("data_equipos.csv", ["Nombre"])
st.session_state.calendario = leer_csv("data_calendario.csv", COLS_CAL)

# --- 3. SEGURIDAD Y ROLES ---
if 'rol' not in st.session_state: st.session_state.rol = "Invitado"

with st.sidebar:
    st.title("🥎 LIGA DOMINICAL")
    if st.session_state.rol == "Invitado":
        with st.form("login"):
            pwd = st.text_input("Contraseña Acceso:", type="password")
            if st.form_submit_button("Entrar"):
                if pwd == "softbol2026": st.session_state.rol = "Admin"; st.rerun()
                elif pwd == "delegado2026": st.session_state.rol = "Delegado"; st.rerun()
                else: st.error("Contraseña Incorrecta")
    else:
        st.success(f"🔓 Sesión: {st.session_state.rol}")
        if st.session_state.rol == "Admin":
            st.divider()
            st.subheader("💾 Respaldos Admin")
            csv_j = st.session_state.jugadores.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Bajar Bateo (CSV)", csv_j, "bateo.csv", "text/csv", use_container_width=True)
        if st.button("Cerrar Sesión"): st.session_state.rol = "Invitado"; st.rerun()

# Menú dinámico
opciones = ["🏠 Inicio", "🏆 LÍDERES", "📊 Standings", "📋 Rosters"]
if st.session_state.rol == "Admin": opciones.append("🏃 Admin General")
if st.session_state.rol == "Delegado": opciones.append("📋 Mi Roster (Delegado)")
menu = st.sidebar.radio("IR A:", opciones)

# ==========================================
# 🏠 SECCIÓN: INICIO
# ==========================================
if menu == "🏠 Inicio":
    st.markdown("<h1 style='text-align: center; color: #D32F2F;'>⚾ LIGA DE SOFTBOL DOMINICAL ⚾</h1>", unsafe_allow_html=True)
    
    if st.session_state.rol == "Admin":
        nuevos = st.session_state.jugadores[st.session_state.jugadores["VB"] == 0]
        if not nuevos.empty:
            st.error(f"📢 **AVISO:** Hay {len(nuevos)} jugadores nuevos registrados por delegados.")
            with st.expander("Ver lista de espera"): st.write(nuevos[["Nombre", "Equipo"]])

    st.divider()
    fotos = sorted(os.listdir(CARPETA_FOTOS), reverse=True)
    if fotos:
        cols = st.columns(3)
        for i, f in enumerate(fotos[:3]):
            with cols[i%3]: st.image(os.path.join(CARPETA_FOTOS, f), use_container_width=True)
    st.subheader("📅 Calendario y Resultados")
    st.dataframe(st.session_state.calendario, use_container_width=True, hide_index=True)

# ==========================================
# 🏆 SECCIÓN: LÍDERES (TODOS LOS DEPARTAMENTOS)
# ==========================================
elif menu == "🏆 LÍDERES":
    t1, t2 = st.tabs(["🥖 Bateo", "🔥 Pitcheo"])
    with t1:
        df = st.session_state.jugadores.copy()
        if not df.empty:
            df['H_T'] = df['H'] + df['H2'] + df['H3'] + df['HR']
            df['AVG'] = (df['H_T'] / df['VB'].replace(0, 1)).fillna(0)
            c1, c2 = st.columns(2)
            c1.subheader("🥇 AVG"); c1.table(df.sort_values("AVG", ascending=False).head(10)[["Nombre", "AVG"]].style.format({"AVG": "{:.3f}"}))
            c2.subheader("🥇 Hits"); c2.table(df.sort_values("H_T", ascending=False).head(10)[["Nombre", "H_T"]])
            c3, c4 = st.columns(2)
            c3.subheader("🥇 HR"); c3.table(df.sort_values("HR", ascending=False).head(10)[["Nombre", "HR"]])
            c4.subheader("🥇 H2"); c4.table(df.sort_values("H2", ascending=False).head(10)[["Nombre", "H2"]])
            st.subheader("🥇 H3"); st.table(df.sort_values("H3", ascending=False).head(10)[["Nombre", "H3"]])
        else: st.info("Sin datos.")
    with t2:
        dfp = st.session_state.pitchers.copy()
        if not dfp.empty:
            dfp['EFE'] = ((dfp['CL'] * 7) / dfp['IP'].replace(0, 1)).fillna(0)
            cp1, cp2 = st.columns(2)
            cp1.subheader("🥇 EFE"); cp1.table(dfp[dfp['IP']>0].sort_values("EFE").head(10)[["Nombre", "EFE"]].style.format({"EFE": "{:.2f}"}))
            cp2.subheader("🥇 JG"); cp2.table(dfp.sort_values("JG", ascending=False).head(10)[["Nombre", "JG"]])
            cp3, cp4 = st.columns(2)
            cp3.subheader("🥇 JP"); cp3.table(dfp.sort_values("JP", ascending=False).head(10)[["Nombre", "JP"]])
            cp4.subheader("🥇 IP"); cp4.table(dfp.sort_values("IP", ascending=False).head(10)[["Nombre", "IP"]])
        else: st.info("Sin datos.")

# ==========================================
# 📊 SECCIÓN: STANDINGS
# ==========================================
elif menu == "📊 Standings":
    st.header("📊 Tabla de Posiciones")
    if not st.session_state.pitchers.empty:
        std = st.session_state.pitchers.groupby("Equipo")[["JG", "JP"]].sum().reset_index()
        std["PCT"] = (std["JG"] / (std["JG"] + std["JP"]).replace(0, 1)).fillna(0)
        st.dataframe(std.sort_values(by=["JG", "PCT"], ascending=False).style.format({"PCT": "{:.3f}"}), use_container_width=True, hide_index=True)

# ==========================================
# 📋 SECCIÓN: MI ROSTER (DELEGADO - SOLO ALTAS)
# ==========================================
elif menu == "📋 Mi Roster (Delegado)":
    st.header("➕ Registrar Jugador")
    if not st.session_state.equipos.empty:
        mi_eq = st.selectbox("Tu Equipo:", st.session_state.equipos["Nombre"].tolist())
        with st.form("alta"):
            nom_n = st.text_input("Nombre Completo")
            if st.form_submit_button("✅ Dar de Alta"):
                if nom_n and nom_n not in st.session_state.jugadores["Nombre"].values:
                    nueva = pd.DataFrame([[nom_n, mi_eq, 0, 0, 0, 0, 0]], columns=COLS_J)
                    pd.concat([st.session_state.jugadores, nueva], ignore_index=True).to_csv(path_archivo("data_jugadores.csv"), index=False)
                    st.success("Registrado. El Admin actualizará los stats."); st.rerun()
                else: st.error("Nombre inválido o ya registrado.")
    else: st.warning("El Admin debe crear equipos primero.")

# ==========================================
# 🏃 SECCIÓN: ADMIN GENERAL (ÚNICO QUE BORRA)
# ==========================================
elif menu == "🏃 Admin General":
    if st.session_state.rol != "Admin": st.warning("Acceso Restringido")
    else:
        tab_e, tab_b, tab_p, tab_c = st.tabs(["Equipos", "Bateo", "Pitcheo", "Calendario"])
        
        with tab_e:
            c1, c2 = st.columns(2)
            with c1:
                n_e = st.text_input("Nuevo Equipo")
                if st.button("Registrar Equipo"):
                    pd.concat([st.session_state.equipos, pd.DataFrame([{"Nombre": n_e}])], ignore_index=True).to_csv(path_archivo("data_equipos.csv"), index=False); st.rerun()
            with c2:
                e_borrar = st.selectbox("Borrar Equipo:", st.session_state.equipos["Nombre"].tolist())
                if st.button("🗑️ Borrar Equipo"):
                    st.session_state.equipos = st.session_state.equipos[st.session_state.equipos["Nombre"] != e_borrar]
                    st.session_state.equipos.to_csv(path_archivo("data_equipos.csv"), index=False); st.rerun()

        with tab_b:
            sel = st.selectbox("Jugador:", ["-- Nuevo --"] + sorted(st.session_state.jugadores["Nombre"].tolist()))
            v_n, v_eq, v_vb, v_h, v_h2, v_h3, v_hr = "", "", 0, 0, 0, 0, 0
            if sel != "-- Nuevo --":
                d = st.session_state.jugadores[st.session_state.jugadores["Nombre"] == sel].iloc[0]
                v_n, v_eq, v_vb, v_h, v_h2, v_h3, v_hr = d["Nombre"], d["Equipo"], int(d["VB"]), int(d["H"]), int(d["H2"]), int(d["H3"]), int(d["HR"])
            
            with st.form("f_b"):
                nom = st.text_input("Nombre", value=v_n); eq = st.selectbox("Equipo", st.session_state.equipos["Nombre"].tolist(), index=0)
                vc1, vc2, vc3, vc4, vc5 = st.columns(5)
                vb = vc1.number_input("VB", value=v_vb); h = vc2.number_input("H", value=v_h); h2 = vc3.number_input("H2", value=v_h2); h3 = vc4.number_input("H3", value=v_h3); hr = vc5.number_input("HR", value=v_hr)
                if st.form_submit_button("💾 Guardar"):
                    df = st.session_state.jugadores[st.session_state.jugadores["Nombre"] != sel]
                    pd.concat([df, pd.DataFrame([[nom, eq, vb, h, h2, h3, hr]], columns=COLS_J)], ignore_index=True).to_csv(path_archivo("data_jugadores.csv"), index=False); st.rerun()
            if sel != "-- Nuevo --" and st.button("🗑️ Eliminar Jugador"):
                st.session_state.jugadores[st.session_state.jugadores["Nombre"] != sel].to_csv(path_archivo("data_jugadores.csv"), index=False); st.rerun()

        with tab_p:
            sel_p = st.selectbox("Pitcher:", ["-- Nuevo --"] + sorted(st.session_state.pitchers["Nombre"].tolist()))
            vp_n, vp_eq, vp_jg, vp_jp, vp_ip, vp_cl = "", "", 0, 0, 0, 0
            if sel_p != "-- Nuevo --":
                dp = st.session_state.pitchers[st.session_state.pitchers["Nombre"] == sel_p].iloc[0]
                vp_n, vp_eq, vp_jg, vp_jp, vp_ip, vp_cl = dp["Nombre"], dp["Equipo"], int(dp["JG"]), int(dp["JP"]), int(dp["IP"]), int(dp["CL"])
            with st.form("f_p"):
                nom_p = st.text_input("Nombre", value=vp_n); eq_p = st.selectbox("Equipo  ", st.session_state.equipos["Nombre"].tolist())
                pc1, pc2, pc3, pc4 = st.columns(4)
                jg = pc1.number_input("JG", value=vp_jg); jp = pc2.number_input("JP", value=vp_jp); ip = pc3.number_input("IP", value=vp_ip); cl = pc4.number_input("CL", value=vp_cl)
                if st.form_submit_button("🔥 Guardar"):
                    dfp = st.session_state.pitchers[st.session_state.pitchers["Nombre"] != sel_p]
                    pd.concat([dfp, pd.DataFrame([[nom_p, eq_p, jg, jp, ip, cl]], columns=COLS_P)], ignore_index=True).to_csv(path_archivo("data_pitchers.csv"), index=False); st.rerun()
            if sel_p != "-- Nuevo --" and st.button("🗑️ Eliminar Pitcher"):
                st.session_state.pitchers[st.session_state.pitchers["Nombre"] != sel_p].to_csv(path_archivo("data_pitchers.csv"), index=False); st.rerun()

        with tab_c:
            with st.form("f_c"):
                f, h, cp = st.text_input("Fecha"), st.text_input("Hora"), st.text_input("Campo")
                loc = st.selectbox("Local", st.session_state.equipos["Nombre"]); vis = st.selectbox("Visitante", st.session_state.equipos["Nombre"])
                sc = st.text_input("Score")
                if st.form_submit_button("📅 Guardar Juego"):
                    pd.concat([st.session_state.calendario, pd.DataFrame([[f, h, cp, loc, vis, sc]], columns=COLS_CAL)], ignore_index=True).to_csv(path_archivo("data_calendario.csv"), index=False); st.rerun()
            if not st.session_state.calendario.empty and st.button("🗑️ Borrar Último Juego"):
                st.session_state.calendario.drop(st.session_state.calendario.index[-1]).to_csv(path_archivo("data_calendario.csv"), index=False); st.rerun()

# Secciones de Rosters (Público)
elif menu == "📋 Rosters":
    if not st.session_state.equipos.empty:
        eq_s = st.selectbox("Ver Equipo:", st.session_state.equipos["Nombre"].tolist())
        st.write("🥖 Bateadores"); st.dataframe(st.session_state.jugadores[st.session_state.jugadores["Equipo"] == eq_s], hide_index=True)
        st.write("🔥 Pitchers"); st.dataframe(st.session_state.pitchers[st.session_state.pitchers["Equipo"] == eq_s], hide_index=True)
