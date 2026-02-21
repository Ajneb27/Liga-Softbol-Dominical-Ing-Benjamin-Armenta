import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN E IDENTIDAD ---
NOMBRE_LIGA = "LIGA DE SOFTBOL DOMINICAL"
ANIO_INICIO_LIGA = 2024
ANIO_ACTUAL = 2026

DATA_DIR = "liga_softbol_final_2026"
if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)

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
    .gold-header { color: #d4af37; font-weight: bold; border-bottom: 3px solid #d4af37; padding-bottom: 10px; margin-bottom: 20px; }
    .stMetric { background-color: white; border-radius: 10px; border-left: 5px solid #d4af37; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    .cal-card { background: white; padding: 15px; border-radius: 10px; border: 1px solid #d4af37; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

if 'admin' not in st.session_state: st.session_state.admin = False

COLS_J = ["Nombre", "Equipo", "Categoria", "VB", "H", "2B", "3B", "HR", "G", "P"]
df_j = cargar_datos(JUGADORES_FILE, COLS_J)
df_e = cargar_datos(EQUIPOS_FILE, ["Nombre", "Debut", "Fin"])
df_games = cargar_datos(JUEGOS_FILE, ["Jornada", "Visitante", "CarrerasV", "HomeClub", "CarrerasH"])
df_cal = cargar_datos(CALENDARIO_FILE, ["Jornada", "Fecha", "Hora", "Visitante", "HomeClub", "Campo"])

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.title(f"🏆 {NOMBRE_LIGA}")
    if not st.session_state.admin:
        with st.expander("🔐 Acceso Administrador"):
            u = st.text_input("Usuario"); p = st.text_input("Clave", type="password")
            if st.button("Entrar"):
                if u == "admin" and p == "123": st.session_state.admin = True; st.rerun()
    else:
        st.success("Modo Admin: ACTIVADO")
        if st.button("Cerrar Sesión"): st.session_state.admin = False; st.rerun()
    
    st.divider()
    menu = st.radio("Secciones:", ["🏠 INICIO", "📊 STANDING", "🏆 LÍDERES", "📋 ROSTERS", "📜 HISTORIAL", "🏘️ EQUIPOS", "✍️ REGISTRAR", "🗑️ BORRAR", "💾 RESPALDO"])

# --- 5. LÓGICA DE SECCIONES ---

if menu == "🏠 INICIO":
    st.markdown(f"<h1 class='gold-header'>{NOMBRE_LIGA}</h1>", unsafe_allow_html=True)
    c_inf, c_cal = st.columns(2)
    with c_inf:
        st.subheader(f"Temporada {ANIO_ACTUAL}")
        if not df_games.empty: st.metric("Jornada Actual", int(df_games["Jornada"].max()))
    with c_cal:
        st.subheader("📅 Próximos Juegos")
        if not df_cal.empty:
            for _, r in df_cal.iterrows():
                st.markdown(f"<div class='cal-card'><b>Jornada {r['Jornada']}</b><br>{r['Fecha']}<br><b>{r['Visitante']} vs {r['HomeClub']}</b></div>", unsafe_allow_html=True)

elif menu == "📊 STANDING":
    st.markdown("<h1 class='gold-header'>📊 Tabla de Posiciones</h1>", unsafe_allow_html=True)
    if not df_games.empty and not df_e.empty:
        stats = []
        for eq in df_e[df_e["Fin"] == 0]["Nombre"].unique():
            v = df_games[df_games["Visitante"] == eq]
            h = df_games[df_games["HomeClub"] == eq]
            g = len(v[v["CarrerasV"] > v["CarrerasH"]]) + len(h[h["CarrerasH"] > h["CarrerasV"]])
            p = len(v[v["CarrerasV"] < v["CarrerasH"]]) + len(h[h["CarrerasH"] < h["CarrerasV"]])
            e = len(v[v["CarrerasV"] == v["CarrerasH"]]) + len(h[h["CarrerasH"] == h["CarrerasV"]])
            cf, ce = (v["CarrerasV"].sum() + h["CarrerasH"].sum()), (v["CarrerasH"].sum() + h["CarrerasV"].sum())
            jj = g + p + e
            avg = g / jj if jj > 0 else 0
            stats.append({"Equipo": eq, "JJ": jj, "G": g, "P": p, "E": e, "CF": cf, "CE": ce, "AVG": round(avg, 3)})
        st.table(pd.DataFrame(stats).sort_values(by=["AVG", "G"], ascending=False))

elif menu == "🏆 LÍDERES":
    st.markdown("<h1 class='gold-header'>🥇 Cuadro de Honor</h1>", unsafe_allow_html=True)
    cat_f = st.selectbox("Filtrar por Categoría:", ["TODOS", "Novato", "Softbolista", "Refuerzo"])
    df_l = df_j if cat_f == "TODOS" else df_j[df_j["Categoria"] == cat_f]
    t1, t2 = st.tabs(["⚾ BATEO", "🎯 PITCHEO"])
    with t1:
        c1, c2 = st.columns(2)
        c1.subheader("Hits (H)"); c1.dataframe(df_l.nlargest(10, 'H')[['Nombre', 'Equipo', 'H']], hide_index=True)
        c2.subheader("Home Runs (HR)"); c2.dataframe(df_l.nlargest(10, 'HR')[['Nombre', 'Equipo', 'HR']], hide_index=True)
    with t2:
        df_p = df_l[(df_l["G"] > 0) | (df_l["P"] > 0)]
        st.dataframe(df_p.sort_values("G", ascending=False)[['Nombre', 'Equipo', 'G', 'P']], hide_index=True)

elif menu == "📋 ROSTERS":
    st.markdown("<h1 class='gold-header'>📋 Rosters y Estadísticas</h1>", unsafe_allow_html=True)
    if not df_e.empty:
        eq_s = st.selectbox("Seleccionar Equipo:", df_e[df_e["Fin"] == 0]["Nombre"].unique())
        df_roster = df_j[df_j["Equipo"] == eq_s].copy()
        
        # --- CÁLCULO DE AVG PARA EL ROSTER ---
        df_roster["AVG"] = (df_roster["H"] / df_roster["VB"]).fillna(0).apply(lambda x: f"{x:.3f}")
        
        # Mostrar columnas clave
        cols_mostrar = ["Nombre", "Categoria", "VB", "H", "2B", "3B", "HR", "AVG"]
        st.dataframe(df_roster[cols_mostrar].sort_values("AVG", ascending=False), use_container_width=True, hide_index=True)
    else: st.info("No hay equipos registrados.")

elif menu == "📜 HISTORIAL":
    if not df_j.empty:
        j_sel = st.selectbox("Jugador:", sorted(df_j["Nombre"].unique()))
        d = df_j[df_j["Nombre"] == j_sel].iloc[0]
        c1, c2, c3 = st.columns(3)
        c1.metric("Equipo", d['Equipo']); c2.metric("Categoría", d['Categoria'])
        avg = (d['H'] / d['VB']) if d['VB'] > 0 else 0
        c3.metric("AVG", f"{avg:.3f}")
        st.info(f"Estadísticas: VB: {int(d['VB'])} | H: {int(d['H'])} | 2B: {int(d['2B'])} | 3B: {int(d['3B'])} | HR: {int(d['HR'])}")

elif menu == "✍️ REGISTRAR":
    if st.session_state.admin:
        tj, tr, tc = st.tabs(["👤 JUGADORES", "⚾ RESULTADOS", "📅 CALENDARIO"])
        with tj:
            sel = st.selectbox("Jugador:", ["NUEVO JUGADOR"] + sorted(df_j["Nombre"].tolist()))
            if 'v' not in st.session_state or st.session_state.get('last') != sel:
                if sel != "NUEVO JUGADOR": st.session_state.v = df_j[df_j["Nombre"] == sel].iloc[0].to_dict()
                else: st.session_state.v = {c:0 for c in COLS_J}; st.session_state.v["Nombre"]=""; st.session_state.v["Categoria"]="Softbolista"
                st.session_state.last = sel
            with st.form("fj"):
                n = st.text_input("Nombre", value=st.session_state.v["Nombre"])
                cat = st.selectbox("Categoría", ["Novato", "Softbolista", "Refuerzo"], index=1)
                eq = st.selectbox("Equipo", df_e["Nombre"].unique() if not df_e.empty else ["Crea equipo"])
                v1, v2, v3, v4, v5 = st.columns(5)
                vb = v1.number_input("VB", value=int(st.session_state.v["VB"])); h = v2.number_input("H", value=int(st.session_state.v["H"]))
                h2 = v3.number_input("2B", value=int(st.session_state.v["2B"])); h3 = v4.number_input("3B", value=int(st.session_state.v["3B"])); hr = v5.number_input("HR", value=int(st.session_state.v["HR"]))
                g = st.number_input("G", value=int(st.session_state.v["G"])); p = st.number_input("P", value=int(st.session_state.v["P"]))
                if st.form_submit_button("💾 GUARDAR"):
                    df_j = df_j[df_j["Nombre"] != n]
                    nueva = pd.DataFrame([{"Nombre":n,"Equipo":eq,"Categoria":cat,"VB":vb,"H":h,"2B":h2,"3B":h3,"HR":hr,"G":g,"P":p}])
                    pd.concat([df_j, nueva], ignore_index=True).to_csv(JUGADORES_FILE, index=False); st.rerun()
        with tr:
            with st.form("fr"):
                jor = st.number_input("Jornada", 1, 50, 1)
                v, cv = st.selectbox("Visitante", df_e["Nombre"].unique()), st.number_input("Carreras V", 0)
                h, ch = st.selectbox("Home Club", df_e["Nombre"].unique()), st.number_input("Carreras H", 0)
                if st.form_submit_button("💾 GUARDAR SCORE"):
                    pd.concat([df_games, pd.DataFrame([{"Jornada":jor, "Visitante":v, "CarrerasV":cv, "HomeClub":h, "CarrerasH":ch}])], ignore_index=True).to_csv(JUEGOS_FILE, index=False); st.rerun()
        with tc:
            with st.form("fc"):
                jor_c = st.number_input("Jornada #", 1, 50, 1); f = st.date_input("Fecha")
                v_c, h_c = st.selectbox("Visitante ", df_e["Nombre"].unique()), st.selectbox("Home Club ", df_e["Nombre"].unique())
                cam = st.text_input("Campo", "Campo Principal")
                if st.form_submit_button("📅 PROGRAMAR"):
                    pd.concat([df_cal, pd.DataFrame([{"Jornada":jor_c, "Fecha":str(f), "Hora":"10:00 AM", "Visitante":v_c, "HomeClub":h_c, "Campo":cam}])], ignore_index=True).to_csv(CALENDARIO_FILE, index=False); st.rerun()

elif menu == "🏘️ EQUIPOS":
    if st.session_state.admin:
        with st.form("fe"):
            n_e = st.text_input("Equipo"); d_e = st.number_input("Debut", 2024, 2026, 2026)
            if st.form_submit_button("Añadir"):
                pd.concat([df_e, pd.DataFrame([{"Nombre":n_e, "Debut":d_e, "Fin":0}])], ignore_index=True).to_csv(EQUIPOS_FILE, index=False); st.rerun()
    st.table(df_e)

elif menu == "🗑️ BORRAR":
    if st.session_state.admin:
        j_d = st.selectbox("Eliminar Jugador:", [""] + sorted(df_j["Nombre"].tolist()))
        if st.button("❌ ELIMINAR"):
            df_j[df_j["Nombre"] != j_d].to_csv(JUGADORES_FILE, index=False); st.rerun()

elif menu == "💾 RESPALDO":
    st.download_button("📥 Descargar Jugadores", df_j.to_csv(index=False), "jugadores.csv")
    st.download_button("📥 Descargar Resultados", df_games.to_csv(index=False), "juegos.csv")
