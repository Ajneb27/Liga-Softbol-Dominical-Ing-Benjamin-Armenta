import streamlit as st
import pandas as pd
import os
import gc

# --- 1. CONFIGURACIÓN E IDENTIDAD ---
NOMBRE_LIGA = "LIGA DE SOFTBOL DOMINICAL"
ANIO_ACTUAL = 2026
LOGO_URL = "https://cdn-icons-png.flaticon.com" 

DATA_DIR = "liga_softbol_final_2026"
if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)

J_FILE = os.path.join(DATA_DIR, "jugadores_master.csv")
E_FILE = os.path.join(DATA_DIR, "equipos_master.csv")
G_FILE = os.path.join(DATA_DIR, "juegos_2026.csv")
C_FILE = os.path.join(DATA_DIR, "calendario_2026.csv")

# --- 2. MOTOR DE DATOS ---
st.set_page_config(page_title=NOMBRE_LIGA, layout="wide", page_icon="🥎")

COLS_J = ["Nombre", "Equipo", "Categoria", "VB", "H", "2B", "3B", "HR", "G", "P", "IP", "ER", "K"]

def cargar_csv(archivo, columnas):
    if os.path.exists(archivo):
        df = pd.read_csv(archivo)
        for c in columnas:
            if c not in df.columns: df[c] = "Softbolista" if c == "Categoria" else 0
        return df
    return pd.DataFrame(columns=columnas)

df_j = cargar_csv(J_FILE, COLS_J)
df_e = cargar_csv(E_FILE, ["Nombre", "Debut", "Fin"])
df_g = cargar_csv(G_FILE, ["Jornada", "Visitante", "CV", "HomeClub", "CH"])
df_c = cargar_csv(C_FILE, ["Jornada", "Fecha", "Hora", "Visitante", "HomeClub", "Campo"])

# --- 3. BARRA LATERAL ---
with st.sidebar:
    st.image(LOGO_URL, width=100)
    st.title(f"🏆 {NOMBRE_LIGA}")
    
    st.info("📂 **RECUPERAR:** Sube tu respaldo si la app se reinicia.")
    subir = st.file_uploader("Subir jugadores.csv", type="csv")
    if subir:
        pd.read_csv(subir).to_csv(J_FILE, index=False)
        st.success("¡Datos recuperados!"); st.rerun()

    if 'admin' not in st.session_state: st.session_state.admin = False
    menu = st.radio("Secciones:", ["🏠 INICIO", "📊 STANDING", "🏆 LÍDERES", "📋 ROSTERS", "📜 HISTORIAL", "🏘️ EQUIPOS", "✍️ REGISTRAR", "🗑️ BORRAR", "💾 RESPALDO"])

# --- 4. LÓGICA DE SECCIONES ---

