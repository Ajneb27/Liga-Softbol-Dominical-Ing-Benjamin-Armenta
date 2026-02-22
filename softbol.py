import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN E IDENTIDAD 2026 ---
NOMBRE_LIGA = "LIGA DE SOFTBOL DOMINICAL"
ESLOGAN = "TEMPORADA ENTRE AMIGOS"
ANIO_ACTUAL = 2026
LOGO_DEFECTO = "https://cdn-icons-png.flaticon.com" 

DATA_DIR = "liga_softbol_final_2026"
if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)

J_FILE = os.path.join(DATA_DIR, "jugadores_master.csv")
E_FILE = os.path.join(DATA_DIR, "equipos_master.csv")
G_FILE = os.path.join(DATA_DIR, "juegos_2026.csv")
P_FILE = os.path.join(DATA_DIR, "programacion_2026.csv")

# --- 2. MOTOR DE DATOS ---
st.set_page_config(page_title=NOMBRE_LIGA, layout="wide", page_icon="🥎")

def cargar_csv(archivo, columnas):
    if os.path.exists(archivo):
        try:
            df = pd.read_csv(archivo)
            for c in columnas:
                if c not in df.columns: df[c] = 0
            return df
        except: return pd.DataFrame(columns=columnas)
    return pd.DataFrame(columns=columnas)

cols_j = ["Nombre", "Equipo", "Categoria", "VB", "H", "2B", "3B", "HR", "BB", "G", "P", "JI", "IP"]
df_j = cargar_csv(J_FILE, cols_j)
df_e = cargar_csv(E_FILE, ["Nombre", "Debut", "Logo"])
df_g = cargar_csv(G_FILE, ["Jornada", "Visitante", "CV", "HomeClub", "CH"])
df_p = cargar_csv(P_FILE, ["Fecha", "Hora", "Visitante", "HomeClub", "Campo"])

# --- 3. BARRA LATERAL ---
with st.sidebar:
    st.image(LOGO_DEFECTO, width=100)
    st.title(f"🏆 {NOMBRE_LIGA}")
    st.subheader(ESLOGAN)
    if 'admin' not in st.session_state: st.session_state.admin = False

    if not st.session_state.admin:
        with st.expander("🔐 Acceso Administrador"):
            u = st.text_input("Usuario")
            p = st.text_input("Clave", type="password")
            if st.button("Entrar"):
                if u == "admin" and p == "123":
                    st.session_state.admin = True
                    st.rerun()
    else:
        st.success("Admin: ACTIVADO")
        if st.button("❌ Cerrar Sesión"):
            st.session_state.admin = False
            st.rerun()

    st.divider()
    opciones = ["🏠 INICIO", "📅 PROGRAMACIÓN", "📊 STANDING", "🏆 LÍDERES", "📋 ROSTERS", "📜 HISTORIAL", "🏘️ EQUIPOS"]
    if st.session_state.admin: opciones += ["✍️ REGISTRAR", "🗑️ BORRAR", "💾 RESPALDO"]
    menu = st.radio("Secciones:", opciones)

# --- 4. SECCIONES ---

if menu == "🏠 INICIO":
    st.title(f"🥎 {NOMBRE_LIGA}")
    st.header(f"🏆 {ESLOGAN} - {ANIO_ACTUAL}")
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Equipos", len(df_e)); c2.metric("Jugadores", len(df_j)); c3.metric("Juegos Jugados", len(df_g))
    st.image("https://images.unsplash.com", use_container_width=True)

