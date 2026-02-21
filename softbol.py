import streamlit as st
import pandas as pd
import os
import gc

# --- 1. CONFIGURACIÓN ---
NOMBRE_LIGA = "LIGA DE SOFTBOL DOMINICAL"
ANIO_ACTUAL = 2026
LOGO_URL = "https://cdn-icons-png.flaticon.com" 

DATA_DIR = "liga_softbol_final_2026"
if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)

J_FILE = os.path.join(DATA_DIR, "jugadores_master.csv")
E_FILE = os.path.join(DATA_DIR, "equipos_master.csv")
G_FILE = os.path.join(DATA_DIR, "juegos_2026.csv")
C_FILE = os.path.join(DATA_DIR, "calendario_2026.csv")

# --- 2. CARGA DE DATOS ---
st.set_page_config(page_title=NOMBRE_LIGA, layout="wide", page_icon="🥎")

COLS_J = ["Nombre", "Equipo", "Categoria", "VB", "H", "2B", "3B", "HR", "G", "P", "IP", "ER", "K"]

if os.path.exists(J_FILE):
    df_j = pd.read_csv(J_FILE)
    for col in COLS_J:
        if col not in df_j.columns: df_j[col] = 0
else:
    df_j = pd.DataFrame(columns=COLS_J)

df_e = pd.read_csv(E_FILE) if os.path.exists(E_FILE) else pd.DataFrame(columns=["Nombre", "Debut", "Fin"])
df_g = pd.read_csv(G_FILE) if os.path.exists(G_FILE) else pd.DataFrame(columns=["Jornada", "Visitante", "CV", "HomeClub", "CH"])
df_c = pd.read_csv(C_FILE) if os.path.exists(C_FILE) else pd.DataFrame(columns=["Jornada", "Fecha", "Hora", "Visitante", "HomeClub", "Campo"])

# --- 3. BARRA LATERAL ---
with st.sidebar:
    st.image(LOGO_URL, width=100)
    st.title(f"🏆 {NOMBRE_LIGA}")
    
    st.info("📂 **RECUPERAR:** Sube tu respaldo si la app se reinicia.")
    subir = st.file_uploader("Subir jugadores.csv", type="csv")
    if subir:
        df_j = pd.read_csv(subir)
        df_j.to_csv(J_FILE, index=False)
        st.success("¡Datos recuperados!"); st.rerun()

    if 'admin' not in st.session_state: st.session_state.admin = False
    menu = st.radio("Secciones:", ["🏠 INICIO", "📊 STANDING", "🏆 LÍDERES", "📋 ROSTERS", "📜 HISTORIAL", "✍️ REGISTRAR", "💾 RESPALDO"])

# --- 4. SECCIONES ---

