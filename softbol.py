import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN E IDENTIDAD 2026 ---
NOMBRE_LIGA = "LIGA DE SOFTBOL DOMINICAL"
ANIO_ACTUAL = 2026
LOGO_DEFECTO = "https://cdn-icons-png.flaticon.com" 

DATA_DIR = "liga_softbol_final_2026"
if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)

J_FILE = os.path.join(DATA_DIR, "jugadores_master.csv")
E_FILE = os.path.join(DATA_DIR, "equipos_master.csv")
G_FILE = os.path.join(DATA_DIR, "juegos_2026.csv")

# --- 2. MOTOR DE DATOS ---
st.set_page_config(page_title=NOMBRE_LIGA, layout="wide", page_icon="🥎")

def cargar_csv(archivo, columnas):
    if os.path.exists(archivo):
        try:
            df = pd.read_csv(archivo)
            for c in columnas:
                if c not in df.columns: 
                    df[c] = LOGO_DEFECTO if c == "Logo" else (ANIO_ACTUAL if c == "Debut" else 0)
            return df
        except: return pd.DataFrame(columns=columnas)
    return pd.DataFrame(columns=columnas)

# Carga de datos inicial
df_j = cargar_csv(J_FILE, ["Nombre", "Equipo", "Categoria", "VB", "H", "2B", "3B", "HR", "BB", "G", "P"])
df_e = cargar_csv(E_FILE, ["Nombre", "Debut", "Logo"])
df_g = cargar_csv(G_FILE, ["Jornada", "Visitante", "CV", "HomeClub", "CH"])

# --- 3. BARRA LATERAL ---
with st.sidebar:
    st.image(LOGO_DEFECTO, width=100)
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
        t_sub = st.selectbox("Archivo:", ["Jugadores", "Equipos", "Resultados"])
        arc_sub = st.file_uploader(f"Subir CSV", type="csv")
        if arc_sub and st.button("🚀 Guardar"):
            dest = {"Jugadores": J_FILE, "Equipos": E_FILE, "Resultados": G_FILE}
            pd.read_csv(arc_sub).to_csv(dest[t_sub], index=False)
            st.success("Actualizado"); st.rerun()
        if st.button("❌ Cerrar Sesión"):
            st.session_state.admin = False
            st.rerun()

    st.divider()
    menu = st.radio("Secciones:", ["🏠 INICIO", "📊 STANDING", "🏆 LÍDERES", "📋 ROSTERS", "📜 HISTORIAL", "🏘️ EQUIPOS", "✍️ REGISTRAR", "🗑️ BORRAR", "💾 RESPALDO"])

# --- 4. SECCIONES ---

if menu == "🏠 INICIO":
    st.header(f"🏠 {NOMBRE_LIGA} - Temporada {ANIO_ACTUAL}")
    st.write("Seleccione una opción en el menú lateral para comenzar.")

elif menu == "📊 STANDING":
    st.header("📊 Tabla de Posiciones (Standing)")
    if not df_e.empty and not df_g.empty:
        res = []
        for eq in df_e["Nombre"].unique():
            v, h = df_g[df_g["Visitante"]==eq], df_g[df_g["HomeClub"]==eq]
            g, p = len(v[v["CV"]>v["CH"]]) + len(h[h["CH"]>h["CV"]]), len(v[v["CV"]<v["CH"]]) + len(h[h["CH"]<h["CV"]])
            cf, cc = v["CV"].sum() + h["CH"].sum(), v["CH"].sum() + h["CV"].sum()
            res.append({"Equipo": eq, "G": g, "P": p, "AVG": round(g/(g+p),3) if (g+p)>0 else 0, "CF": cf, "CC": cc, "DIF": cf-cc})
        st.table(pd.DataFrame(res).sort_values(by=["AVG", "DIF"], ascending=False))

