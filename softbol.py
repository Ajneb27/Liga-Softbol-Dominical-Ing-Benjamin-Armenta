import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN E IDENTIDAD ---
NOMBRE_LIGA = "LIGA DE SOFTBOL DOMINICAL"
ANIO_INICIO_LIGA = 2024
ANIO_ACTUAL = 2026

DATA_DIR = "liga_softbol_final_2026"
if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)

# Archivos de base de datos
JUGADORES_FILE = os.path.join(DATA_DIR, "jugadores_master.csv")
EQUIPOS_FILE = os.path.join(DATA_DIR, "equipos_master.csv")
JUEGOS_FILE = os.path.join(DATA_DIR, "juegos_2026.csv")
CALENDARIO_FILE = os.path.join(DATA_DIR, "calendario_2026.csv")

# --- 2. MOTOR DE DATOS ---
def cargar_datos(archivo, columnas):
    if os.path.exists(archivo):
        try:
            df = pd.read_csv(archivo)
            for c in columnas:
                if c not in df.columns: 
                    df[c] = "Softbolista" if c == "Categoria" else 0
            return df
        except: return pd.DataFrame(columns=columnas)
    return pd.DataFrame(columns=columnas)

# --- 3. INICIALIZACIÓN Y ESTILO ---
st.set_page_config(page_title=NOMBRE_LIGA, layout="wide", page_icon="🥎")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .gold-header { color: #d4af37; font-weight: bold; border-bottom: 3px solid #d4af37; padding-bottom: 10px; margin-bottom: 20px; }
    .stMetric { background-color: white; border-radius: 10px; border-left: 5px solid #d4af37; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    .cal-card { background: white; padding: 15px; border-radius: 10px; border: 1px solid #d4af37; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

if 'admin' not in st.session_state: st.session_state.admin = False

# Cargar todas las bases de datos
df_j = cargar_datos(JUGADORES_FILE, ["Nombre", "Equipo", "Categoria", "VB", "H", "2B", "3B", "HR", "G", "P"])
df_e = cargar_datos(EQUIPOS_FILE, ["Nombre", "Debut", "Fin"])
df_games = cargar_datos(JUEGOS_FILE, ["Visitante", "CarrerasV", "HomeClub", "CarrerasH"])
df_cal = cargar_datos(CALENDARIO_FILE, ["Fecha", "Hora", "Visitante", "HomeClub", "Campo"])

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.title(f"🏆 {NOMBRE_LIGA}")
    if not st.session_state.admin:
        with st.expander("🔐 Acceso Administrador"):
            u = st.text_input("Usuario"); p = st.text_input("Clave", type="password")
            if st.button("Entrar"):
                if u == "admin" and p == "123": 
                    st.session_state.admin = True
                    st.rerun()
    else:
        st.success("Modo Admin: ACTIVADO")
        if st.button("Cerrar Sesión"): 
            st.session_state.admin = False
            st.rerun()
    
    st.divider()
    menu = st.radio("Secciones:", ["🏠 INICIO", "📊 STANDING", "🏆 LÍDERES", "📋 ROSTERS", "📜 HISTORIAL", "🏘️ EQUIPOS", "✍️ REGISTRAR", "🗑️ BORRAR", "💾 RESPALDO"])

# --- 5. LÓGICA DE SECCIONES ---

if menu == "🏠 INICIO":
    st.markdown(f"<h1 class='gold-header'>{NOMBRE_LIGA}</h1>", unsafe_allow_html=True)
    c_inf, c_cal = st.columns([1, 1])
    
    with c_inf:
        st.subheader(f"Temporada {ANIO_ACTUAL}")
        st.info(f"Fomentando el deporte desde {ANIO_INICIO_LIGA}.")
        st.write("---")
        st.write("⚾ **¡Bienvenidos!** Consulta aquí los roles de juego y posiciones actualizadas.")

    with c_cal:
        st.subheader("📅 Calendario de Juegos")
        if not df_cal.empty:
            for _, r in df_cal.iterrows():
                st.markdown(f"""
                <div class='cal-card'>
                    <small>{r['Fecha']} | {r['Hora']}</small><br>
                    <b>{r['Visitante']}</b> vs <b>{r['HomeClub']}</b><br>
                    <small>📍 Campo: {r['Campo']}</small>
                </div>
                """, unsafe_allow_html=True)
        else: st.info("No hay juegos programados.")

elif menu == "📊 STANDING":
    st.markdown("<h1 class='gold-header'>📊 Standing General (G-P-E)</h1>", unsafe_allow_html=True)
    if not df_games.empty and not df_e.empty:
        stats = []
        for eq in df_e[df_e["Fin"] == 0]["Nombre"].unique():
            v = df_games[df_games["Visitante"] == eq]
            h = df_games[df_games["HomeClub"] == eq]
            gan = len(v[v["CarrerasV"] > v["CarrerasH"]]) + len(h[h["CarrerasH"] > h["CarrerasV"]])
            per = len(v[v["CarrerasV"] < v["CarrerasH"]]) + len(h[h["CarrerasH"] < h["CarrerasV"]])
            emp = len(v[v["CarrerasV"] == v["CarrerasH"]]) + len(h[h["CarrerasH"] == h["CarrerasV"]])
            cf = v["CarrerasV"].sum() + h["CarrerasH"].sum()
            ce = v["CarrerasH"].sum() + h["CarrerasV"].sum()
            jj = gan + per + emp
            avg = gan / jj if jj > 0 else 0
            stats.append({"Equipo": eq, "JJ": jj, "G": gan, "P": per, "E": emp, "CF": cf, "CE": ce, "AVG": round(avg, 3)})
        st.table(pd.DataFrame(stats).sort_values(by=["AVG", "G", "CF"], ascending=False))
    else: st.info("Sin juegos registrados para calcular posiciones.")

elif menu == "🏆 LÍDERES":
    st.markdown("<h1 class='gold-header'>🥇 Líderes Individuales</h1>", unsafe_allow_html=True)
    cat_f = st.selectbox("Filtrar por Categoría:", ["TODOS", "Novato", "Softbolista", "Refuerzo"])
    df_l = df_j if cat_f == "TODOS" else df_j[df_j["Categoria"] == cat_f]
    
    t1, t2 = st.tabs(["⚾ BATEO", "🎯 PITCHEO"])
    with t1:
        c1, c2 = st.columns(2)
        c1.subheader("Hits"); c1.dataframe(df_l.nlargest(10, 'H')[['Nombre', 'Equipo', 'H']], hide_index=True)
        c2.subheader("Home Runs"); c2.dataframe(df_l.nlargest(10, 'HR')[['Nombre', 'Equipo', 'HR']], hide_index=True)
    with t2:
        c1, c2 = st.columns(2)
        c1.subheader("Ganados"); c1.dataframe(df_l.nlargest(10, 'G')[['Nombre', 'Equipo', 'G']], hide_index=True)
        c2.subheader("Perdidos"); c2.dataframe(df_l.nlargest(10, 'P')[['Nombre', 'Equipo', 'P']], hide_index=True)

elif menu == "📋 ROSTERS":
    st.markdown("<h1 class='gold-header'>📋 Rosters Oficiales</h1>", unsafe_allow_html=True)
    if not df_e.empty:
        eq_s = st.selectbox("Equipo:", df_e[df_e["Fin"] == 0]["Nombre"].unique())
        st.dataframe(df_j[df_j["Equipo"] == eq_s], use_container_width=True, hide_index=True)

elif menu == "📜 HISTORIAL":
    st.markdown("<h1 class='gold-header'>📜 Historial del Jugador</h1>", unsafe_allow_html=True)
    if not df_j.empty:
        j_sel = st.selectbox("Seleccionar Jugador:", sorted(df_j["Nombre"].unique()))
        d = df_j[df_j["Nombre"] == j_sel].iloc[0]
        c1, c2, c3 = st.columns(3)
        c1.metric("Equipo", d['Equipo']); c2.metric("Categoría", d['Categoria'])
        avg = (d['H'] / d['VB']) if d['VB'] > 0 else 0
        c3.metric("Promedio (AVG)", f"{avg:.3f}")
        st.info(f"**Bateo:** VB: {int(d['VB'])} | H: {int(d['H'])} | HR: {int(d['HR'])} | 2B: {int(d['2B'])} | 3B: {int(d['3B'])}")
        st.success(f"**Pitching:** G: {int(d['G'])} | P: {int(d['P'])}")

elif menu == "✍️ REGISTRAR":
    if st.session_state.admin:
        tj, tr, tc = st.tabs(["👤 JUGADORES", "⚾ RESULTADOS JUEGOS", "📅 CALENDARIO"])
        with tj:
            st.subheader("Registro de Estadísticas")
            sel = st.selectbox("Jugador:", ["NUEVO JUGADOR"] + sorted(df_j["Nombre"].tolist()))
            if 'v' not in st.session_state or st.session_state.get('last') != sel:
                if sel != "NUEVO JUGADOR": st.session_state.v = df_j[df_j["Nombre"] == sel].iloc[0].to_dict()
                else: st.session_state.v = {"Nombre": "", "Equipo": None, "Categoria": "Softbolista", "VB": 0, "H": 0, "2B": 0, "3B": 0, "HR": 0, "G": 0, "P": 0}
                st.session_state.last = sel
            with st.form("fj"):
                n = st.text_input("Nombre", value=st.session_state.v["Nombre"])
                c = st.selectbox("Categoría", ["Novato", "Softbolista", "Refuerzo"], index=1)
                e = st.selectbox("Equipo", df_e["Nombre"].unique() if not df_e.empty else ["Crea equipo"])
                v1, v2, v3, v4, v5 = st.columns(5)
                vb = v1.number_input("VB", value=int(st.session_state.v["VB"])); h = v2.number_input("H", value=int(st.session_state.v["H"]))
                h2 = v3.number_input("2B", value=int(st.session_state.v["2B"])); h3 = v4.number_input("3B", value=int(st.session_state.v["3B"])); hr = v5.number_input("HR", value=int(st.session_state.v["HR"]))
                g = st.number_input("G", value=int(st.session_state.v["G"])); p = st.number_input("P", value=int(st.session_state.v["P"]))
                if st.form_submit_button("💾 GUARDAR"):
                    df_j = df_j[df_j["Nombre"] != n]
                    pd.concat([df_j, pd.DataFrame([{"Nombre":n, "Equipo":e, "Categoria":c, "VB":vb, "H":h, "2B":h2, "3B":h3, "HR":hr, "G":g, "P":p}])], ignore_index=True).to_csv(JUGADORES_FILE, index=False); st.rerun()
        with tr:
            with st.form("fr"):
                v = st.selectbox("Visitante", df_e["Nombre"].unique()); cv = st.number_input("Carreras V", 0)
                h = st.selectbox("Home Club", df_e["Nombre"].unique()); ch = st.number_input("Carreras H", 0)
                if st.form_submit_button("💾 GUARDAR SCORE"):
                    pd.concat([df_games, pd.DataFrame([{"Visitante":v, "CarrerasV":cv, "HomeClub":h, "CarrerasH":ch}])], ignore_index=True).to_csv(JUEGOS_FILE, index=False); st.rerun()
        with tc:
            with st.form("fc"):
                f = st.date_input("Fecha"); hr_c = st.text_input("Hora (10:00 AM)"); camp = st.text_input("Campo")
                v_c = st.selectbox("Visitante ", df_e["Nombre"].unique()); h_c = st.selectbox("Home Club ", df_e["Nombre"].unique())
                if st.form_submit_button("📅 PROGRAMAR"):
                    pd.concat([df_cal, pd.DataFrame([{"Fecha":str(f), "Hora":hr_c, "Visitante":v_c, "HomeClub":h_c, "Campo":camp}])], ignore_index=True).to_csv(CALENDARIO_FILE, index=False); st.rerun()
    else: st.warning("Área exclusiva para administradores.")

elif menu == "🏘️ EQUIPOS":
    if st.session_state.admin:
        with st.form("fe"):
            n_e = st.text_input("Nombre Equipo"); d_e = st.number_input("Debut", 2024, 2026, 2026)
            if st.form_submit_button("Añadir"):
                pd.concat([df_e, pd.DataFrame([{"Nombre":n_e, "Debut":d_e, "Fin":0}])], ignore_index=True).to_csv(EQUIPOS_FILE, index=False); st.rerun()
    st.table(df_e)

elif menu == "🗑️ BORRAR":
    if st.session_state.admin:
        st.subheader("Borrar Jugador")
        j_d = st.selectbox("Jugador a eliminar:", [""] + sorted(df_j["Nombre"].tolist()))
        if st.button("❌ ELIMINAR JUGADOR") and j_d != "":
            df_j[df_j["Nombre"] != j_d].to_csv(JUGADORES_FILE, index=False); st.rerun()
        st.divider()
        st.subheader("Limpiar Calendario")
        if st.button("🗑️ Vaciar todo el Calendario"):
            pd.DataFrame(columns=["Fecha", "Hora", "Visitante", "HomeClub", "Campo"]).to_csv(CALENDARIO_FILE, index=False); st.rerun()

elif menu == "💾 RESPALDO":
    st.subheader("Descargar Bases de Datos")
    st.download_button("📥 Descargar Jugadores", df_j.to_csv(index=False), "jugadores.csv", "text/csv")
    st.download_button("📥 Descargar Resultados", df_games.to_csv(index=False), "resultados.csv", "text/csv")
