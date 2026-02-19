import streamlit as st
import pandas as pd
import os
import urllib.parse

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="LIGA SOFTBOL BENJAMIN ARMENTA", page_icon="⚾", layout="wide")

# Carpetas
CARPETA_DATOS = "datos_liga"
CARPETA_FOTOS = "galeria_liga"
for c in [CARPETA_DATOS, CARPETA_FOTOS]:
    if not os.path.exists(c): os.makedirs(c)

def ruta(archivo): return os.path.join(CARPETA_DATOS, archivo)

# Columnas exactas
COLS_J = ["Nombre", "Equipo", "VB", "H", "H2", "H3", "HR"]
COLS_P = ["Nombre", "Equipo", "JG", "JP", "IP", "CL"]
COLS_CAL = ["Fecha", "Hora", "Campo", "Local", "Visitante", "Score"]

def cargar_datos(archivo, columnas):
    path = ruta(archivo)
    if os.path.exists(path):
        df = pd.read_csv(path)
        df.columns = df.columns.str.strip()
        for col in columnas:
            if col not in df.columns: df[col] = "" if col == "Score" else 0
        return df[columnas]
    return pd.DataFrame(columns=columnas)

# Carga de datos
st.session_state.jugadores = cargar_datos("data_jugadores.csv", COLS_J)
st.session_state.pitchers = cargar_datos("data_pitchers.csv", COLS_P)
st.session_state.equipos = pd.read_csv(ruta("data_equipos.csv")) if os.path.exists(ruta("data_equipos.csv")) else pd.DataFrame(columns=["Nombre"])
st.session_state.calendario = cargar_datos("data_calendario.csv", COLS_CAL)

# --- 2. SIDEBAR ---
if 'autenticado' not in st.session_state: st.session_state.autenticado = False
with st.sidebar:
    st.title("⚾ MENÚ LIGA")
    if not st.session_state.autenticado:
        with st.form("login"):
            pwd = st.text_input("Contraseña:", type="password")
            if st.form_submit_button("Entrar"):
                if pwd == "softbol2026": st.session_state.autenticado = True; st.rerun()
                else: st.error("Incorrecta")
    else:
        st.success("🔓 ADMIN")
        if st.button("Cerrar Sesión"): st.session_state.autenticado = False; st.rerun()

menu = st.sidebar.radio("IR A:", ["🏠 Inicio", "🏆 LÍDERES", "📊 Standings", "📋 Rosters por Equipo", "📅 Programación (Admin)", "🖼️ Galería", "🏃 Estadísticas (Admin)", "👥 Equipos"])

# ==========================================
# 🏠 INICIO
# ==========================================
if menu == "🏠 Inicio":
    st.markdown("<h1 style='text-align: center;'>⚾ LIGA BENJAMIN ARMENTA 2026</h1>", unsafe_allow_html=True)
    st.divider()
    fotos = sorted(os.listdir(CARPETA_FOTOS), reverse=True)
    if fotos:
        st.subheader("📸 Galería Reciente")
        cols_gal = st.columns(3)
        for i, foto in enumerate(fotos[:3]):
            with cols_gal[i]: st.image(os.path.join(CARPETA_FOTOS, foto), use_container_width=True)
    st.divider()
    st.subheader("📅 Próximos Juegos y Resultados")
    st.dataframe(st.session_state.calendario, use_container_width=True, hide_index=True)

