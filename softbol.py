import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN E IDENTIDAD ---
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

df_j = cargar_csv(J_FILE, ["Nombre", "Equipo", "VB", "H", "2B", "3B", "HR", "BB", "G", "P", "JI"])
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
            cf = v["CV"].sum() + h["CH"].sum()
            cc = v["CH"].sum() + h["CV"].sum()
            res.append({"Equipo": eq, "G": g, "P": p, "AVG": round(g/(g+p),3) if (g+p)>0 else 0, "CF": cf, "CC": cc, "DIF": cf-cc})
        st.table(pd.DataFrame(res).sort_values(by=["AVG", "DIF"], ascending=False))

elif menu == "🏆 LÍDERES":
    st.header("🥇 Líderes")
    jor_max = df_g["Jornada"].max() if not df_g.empty else 1
    # Turnos mínimos configurados por Admin o por defecto
    min_vb = st.sidebar.number_input("Min VB:", 0, 500, int(jor_max * 2.5)) if st.session_state.admin else int(jor_max * 2.5)
    
    df_l = df_j.copy()
    df_l["HT"] = df_l["H"] + df_l["2B"] + df_l["3B"] + df_l["HR"]
    df_l["TB"] = df_l["VB"] + df_l["BB"]
    df_l["AVG_N"] = (df_l["HT"] / df_l["VB"]).fillna(0)
    
    t1, t2 = st.tabs(["⚾ BATEO", "🎯 PITCHEO"])
    with t1:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.write("### AVG")
            l_avg = df_l[df_l["VB"] >= min_vb].sort_values(by=["AVG_N", "TB"], ascending=False).head(10)
            st.dataframe(l_avg[['Nombre', 'HT']].assign(AVG=l_avg["AVG_N"].map('{:.3f}'.format))[['Nombre','AVG']], hide_index=True)
        with c2: st.write("### HT"); st.dataframe(df_l.sort_values(by=["HT","TB"], ascending=False).head(10)[['Nombre','HT']], hide_index=True)
        with c3: st.write("### HR"); st.dataframe(df_l.sort_values(by=["HR","TB"], ascending=False).head(10)[['Nombre','HR']], hide_index=True)
    with t2:
        st.write("### Líderes Pitcheo (G/JI)")
        st.dataframe(df_l[df_l["G"]+df_l["JI"] > 0].sort_values(by=["G","JI"], ascending=False)[['Nombre','Equipo','G','P','JI']], hide_index=True)

elif menu == "🏘️ EQUIPOS":
    st.header("🏘️ Equipos")
    if st.session_state.admin:
        with st.form("nuevo_equipo"):
            n_eq = st.text_input("Nombre del Equipo")
            if st.form_submit_button("Añadir Equipo") and n_eq:
                pd.concat([df_e, pd.DataFrame([{"Nombre":n_eq,"Debut":ANIO_ACTUAL,"Logo":LOGO_DEFECTO}])]).to_csv(E_FILE, index=False)
                st.rerun()
    st.table(df_e[["Nombre", "Debut"]])

elif menu == "✍️ REGISTRAR" and st.session_state.admin:
    t_j, t_r = st.tabs(["👤 JUGADORES", "⚾ RESULTADOS"])
    with t_j:
        with st.form("rj"):
            n, eq = st.text_input("Nombre"), st.selectbox("Equipo", df_e["Nombre"].unique()) if not df_e.empty else ""
            c1, c2, c3 = st.columns(3)
            vb, h, bb = c1.number_input("VB",0), c2.number_input("H",0), c3.number_input("BB",0)
            h2, h3, hr = c1.number_input("2B",0), c2.number_input("3B",0), c3.number_input("HR",0)
            pg, pp, ji = c1.number_input("G",0), c2.number_input("P",0), c3.number_input("JI",0)
            if st.form_submit_button("Guardar"):
                if n in df_j["Nombre"].values:
                    df_j.loc[df_j["Nombre"]==n, ["VB","H","2B","3B","HR","BB","G","P","JI"]] += [vb, h, h2, h3, hr, bb, pg, pp, ji]
                else:
                    df_j = pd.concat([df_j, pd.DataFrame([{"Nombre":n,"Equipo":eq,"VB":vb,"H":h,"2B":h2,"3B":h3,"HR":hr,"BB":bb,"G":pg,"P":pp,"JI":ji}])])
                df_j.to_csv(J_FILE, index=False); st.rerun()
    with t_r:
        with st.form("rr"):
            jor, v, cv = st.number_input("Jor",1), st.selectbox("Vis", df_e["Nombre"].unique()), st.number_input("C.V",0)
            h, ch = st.selectbox("Home", df_e["Nombre"].unique()), st.number_input("C.H",0)
            if st.form_submit_button("Guardar Juego"):
                pd.concat([df_g, pd.DataFrame([{"Jornada":jor,"Visitante":v,"CV":cv,"HomeClub":h,"CH":ch}])]).to_csv(G_FILE, index=False); st.rerun()

elif menu == "🗑️ BORRAR" and st.session_state.admin:
    st.header("🗑️ Borrar Jugador")
    sel = st.selectbox("Jugador:", sorted(df_j["Nombre"].unique()))
    if st.button("Eliminar"):
        df_j[df_j["Nombre"]!=sel].to_csv(J_FILE, index=False); st.rerun()

elif menu == "💾 RESPALDO" and st.session_state.admin:
    st.download_button("Descargar Jugadores", df_j.to_csv(index=False), "jugadores_2026.csv")
