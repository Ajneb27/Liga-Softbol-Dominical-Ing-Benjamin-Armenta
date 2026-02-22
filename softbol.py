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
        if st.button("❌ Cerrar Sesión"):
            st.session_state.admin = False
            st.rerun()

    st.divider()
    menu = st.radio("Secciones:", ["🏠 INICIO", "📊 STANDING", "🏆 LÍDERES", "📋 ROSTERS", "📜 HISTORIAL", "🏘️ EQUIPOS", "✍️ REGISTRAR", "🗑️ BORRAR", "💾 RESPALDO"])

# Carga de datos con columna Logo
df_j = cargar_csv(J_FILE, ["Nombre", "Equipo", "Categoria", "VB", "H", "2B", "3B", "HR", "BB", "G", "P"])
df_e = cargar_csv(E_FILE, ["Nombre", "Debut", "Logo"])
df_g = cargar_csv(G_FILE, ["Jornada", "Visitante", "CV", "HomeClub", "CH"])

# --- 4. SECCIONES ---

if menu == "🏘️ EQUIPOS":
    st.header("🏘️ Gestión de Equipos")
    
    if st.session_state.admin:
        t_ver, t_nuevo, t_edit = st.tabs(["📋 LISTA", "➕ NUEVO", "✏️ EDITAR"])
        
        with t_ver:
            st.dataframe(df_e, hide_index=True, use_container_width=True)
            
        with t_nuevo:
            with st.form("n_e"):
                n = st.text_input("Nombre del Equipo")
                d = st.number_input("Año de Debut", 1980, ANIO_ACTUAL, ANIO_ACTUAL)
                l = st.text_input("URL del Logo (Link de imagen)", LOGO_DEFECTO)
                if st.form_submit_button("Registrar Equipo"):
                    if n:
                        nuevo = pd.DataFrame([{"Nombre":n, "Debut":d, "Logo":l}])
                        pd.concat([df_e, nuevo], ignore_index=True).to_csv(E_FILE, index=False)
                        st.success(f"Equipo {n} creado."); st.rerun()
        
        with t_edit:
            if not df_e.empty:
                eq_edit = st.selectbox("Seleccione equipo a editar:", df_e["Nombre"].unique())
                idx = df_e[df_e["Nombre"] == eq_edit].index[0]
                
                with st.form("f_edit"):
                    en = st.text_input("Nombre", df_e.at[idx, "Nombre"])
                    ed = st.number_input("Debut", 1980, ANIO_ACTUAL, int(df_e.at[idx, "Debut"]))
                    el = st.text_input("URL Logo", df_e.at[idx, "Logo"])
                    if st.form_submit_button("Guardar Cambios"):
                        df_e.at[idx, "Nombre"] = en
                        df_e.at[idx, "Debut"] = ed
                        df_e.at[idx, "Logo"] = el
                        df_e.to_csv(E_FILE, index=False)
                        st.success("Cambios guardados"); st.rerun()
            else: st.info("No hay equipos para editar.")
    else:
        st.dataframe(df_e[["Nombre", "Debut"]], hide_index=True, use_container_width=True)

elif menu == "📋 ROSTERS":
    st.header("📋 Rosters de Equipos")
    if not df_e.empty:
        col_sel, col_logo = st.columns([3, 1])
        with col_sel:
            eq_sel = st.selectbox("Seleccione un Equipo:", df_e["Nombre"].unique())
        
        # Mostrar Logo del equipo
        logo_url = df_e[df_e["Nombre"] == eq_sel]["Logo"].values[0]
        with col_logo:
            st.image(logo_url, width=100)
            
        df_roster = df_j[df_j["Equipo"] == eq_sel].copy()
        df_roster["TB"] = (df_roster["H"] - df_roster["2B"] - df_roster["3B"] - df_roster["HR"]) + (df_roster["2B"]*2) + (df_roster["3B"]*3) + (df_roster["HR"]*4)
        df_roster["AVG"] = (df_roster["H"] / df_roster["VB"]).fillna(0).apply(lambda x: f"{x:.3f}")
        st.dataframe(df_roster[["Nombre", "AVG", "BB", "TB"]], use_container_width=True, hide_index=True)
    else: st.warning("Cree equipos primero.")

