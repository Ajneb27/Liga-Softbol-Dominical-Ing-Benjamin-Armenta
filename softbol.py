import streamlit as st
import pandas as pd
import os
import gc

# --- 1. CONFIGURACIÓN E IDENTIDAD ---
NOMBRE_LIGA = "LIGA DE SOFTBOL DOMINICAL"
ANIO_ACTUAL = 2026
LOGO_LIGA = "https://cdn-icons-png.flaticon.com" 

DATA_DIR = "liga_softbol_final_2026"
LOGOS_DIR = os.path.join(DATA_DIR, "logos_equipos")
if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)
if not os.path.exists(LOGOS_DIR): os.makedirs(LOGOS_DIR)

J_FILE = os.path.join(DATA_DIR, "jugadores_master.csv")
E_FILE = os.path.join(DATA_DIR, "equipos_master.csv")
G_FILE = os.path.join(DATA_DIR, "juegos_2026.csv")
C_FILE = os.path.join(DATA_DIR, "calendario_2026.csv")

# --- 2. MOTOR DE DATOS ---
st.set_page_config(page_title=NOMBRE_LIGA, layout="wide", page_icon="🥎")

def cargar_csv(archivo, columnas):
    if os.path.exists(archivo):
        try:
            df = pd.read_csv(archivo)
            for c in columnas:
                if c not in df.columns: df[c] = "Softbolista" if c == "Categoria" else 0
            return df
        except: return pd.DataFrame(columns=columnas)
    return pd.DataFrame(columns=columnas)

df_j = cargar_csv(J_FILE, ["Nombre", "Equipo", "Categoria", "VB", "H", "2B", "3B", "HR", "G", "P"])
df_e = cargar_csv(E_FILE, ["Nombre", "Debut", "Fin", "Logo"])
df_g = cargar_csv(G_FILE, ["Jornada", "Visitante", "CV", "HomeClub", "CH"])
df_c = cargar_csv(C_FILE, ["Jornada", "Fecha", "Hora", "Visitante", "HomeClub", "Campo"])

# --- 3. BARRA LATERAL ---
with st.sidebar:
    st.image(LOGO_LIGA, width=100)
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
    c1, c2 = st.columns([1, 4])
    with c1: st.image(LOGO_LIGA, width=120)
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
        for _, row_e in df_e[df_e["Fin"] == 0].iterrows():
            eq = row_e["Nombre"]
            logo = row_e["Logo"] if pd.notna(row_e["Logo"]) else None
            v, h = df_g[df_g["Visitante"] == eq], df_g[df_g["HomeClub"] == eq]
            g = len(v[v["CV"] > v["CH"]]) + len(h[h["CH"] > h["CV"]])
            p = len(v[v["CV"] < v["CH"]]) + len(h[h["CH"] < h["CV"]])
            stats.append({"Logo": logo, "Equipo": eq, "JJ": g+p, "G": g, "P": p, "AVG": round(g/(g+p), 3) if (g+p)>0 else 0})
        
        df_pos = pd.DataFrame(stats).sort_values(by=["AVG", "G"], ascending=False)
        for _, r in df_pos.iterrows():
            col_l, col_t = st.columns([1, 8])
            if r["Logo"] and os.path.exists(r["Logo"]): col_l.image(r["Logo"], width=40)
            col_t.write(f"**{r['Equipo']}** | G: {r['G']} | P: {r['P']} | AVG: {r['AVG']}")
            st.divider()

elif menu == "🏆 LÍDERES":
    st.header("🥇 Cuadro de Honor")
    cat_f = st.selectbox("Categoría:", ["TODOS", "Novato", "Softbolista", "Refuerzo"])
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
        st.write("### Mejores Lanzadores (G-P)")
        st.dataframe(df_p.sort_values(by=["G", "P"], ascending=[False, True]).head(10)[['Nombre', 'Equipo', 'G', 'P']], hide_index=True)

elif menu == "📋 ROSTERS":
    if not df_e.empty:
        eq_s = st.selectbox("Equipo:", df_e["Nombre"].unique())
        df_roster = df_j[df_j["Equipo"] == eq_s].copy()
        df_roster["AVG"] = (df_roster["H"] / df_roster["VB"]).fillna(0).apply(lambda x: f"{x:.3f}")
        st.dataframe(df_roster[["Nombre", "Categoria", "VB", "H", "2B", "3B", "HR", "AVG"]], use_container_width=True, hide_index=True)

