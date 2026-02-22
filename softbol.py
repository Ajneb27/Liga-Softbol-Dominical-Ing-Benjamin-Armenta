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
                if c not in df.columns: df[c] = LOGO_DEFECTO if c == "Logo" else 0
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
    
    st.subheader("📅 Próximos Encuentros (Programación)")
    if not df_p.empty: st.table(df_p)
    else: st.info("No hay juegos programados.")
    st.image("https://images.unsplash.com", use_container_width=True)

elif menu == "📅 PROGRAMACIÓN":
    st.header("📅 Gestión del Calendario")
    if st.session_state.admin:
        with st.form("f_prog"):
            f, h = st.text_input("Fecha (Ej: Dom 22 Feb)"), st.text_input("Hora")
            v = st.selectbox("Visitante", df_e["Nombre"].unique()) if not df_e.empty else ""
            hc = st.selectbox("Home Club", df_e["Nombre"].unique()) if not df_e.empty else ""
            cam = st.text_input("Campo", "Principal")
            if st.form_submit_button("Programar"):
                new_p = pd.DataFrame([{"Fecha":f,"Hora":h,"Visitante":v,"HomeClub":hc,"Campo":cam}])
                df_p = pd.concat([df_p, new_p], ignore_index=True)
                df_p.to_csv(P_FILE, index=False); st.rerun()
        if not df_p.empty:
            sel = st.selectbox("Borrar juego:", df_p.index, format_func=lambda x: f"{df_p.at[x,'Visitante']} vs {df_p.at[x,'HomeClub']}")
            if st.button("Eliminar"):
                df_p.drop(sel).to_csv(P_FILE, index=False); st.rerun()
    st.table(df_p)

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
    min_vb = c1.number_input("Min VB (Bateo):", 0, 500, int(jor_max * 2.5))
    min_ip = c2.number_input("Min IP (Pitcheo):", 0, 500, int(jor_max * 2))
    
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
    st.header("📋 Rosters por Equipo")
    if not df_e.empty:
        c1, c2 = st.columns([3, 1])
        eq_sel = c1.selectbox("Seleccione Equipo:", df_e["Nombre"].unique())
        logo_data = df_e[df_e["Nombre"] == eq_sel]["Logo"]
        logo_url = logo_data.iloc[0] if not logo_data.empty else LOGO_DEFECTO
        c2.image(logo_url, width=100)
        
        df_r = df_j[df_j["Equipo"] == eq_sel].copy()
        if not df_r.empty:
            df_r["HT"] = df_r["H"] + df_r["2B"] + df_r["3B"] + df_r["HR"]
            df_r["TB"] = df_r["VB"] + df_r["BB"]
            df_r["AVG"] = (df_r["HT"] / df_r["VB"]).fillna(0).map('{:.3f}'.format)
            st.dataframe(df_r[["Nombre", "Categoria", "TB", "VB", "H", "2B", "3B", "HR", "BB", "G", "P", "JI", "IP", "AVG"]], hide_index=True, use_container_width=True)

elif menu == "📜 HISTORIAL":
    st.header("📜 Ficha de Jugador")
    if not df_j.empty:
        js = st.selectbox("Buscar Jugador:", sorted(df_j["Nombre"].unique()))
        d = df_j[df_j["Nombre"]==js].iloc[0]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Equipo", d['Equipo']); c2.metric("VB", int(d['VB'])); c3.metric("TB (Apariciones)", int(d['VB']+d['BB'])); c4.metric("JI", int(d['JI']))
        st.divider()
        col_a, col_b = st.columns(2)
        with col_a:
            st.write("### ⚾ Bateo")
            st.write(f"**Hits:** {int(d['H'])} | **Dobles:** {int(d['2B'])} | **Triples:** {int(d['3B'])} | **Jonrones:** {int(d['HR'])} | **BB:** {int(d['BB'])}")
            avg = (d['H']+d['2B']+d['3B']+d['HR'])/d['VB'] if d['VB']>0 else 0
            st.metric("Promedio (AVG)", f"{avg:.3f}")
        with col_b:
            st.write("### 🎯 Pitcheo")
            st.write(f"**Ganados:** {int(d['G'])} | **Perdidos:** {int(d['P'])} | **Iniciados:** {int(d['JI'])} | **Entradas (IP):** {d['IP']}")