if menu == "🏠 INICIO":
    st.markdown(f"<h1 style='color:#d4af37;'>{NOMBRE_LIGA}</h1>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader(f"Temporada {ANIO_ACTUAL}")
        if not df_g.empty: st.metric("Jornada Actual", int(df_g["Jornada"].max()))
    with col_b:
        st.subheader("📅 Próximos Juegos")
        st.dataframe(df_c, hide_index=True)

elif menu == "📊 STANDING":
    st.header("Tabla de Posiciones")
    if not df_g.empty:
        stats = []
        for eq in df_e["Nombre"].unique():
            v, h = df_g[df_g["Visitante"] == eq], df_g[df_g["HomeClub"] == eq]
            g = len(v[v["CV"] > v["CH"]]) + len(h[h["CH"] > h["CV"]])
            p = len(v[v["CV"] < v["CH"]]) + len(h[h["CH"] < h["CV"]])
            stats.append({"Equipo": eq, "G": g, "P": p, "AVG": round(g/(g+p), 3) if (g+p)>0 else 0})
        st.table(pd.DataFrame(stats).sort_values("AVG", ascending=False))

elif menu == "🏆 LÍDERES":
    st.header("🥇 Cuadro de Honor Departamental")
    t1, t2 = st.tabs(["⚾ BATEO", "🎯 PITCHEO"])
    
    with t1:
        c1, c2 = st.columns(2)
        c1.write("### Hits (H)"); c1.dataframe(df_j.nlargest(10, 'H')[['Nombre', 'Equipo', 'H']], hide_index=True)
        c1.write("### Dobles (2B)"); c1.dataframe(df_j.nlargest(10, '2B')[['Nombre', 'Equipo', '2B']], hide_index=True)
        c2.write("### Home Runs (HR)"); c2.dataframe(df_j.nlargest(10, 'HR')[['Nombre', 'Equipo', 'HR']], hide_index=True)
        c2.write("### Triples (3B)"); c2.dataframe(df_j.nlargest(10, '3B')[['Nombre', 'Equipo', '3B']], hide_index=True)

    with t2:
        df_p = df_j[df_j["IP"] > 0].copy()
        df_p["ERA"] = (df_p["ER"] * 7) / df_p["IP"]
        
        c1, c2 = st.columns(2)
        c1.write("### Efectividad (ERA)"); c1.dataframe(df_p.nsmallest(5, 'ERA')[['Nombre', 'Equipo', 'ERA']], hide_index=True)
        c1.write("### Ponches (K)"); c1.dataframe(df_p.nlargest(5, 'K')[['Nombre', 'Equipo', 'K']], hide_index=True)
        c2.write("### Ganados (G)"); c2.dataframe(df_p.nlargest(5, 'G')[['Nombre', 'Equipo', 'G']], hide_index=True)
        c2.write("### Innings (IP)"); c2.dataframe(df_p.nlargest(5, 'IP')[['Nombre', 'Equipo', 'IP']], hide_index=True)

elif menu == "📋 ROSTERS":
    eq_s = st.selectbox("Equipo:", df_e["Nombre"].unique())
    roster = df_j[df_j["Equipo"] == eq_s].copy()
    roster["AVG"] = (roster["H"] / roster["VB"]).fillna(0).apply(lambda x: f"{x:.3f}")
    st.dataframe(roster, hide_index=True)

elif menu == "✍️ REGISTRAR":
    if st.session_state.admin:
        tj, tp = st.tabs(["BATEO", "PITCHEO"])
        with tj:
            with st.form("f_b"):
                nom = st.text_input("Nombre"); eq = st.selectbox("Equipo", df_e["Nombre"].unique())
                v1, v2, v3, v4, v5 = st.columns(5)
                vb, h = v1.number_input("VB", 0), v2.number_input("H", 0)
                d2, d3, hr = v3.number_input("2B", 0), v4.number_input("3B", 0), v5.number_input("HR", 0)
                if st.form_submit_button("💾 GUARDAR BATEO"):
                    df_j = pd.concat([df_j[df_j["Nombre"] != nom], pd.DataFrame([{"Nombre":nom,"Equipo":eq,"VB":vb,"H":h,"2B":d2,"3B":d3,"HR":hr}])], ignore_index=True)
                    df_j.to_csv(J_FILE, index=False); gc.collect(); st.success("¡Guardado!"); st.rerun()
        with tp:
            with st.form("f_p"):
                nom_p = st.selectbox("Lanzador:", df_j["Nombre"].unique())
                c1, c2, c3, c4, c5 = st.columns(5)
                g, p = c1.number_input("G", 0), c2.number_input("P", 0)
                ip, er, k = c3.number_input("IP", 0.0), c4.number_input("ER", 0), c5.number_input("K", 0)
                if st.form_submit_button("💾 GUARDAR PITCHEO"):
                    df_j.loc[df_j["Nombre"] == nom_p, ["G", "P", "IP", "ER", "K"]] = [g, p, ip, er, k]
                    df_j.to_csv(J_FILE, index=False); gc.collect(); st.success("¡Guardado!"); st.rerun()
    else: st.warning("Área de Administrador.")

elif menu == "💾 RESPALDO":
    if st.session_state.admin:
        st.download_button("📥 DESCARGAR JUGADORES", df_j.to_csv(index=False), "jugadores.csv")
        st.download_button("📥 DESCARGAR RESULTADOS", df_g.to_csv(index=False), "juegos.csv")
