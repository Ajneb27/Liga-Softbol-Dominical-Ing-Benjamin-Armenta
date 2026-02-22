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
                    df[c] = LOGO_DEFECTO if c == "Logo" else (0)
            return df
        except: return pd.DataFrame(columns=columnas)
    return pd.DataFrame(columns=columnas)

# EL y IP (Entradas Lanzadas) añadidos
df_j = cargar_csv(J_FILE, ["Nombre", "Equipo", "VB", "H", "2B", "3B", "HR", "BB", "G", "P", "JI", "IP"])
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
        if st.button("❌ Cerrar Sesión"):
            st.session_state.admin = False
            st.rerun()

    st.divider()
    opciones = ["🏠 INICIO", "📊 STANDING", "🏆 LÍDERES", "📋 ROSTERS", "📜 HISTORIAL", "🏘️ EQUIPOS"]
    if st.session_state.admin: opciones += ["✍️ REGISTRAR", "🗑️ BORRAR", "💾 RESPALDO"]
    menu = st.radio("Secciones:", opciones)

# --- 4. SECCIONES ---

if menu == "📊 STANDING":
    st.header("📊 Tabla de Posiciones")
    if not df_e.empty and not df_g.empty:
        res = []
        for eq in df_e["Nombre"].unique():
            v, h = df_g[df_g["Visitante"]==eq], df_g[df_g["HomeClub"]==eq]
            g = len(v[v["CV"]>v["CH"]]) + len(h[h["CH"]>h["CV"]])
            p = len(v[v["CV"]<v["CH"]]) + len(h[h["CH"]<h["CV"]])
            cf, cc = v["CV"].sum() + h["CH"].sum(), v["CH"].sum() + h["CV"].sum()
            res.append({"Equipo": eq, "G": g, "P": p, "AVG": round(g/(g+p),3) if (g+p)>0 else 0, "CF": cf, "CC": cc, "DIF": cf-cc})
        st.table(pd.DataFrame(res).sort_values(by=["AVG", "DIF"], ascending=False))

elif menu == "🏆 LÍDERES":
    st.header("🥇 Líderes de la Liga")
    jor_max = df_g["Jornada"].max() if not df_g.empty else 1
    
    col_f1, col_f2 = st.columns(2)
    min_vb = col_f1.number_input("Mínimo VB (Bateo):", 0, 500, int(jor_max * 2.5))
    min_ip = col_f2.number_input("Mínimo Entradas (IP):", 0, 500, int(jor_max * 2))

    t1, t2 = st.tabs(["⚾ BATEO", "🎯 PITCHEO"])
    with t1:
        df_l = df_j.copy()
        df_l["HT"] = df_l["H"] + df_l["2B"] + df_l["3B"] + df_l["HR"]
        df_l["TB"] = df_l["VB"] + df_l["BB"]
        df_l["AVG_N"] = (df_l["HT"] / df_l["VB"]).fillna(0)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.write("### AVG")
            l_avg = df_l[df_l["VB"] >= min_vb].sort_values(by=["AVG_N", "TB"], ascending=False).head(10)
            st.dataframe(l_avg[['Nombre']].assign(AVG=l_avg["AVG_N"].map('{:.3f}'.format)), hide_index=True)
        with c2: st.write("### HT"); st.dataframe(df_l.sort_values(by=["HT","TB"], ascending=False).head(10)[['Nombre','HT']], hide_index=True)
        with c3: st.write("### HR"); st.dataframe(df_l.sort_values(by=["HR","TB"], ascending=False).head(10)[['Nombre','HR']], hide_index=True)

    with t2:
        st.write("### Líderes de Pitcheo")
        df_p = df_j[df_j["IP"] >= min_ip].sort_values(by=["G", "JI"], ascending=False).head(10)
        st.dataframe(df_p[['Nombre', 'Equipo', 'G', 'P', 'JI', 'IP']], hide_index=True)

elif menu == "📋 ROSTERS":
    st.header("📋 Rosters")
    if not df_e.empty:
        c_roster1, c_roster2 = st.columns([3,1])
        eq_sel = c_roster1.selectbox("Equipo:", df_e["Nombre"].unique())
        logo_url = df_e[df_e["Nombre"] == eq_sel]["Logo"].iloc[0]
        c_roster2.image(logo_url, width=100)
        
        df_r = df_j[df_j["Equipo"] == eq_sel].copy()
        if not df_r.empty:
            df_r["HT"] = df_r["H"] + df_r["2B"] + df_r["3B"] + df_r["HR"]
            df_r["TB"] = df_r["VB"] + df_r["BB"]
            df_r["AVG"] = (df_r["HT"] / df_r["VB"]).fillna(0).map('{:.3f}'.format)
            st.dataframe(df_r[["Nombre", "TB", "VB", "H", "2B", "3B", "HR", "BB", "G", "P", "JI", "IP", "AVG"]], hide_index=True, use_container_width=True)

