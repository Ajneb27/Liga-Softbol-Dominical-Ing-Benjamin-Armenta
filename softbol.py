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

# --- 2. MOTOR DE DATOS ---
def cargar_datos(archivo, columnas):
    if os.path.exists(archivo):
        try:
            df = pd.read_csv(archivo)
            for c in columnas:
                if c not in df.columns: df[c] = "Softbolista" if c == "Categoria" else 0
            return df
        except: return pd.DataFrame(columns=columnas)
    return pd.DataFrame(columns=columnas)

# --- 3. INICIALIZACIÓN Y ESTILO ---
st.set_page_config(page_title=NOMBRE_LIGA, layout="wide", page_icon="🥎")

st.markdown("""
    <style>
    .gold-header { color: #d4af37; font-weight: bold; border-bottom: 3px solid #d4af37; padding-bottom: 10px; margin-bottom: 20px; }
    .stMetric { background-color: white; border-radius: 10px; border-left: 5px solid #d4af37; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

if 'admin' not in st.session_state: st.session_state.admin = False

df_j = cargar_datos(JUGADORES_FILE, ["Nombre", "Equipo", "Categoria", "VB", "H", "2B", "3B", "HR", "G", "P"])
df_e = cargar_datos(EQUIPOS_FILE, ["Nombre", "Debut", "Fin"])
df_games = cargar_datos(JUEGOS_FILE, ["Visitante", "CarrerasV", "HomeClub", "CarrerasH"])

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
    st.write(f"### Bienvenidos a la Temporada {ANIO_ACTUAL}")
    st.info(f"Uniendo a la familia deportiva desde {ANIO_INICIO_LIGA}.")

elif menu == "📊 STANDING":
    st.markdown("<h1 class='gold-header'>📊 Tabla de Posiciones General</h1>", unsafe_allow_html=True)
    if not df_games.empty and not df_e.empty:
        stats = []
        for equipo in df_e[df_e["Fin"] == 0]["Nombre"].unique():
            v = df_games[df_games["Visitante"] == equipo]
            h = df_games[df_games["HomeClub"] == equipo]
            
            ganados = len(v[v["CarrerasV"] > v["CarrerasH"]]) + len(h[h["CarrerasH"] > h["CarrerasV"]])
            perdidos = len(v[v["CarrerasV"] < v["CarrerasH"]]) + len(h[h["CarrerasH"] < h["CarrerasV"]])
            empates = len(v[v["CarrerasV"] == v["CarrerasH"]]) + len(h[h["CarrerasH"] == h["CarrerasV"]])
            
            cf = v["CarrerasV"].sum() + h["CarrerasH"].sum()
            ce = v["CarrerasH"].sum() + h["CarrerasV"].sum()
            jj = ganados + perdidos + empates
            avg = ganados / jj if jj > 0 else 0
            
            stats.append({"Equipo": equipo, "JJ": jj, "G": ganados, "P": perdidos, "E": empates, "CF": cf, "CE": ce, "AVG": round(avg, 3)})
        
        df_st = pd.DataFrame(stats).sort_values(by=["AVG", "G", "CF"], ascending=False)
        st.table(df_st)
    else: st.info("No hay juegos registrados.")

elif menu == "🏆 LÍDERES":
    st.markdown("<h1 class='gold-header'>🥇 Cuadro de Honor</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["⚾ BATEO", "🎯 PITCHEO"])
    with t1:
        c1, c2 = st.columns(2)
        c1.subheader("Hits (H)"); c1.dataframe(df_j.nlargest(10, 'H')[['Nombre', 'Equipo', 'H']], hide_index=True)
        c2.subheader("Home Runs (HR)"); c2.dataframe(df_j.nlargest(10, 'HR')[['Nombre', 'Equipo', 'HR']], hide_index=True)
    with t2:
        c1, c2 = st.columns(2)
        c1.subheader("Ganados (G)"); c1.dataframe(df_j.nlargest(10, 'G')[['Nombre', 'Equipo', 'G']], hide_index=True)
        c2.subheader("Perdidos (P)"); c2.dataframe(df_j.nlargest(10, 'P')[['Nombre', 'Equipo', 'P']], hide_index=True)

elif menu == "📋 ROSTERS":
    if not df_e.empty:
        eq = st.selectbox("Equipo:", df_e[df_e["Fin"] == 0]["Nombre"].unique())
        st.dataframe(df_j[df_j["Equipo"] == eq], use_container_width=True, hide_index=True)

elif menu == "📜 HISTORIAL":
    if not df_j.empty:
        j_s = st.selectbox("Jugador:", sorted(df_j["Nombre"].unique().tolist()))
        d = df_j[df_j["Nombre"] == j_s].iloc[0]
        st.header(f"Ficha: {d['Nombre']}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Equipo", d['Equipo']); c2.metric("Categoría", d['Categoria'])
        avg = (d['H'] / d['VB']) if d['VB'] > 0 else 0
        c3.metric("AVG", f"{avg:.3f}")
        st.write(f"**Bateo:** VB:{int(d['VB'])} H:{int(d['H'])} 2B:{int(d['2B'])} 3B:{int(d['3B'])} HR:{int(d['HR'])}")
        st.write(f"**Pitching:** G:{int(d['G'])} P:{int(d['P'])}")

elif menu == "✍️ REGISTRAR":
    if st.session_state.admin:
        t_jug, t_res = st.tabs(["👤 JUGADORES", "⚾ RESULTADOS"])
        with t_jug:
            sel = st.selectbox("Jugador:", ["NUEVO JUGADOR"] + sorted(df_j["Nombre"].unique().tolist()))
            if 'vals' not in st.session_state or st.session_state.get('last_sel') != sel:
                if sel != "NUEVO JUGADOR": st.session_state.vals = df_j[df_j["Nombre"] == sel].iloc[0].to_dict()
                else: st.session_state.vals = {"Nombre": "", "Equipo": None, "Categoria": "Softbolista", "VB": 0, "H": 0, "2B": 0, "3B": 0, "HR": 0, "G": 0, "P": 0}
                st.session_state.last_sel = sel
            
            with st.form("f_j"):
                nom = st.text_input("Nombre", value=st.session_state.vals["Nombre"])
                cat = st.selectbox("Categoría", ["Novato", "Softbolista", "Refuerzo"], index=["Novato", "Softbolista", "Refuerzo"].index(st.session_state.vals["Categoria"]) if st.session_state.vals["Categoria"] in ["Novato", "Softbolista", "Refuerzo"] else 1)
                eq = st.selectbox("Equipo", df_e["Nombre"].unique() if not df_e.empty else ["Crea equipo"])
                c1, c2, c3, c4, c5 = st.columns(5)
                vb = c1.number_input("VB", value=int(st.session_state.vals["VB"])); h = c2.number_input("H", value=int(st.session_state.vals["H"]))
                h2 = c3.number_input("2B", value=int(st.session_state.vals["2B"])); h3 = c4.number_input("3B", value=int(st.session_state.vals["3B"])); hr = c5.number_input("HR", value=int(st.session_state.vals["HR"]))
                pg = st.number_input("G", value=int(st.session_state.vals["G"])); pp = st.number_input("P", value=int(st.session_state.vals["P"]))
                if st.form_submit_button("💾 GUARDAR JUGADOR"):
                    df_j = df_j[df_j["Nombre"] != nom]
                    nueva = pd.DataFrame([{"Nombre": nom, "Equipo": eq, "Categoria": cat, "VB": vb, "H": h, "2B": h2, "3B": h3, "HR": hr, "G": pg, "P": pp}])
                    pd.concat([df_j, nueva], ignore_index=True).to_csv(JUGADORES_FILE, index=False); st.success("Guardado"); st.rerun()

        with t_res:
            with st.form("f_g"):
                v = st.selectbox("Visitante", df_e["Nombre"].unique()); cv = st.number_input("Carreras V", 0)
                h = st.selectbox("Home Club", df_e["Nombre"].unique()); ch = st.number_input("Carreras H", 0)
                if st.form_submit_button("💾 GUARDAR RESULTADO"):
                    nuevo_g = pd.DataFrame([{"Visitante": v, "CarrerasV": cv, "HomeClub": h, "CarrerasH": ch}])
                    pd.concat([df_games, nuevo_g], ignore_index=True).to_csv(JUEGOS_FILE, index=False); st.success("Juego registrado"); st.rerun()
    else: st.warning("Solo Admin")

elif menu == "🏘️ EQUIPOS":
    if st.session_state.admin:
        with st.form("eq"):
            n = st.text_input("Equipo"); d = st.number_input("Debut", 2024, 2026, 2026)
            if st.form_submit_button("Añadir"):
                pd.concat([df_e, pd.DataFrame([{"Nombre": n, "Debut": d, "Fin": 0}])], ignore_index=True).to_csv(EQUIPOS_FILE, index=False); st.rerun()
    st.table(df_e)

elif menu == "🗑️ BORRAR":
    if st.session_state.admin:
        j_del = st.selectbox("Borrar Jugador:", [""] + sorted(df_j["Nombre"].tolist()))
        if st.button("❌ Eliminar") and j_del != "":
            df_j = df_j[df_j["Nombre"] != j_del]; df_j.to_csv(JUGADORES_FILE, index=False); st.rerun()

elif menu == "💾 RESPALDO":
    st.download_button("📥 Jugadores", df_j.to_csv(index=False), "jugadores.csv")
    st.download_button("📥 Juegos", df_games.to_csv(index=False), "juegos.csv")
