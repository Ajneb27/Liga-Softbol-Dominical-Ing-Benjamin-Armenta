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

# Carga de datos inicial
df_j = cargar_csv(J_FILE, ["Nombre", "Equipo", "Categoria", "VB", "H", "2B", "3B", "HR", "BB", "G", "P"])
df_e = cargar_csv(E_FILE, ["Nombre", "Debut", "Logo"])
df_g = cargar_csv(G_FILE, ["Jornada", "Visitante", "CV", "HomeClub", "CH"])

# --- 4. SECCIONES ---

if menu == "🏆 LÍDERES":
    st.header("🥇 Líderes de Bateo")
    jor_max = df_g["Jornada"].max() if not df_g.empty else 1
    min_vb = st.sidebar.slider("Mínimo AB:", 0, 100, int(jor_max * 3)) if st.session_state.admin else int(jor_max * 3)

    df_l = df_j.copy()
    # HT (Hits Totales) = H (Sencillos) + 2B + 3B + HR
    df_l["HT"] = df_l["H"] + df_l["2B"] + df_l["3B"] + df_l["HR"]
    df_l["AVG_NUM"] = (df_l["HT"] / df_l["VB"]).fillna(0)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.write("### AVG")
        l_avg = df_l[df_l["VB"] >= min_vb].nlargest(10, 'AVG_NUM').copy()
        l_avg["AVG"] = l_avg["AVG_NUM"].apply(lambda x: f"{x:.3f}")
        st.dataframe(l_avg[['Nombre', 'AVG']], hide_index=True)
    with c2:
        st.write("### Hits Totales (HT)"); st.dataframe(df_l.nlargest(10,'HT')[['Nombre','HT']], hide_index=True)
    with c3:
        st.write("### Home Runs"); st.dataframe(df_l.nlargest(10,'HR')[['Nombre','HR']], hide_index=True)
    
    st.divider()
    c4, c5 = st.columns(2)
    with c4:
        st.write("### Dobles (2B)"); st.dataframe(df_l.nlargest(10,'2B')[['Nombre','2B']], hide_index=True)
    with c5:
        st.write("### Triples (3B)"); st.dataframe(df_l.nlargest(10,'3B')[['Nombre','3B']], hide_index=True)

elif menu == "📋 ROSTERS":
    st.header("📋 Rosters Detallados")
    if not df_e.empty:
        col1, col2 = st.columns([3, 1])
        eq_sel = col1.selectbox("Seleccione un Equipo:", df_e["Nombre"].unique())
        logo_data = df_e[df_e["Nombre"] == eq_sel]["Logo"].values[0]
        col2.image(logo_data, width=80)
            
        df_r = df_j[df_j["Equipo"] == eq_sel].copy()
        
        # --- CÁLCULOS ROSTER ---
        df_r["AB"] = df_r["VB"] # AB = Turnos
        df_r["HT"] = df_r["H"] + df_r["2B"] + df_r["3B"] + df_r["HR"] # HT = Suma de todo
        df_r["TB"] = df_r["BB"] + df_r["AB"] # TB = BB + AB como solicitaste
        df_r["AVG"] = (df_r["HT"] / df_r["AB"]).fillna(0).apply(lambda x: f"{x:.3f}")
        
        # --- ORDEN SOLICITADO ---
        cols = ["Nombre", "TB", "AB", "H", "2B", "3B", "HR", "BB", "HT", "AVG"]
        st.dataframe(df_r[cols], use_container_width=True, hide_index=True)
    else: st.warning("No hay equipos registrados.")

elif menu == "🏘️ EQUIPOS":
    st.header("🏘️ Gestión de Equipos")
    if st.session_state.admin:
        t_v, t_n, t_e = st.tabs(["LISTA", "NUEVO", "EDITAR"])
        with t_v: st.dataframe(df_e, hide_index=True, use_container_width=True)
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
                    en = st.text_input("Nombre", df_e.at[idx, "Nombre"])
                    ed = st.number_input("Debut", 1980, 2026, int(df_e.at[idx, "Debut"]))
                    el = st.text_input("Logo URL", df_e.at[idx, "Logo"])
                    if st.form_submit_button("Actualizar"):
                        df_e.at[idx, "Nombre"], df_e.at[idx, "Debut"], df_e.at[idx, "Logo"] = en, ed, el
                        df_e.to_csv(E_FILE, index=False); st.rerun()

elif menu == "✍️ REGISTRAR":
    if st.session_state.admin:
        tj, tr = st.tabs(["👤 JUGADORES", "⚾ RESULTADOS"])
        with tj:
            with st.form("rj"):
                n, e = st.text_input("Nombre"), st.selectbox("Equipo", df_e["Nombre"].unique())
                v1, v2, v3 = st.columns(3)
                vb, h, bb = v1.number_input("AB (Turnos)", 0), v2.number_input("H (Sencillos)", 0), v3.number_input("BB", 0)
                d2, d3, hr = v1.number_input("2B", 0), v2.number_input("3B", 0), v3.number_input("HR", 0)
                if st.form_submit_button("Guardar"):
                    df_j = pd.concat([df_j[df_j["Nombre"]!=n], pd.DataFrame([{"Nombre":n,"Equipo":e,"VB":vb,"H":h,"2B":d2,"3B":d3,"HR":hr,"BB":bb}])], ignore_index=True)
                    df_j.to_csv(J_FILE, index=False); st.rerun()
        with tr:
            with st.form("rs"):
                j, v, cv = st.number_input("Jornada",1), st.selectbox("Vis", df_e["Nombre"].unique()), st.number_input("CV",0)
                hc, ch = st.selectbox("HC", df_e["Nombre"].unique()), st.number_input("CH",0)
                if st.form_submit_button("Guardar"):
                    pd.concat([df_g, pd.DataFrame([{"Jornada":j,"Visitante":v,"CV":cv,"HomeClub":hc,"CH":ch}])], ignore_index=True).to_csv(G_FILE, index=False); st.rerun()

elif menu == "📊 STANDING":
    st.header("📊 Tabla de Posiciones")
    if not df_g.empty:
        res = []
        for eq in df_e["Nombre"].unique():
            v, h = df_g[df_g["Visitante"]==eq], df_g[df_g["HomeClub"]==eq]
            g, p = len(v[v["CV"]>v["CH"]]) + len(h[h["CH"]>h["CV"]]), len(v[v["CV"]<v["CH"]]) + len(h[h["CH"]<h["CV"]])
            cf, cc = v["CV"].sum() + h["CH"].sum(), v["CH"].sum() + h["CV"].sum()
            res.append({"Equipo": eq, "G": g, "P": p, "AVG": round(g/(g+p),3) if (g+p)>0 else 0, "CF": cf, "CC": cc, "DIF": cf-cc})
        st.table(pd.DataFrame(res).sort_values(by=["AVG", "DIF"], ascending=False))

elif menu == "🗑️ BORRAR":
    if st.session_state.admin:
        sel = st.selectbox("Eliminar:", sorted(df_j["Nombre"].unique()))
        if st.button("Confirmar", type="primary"):
            df_j[df_j["Nombre"]!=sel].to_csv(J_FILE, index=False); st.rerun()

elif menu == "💾 RESPALDO":
    if st.session_state.admin:
        st.download_button("Descargar Jugadores", df_j.to_csv(index=False), "jugadores.csv")