if menu == "🏠 INICIO":
    c1, c2 = st.columns([1, 3])
    with c1: st.image(LOGO_URL, width=150)
    with c2: st.markdown(f"<h1 style='color:#d4af37;'>{NOMBRE_LIGA}</h1>", unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader(f"Temporada {ANIO_ACTUAL}")
        if not df_g.empty: st.metric("Jornada Actual", int(df_g["Jornada"].max()))
    with col_b:
        st.subheader("📅 Próximos Juegos")
        st.dataframe(df_c, hide_index=True, use_container_width=True)

elif menu == "📊 STANDING":
    st.header("📊 Tabla de Posiciones")
    if not df_g.empty and not df_e.empty:
        stats = []
        for eq in df_e[df_e["Fin"] == 0]["Nombre"].unique():
            v, h = df_g[df_g["Visitante"] == eq], df_g[df_g["HomeClub"] == eq]
            g = len(v[v["CV"] > v["CH"]]) + len(h[h["CH"] > h["CV"]])
            p = len(v[v["CV"] < v["CH"]]) + len(h[h["CH"] < h["CV"]])
            stats.append({"Equipo": eq, "JJ": g+p, "G": g, "P": p, "AVG": round(g/(g+p), 3) if (g+p)>0 else 0})
        st.table(pd.DataFrame(stats).sort_values(by=["AVG", "G"], ascending=False))

elif menu == "🏆 LÍDERES":
    st.header("🥇 Cuadro de Honor Departamental")
    cat_f = st.selectbox("Filtrar por Categoría:", ["TODOS", "Novato", "Softbolista", "Refuerzo"])
    df_l = df_j if cat_f == "TODOS" else df_j[df_j["Categoria"] == cat_f]
    
    t1, t2 = st.tabs(["⚾ BATEO", "🎯 PITCHEO"])
    with t1:
        c1, c2 = st.columns(2)
        c1.write("### Hits (H)"); c1.dataframe(df_l.nlargest(10, 'H')[['Nombre', 'Equipo', 'H']], hide_index=True)
        c1.write("### Dobles (2B)"); c1.dataframe(df_l.nlargest(10, '2B')[['Nombre', 'Equipo', '2B']], hide_index=True)
        c2.write("### Home Runs (HR)"); c2.dataframe(df_l.nlargest(10, 'HR')[['Nombre', 'Equipo', 'HR']], hide_index=True)
        c2.write("### Triples (3B)"); c2.dataframe(df_l.nlargest(10, '3B')[['Nombre', 'Equipo', '3B']], hide_index=True)
    with t2:
        df_p = df_l[(df_l["G"] > 0) | (df_l["P"] > 0)].copy()
        c1, c2 = st.columns(2)
        c1.write("### Juegos Ganados (G)"); c1.dataframe(df_p.nlargest(10, 'G')[['Nombre', 'Equipo', 'G', 'P']], hide_index=True)
        c2.write("### Ponches (K)"); c2.dataframe(df_p.nlargest(10, 'K')[['Nombre', 'Equipo', 'K', 'G', 'P']], hide_index=True)

elif menu == "📋 ROSTERS":
    if not df_e.empty:
        eq_s = st.selectbox("Equipo:", df_e["Nombre"].unique())
        df_roster = df_j[df_j["Equipo"] == eq_s].copy()
        df_roster["AVG"] = (df_roster["H"] / df_roster["VB"]).fillna(0).apply(lambda x: f"{x:.3f}")
        st.dataframe(df_roster[["Nombre", "Categoria", "VB", "H", "2B", "3B", "HR", "AVG"]], use_container_width=True, hide_index=True)

elif menu == "📜 HISTORIAL":
    st.header("📜 Historial de Carrera")
    if not df_j.empty:
        j_sel = st.selectbox("Buscar Jugador:", sorted(df_j["Nombre"].unique()))
        d = df_j[df_j["Nombre"] == j_sel].iloc[0]
        c1, c2, c3 = st.columns(3)
        c1.metric("Equipo Actual", d['Equipo'])
        c2.metric("Categoría", d['Categoria'])
        avg = (d['H'] / d['VB']) if d['VB'] > 0 else 0
        c3.metric("AVG Carrera", f"{avg:.3f}")
        st.info(f"**Bateo:** VB: {int(d['VB'])} | H: {int(d['H'])} | 2B: {int(d['2B'])} | 3B: {int(d['3B'])} | HR: {int(d['HR'])}")
        st.success(f"**Pitcheo:** G: {int(d['G'])} | P: {int(d['P'])} | IP: {d['IP']} | K: {int(d['K'])}")

elif menu == "✍️ REGISTRAR":
    if st.session_state.admin:
        tj, tp = st.tabs(["BATEO Y CATEGORÍA", "PITCHEO"])
        with tj:
            with st.form("f_bateo"):
                nom = st.text_input("Nombre Completo")
                cat = st.selectbox("Categoría", ["Novato", "Softbolista", "Refuerzo"])
                eq = st.selectbox("Equipo", df_e["Nombre"].unique() if not df_e.empty else ["Crea equipo"])
                c1, c2, c3, c4, c5 = st.columns(5)
                vb, h = c1.number_input("VB", 0), c2.number_input("H", 0)
                d2, d3, hr = c3.number_input("2B", 0), c4.number_input("3B", 0), c5.number_input("HR", 0)
                if st.form_submit_button("💾 GUARDAR BATEO"):
                    df_j = pd.concat([df_j[df_j["Nombre"] != nom], pd.DataFrame([{"Nombre":nom,"Equipo":eq,"Categoria":cat,"VB":vb,"H":h,"2B":d2,"3B":d3,"HR":hr}])], ignore_index=True)
                    df_j.to_csv(J_FILE, index=False); gc.collect(); st.success("¡Guardado!"); st.rerun()
        with tp:
            with st.form("f_pitching"):
                nom_p = st.selectbox("Lanzador:", df_j["Nombre"].unique() if not df_j.empty else ["No hay jugadores"])
                c1, c2, c3, c4, c5 = st.columns(5)
                g, p = c1.number_input("G", 0), c2.number_input("P", 0)
                ip, er, k = c3.number_input("IP", 0.0), c4.number_input("ER", 0), c5.number_input("K", 0)
                if st.form_submit_button("💾 GUARDAR PITCHEO"):
                    df_j.loc[df_j["Nombre"] == nom_p, ["G", "P", "IP", "ER", "K"]] = [g, p, ip, er, k]
                    df_j.to_csv(J_FILE, index=False); gc.collect(); st.success("¡Pitcheo Guardado!"); st.rerun()
    else: st.warning("Inicia sesión como administrador.")

elif menu == "💾 RESPALDO":
    if st.session_state.admin:
        st.download_button("📥 DESCARGAR JUGADORES", df_j.to_csv(index=False), "jugadores.csv")
        st.download_button("📥 DESCARGAR RESULTADOS", df_g.to_csv(index=False), "juegos.csv")

elif menu == "🏘️ EQUIPOS":
    if st.session_state.admin:
        with st.form("fe"):
            n_e = st.text_input("Nombre Equipo"); d_e = st.number_input("Debut", 2024, 2026, 2026)
            if st.form_submit_button("Añadir Equipo"):
                pd.concat([df_e, pd.DataFrame([{"Nombre":n_e, "Debut":d_e, "Fin":0}])], ignore_index=True).to_csv(E_FILE, index=False); st.rerun()
    st.table(df_e)

elif menu == "🗑️ BORRAR":
    if st.session_state.admin:
        j_d = st.selectbox("Eliminar Jugador:", [""] + sorted(df_j["Nombre"].tolist()))
        if st.button("❌ ELIMINAR"):
            df_j[df_j["Nombre"] != j_d].to_csv(J_FILE, index=False); st.rerun()
