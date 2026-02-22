import streamlit as st
import pandas as pd
import os
import gc

# --- 1. CONFIGURACIÓN E IDENTIDAD ---
NOMBRE_LIGA = "LIGA DE SOFTBOL DOMINICAL"
ANIO_ACTUAL = 2026
LOGO_LIGA = "https://cdn-icons-png.flaticon.com" 

DATA_DIR = "liga_softbol_final_2026"
if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)

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
                if c not in df.columns: 
                    if c == "Debut": df[c] = ANIO_ACTUAL
                    elif c == "Categoria": df[c] = "Softbolista"
                    else: df[c] = 0
            return df
        except: return pd.DataFrame(columns=columnas)
    return pd.DataFrame(columns=columnas)

# --- 3. BARRA LATERAL (ADMIN Y CARGA) ---
with st.sidebar:
    st.image(LOGO_LIGA, width=100)
    st.title(f"🏆 {NOMBRE_LIGA}")
    
    if 'admin' not in st.session_state: st.session_state.admin = False

    if not st.session_state.admin:
        with st.expander("🔐 Acceso Administrador"):
            u = st.text_input("Usuario", key="u_log")
            p = st.text_input("Clave", type="password", key="p_log")
            if st.button("Entrar"):
                if u == "admin" and p == "123":
                    st.session_state.admin = True
                    st.rerun()
    else:
        st.success("Modo Admin: ACTIVADO")
        st.divider()
        st.subheader("📥 Cargar Base de Datos")
        t_sub = st.selectbox("Archivo:", ["Jugadores", "Equipos", "Calendario", "Resultados"])
        arc_sub = st.file_uploader(f"Subir CSV de {t_sub}", type="csv")
        if arc_sub and st.button("🚀 Guardar en Sistema"):
            dest = {"Jugadores": J_FILE, "Equipos": E_FILE, "Calendario": C_FILE, "Resultados": G_FILE}
            pd.read_csv(arc_sub).to_csv(dest[t_sub], index=False)
            st.success("¡Datos actualizados!"); st.rerun()
        st.divider()
        if st.button("❌ Cerrar Sesión"):
            st.session_state.admin = False
            st.rerun()

    st.divider()
    menu = st.radio("Secciones:", ["🏠 INICIO", "📊 STANDING", "🏆 LÍDERES", "📋 ROSTERS", "📜 HISTORIAL", "🏘️ EQUIPOS", "✍️ REGISTRAR", "🗑️ BORRAR", "💾 RESPALDO"])

# Carga de datos global
df_j = cargar_csv(J_FILE, ["Nombre", "Equipo", "Categoria", "VB", "H", "2B", "3B", "HR", "G", "P"])
df_e = cargar_csv(E_FILE, ["Nombre", "Debut", "Fin", "Logo"])
df_g = cargar_csv(G_FILE, ["Jornada", "Visitante", "CV", "HomeClub", "CH"])
df_c = cargar_csv(C_FILE, ["Tipo", "Jornada", "Fecha", "Hora", "Visitante", "HomeClub", "Campo"])

# --- 4. SECCIONES ---

if menu == "🏠 INICIO":
    st.markdown(f"<h1 style='color:#d4af37;'>{NOMBRE_LIGA}</h1>", unsafe_allow_html=True)
    t_reg, t_play = st.tabs(["📅 REGULAR", "🔥 PLAYOFFS"])
    with t_reg:
        if not df_c.empty:
            st.dataframe(df_c[df_c["Tipo"]=="Regular"], use_container_width=True, hide_index=True)
        else: st.info("No hay calendario registrado.")
    with t_play:
        playoffs = df_c[df_c["Tipo"]!="Regular"] if not df_c.empty else pd.DataFrame()
        if not playoffs.empty: st.table(playoffs)
        else: st.warning("Playoffs no definidos.")