# ==========================================
# 🏆 LÍDERES (TODAS LAS OPCIONES)
# ==========================================
elif menu == "🏆 LÍDERES":
    t_b, t_p = st.tabs(["🥖 Bateo", "🔥 Pitcheo"])
    with t_b:
        df_b = st.session_state.jugadores.copy()
        if not df_b.empty:
            df_b['H_T'] = df_b['H'] + df_b['H2'] + df_b['H3'] + df_b['HR']
            df_b['AVG'] = (df_b['H_T'] / df_b['VB'].replace(0, 1)).fillna(0)
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("🥇 AVG"); st.table(df_b.sort_values("AVG", ascending=False).head(10)[["Nombre", "AVG"]].style.format({"AVG": "{:.3f}"}))
                st.subheader("🥇 Hits Totales"); st.table(df_b.sort_values("H_T", ascending=False).head(10)[["Nombre", "H_T"]])
                st.subheader("🥇 Triples (H3)"); st.table(df_b.sort_values("H3", ascending=False).head(10)[["Nombre", "H3"]])
            with c2:
                st.subheader("🥇 Jonrones (HR)"); st.table(df_b.sort_values("HR", ascending=False).head(10)[["Nombre", "HR"]])
                st.subheader("🥇 Dobles (H2)"); st.table(df_b.sort_values("H2", ascending=False).head(10)[["Nombre", "H2"]])
        else: st.info("Sin datos.")
    with t_p:
        df_p = st.session_state.pitchers.copy()
        if not df_p.empty:
            df_p['EFE'] = ((df_p['CL'] * 7) / df_p['IP'].replace(0, 1)).fillna(0)
            cp1, cp2 = st.columns(2)
            with cp1:
                st.subheader("🥇 Efectividad"); st.table(df_p[df_p['IP'] > 0].sort_values("EFE").head(10)[["Nombre", "EFE"]].style.format({"EFE": "{:.2f}"}))
                st.subheader("🥇 Ganados (JG)"); st.table(df_p.sort_values("JG", ascending=False).head(10)[["Nombre", "JG"]])
            with cp2:
                st.subheader("🥇 Perdidos (JP)"); st.table(df_p.sort_values("JP", ascending=False).head(10)[["Nombre", "JP"]])
                st.subheader("🥇 Innings (IP)"); st.table(df_p.sort_values("IP", ascending=False).head(10)[["Nombre", "IP"]])

# ==========================================
# 📋 ROSTERS (INCLUYE PITCHERS AHORA)
# ==========================================
elif menu == "📋 Rosters por Equipo":
    if not st.session_state.equipos.empty:
        eq_s = st.selectbox("Selecciona Equipo:", st.session_state.equipos["Nombre"].tolist())
        
        # Bateadores
        st.subheader(f"🥖 Bateadores - {eq_s}")
        df_r = st.session_state.jugadores[st.session_state.jugadores["Equipo"] == eq_s].copy()
        if not df_r.empty:
            df_r['AVG'] = ((df_r['H']+df_r['H2']+df_r['H3']+df_r['HR'])/df_r['VB'].replace(0,1)).fillna(0)
            st.dataframe(df_r[["Nombre", "VB", "H", "H2", "H3", "HR", "AVG"]].style.format({"AVG": "{:.3f}"}), use_container_width=True)
        else: st.write("No hay bateadores registrados.")

        # Pitchers (ESTA ES LA PARTE QUE FALTABA)
        st.subheader(f"🔥 Pitchers - {eq_s}")
        df_rp = st.session_state.pitchers[st.session_state.pitchers["Equipo"] == eq_s].copy()
        if not df_rp.empty:
            df_rp['EFE'] = ((df_rp['CL'] * 7) / df_rp['IP'].replace(0, 1)).fillna(0)
            st.dataframe(df_rp[["Nombre", "JG", "JP", "IP", "CL", "EFE"]].style.format({"EFE": "{:.2f}"}), use_container_width=True)
        else: st.write("No hay pitchers registrados.")

        txt = f"Roster de {eq_s} - Liga Benjamin Armenta"
        st.markdown(f'[📲 Compartir en WhatsApp](https://wa.me{urllib.parse.quote(txt)})')
    else: st.warning("Crea equipos primero.")

