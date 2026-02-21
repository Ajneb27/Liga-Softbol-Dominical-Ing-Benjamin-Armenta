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
df_c = cargar_csv(C_FILE, ["Tipo", "Jornada", "Fecha", "Hora", "Visitante", "HomeClub", "Campo"])

# --- 3. BARRA LATERAL (CONTROL DE ACCESO) ---
with st.sidebar:
    st.image(LOGO_LIGA, width=100)
    st.title(f"🏆 {NOMBRE_LIGA}")
    
    if 'admin' not in st.session_state: st.session_state.admin = False

    if not st.session_state.admin:
        with st.expander("🔐 Acceso Administrador"):
            u = st.text_input("Usuario", key="user_login")
            p = st.text_input("Clave", type="password", key="pass_login")
            if st.button("Entrar"):
                if u == "admin" and p == "123":
                    st.session_state.admin = True
                    st.success("¡Bienvenido!")
                    st.rerun()
    else:
        st.success("Modo Admin: ACTIVADO")
        if st.button("❌ Cerrar Sesión"):
            st.session_state.admin = False
            st.rerun()

    st.divider()
    menu = st.radio("Secciones:", ["🏠 INICIO", "📊 STANDING", "🏆 LÍDERES", "📋 ROSTERS", "📜 HISTORIAL", "🏘️ EQUIPOS", "✍️ REGISTRAR", "🗑️ BORRAR", "💾 RESPALDO"])

# --- 4. SECCIONES ---

if menu == "🏠 INICIO":
    st.markdown(f"<h1 style='color:#d4af37;'>{NOMBRE_LIGA}</h1>", unsafe_allow_html=True)
    tab_reg, tab_play = st.tabs(["📅 TEMPORADA REGULAR", "🔥 PLAYOFFS"])
    with tab_reg:
        regular = df_c[df_c["Tipo"] == "Regular"] if "Tipo" in df_c.columns else df_c
        if not regular.empty: st.dataframe(regular, hide_index=True, use_container_width=True)
        else: st.info("No hay juegos programados.")
    with tab_play:
        if "Tipo" in df_c.columns and not df_c[df_c["Tipo"] != "Regular"].empty:
            playoffs = df_c[df_c["Tipo"] != "Regular"]
            c_s, c_f = st.columns(2)
            c_s.subheader("Semifinales"); c_s.dataframe(playoffs[playoffs["Tipo"] == "Semifinal"], hide_index=True)
            c_f.subheader("Gran Final"); c_f.dataframe(playoffs[playoffs["Tipo"] == "Final"], hide_index=True)
        else: st.warning("Aún no se han programado Playoffs.")

elif menu == "📊 STANDING":
    st.header("📊 Tabla de Posiciones")
    if not df_g.empty and not df_e.empty:
        stats = []
        for eq in df_e["Nombre"].unique():
            v, h = df_g[df_g["Visitante"] == eq], df_g[df_g["HomeClub"] == eq]
            g = len(v[v["CV"] > v["CH"]]) + len(h[h["CH"] > h["CV"]])
            p = len(v[v["CV"] < v["CH"]]) + len(h[h["CH"] < h["CV"]])
            stats.append({"Equipo": eq, "JJ": g+p, "G": g, "P": p, "AVG": round(g/(g+p), 3) if (g+p)>0 else 0})
        st.table(pd.DataFrame(stats).sort_values(by=["AVG", "G"], ascending=False))

elif menu == "🏆 LÍDERES":
    st.header("🥇 Líderes")
    cat_f = st.selectbox("Categoría:", ["TODOS", "Novato", "Softbolista", "Refuerzo"])
    df_l = df_j if cat_f == "TODOS" else df_j[df_j["Categoria"] == cat_f]
    t1, t2 = st.tabs(["⚾ BATEO", "🎯 PITCHEO"])
    with t1:
        c1, c2 = st.columns(2)
        c1.write("### Hits"); c1.dataframe(df_l.nlargest(10, 'H')[['Nombre', 'Equipo', 'H']], hide_index=True)
        c2.write("### HR"); c2.dataframe(df_l.nlargest(10, 'HR')[['Nombre', 'Equipo', 'HR']], hide_index=True)
    with t2:
        df_p = df_l[(df_l["G"] > 0) | (df_l["P"] > 0)]
        st.dataframe(df_p.sort_values(by="G", ascending=False)[['Nombre', 'Equipo', 'G', 'P']], hide_index=True)

elif menu == "📋 ROSTERS":
    if not df_e.empty:
        eq_s = st.selectbox("Equipo:", df_e["Nombre"].unique())
        df_roster = df_j[df_j["Equipo"] == eq_s].copy()
        df_roster["AVG"] = (df_roster["H"] / df_roster["VB"]).fillna(0).apply(lambda x: f"{x:.3f}")
        st.dataframe(df_roster, use_container_width=True, hide_index=True)