elif menu == "🏘️ EQUIPOS":
    st.header("🏘️ Gestión de Equipos")
    if st.session_state.admin:
        t_list, t_edit = st.tabs(["Lista y Nuevo", "Editar Logo/Nombre"])
        with t_list:
            with st.form("n_eq"):
                n, l = st.text_input("Nombre"), st.text_input("Logo URL (Link)", LOGO_DEFECTO)
                if st.form_submit_button("Añadir"):
                    df_e = pd.concat([df_e, pd.DataFrame([{"Nombre":n,"Debut":ANIO_ACTUAL,"Logo":l}])], ignore_index=True)
                    df_e.to_csv(E_FILE, index=False); st.rerun()
        with t_edit:
            if not df_e.empty:
                sel = st.selectbox("Seleccionar Equipo:", df_e["Nombre"].unique())
                idx = df_e[df_e["Nombre"] == sel].index[0]
                with st.form("e_eq"):
                    en = st.text_input("Nombre", df_e.at[idx, "Nombre"])
                    el = st.text_input("Logo URL", df_e.at[idx, "Logo"])
                    if st.form_submit_button("Actualizar"):
                        df_e.at[idx, "Nombre"], df_e.at[idx, "Logo"] = en, el
                        df_e.to_csv(E_FILE, index=False); st.rerun()
    st.dataframe(df_e, hide_index=True)

elif menu == "✍️ REGISTRAR" and st.session_state.admin:
    t1, t2 = st.tabs(["👤 JUGADOR", "⚾ RESULTADO"])
    with t1:
        with st.form("rj"):
            n, eq, cat = st.text_input("Nombre"), st.selectbox("Equipo", df_e["Nombre"].unique() if not df_e.empty else [""]), st.text_input("Categoría")
            c1, c2, c3 = st.columns(3)
            vb, h, bb = c1.number_input("VB",0), c2.number_input("H",0), c3.number_input("BB",0)
            h2, h3, hr = c1.number_input("2B",0), c2.number_input("3B",0), c3.number_input("HR",0)
            pg, pp, ji, ip = c1.number_input("G",0), c2.number_input("P",0), c3.number_input("JI",0), c1.number_input("IP",0.0)
            if st.form_submit_button("Guardar Datos"):
                if n in df_j["Nombre"].values:
                    df_j.loc[df_j["Nombre"]==n, ["VB","H","2B","3B","HR","BB","G","P","JI","IP"]] += [vb, h, h2, h3, hr, bb, pg, pp, ji, ip]
                else:
                    df_j = pd.concat([df_j, pd.DataFrame([{"Nombre":n,"Equipo":eq,"Categoria":cat,"VB":vb,"H":h,"2B":h2,"3B":h3,"HR":hr,"BB":bb,"G":pg,"P":pp,"JI":ji,"IP":ip}])], ignore_index=True)
                df_j.to_csv(J_FILE, index=False); st.success("Guardado"); st.rerun()
    with t2:
        with st.form("rg"):
            jor, v, cv = st.number_input("Jornada",1), st.selectbox("Visitante", df_e["Nombre"].unique()), st.number_input("Carreras Vis",0)
            h, ch = st.selectbox("Home Club", df_e["Nombre"].unique()), st.number_input("Carreras Home",0)
            if st.form_submit_button("Guardar Juego"):
                pd.concat([df_g, pd.DataFrame([{"Jornada":jor,"Visitante":v,"CV":cv,"HomeClub":h,"CH":ch}])], ignore_index=True).to_csv(G_FILE, index=False); st.rerun()

elif menu == "🗑️ BORRAR" and st.session_state.admin:
    sel = st.selectbox("Eliminar Jugador:", sorted(df_j["Nombre"].unique()) if not df_j.empty else [""])
    if st.button("CONFIRMAR ELIMINACIÓN"):
        df_j[df_j["Nombre"]!=sel].to_csv(J_FILE, index=False); st.rerun()

elif menu == "💾 RESPALDO" and st.session_state.admin:
    st.header("💾 Control de Datos")
    with st.expander("🧨 NUEVA TEMPORADA (RESET)"):
        st.warning("Escriba la clave para borrar jugadores, juegos y programación.")
        confirm = st.text_input("Clave de confirmación:")
        if st.button("RESET TOTAL"):
            if confirm == "RESET2026":
                for f in [J_FILE, G_FILE, P_FILE]:
                    if os.path.exists(f): os.remove(f)
                st.success("Temporada reseteada."); st.rerun()
    st.divider()
    st.download_button("Descargar Jugadores", df_j.to_csv(index=False), "jugadores.csv")
    st.download_button("Descargar Equipos", df_e.to_csv(index=False), "equipos.csv")
