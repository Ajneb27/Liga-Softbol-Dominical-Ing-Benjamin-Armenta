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

# --- 2. SISTEMA DE RECUPERACIÓN DE DATOS ---
st.set_page_config(page_title=NOMBRE_LIGA, layout="wide", page_icon="🥎")

with st.sidebar:
    st.image(LOGO_URL, width=100)
    st.title(f"🏆 {NOMBRE_LIGA}")
    
    st.info("📂 **RECUPERAR DATOS:** Si la app se reinicia, sube aquí tus archivos descargados.")
    subir_j = st.file_uploader("Subir jugadores.csv", type="csv")
    if subir_j:
        pd.read_csv(subir_j).to_csv(J_FILE, index=False)
        st.success("Jugadores cargados.")

    # Carga interna de archivos
    COLS_J = ["Nombre", "Equipo", "Categoria", "VB", "H", "2B", "3B", "HR", "G", "P"]
    df_j = pd.read_csv(J_FILE) if os.path.exists(J_FILE) else pd.DataFrame(columns=COLS_J)
    df_e = pd.read_csv(E_FILE) if os.path.exists(E_FILE) else pd.DataFrame(columns=["Nombre", "Debut", "Fin"])
    df_g = pd.read_csv(G_FILE) if os.path.exists(G_FILE) else pd.DataFrame(columns=["Jornada", "Visitante", "CV", "HomeClub", "CH"])
    df_c = pd.read_csv(C_FILE) if os.path.exists(C_FILE) else pd.DataFrame(columns=["Jornada", "Fecha", "Hora", "Visitante", "HomeClub", "Campo"])

    st.divider()
    if 'admin' not in st.session_state: st.session_state.admin = False
    menu = st.radio("Secciones:", ["🏠 INICIO", "📊 STANDING", "🏆 LÍDERES", "📋 ROSTERS", "📜 HISTORIAL", "🏘️ EQUIPOS", "✍️ REGISTRAR", "🗑️ BORRAR", "💾 RESPALDO"])

# --- 3. SECCIONES (TODO RECUPERADO) ---