# ==========================================
# 🏃 ESTADÍSTICAS ADMIN (CON ELIMINAR)
# ==========================================
elif menu == "🏃 Estadísticas (Admin)":
    if not st.session_state.autenticado: st.warning("Inicia sesión.")
    else:
        t1, t2 = st.tabs(["🥖 Bateo", "🔥 Pitcheo"])
        with t1:
            sel_j = st.selectbox("Jugador:", ["-- Nuevo --"] + sorted(st.session_state.jugadores["Nombre"].tolist()))
            v_n, v_eq, v_vb, v_h, v_h2, v_h3, v_hr = "", "", 1, 0, 0, 0, 0
            if sel_j != "-- Nuevo --":
                d = st.session_state.jugadores[st.session_state.jugadores["Nombre"] == sel_j].iloc[0]
                v_n, v_eq, v_vb, v_h, v_h2, v_h3, v_hr = d["Nombre"], d["Equipo"], int(d["VB"]), int(d["H"]), int(d["H2"]), int(d["H3"]), int(d["HR"])
            with st.form("f_j"):
                nom = st.text_input("Nombre", value=v_n); eq = st.selectbox("Equipo", st.session_state.equipos["Nombre"].tolist())
                c1, c2, c3, c4, c5 = st.columns(5)
                vb = c1.number_input("VB", value=v_vb); h = c2.number_input("H", value=v_h)
                h2 = c3.number_input("H2", value=v_h2); h3 = c4.number_input("H3", value=v_h3); hr = c5.number_input("HR", value=v_hr)
                if st.form_submit_button("Guardar Bateador"):
                    df = st.session_state.jugadores[st.session_state.jugadores["Nombre"] != sel_j]
                    nuevo = pd.DataFrame([[nom, eq, vb, h, h2, h3, hr]], columns=COLS_J)
                    pd.concat([df, nuevo], ignore_index=True).to_csv(ruta("data_jugadores.csv"), index=False); st.rerun()
            if sel_j != "-- Nuevo --" and st.button("🗑️ Eliminar Bateador"):
                st.session_state.jugadores[st.session_state.jugadores["Nombre"] != sel_j].to_csv(ruta("data_jugadores.csv"), index=False); st.rerun()

        with t2:
            sel_p = st.selectbox("Pitcher:", ["-- Nuevo --"] + sorted(st.session_state.pitchers["Nombre"].tolist()))
            vp_n, vp_eq, vp_jg, vp_jp, vp_ip, vp_cl = "", "", 0, 0, 0, 0
            if sel_p != "-- Nuevo --":
                d = st.session_state.pitchers[st.session_state.pitchers["Nombre"] == sel_p].iloc[0]
                vp_n, vp_eq, vp_jg, vp_jp, vp_ip, vp_cl = d["Nombre"], d["Equipo"], int(d["JG"]), int(d["JP"]), int(d["IP"]), int(d["CL"])
            with st.form("f_p"):
                nom_p = st.text_input("Nombre", value=vp_n); eq_p = st.selectbox("Equipo  ", st.session_state.equipos["Nombre"].tolist())
                c1, c2, c3, c4 = st.columns(4)
                jg = c1.number_input("JG", value=vp_jg); jp = c2.number_input("JP", value=vp_jp)
                ip = c3.number_input("IP", value=vp_ip); cl = c4.number_input("CL", value=vp_cl)
                if st.form_submit_button("Guardar Pitcher"):
                    dfp = st.session_state.pitchers[st.session_state.pitchers["Nombre"] != sel_p]
                    nuevo_p = pd.DataFrame([[nom_p, eq_p, jg, jp, ip, cl]], columns=COLS_P)
                    pd.concat([dfp, nuevo_p], ignore_index=True).to_csv(ruta("data_pitchers.csv"), index=False); st.rerun()
            if sel_p != "-- Nuevo --" and st.button("🗑️ Eliminar Pitcher"):
                st.session_state.pitchers[st.session_state.pitchers["Nombre"] != sel_p].to_csv(ruta("data_pitchers.csv"), index=False); st.rerun()

# (Incluye el resto de secciones: Galería, Standings, Programación y Equipos del código anterior)