elif menu == "📊 STANDING":
    st.header("📊 Tabla de Posiciones")
    if not df_g.empty and not df_e.empty:
        res = []
        for eq in df_e["Nombre"].unique():
            v, h = df_g[df_g["Visitante"]==eq], df_g[df_g["HomeClub"]==eq]
            g = len(v[v["CV"]>v["CH"]]) + len(h[h["CH"]>h["CV"]])
            p = len(v[v["CV"]<v["CH"]]) + len(h[h["CH"]<h["CV"]])
            res.append({"Equipo":eq, "JJ":g+p, "G":g, "P":p, "AVG":round(g/(g+p),3) if (g+p)>0 else 0})
        st.table(pd.DataFrame(res).sort_values(by=["AVG","G"], ascending=False))

elif menu == "🏆 LÍDERES":
    st.header("🥇 Líderes de la Temporada")
    
    jor_max = df_g["Jornada"].max() if not df_g.empty else 1
    if st.session_state.admin:
        with st.expander("⚙️ CRITERIOS DE CLASIFICACIÓN (Solo Admin)"):
            c_a1, c_a2 = st.columns(2)
            min_vb = c_a1.slider("Mínimo de Turnos (VB):", 0, 100, int(jor_max * 3.1))
            min_dec = c_a2.slider("Mínimo Juegos Decididos (G+P):", 0, 20, 1)
    else:
        min_vb, min_dec = int(jor_max * 3), 1
        st.info(f"Requisitos: AVG (Min {min_vb} VB) | Pitcheo (Min {min_dec} G+P)")

    cat = st.selectbox("Categoría:", ["TODOS", "Novato", "Softbolista", "Refuerzo"])
    df_l = df_j.copy() if cat=="TODOS" else df_j[df_j["Categoria"]==cat].copy()
    
    df_l["AVG_N"] = (df_l["H"] / df_l["VB"]).fillna(0)
    df_l["AVG_S"] = df_l["AVG_N"].apply(lambda x: f"{x:.3f}")

    tb, tp = st.tabs(["⚾ BATEO", "🎯 PITCHEO"])
    with tb:
        # FILA 1: AVG, Hits y HR
        c1, c2, c3 = st.columns(3)
        with c1:
            st.write("### Average (H/VB)")
            st.dataframe(df_l[df_l["VB"] >= min_vb].nlargest(10, 'AVG_N')[['Nombre', 'AVG_S']], hide_index=True)
        with c2:
            st.write("### Hits"); st.dataframe(df_l.nlargest(10,'H')[['Nombre','H']], hide_index=True)
        with c3:
            st.write("### HR"); st.dataframe(df_l.nlargest(10,'HR')[['Nombre','HR']], hide_index=True)
        
        st.divider()
        
        # FILA 2: Dobles y Triples (RESTAURADOS)
        c4, c5 = st.columns(2)
        with c4:
            st.write("### Dobles (2B)"); st.dataframe(df_l.nlargest(10,'2B')[['Nombre','2B']], hide_index=True)
        with c5:
            st.write("### Triples (3B)"); st.dataframe(df_l.nlargest(10,'3B')[['Nombre','3B']], hide_index=True)
            
    with tp:
        st.write(f"### Pitchers Decididos (Min {min_dec} G+P)")
        solo_p = df_l[(df_l["G"] + df_l["P"]) >= min_dec]
        st.dataframe(solo_p.sort_values(by=["G","P"], ascending=[False, True])[['Nombre','G','P']], hide_index=True)

elif menu == "📋 ROSTERS":
    if not df_e.empty:
        eq = st.selectbox("Equipo:", df_e["Nombre"].unique())
        df_r = df_j[df_j["Equipo"]==eq].copy()
        df_r["AVG"] = (df_r["H"]/df_r["VB"]).fillna(0).apply(lambda x: f"{x:.3f}")
        st.dataframe(df_r, use_container_width=True, hide_index=True)

