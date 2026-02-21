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
                    df[c] = ANIO_ACTUAL if c == "Debut" else (0 if c != "Categoria" else "Softbolista")
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
            u = st.text_input("Usuario", key="user_login")
            p = st.text_input("Clave", type="password", key="pass_login")
            if st.button("Entrar"):
                if u == "admin" and p == "123":
                    st.session_state.admin = True
                    st.rerun()
    else:
        st.success("Modo Admin: ACTIVADO")
        st.divider()
        st.subheader("📥 Cargar CSV")
        tipo_subida = st.selectbox("Destino:", ["Jugadores", "Equipos", "Calendario", "Resultados"])
        archivo_subido = st.file_uploader(f"Subir {tipo_subida}", type="csv")
        if archivo_subido and st.button("🚀 Guardar Archivo"):
            destinos = {"Jugadores": J_FILE, "Equipos": E_FILE, "Calendario": C_FILE, "Resultados": G_FILE}
            pd.read_csv(archivo_subido).to_csv(destinos[tipo_subida], index=False)
            st.success("Datos actualizados"); st.rerun()
        st.divider()
        if st.button("❌ Cerrar Sesión"):
            st.session_state.admin = False
            st.rerun()

    st.divider()
    menu = st.radio("Secciones:", ["🏠 INICIO", "📊 STANDING", "🏆 LÍDERES", "📋 ROSTERS", "📜 HISTORIAL", "🏘️ EQUIPOS", "✍️ REGISTRAR", "🗑️ BORRAR", "💾 RESPALDO"])

# Carga de datos
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
        else: st.info("No hay juegos programados.")
    with t_play:
        playoffs = df_c[df_c["Tipo"]!="Regular"] if not df_c.empty else pd.DataFrame()
        if not playoffs.empty: st.table(playoffs)
        else: st.warning("Playoffs no definidos.")

elif menu == "📊 STANDING":
    st.header("📊 Posiciones")
    if not df_g.empty and not df_e.empty:
        res = []
        for eq in df_e["Nombre"].unique():
            v, h = df_g[df_g["Visitante"]==eq], df_g[df_g["HomeClub"]==eq]
            g = len(v[v["CV"]>v["CH"]]) + len(h[h["CH"]>h["CV"]])
            p = len(v[v["CV"]<v["CH"]]) + len(h[h["CH"]<h["CV"]])
            res.append({"Equipo":eq, "JJ":g+p, "G":g, "P":p, "AVG":round(g/(g+p),3) if (g+p)>0 else 0})
        st.table(pd.DataFrame(res).sort_values(by=["AVG","G"], ascending=False))

elif menu == "🏆 LÍDERES":
    st.header("🥇 Líderes de Temporada")
    
    # Lógica de turnos mínimos (4 por jornada jugada)
    jornada_max = df_g["Jornada"].max() if not df_g.empty else 1
    min_vb_req = jornada_max * 4
    
    st.info(f"Requisito para liderar Average: Mínimo **{min_vb_req}** turnos al bate (4 por jornada).")
    
    cat = st.selectbox("Filtrar Categoría:", ["TODOS", "Novato", "Softbolista", "Refuerzo"])
    df_l = df_j.copy() if cat=="TODOS" else df_j[df_j["Categoria"]==cat].copy()
    df_l["AVG_N"] = (df_l["H"]/df_l["VB"]).fillna(0)
    df_l["AVG_STR"] = df_l["AVG_N"].apply(lambda x: f"{x:.3f}")

    tb, tp = st.tabs(["⚾ BATEO", "🎯 PITCHEO"])
    with tb:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.write("### Average")
            # FILTRO CRÍTICO: Solo los que cumplen los turnos mínimos
            lideres_avg = df_l[df_l["VB"] >= min_vb_req].nlargest(10, 'AVG_N')
            if not lideres_avg.empty:
                st.dataframe(lideres_avg[['Nombre', 'AVG_STR']], hide_index=True)
            else: st.warning("Nadie cumple el mínimo.")
        with c2:
            st.write("### Hits"); st.dataframe(df_l.nlargest(10,'H')[['Nombre','H']], hide_index=True)
        with c3:
            st.write("### Home Runs"); st.dataframe(df_l.nlargest(10,'HR')[['Nombre','HR']], hide_index=True)
        
        st.divider()
        c4, c5 = st.columns(2)
        with c4: st.write("### Dobles"); st.dataframe(df_l.nlargest(10,'2B')[['Nombre','2B']], hide_index=True)
        with c5: st.write("### Triples"); st.dataframe(df_l.nlargest(10,'3B')[['Nombre','3B']], hide_index=True)

    with tp:
        solo_p = df_l[(df_l["G"] > 0) | (df_l["P"] > 0)]
        if not solo_p.empty:
            st.dataframe(solo_p.sort_values(by=["G","P"], ascending=[False, True])[['Nombre','Equipo','G','P']], hide_index=True, use_container_width=True)
        else: st.info("Sin registros de picheo.")