if menu == "🏠 INICIO":
    c1, c2 = st.columns([1, 4])
    with c1: st.image(LOGO_URL, width=120)
    with c2: st.markdown(f"<h1 style='color:#d4af37;'>{NOMBRE_LIGA}</h1>", unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader(f"Temporada {ANIO_ACTUAL}")
        if not df_g.empty: st.metric("Jornada Actual", int(df_g["Jornada"].max()))
    with col_b:
        st.subheader("📅 Próximos Juegos")
        if not df_c.empty:
            for _, r in df_c.iterrows():
                st.info(f"**Jor {r['Jornada']}** | {r['Fecha']} - {r['Hora']}\n\n**{r['Visitante']}** vs **{r['HomeClub']}**\n\n📍 {r['Campo']}")

elif menu == "📊 STANDING":
    st.header("📊 Tabla de Posiciones")
    if not df_g.empty and not df_e.empty:
        stats = []
        for eq in df_e[df_e["Fin"] == 0]["Nombre"].unique():
            v, h = df_g[df_g["Visitante"] == eq], df_g[df_g["HomeClub"] == eq]
            g = len(v[v["CV"] > v["CH"]]) + len(h[h["CH"] > h["CV"]])
            p = len(v[v["CV"] < v["CH"]]) + len(h[h["CH"] < h["CV"]])
            cf, ce = (v["CV"].sum() + h["CH"].sum()), (v["CH"].sum() + v["CV"].sum())
            jj = g + p
            avg = g / jj if jj > 0 else 0
            stats.append({"Equipo": eq, "JJ": jj, "G": g, "P": p, "CF": cf, "CE": ce, "DIF": cf-ce, "AVG": round(avg, 3)})
        st.table(pd.DataFrame(stats).sort_values(by=["AVG", "G"], ascending=False))

elif menu == "🏆 LÍDERES":
    st.header("🥇 Departamentos Individuales")
    cat_f = st.selectbox("Filtrar Categoría:", ["TODOS", "Novato", "Softbolista", "Refuerzo"])
    df_l = df_j if cat_f == "TODOS" else df_j[df_j["Categoria"] == cat_f]
    
    t1, t2 = st.tabs(["⚾ BATEO", "🎯 PITCHEO"])
    with t1:
        c1, c2 = st.columns(2)
        c1.write("### Hits (H)"); c1.dataframe(df_l.nlargest(10, 'H')[['Nombre', 'Equipo', 'H']], hide_index=True)
        c1.write("### Dobles (2B)"); c1.dataframe(df_l.nlargest(10, '2B')[['Nombre', 'Equipo', '2B']], hide_index=True)
        c2.write("### Home Runs (HR)"); c2.dataframe(df_l.nlargest(10, 'HR')[['Nombre', 'Equipo', 'HR']], hide_index=True)
        c2.write("### Triples (3B)"); c2.dataframe(df_l.nlargest(10, '3B')[['Nombre', 'Equipo', '3B']], hide_index=True)
    with t2:
        df_p = df_l[(df_l["G"] > 0) | (df_l["P"] > 0)]
        st.write("### Ganados (G)")
        st.dataframe(df_p.nlargest(10, 'G')[['Nombre', 'Equipo', 'G', 'P']], hide_index=True)

elif menu == "📋 ROSTERS":
    if not df_e.empty:
        eq_s = st.selectbox("Seleccionar Equipo:", df_e["Nombre"].unique())
        df_roster = df_j[df_j["Equipo"] == eq_s].copy()
        df_roster["AVG"] = (df_roster["H"] / df_roster["VB"]).fillna(0).apply(lambda x: f"{x:.3f}")
        st.dataframe(df_roster[["Nombre", "Categoria", "VB", "H", "2B", "3B", "HR", "AVG"]].sort_values("AVG", ascending=False), hide_index=True)

elif menu == "📜 HISTORIAL":
    if not df_j.empty:
        j_sel = st.selectbox("Jugador:", sorted(df_j["Nombre"].unique()))
        d = df_j[df_j["Nombre"] == j_sel].iloc
        st.subheader(f"Ficha de {d['Nombre']}")
        st.write(f"**Bateo:** VB: {int(d['VB'])} | H: {int(d['H'])} | 2B: {int(d['2B'])} | 3B: {int(d['3B'])} | HR: {int(d['HR'])}")
        st.write(f"**Pitcheo:** Ganados: {int(d['G'])} | Perdidos: {int(d['P'])}")

elif menu == "✍️ REGISTRAR":
    if st.session_state.admin:
        tj, tr, tc = st.tabs(["👤 JUGADORES", "⚾ RESULTADOS", "📅 CALENDARIO"])
        with tj:
            with st.form("fj"):
                n = st.text_input("Nombre"); c = st.selectbox("Cat", ["Novato", "Softbolista", "Refuerzo"]); e = st.selectbox("Equipo", df_e["Nombre"].unique())
                v1, v2, v3, v4, v5 = st.columns(5)
                vb, h = v1.number_input("VB", 0), v2.number_input("H", 0)
                h2, h3 = v3.number_input("2B", 0), v4.number_input("3B", 0)
                hr = v5.number_input("HR", 0)
                pg, pp = st.number_input("G", 0), st.number_input("P", 0)
                if st.form_submit_button("💾 GUARDAR"):
                    df_j = pd.concat([df_j[df_j["Nombre"] != n], pd.DataFrame([{"Nombre":n,"Equipo":e,"Categoria":c,"VB":vb,"H":h,"2B":h2,"3B":h3,"HR":hr,"G":pg,"P":pp}])], ignore_index=True)
                    df_j.to_csv(J_FILE, index=False); gc.collect(); st.success("Guardado!"); st.rerun()
        with tr:
            with st.form("fr"):
                jor = st.number_input("Jornada", 1); v = st.selectbox("Visitante", df_e["Nombre"].unique()); cv = st.number_input("CV", 0)
                h_c = st.selectbox("Home Club", df_e["Nombre"].unique()); ch = st.number_input("CH", 0)
                if st.form_submit_button("💾 GUARDAR SCORE"):
                    pd.concat([df_g, pd.DataFrame([{"Jornada":jor, "Visitante":v, "CV":cv, "HomeClub":h_c, "CH":ch}])], ignore_index=True).to_csv(G_FILE, index=False); st.rerun()
        with tc:
            with st.form("fc"):
                j_c, f, ho = st.number_input("Jornada", 1), st.text_input("Fecha"), st.text_input("Hora")
                vi, hc, ca = st.selectbox("Vis", df_e["Nombre"].unique()), st.selectbox("HC", df_e["Nombre"].unique()), st.text_input("Campo")
                if st.form_submit_button("📅 PROGRAMAR"):
                    pd.concat([df_c, pd.DataFrame([{"Jornada":j_c, "Fecha":f, "Hora":ho, "Visitante":vi, "HomeClub":hc, "Campo":ca}])], ignore_index=True).to_csv(C_FILE, index=False); st.rerun()

elif menu == "💾 RESPALDO":
    if st.session_state.admin:
        st.download_button("📥 DESCARGAR JUGADORES", df_j.to_csv(index=False), "jugadores.csv")
        st.download_button("📥 DESCARGAR RESULTADOS", df_g.to_csv(index=False), "juegos.csv")