elif menu == "🏘️ EQUIPOS":
    st.header("🏘️ Gestión de Equipos")
    if st.session_state.admin:
        tab_list, tab_edit = st.tabs(["Lista y Nuevo", "Editar Existente"])
        with tab_list:
            with st.form("n_eq"):
                n, d, l = st.text_input("Nombre"), st.number_input("Debut", 1900, 2026, 2026), st.text_input("Logo URL", LOGO_DEFECTO)
                if st.form_submit_button("Añadir"):
                    pd.concat([df_e, pd.DataFrame([{"Nombre":n,"Debut":d,"Logo":l}])]).to_csv(E_FILE, index=False); st.rerun()
        with tab_edit:
            if not df_e.empty:
                sel = st.selectbox("Equipo a editar:", df_e["Nombre"].unique())
                idx = df_e[df_e["Nombre"] == sel].index[0]
                with st.form("e_eq"):
                    en = st.text_input("Nombre", df_e.at[idx, "Nombre"])
                    el = st.text_input("Logo URL", df_e.at[idx, "Logo"])
                    if st.form_submit_button("Actualizar"):
                        df_e.at[idx, "Nombre"], df_e.at[idx, "Logo"] = en, el
                        df_e.to_csv(E_FILE, index=False); st.rerun()
    st.dataframe(df_e, hide_index=True)

elif menu == "✍️ REGISTRAR" and st.session_state.admin:
    tj, tr = st.tabs(["👤 JUGADORES", "⚾ RESULTADOS"])
    with tj:
        with st.form("rj"):
            n, eq = st.text_input("Nombre"), st.selectbox("Equipo", df_e["Nombre"].unique()) if not df_e.empty else ""
            c1, c2, c3 = st.columns(3)
            vb, h, bb = c1.number_input("VB",0), c2.number_input("H",0), c3.number_input("BB",0)
            h2, h3, hr = c1.number_input("2B",0), c2.number_input("3B",0), c3.number_input("HR",0)
            pg, pp, ji, ip = c1.number_input("G",0), c2.number_input("P",0), c3.number_input("JI",0), c1.number_input("IP (Entradas)", 0.0)
            if st.form_submit_button("Guardar"):
                if n in df_j["Nombre"].values:
                    df_j.loc[df_j["Nombre"]==n, ["VB","H","2B","3B","HR","BB","G","P","JI","IP"]] += [vb, h, h2, h3, hr, bb, pg, pp, ji, ip]
                else:
                    df_j = pd.concat([df_j, pd.DataFrame([{"Nombre":n,"Equipo":eq,"VB":vb,"H":h,"2B":h2,"3B":h3,"HR":hr,"BB":bb,"G":pg,"P":pp,"JI":ji,"IP":ip}])])
                df_j.to_csv(J_FILE, index=False); st.success("Guardado"); st.rerun()
    with tr:
        with st.form("rr"):
            jor, v, cv = st.number_input("Jor",1), st.selectbox("Vis", df_e["Nombre"].unique()), st.number_input("C.V",0)
            h, ch = st.selectbox("Home", df_e["Nombre"].unique()), st.number_input("C.H",0)
            if st.form_submit_button("Guardar"):
                pd.concat([df_g, pd.DataFrame([{"Jornada":jor,"Visitante":v,"CV":cv,"HomeClub":h,"CH":ch}])]).to_csv(G_FILE, index=False); st.rerun()

elif menu == "🗑️ BORRAR" and st.session_state.admin:
    sel = st.selectbox("Eliminar Jugador:", sorted(df_j["Nombre"].unique()))
    if st.button("CONFIRMAR BORRADO"):
        df_j[df_j["Nombre"]!=sel].to_csv(J_FILE, index=False); st.rerun()

elif menu == "💾 RESPALDO" and st.session_state.admin:
    st.download_button("Descargar Jugadores", df_j.to_csv(index=False), "jugadores_2026.csv")
    st.download_button("Descargar Equipos", df_e.to_csv(index=False), "equipos_2026.csv")