elif menu == "🏆 LÍDERES":
    st.header("🥇 Líderes de la Liga")
    jor_max = df_g["Jornada"].max() if not df_g.empty else 1
    min_vb = st.sidebar.slider("Min VB (Líderes):", 0, 100, int(jor_max * 3)) if st.session_state.admin else int(jor_max * 3)

    df_l = df_j.copy()
    df_l["HT"] = df_l["H"] + df_l["2B"] + df_l["3B"] + df_l["HR"]
    df_l["AVG_N"] = (df_l["HT"] / df_l["VB"]).fillna(0)
    
    t_bat, t_pit = st.tabs(["⚾ BATEO", "🎯 PITCHEO"])
    with t_bat:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.write("### AVG"); l_avg = df_l[df_l["VB"] >= min_vb].nlargest(10, 'AVG_N').copy()
            l_avg["AVG"] = l_avg["AVG_N"].apply(lambda x: f"{x:.3f}"); st.dataframe(l_avg[['Nombre', 'AVG']], hide_index=True)
        with c2: st.write("### HT"); st.dataframe(df_l.nlargest(10,'HT')[['Nombre','HT']], hide_index=True)
        with c3: st.write("### HR"); st.dataframe(df_l.nlargest(10,'HR')[['Nombre','HR']], hide_index=True)
    with t_pit:
        st.write("### Pitchers (Ganados)"); solo_p = df_l[(df_l["G"] > 0) | (df_l["P"] > 0)]
        st.dataframe(solo_p.sort_values(by=["G","P"], ascending=[False, True])[['Nombre','Equipo','G','P']], hide_index=True)

elif menu == "📋 ROSTERS":
    st.header("📋 Rosters Detallados")
    if not df_e.empty:
        col1, col2 = st.columns([3,1])
        eq_sel = col1.selectbox("Equipo:", df_e["Nombre"].unique())
        logo_url = df_e[df_e["Nombre"] == eq_sel]["Logo"].iloc[0]
        col2.image(logo_url, width=80)
        
        df_r = df_j[df_j["Equipo"] == eq_sel].copy()
        df_r["HT"] = df_r["H"] + df_r["2B"] + df_r["3B"] + df_r["HR"]
        df_r["AVG"] = (df_r["HT"] / df_r["VB"]).fillna(0).apply(lambda x: f"{x:.3f}")
        st.dataframe(df_r[["Nombre", "VB", "H", "2B", "3B", "HR", "BB", "HT", "AVG"]], hide_index=True, use_container_width=True)

elif menu == "📜 HISTORIAL":
    st.header("📜 Ficha de Jugador")
    if not df_j.empty:
        js = st.selectbox("Buscar:", sorted(df_j["Nombre"].unique()))
        d = df_j[df_j["Nombre"]==js].iloc[0]
        c1, c2, c3 = st.columns(3)
        c1.metric("Equipo", d['Equipo']); c2.metric("VB", int(d['VB'])); c3.metric("AVG", f"{((d['H']+d['2B']+d['3B']+d['HR'])/d['VB'] if d['VB']>0 else 0):.3f}")
        st.write(f"**Bateo:** H: {int(d['H'])} | 2B: {int(d['2B'])} | 3B: {int(d['3B'])} | HR: {int(d['HR'])} | BB: {int(d['BB'])}")
        st.write(f"**Picheo:** G: {int(d['G'])} | P: {int(d['P'])}")