elif menu == "📜 HISTORIAL":
    st.header("📜 Historial Individual")
    if not df_j.empty:
        j_sel = st.selectbox("Buscar Jugador:", sorted(df_j["Nombre"].unique()))
        d = df_j[df_j["Nombre"] == j_sel].iloc[0]
        st.info(f"**Bateo:** VB: {int(d['VB'])} | H: {int(d['H'])} | 2B: {int(d['2B'])} | 3B: {int(d['3B'])} | HR: {int(d['HR'])}")
        st.success(f"**Pitcheo:** Ganados: {int(d['G'])} | Perdidos: {int(d['P'])}")

elif menu == "🏘️ EQUIPOS":
    st.header("🏘️ Gestión de Equipos y Logos")
    if st.session_state.admin:
        with st.form("nuevo_eq"):
            n_e = st.text_input("Nombre del Equipo")
            logo_f = st.file_uploader("Subir Escudo", type=["png", "jpg"])
            if st.form_submit_button("💾 AÑADIR EQUIPO"):
                path_l = ""
                if logo_f:
                    path_l = os.path.join(LOGOS_DIR, f"{n_e}.png")
                    with open(path_l, "wb") as f: f.write(logo_f.getbuffer())
                pd.concat([df_e, pd.DataFrame([{"Nombre":n_e, "Debut":2026, "Fin":0, "Logo":path_l}])], ignore_index=True).to_csv(E_FILE, index=False)
                st.rerun()
    st.dataframe(df_e[["Nombre", "Debut"]], hide_index=True)

elif menu == "✍️ REGISTRAR":
    if not st.session_state.admin:
        with st.expander("🔐 Acceso Admin"):
            u = st.text_input("Usuario"); p = st.text_input("Clave", type="password")
            if st.button("Entrar"):
                if u == "admin" and p == "123": st.session_state.admin = True; st.rerun()
    else:
        tj, tr, tc = st.tabs(["JUGADORES", "RESULTADOS", "CALENDARIO"])
        with tj:
            with st.form("fj"):
                n = st.text_input("Nombre"); c = st.selectbox("Categoría", ["Novato", "Softbolista", "Refuerzo"]); eq = st.selectbox("Equipo", df_e["Nombre"].unique())
                v1, v2, v3, v4, v5 = st.columns(5)
                vb, h, d2, d3, hr = v1.number_input("VB", 0), v2.number_input("H", 0), v3.number_input("2B", 0), v4.number_input("3B", 0), v5.number_input("HR", 0)
                gp, pp = st.number_input("G (Pitcheo)", 0), st.number_input("P (Pitcheo)", 0)
                if st.form_submit_button("💾 GUARDAR JUGADOR"):
                    df_j = pd.concat([df_j[df_j["Nombre"] != n], pd.DataFrame([{"Nombre":n,"Equipo":eq,"Categoria":c,"VB":vb,"H":h,"2B":d2,"3B":d3,"HR":hr,"G":gp,"P":pp}])], ignore_index=True)
                    df_j.to_csv(J_FILE, index=False); gc.collect(); st.success("Guardado!"); st.rerun()
        with tr:
            with st.form("fr"):
                jor = st.number_input("Jornada", 1); v = st.selectbox("Visitante", df_e["Nombre"].unique()); cv = st.number_input("CV", 0)
                h_c = st.selectbox("Home Club", df_e["Nombre"].unique()); ch = st.number_input("CH", 0)
                if st.form_submit_button("💾 GUARDAR SCORE"):
                    pd.concat([df_g, pd.DataFrame([{"Jornada":jor, "Visitante":v, "CV":cv, "HomeClub":h_c, "CH":ch}])], ignore_index=True).to_csv(G_FILE, index=False); st.rerun()
        with tc:
            with st.form("fcal"):
                j_c, fec, hor = st.number_input("Jornada ", 1), st.text_input("Fecha"), st.text_input("Hora")
                vi, hc, ca = st.selectbox("Vis ", df_e["Nombre"].unique()), st.selectbox("HC ", df_e["Nombre"].unique()), st.text_input("Campo")
                if st.form_submit_button("📅 PROGRAMAR"):
                    pd.concat([df_c, pd.DataFrame([{"Jornada":j_c, "Fecha":fec, "Hora":hor, "Visitante":vi, "HomeClub":hc, "Campo":ca}])], ignore_index=True).to_csv(C_FILE, index=False); st.rerun()

elif menu == "💾 RESPALDO":
    if st.session_state.admin:
        st.download_button("📥 JUGADORES", df_j.to_csv(index=False), "jugadores.csv")
        st.download_button("📥 JUEGOS", df_g.to_csv(index=False), "juegos.csv")

elif menu == "🗑️ BORRAR":
    if st.session_state.admin:
        j_d = st.selectbox("Eliminar Jugador:", [""] + sorted(df_j["Nombre"].tolist()))
        if st.button("❌ ELIMINAR"):
            df_j[df_j["Nombre"] != j_d].to_csv(J_FILE, index=False); st.rerun()