elif menu == "📜 HISTORIAL":
    j_sel = st.selectbox("Buscar Jugador:", sorted(df_j["Nombre"].unique()) if not df_j.empty else [])
    if j_sel:
        d = df_j[df_j["Nombre"] == j_sel].iloc[0]
        st.write(f"### {d['Nombre']} ({d['Categoria']})")
        st.write(f"**Bateo:** H: {int(d['H'])} | HR: {int(d['HR'])} | VB: {int(d['VB'])}")
        st.write(f"**Pitcheo:** G: {int(d['G'])} | P: {int(d['P'])}")

elif menu == "🏘️ EQUIPOS":
    st.header("🏘️ Gestión de Equipos")
    if st.session_state.admin:
        with st.form("nuevo_e"):
            n_e = st.text_input("Nombre del Equipo")
            if st.form_submit_button("Registrar"):
                pd.concat([df_e, pd.DataFrame([{"Nombre":n_e, "Debut":ANIO_ACTUAL}])], ignore_index=True).to_csv(E_FILE, index=False); st.rerun()
    st.dataframe(df_e, hide_index=True)

elif menu == "✍️ REGISTRAR":
    if st.session_state.admin:
        tj, tr, tc = st.tabs(["JUGADORES", "RESULTADOS", "CALENDARIO"])
        with tj:
            with st.form("reg_j"):
                nom = st.text_input("Nombre"); cat = st.selectbox("Cat", ["Novato", "Softbolista", "Refuerzo"])
                eq = st.selectbox("Equipo", df_e["Nombre"].unique())
                v1, v2, v3, v4, v5 = st.columns(5)
                vb, h, d2, d3, hr = v1.number_input("VB",0), v2.number_input("H",0), v3.number_input("2B",0), v4.number_input("3B",0), v5.number_input("HR",0)
                gp, pp = st.number_input("G",0), st.number_input("P",0)
                if st.form_submit_button("Guardar"):
                    df_j = pd.concat([df_j[df_j["Nombre"] != nom], pd.DataFrame([{"Nombre":nom,"Equipo":eq,"Categoria":cat,"VB":vb,"H":h,"2B":d2,"3B":d3,"HR":hr,"G":gp,"P":pp}])], ignore_index=True)
                    df_j.to_csv(J_FILE, index=False); gc.collect(); st.rerun()
        with tr:
            with st.form("reg_s"):
                jor = st.number_input("Jornada", 1); v = st.selectbox("Vis", df_e["Nombre"].unique()); cv = st.number_input("CV", 0)
                h_c = st.selectbox("HC", df_e["Nombre"].unique()); ch = st.number_input("CH", 0)
                if st.form_submit_button("Guardar Score"):
                    pd.concat([df_g, pd.DataFrame([{"Jornada":jor, "Visitante":v, "CV":cv, "HomeClub":h_c, "CH":ch}])], ignore_index=True).to_csv(G_FILE, index=False); st.rerun()
        with tc:
            with st.form("reg_cal"):
                tipo = st.selectbox("Tipo de Juego", ["Regular", "Semifinal", "Final"])
                j_c = st.number_input("Jornada/Juego #", 1); f = st.text_input("Fecha (DD/MM)"); h_t = st.text_input("Hora")
                vi = st.selectbox("Visitante", df_e["Nombre"].unique()); hc = st.selectbox("Home Club", df_e["Nombre"].unique()); ca = st.text_input("Campo")
                if st.form_submit_button("Programar"):
                    pd.concat([df_c, pd.DataFrame([{"Tipo":tipo, "Jornada":j_c, "Fecha":f, "Hora":h_t, "Visitante":vi, "HomeClub":hc, "Campo":ca}])], ignore_index=True).to_csv(C_FILE, index=False); st.rerun()
    else: st.warning("Acceso solo para administradores.")

elif menu == "💾 RESPALDO":
    if st.session_state.admin:
        st.download_button("Descargar Jugadores", df_j.to_csv(index=False), "jugadores.csv")
        st.download_button("Descargar Calendario", df_c.to_csv(index=False), "calendario.csv")
    else: st.error("Sección restringida.")

elif menu == "🗑️ BORRAR":
    if st.session_state.admin:
        st.subheader("⚠️ Zona de Peligro")
        if st.button("🗑️ Borrar Calendario Completo"):
            pd.DataFrame(columns=["Tipo", "Jornada", "Fecha", "Hora", "Visitante", "HomeClub", "Campo"]).to_csv(C_FILE, index=False)
            st.success("Calendario borrado con éxito.")
            st.rerun()
        
        if st.button("🗑️ Borrar Todos los Jugadores"):
            pd.DataFrame(columns=["Nombre", "Equipo", "Categoria", "VB", "H", "2B", "3B", "HR", "G", "P"]).to_csv(J_FILE, index=False)
            st.success("Base de datos de jugadores reiniciada.")
            st.rerun()
    else:
        st.error("Acceso restringido.")