elif menu == "📜 HISTORIAL":
    st.header("📜 Ficha Técnica")
    if not df_j.empty:
        js = st.selectbox("Buscar Jugador:", sorted(df_j["Nombre"].unique()))
        d = df_j[df_j["Nombre"]==js].iloc
        c1, c2, c3 = st.columns(3)
        calc_avg = d['H']/d['VB'] if d['VB']>0 else 0
        c1.metric("Equipo", d['Equipo']); c2.metric("Cat", d['Categoria']); c3.metric("AVG", f"{calc_avg:.3f}")
        st.write(f"**Bateo:** VB: {int(d['VB'])} | H: {int(d['H'])} | HR: {int(d['HR'])} | 2B: {int(d['2B'])} | 3B: {int(d['3B'])}")
        st.write(f"**Picheo:** G: {int(d['G'])} | P: {int(d['P'])}")

elif menu == "🏘️ EQUIPOS":
    st.header("🏘️ Equipos y Antigüedad")
    if st.session_state.admin:
        with st.form("ne"):
            n, a = st.text_input("Nombre"), st.number_input("Debut", 1980, ANIO_ACTUAL, ANIO_ACTUAL)
            if st.form_submit_button("Ok"):
                pd.concat([df_e, pd.DataFrame([{"Nombre":n, "Debut":a}])], ignore_index=True).to_csv(E_FILE, index=False); st.rerun()
    if not df_e.empty:
        df_ant = df_e.copy()
        df_ant["Años en Liga"] = ANIO_ACTUAL - df_ant["Debut"]
        st.dataframe(df_ant[["Nombre", "Debut", "Años en Liga"]], hide_index=True, use_container_width=True)

elif menu == "✍️ REGISTRAR":
    if st.session_state.admin:
        tj, tr = st.tabs(["JUGADORES", "RESULTADOS"])
        with tj:
            with st.form("rj"):
                n, c = st.text_input("Nombre"), st.selectbox("Cat", ["Novato", "Softbolista", "Refuerzo"])
                e = st.selectbox("Equipo", df_e["Nombre"].unique()) if not df_e.empty else "N/A"
                v1, v2, v3, v4, v5 = st.columns(5)
                vb, h, d2, d3, hr = v1.number_input("VB",0), v2.number_input("H",0), v3.number_input("2B",0), v4.number_input("3B",0), v5.number_input("HR",0)
                g, p = st.number_input("G",0), st.number_input("P",0)
                if st.form_submit_button("Guardar"):
                    df_j = pd.concat([df_j[df_j["Nombre"]!=n], pd.DataFrame([{"Nombre":n,"Equipo":e,"Categoria":c,"VB":vb,"H":h,"2B":d2,"3B":d3,"HR":hr,"G":g,"P":p}])], ignore_index=True)
                    df_j.to_csv(J_FILE, index=False); st.rerun()
        with tr:
            with st.form("rs"):
                j, v, cv = st.number_input("Jornada",1), st.selectbox("Vis", df_e["Nombre"].unique()), st.number_input("CV",0)
                hc, ch = st.selectbox("HC", df_e["Nombre"].unique()), st.number_input("CH",0)
                if st.form_submit_button("Guardar Score"):
                    pd.concat([df_g, pd.DataFrame([{"Jornada":j,"Visitante":v,"CV":cv,"HomeClub":hc,"CH":ch}])], ignore_index=True).to_csv(G_FILE, index=False); st.rerun()

elif menu == "🗑️ BORRAR":
    if st.session_state.admin:
        st.header("🗑️ Borrar Jugador")
        if not df_j.empty:
            sel = st.selectbox("Seleccione:", sorted(df_j["Nombre"].unique()))
            if st.button("❌ Eliminar Permanentemente", type="primary"):
                df_j[df_j["Nombre"]!=sel].to_csv(J_FILE, index=False); st.rerun()

elif menu == "💾 RESPALDO":
    if st.session_state.admin:
        st.download_button("Descargar Jugadores CSV", df_j.to_csv(index=False), "jugadores.csv")