elif menu == "📅 PROGRAMACIÓN":
    st.header("📅 Programación de Juegos")
    if st.session_state.admin:
        with st.expander("➕ Añadir/Editar Calendario"):
            with st.form("f_prog"):
                f, h = st.text_input("Fecha"), st.text_input("Hora")
                v = st.selectbox("Visitante", df_e["Nombre"].unique()) if not df_e.empty else ""
                hc = st.selectbox("Home Club", df_e["Nombre"].unique()) if not df_e.empty else ""
                cam = st.text_input("Campo", "Principal")
                if st.form_submit_button("Programar"):
                    new_p = pd.DataFrame([{"Fecha":f,"Hora":h,"Visitante":v,"HomeClub":hc,"Campo":cam}])
                    df_p = pd.concat([df_p, new_p], ignore_index=True)
                    df_p.to_csv(P_FILE, index=False); st.rerun()
        if not df_p.empty:
            sel_p = st.selectbox("Borrar juego:", df_p.index, format_func=lambda x: f"{df_p.at[x,'Visitante']} vs {df_p.at[x,'HomeClub']}")
            if st.button("Eliminar Seleccionado"):
                df_p.drop(sel_p).to_csv(P_FILE, index=False); st.rerun()
    st.table(df_p) if not df_p.empty else st.info("No hay programación.")

elif menu == "📊 STANDING":
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
    st.header("🥇 Líderes Individuales")
    jor_max = df_g["Jornada"].max() if not df_g.empty else 1
    c1, c2 = st.columns(2)
    min_vb = c1.number_input("Min VB:", 0, 500, int(jor_max * 2.5))
    min_ip = c2.number_input("Min IP:", 0, 500, int(jor_max * 2))
    
    t1, t2 = st.tabs(["⚾ BATEO", "🎯 PITCHEO"])
    with t1:
        df_l = df_j.copy()
        df_l["HT"] = df_l["H"] + df_l["2B"] + df_l["3B"] + df_l["HR"]
        df_l["TB"] = df_l["VB"] + df_l["BB"]
        df_l["AVG_N"] = (df_l["HT"] / df_l["VB"]).fillna(0)
        
        ca, cb, cc = st.columns(3)
        with ca:
            st.write("### AVG")
            l_avg = df_l[df_l["VB"] >= min_vb].sort_values(by=["AVG_N", "TB"], ascending=False).head(10)
            st.dataframe(l_avg[['Nombre', 'Equipo']].assign(AVG=l_avg["AVG_N"].map('{:.3f}'.format)), hide_index=True)
        with cb: st.write("### HT"); st.dataframe(df_l.sort_values(by=["HT","TB"], ascending=False).head(10)[['Nombre','Equipo','HT']], hide_index=True)
        with cc: st.write("### HR"); st.dataframe(df_l.sort_values(by=["HR","TB"], ascending=False).head(10)[['Nombre','Equipo','HR']], hide_index=True)
        
        cd, ce = st.columns(2)
        with cd: st.write("### 2B"); st.dataframe(df_l.sort_values(by=["2B","TB"], ascending=False).head(10)[['Nombre','Equipo','2B']], hide_index=True)
        with ce: st.write("### 3B"); st.dataframe(df_l.sort_values(by=["3B","TB"], ascending=False).head(10)[['Nombre','Equipo','3B']], hide_index=True)
    with t2:
        st.write("### Ganados / JI")
        st.dataframe(df_j[df_j["IP"] >= min_ip].sort_values(by=["G","JI"], ascending=False).head(10)[['Nombre','Equipo','G','P','JI','IP']], hide_index=True)

elif menu == "📋 ROSTERS":
    st.header("📋 Rosters")
    if not df_e.empty:
        c1, c2 = st.columns(2)
        eq_sel = c1.selectbox("Equipo:", df_e["Nombre"].unique())
        logo = df_e[df_e["Nombre"] == eq_sel]["Logo"].iloc[0] if not df_e[df_e["Nombre"] == eq_sel].empty else LOGO_DEFECTO
        c2.image(logo, width=80)
        df_r = df_j[df_j["Equipo"] == eq_sel].copy()
        if not df_r.empty:
            df_r["HT"] = df_r["H"] + df_r["2B"] + df_r["3B"] + df_r["HR"]
            df_r["AVG"] = (df_r["HT"] / df_r["VB"]).fillna(0).map('{:.3f}'.format)
            st.dataframe(df_r[["Nombre", "Categoria", "VB", "H", "2B", "3B", "HR", "BB", "G", "P", "JI", "IP", "AVG"]], hide_index=True)