elif menu == "🏘️ EQUIPOS":
    st.header("🏘️ Gestión de Equipos")
    if st.session_state.admin:
        t_l, t_n, t_e = st.tabs(["LISTA", "NUEVO", "EDITAR"])
        with t_l: 
            df_ee = df_e.copy(); df_ee["Antigüedad"] = ANIO_ACTUAL - df_ee["Debut"]
            st.dataframe(df_ee[["Nombre", "Debut", "Antigüedad", "Logo"]], hide_index=True)
        with t_n:
            with st.form("n_e"):
                n, d, l = st.text_input("Nombre"), st.number_input("Debut", 1980, 2026, 2026), st.text_input("Logo URL", LOGO_DEFECTO)
                if st.form_submit_button("Guardar"):
                    pd.concat([df_e, pd.DataFrame([{"Nombre":n,"Debut":d,"Logo":l}])], ignore_index=True).to_csv(E_FILE, index=False); st.rerun()
        with t_e:
            if not df_e.empty:
                sel = st.selectbox("Editar:", df_e["Nombre"].unique())
                idx = df_e[df_e["Nombre"] == sel].index[0]
                with st.form("e_e"):
                    en, ed, el = st.text_input("Nombre", df_e.at[idx, "Nombre"]), st.number_input("Debut", 1980, 2026, int(df_e.at[idx, "Debut"])), st.text_input("Logo URL", df_e.at[idx, "Logo"])
                    if st.form_submit_button("Actualizar"):
                        df_e.at[idx, "Nombre"], df_e.at[idx, "Debut"], df_e.at[idx, "Logo"] = en, ed, el
                        df_e.to_csv(E_FILE, index=False); st.rerun()

elif menu == "✍️ REGISTRAR":
    if st.session_state.admin:
        tj, tr = st.tabs(["👤 JUGADORES", "⚾ RESULTADOS"])
        with tj:
            with st.form("rj"):
                n, e = st.text_input("Nombre"), st.selectbox("Equipo", df_e["Nombre"].unique()) if not df_e.empty else st.info("Cree un equipo primero")
                v1, v2, v3 = st.columns(3)
                vb, h, bb = v1.number_input("AB (Turnos)", 0), v2.number_input("H (Sencillos)", 0), v3.number_input("BB", 0)
                d2, d3, hr = v1.number_input("2B", 0), v2.number_input("3B", 0), v3.number_input("HR", 0)
                g, p = v1.number_input("G (Picheo)",0), v2.number_input("P (Picheo)",0)
                if st.form_submit_button("Guardar Jugador"):
                    df_j = pd.concat([df_j[df_j["Nombre"]!=n], pd.DataFrame([{"Nombre":n,"Equipo":e,"VB":vb,"H":h,"2B":d2,"3B":d3,"HR":hr,"BB":bb,"G":g,"P":p}])], ignore_index=True)
                    df_j.to_csv(J_FILE, index=False); st.success("Jugador Guardado"); st.rerun()
        with tr:
            with st.form("rs"):
                j = st.number_input("Jornada",1)
                v = st.selectbox("Visitante", df_e["Nombre"].unique()) if not df_e.empty else ""
                cv = st.number_input("Carreras Visitante",0)
                hc = st.selectbox("Home Club", df_e["Nombre"].unique()) if not df_e.empty else ""
                ch = st.number_input("Carreras Home Club",0)
                if st.form_submit_button("Guardar Score"):
                    pd.concat([df_g, pd.DataFrame([{"Jornada":j,"Visitante":v,"CV":cv,"HomeClub":hc,"CH":ch}])], ignore_index=True).to_csv(G_FILE, index=False); st.success("Score Guardado"); st.rerun()

elif menu == "🗑️ BORRAR":
    if st.session_state.admin:
        st.header("🗑️ Borrar Jugador")
        if not df_j.empty:
            sel = st.selectbox("Seleccionar Jugador para eliminar:", sorted(df_j["Nombre"].unique()))
            if st.button("Confirmar Eliminación", type="primary"):
                df_j[df_j["Nombre"]!=sel].to_csv(J_FILE, index=False)
                st.success(f"{sel} eliminado"); st.rerun()
        else:
            st.info("No hay jugadores registrados.")

elif menu == "💾 RESPALDO":
    if st.session_state.admin:
        st.header("💾 Descarga de Respaldos")
        st.download_button("Descargar CSV Jugadores", df_j.to_csv(index=False), "jugadores.csv", "text/csv")
        st.download_button("Descargar CSV Resultados", df_g.to_csv(index=False), "resultados.csv", "text/csv")