elif menu == "🏆 LÍDERES":
    st.header("🥇 Líderes de la Temporada")
    jor_max = df_g["Jornada"].max() if not df_g.empty else 1
    min_vb = st.sidebar.slider("Mínimo VB (Líderes):", 0, 100, int(jor_max * 3)) if st.session_state.admin else int(jor_max * 3)

    df_l = df_j.copy()
    df_l["TB"] = (df_l["H"] - df_l["2B"] - df_l["3B"] - df_l["HR"]) + (df_l["2B"]*2) + (df_l["3B"]*3) + (df_l["HR"]*4)
    df_l["AVG_NUM"] = (df_l["H"] / df_l["VB"]).fillna(0)
    
    t1, t2 = st.tabs(["⚾ BATEO", "🎯 PITCHEO"])
    with t1:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.write("### AVG")
            lideres_avg = df_l[df_l["VB"] >= min_vb].nlargest(10, 'AVG_NUM').copy()
            lideres_avg["AVG"] = lideres_avg["AVG_NUM"].apply(lambda x: f"{x:.3f}")
            st.dataframe(lideres_avg[['Nombre', 'AVG']], hide_index=True)
        with c2:
            st.write("### Bases Totales (TB)")
            st.dataframe(df_l.nlargest(10, 'TB')[['Nombre', 'TB']], hide_index=True)
        with c3:
            st.write("### Bases x Bola (BB)")
            st.dataframe(df_l.nlargest(10, 'BB')[['Nombre', 'BB']], hide_index=True)

elif menu == "📊 STANDING":
    st.header("📊 Tabla de Posiciones 2026")
    if not df_g.empty and not df_e.empty:
        res = []
        for eq in df_e["Nombre"].unique():
            v, h = df_g[df_g["Visitante"] == eq], df_g[df_g["HomeClub"] == eq]
            gan, perd = len(v[v["CV"] > v["CH"]]) + len(h[h["CH"] > h["CV"]]), len(v[v["CV"] < v["CH"]]) + len(h[h["CH"] < h["CV"]])
            cf, cc = v["CV"].sum() + h["CH"].sum(), v["CH"].sum() + h["CV"].sum()
            res.append({"Equipo": eq, "JJ": gan+perd, "G": gan, "P": perd, "AVG": round(gan/(gan+perd),3) if (gan+perd)>0 else 0, "CF": cf, "CC": cc, "DIF": cf-cc})
        st.table(pd.DataFrame(res).sort_values(by=["AVG", "DIF"], ascending=False))

elif menu == "✍️ REGISTRAR":
    if st.session_state.admin:
        tj, tr = st.tabs(["👤 JUGADORES", "⚾ RESULTADOS"])
        with tj:
            with st.form("rj"):
                n = st.text_input("Nombre completo")
                e = st.selectbox("Equipo", df_e["Nombre"].unique()) if not df_e.empty else "N/A"
                v1, v2, v3 = st.columns(3)
                vb, h, bb = v1.number_input("VB",0), v2.number_input("H (TOTAL)",0), v3.number_input("BB",0)
                d2, d3, hr = v1.number_input("2B",0), v2.number_input("3B",0), v3.number_input("HR",0)
                if st.form_submit_button("Guardar Jugador"):
                    df_j = pd.concat([df_j[df_j["Nombre"]!=n], pd.DataFrame([{"Nombre":n,"Equipo":e,"VB":vb,"H":h,"2B":d2,"3B":d3,"HR":hr,"BB":bb}])], ignore_index=True)
                    df_j.to_csv(J_FILE, index=False); st.success("Guardado"); st.rerun()
        with tr:
            with st.form("rs"):
                j, v = st.number_input("Jornada",1), st.selectbox("Visitante", df_e["Nombre"].unique())
                cv = st.number_input("Carreras Vis",0)
                hc = st.selectbox("Home Club", df_e["Nombre"].unique())
                ch = st.number_input("Carreras HC",0)
                if st.form_submit_button("Guardar Score"):
                    pd.concat([df_g, pd.DataFrame([{"Jornada":j,"Visitante":v,"CV":cv,"HomeClub":hc,"CH":ch}])], ignore_index=True).to_csv(G_FILE, index=False); st.rerun()

elif menu == "🗑️ BORRAR":
    if st.session_state.admin:
        sel = st.selectbox("Seleccione para eliminar:", sorted(df_j["Nombre"].unique()))
        if st.button("Confirmar Borrado", type="primary"):
            df_j[df_j["Nombre"]!=sel].to_csv(J_FILE, index=False); st.rerun()

elif menu == "💾 RESPALDO":
    if st.session_state.admin:
        st.download_button("Descargar CSV Jugadores", df_j.to_csv(index=False), "jugadores.csv")
        st.download_button("Descargar CSV Equipos", df_e.to_csv(index=False), "equipos.csv")