elif menu == "📜 HISTORIAL":
    st.header("📜 Ficha de Jugador")
    if not df_j.empty:
        js = st.selectbox("Buscar:", sorted(df_j["Nombre"].unique()))
        d = df_j[df_j["Nombre"]==js].iloc[0]
        c1, c2, c3 = st.columns(3)
        c1.metric("Equipo", d['Equipo']); c2.metric("VB", int(d['VB'])); c3.metric("JI", int(d['JI']))
        st.write(f"**Bateo:** H: {int(d['H'])} | 2B: {int(d['2B'])} | 3B: {int(d['3B'])} | HR: {int(d['HR'])} | BB: {int(d['BB'])}")
        st.write(f"**Pitcheo:** G: {int(d['G'])} | P: {int(d['P'])} | IP: {d['IP']}")

elif menu == "🏘️ EQUIPOS":
    st.header("🏘️ Gestión de Equipos")
    if st.session_state.admin:
        with st.form("n_eq"):
            n, l = st.text_input("Nombre"), st.text_input("Logo URL", LOGO_DEFECTO)
            if st.form_submit_button("Añadir"):
                df_e = pd.concat([df_e, pd.DataFrame([{"Nombre":n,"Debut":ANIO_ACTUAL,"Logo":l}])], ignore_index=True)
                df_e.to_csv(E_FILE, index=False); st.rerun()
    st.dataframe(df_e[["Nombre", "Logo"]], hide_index=True)

elif menu == "✍️ REGISTRAR" and st.session_state.admin:
    t1, t2 = st.tabs(["👤 JUGADOR", "⚾ RESULTADO"])
    with t1:
        with st.form("rj"):
            n, eq, cat = st.text_input("Nombre"), st.selectbox("Equipo", df_e["Nombre"].unique() if not df_e.empty else [""]), st.text_input("Cat")
            c1, c2, c3 = st.columns(3)
            vb, h, bb = c1.number_input("VB",0), c2.number_input("H",0), c3.number_input("BB",0)
            h2, h3, hr = c1.number_input("2B",0), c2.number_input("3B",0), c3.number_input("HR",0)
            pg, pp, ji, ip = c1.number_input("G",0), c2.number_input("P",0), c3.number_input("JI",0), c1.number_input("IP",0.0)
            if st.form_submit_button("Guardar"):
                if n in df_j["Nombre"].values:
                    df_j.loc[df_j["Nombre"]==n, ["VB","H","2B","3B","HR","BB","G","P","JI","IP"]] += [vb, h, h2, h3, hr, bb, pg, pp, ji, ip]
                else:
                    df_j = pd.concat([df_j, pd.DataFrame([{"Nombre":n,"Equipo":eq,"Categoria":cat,"VB":vb,"H":h,"2B":h2,"3B":h3,"HR":hr,"BB":bb,"G":pg,"P":pp,"JI":ji,"IP":ip}])], ignore_index=True)
                df_j.to_csv(J_FILE, index=False); st.success("Guardado"); st.rerun()
    with t2:
        with st.form("rg"):
            jor, v, cv = st.number_input("Jor",1), st.selectbox("Vis", df_e["Nombre"].unique() if not df_e.empty else [""]), st.number_input("C.V",0)
            h, ch = st.selectbox("Home", df_e["Nombre"].unique() if not df_e.empty else [""]), st.number_input("C.H",0)
            if st.form_submit_button("Guardar"):
                pd.concat([df_g, pd.DataFrame([{"Jornada":jor,"Visitante":v,"CV":cv,"HomeClub":h,"CH":ch}])], ignore_index=True).to_csv(G_FILE, index=False); st.rerun()

elif menu == "🗑️ BORRAR" and st.session_state.admin:
    sel = st.selectbox("Borrar:", sorted(df_j["Nombre"].unique()) if not df_j.empty else [""])
    if st.button("ELIMINAR"):
        df_j[df_j["Nombre"]!=sel].to_csv(J_FILE, index=False); st.rerun()

elif menu == "💾 RESPALDO" and st.session_state.admin:
    st.download_button("Descargar Jugadores", df_j.to_csv(index=False), "jugadores.csv")