elif menu == "📋 ROSTERS":
    if not df_e.empty:
        eq_sel = st.selectbox("Equipo:", df_e["Nombre"].unique())
        df_r = df_j[df_j["Equipo"]==eq_sel].copy()
        df_r["AVG"] = (df_r["H"]/df_r["VB"]).fillna(0).apply(lambda x: f"{x:.3f}")
        st.dataframe(df_r, use_container_width=True, hide_index=True)

elif menu == "📜 HISTORIAL":
    st.header("📜 Ficha Técnica")
    if not df_j.empty:
        js = st.selectbox("Buscar Jugador:", sorted(df_j["Nombre"].unique()))
        d = df_j[df_j["Nombre"]==js].iloc[0]
        c1, c2, c3 = st.columns(3)
        c1.metric("Equipo", d['Equipo']); c2.metric("Cat", d['Categoria'])
        c3.metric("AVG", f"{(d['H']/d['VB'] if d['VB']>0 else 0):.3f}")
        st.write(f"**Bateo:** VB: {int(d['VB'])} | H: {int(d['H'])} | HR: {int(d['HR'])}")
        st.write(f"**Picheo:** G: {int(d['G'])} | P: {int(d['P'])}")

elif menu == "🏘️ EQUIPOS":
    st.header("🏘️ Gestión de Equipos")
    if st.session_state.admin:
        with st.form("n_e"):
            n, a = st.text_input("Nombre"), st.number_input("Debut", 1980, ANIO_ACTUAL, ANIO_ACTUAL)
            if st.form_submit_button("Registrar"):
                pd.concat([df_e, pd.DataFrame([{"Nombre":n, "Debut":a}])], ignore_index=True).to_csv(E_FILE, index=False); st.rerun()
    if not df_e.empty:
        df_ant = df_e.copy()
        df_ant["Antigüedad"] = ANIO_ACTUAL - df_ant["Debut"]
        st.dataframe(df_ant[["Nombre", "Debut", "Antigüedad"]], hide_index=True, use_container_width=True)

elif menu == "✍️ REGISTRAR":
    if st.session_state.admin:
        tj, tr, tc = st.tabs(["JUGADORES", "RESULTADOS", "CALENDARIO"])
        with tj:
            if not df_e.empty:
                with st.form("rj"):
                    n, c = st.text_input("Nombre"), st.selectbox("Cat", ["Novato", "Softbolista", "Refuerzo"])
                    e = st.selectbox("Equipo", df_e["Nombre"].unique())
                    v1, v2, v3, v4, v5 = st.columns(5)
                    vb, h, d2, d3, hr = v1.number_input("VB",0), v2.number_input("H",0), v3.number_input("2B",0), v4.number_input("3B",0), v5.number_input("HR",0)
                    g, p = st.number_input("G",0), st.number_input("P",0)
                    if st.form_submit_button("Guardar"):
                        df_j = pd.concat([df_j[df_j["Nombre"]!=n], pd.DataFrame([{"Nombre":n,"Equipo":e,"Categoria":c,"VB":vb,"H":h,"2B":d2,"3B":d3,"HR":hr,"G":g,"P":p}])], ignore_index=True)
                        df_j.to_csv(J_FILE, index=False); st.rerun()
        with tr:
            if not df_e.empty:
                with st.form("rs"):
                    j, v, cv = st.number_input("Jornada",1), st.selectbox("Vis", df_e["Nombre"].unique()), st.number_input("CV",0)
                    hc_n, ch = st.selectbox("HC", df_e["Nombre"].unique()), st.number_input("CH",0)
                    if st.form_submit_button("Guardar Score"):
                        pd.concat([df_g, pd.DataFrame([{"Jornada":j,"Visitante":v,"CV":cv,"HomeClub":hc_n,"CH":ch}])], ignore_index=True).to_csv(G_FILE, index=False); st.rerun()
        with tc:
            if not df_e.empty:
                with st.form("rc"):
                    t, f, ho, ca = st.selectbox("Tipo", ["Regular", "Final"]), st.text_input("Fecha"), st.text_input("Hora"), st.text_input("Campo")
                    vi, hc_c = st.selectbox("Vis ", df_e["Nombre"].unique()), st.selectbox("HC ", df_e["Nombre"].unique())
                    if st.form_submit_button("Agendar"):
                        pd.concat([df_c, pd.DataFrame([{"Tipo":t,"Fecha":f,"Hora":ho,"Visitante":vi,"HomeClub":hc_c,"Campo":ca}])], ignore_index=True).to_csv(C_FILE, index=False); st.rerun()

elif menu == "🗑️ BORRAR":
    if st.session_state.admin:
        st.header("🗑️ Borrar Registro")
        if not df_j.empty:
            sel = st.selectbox("Elegir Jugador:", sorted(df_j["Nombre"].unique()))
            if st.button("❌ Eliminar", type="primary"):
                df_j[df_j["Nombre"]!=sel].to_csv(J_FILE, index=False); st.rerun()

elif menu == "💾 RESPALDO":
    if st.session_state.admin:
        st.download_button("Descargar Jugadores CSV", df_j.to_csv(index=False), "jugadores.csv")
        st.download_button("Descargar Resultados CSV", df_g.to_csv(index=False), "resultados.csv")
