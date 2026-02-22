import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN E IDENTIDAD 2026 ---
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
                    df[c] = ANIO_ACTUAL if c == "Debut" else 0
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
        st.subheader("📥 Cargar CSV")
        t_sub = st.selectbox("Archivo:", ["Jugadores", "Equipos", "Calendario", "Resultados"])
        arc_sub = st.file_uploader(f"Subir CSV", type="csv")
        if arc_sub and st.button("🚀 Guardar"):
            dest = {"Jugadores": J_FILE, "Equipos": E_FILE, "Calendario": C_FILE, "Resultados": G_FILE}
            pd.read_csv(arc_sub).to_csv(dest[t_sub], index=False)
            st.success("Actualizado"); st.rerun()
        st.divider()
        if st.button("❌ Cerrar Sesión"):
            st.session_state.admin = False
            st.rerun()

    st.divider()
    menu = st.radio("Secciones:", ["🏠 INICIO", "📊 STANDING", "🏆 LÍDERES", "📋 ROSTERS", "📜 HISTORIAL", "🏘️ EQUIPOS", "✍️ REGISTRAR", "🗑️ BORRAR", "💾 RESPALDO"])

# Carga de datos
df_j = cargar_csv(J_FILE, ["Nombre", "Equipo", "Categoria", "VB", "H", "2B", "3B", "HR", "BB", "G", "P"])
df_e = cargar_csv(E_FILE, ["Nombre", "Debut"])
df_g = cargar_csv(G_FILE, ["Jornada", "Visitante", "CV", "HomeClub", "CH"])
df_c = cargar_csv(C_FILE, ["Tipo", "Jornada", "Fecha", "Hora", "Visitante", "HomeClub", "Campo"])

# --- 4. SECCIONES ---

if menu == "🏠 INICIO":
    st.markdown(f"<h1>{NOMBRE_LIGA} 2026</h1>", unsafe_allow_html=True)
    if not df_c.empty:
        st.subheader("Próximos Juegos")
        st.dataframe(df_c, hide_index=True, use_container_width=True)
    else: st.info("No hay juegos programados.")

elif menu == "📊 STANDING":
    st.header("📊 Tabla de Posiciones 2026")
    if not df_g.empty and not df_e.empty:
        res = []
        for eq in df_e["Nombre"].unique():
            # Juegos como Visitante
            v = df_g[df_g["Visitante"] == eq]
            # Juegos como Home Club
            h = df_g[df_g["HomeClub"] == eq]
            
            ganados = len(v[v["CV"] > v["CH"]]) + len(h[h["CH"] > h["CV"]])
            perdidos = len(v[v["CV"] < v["CH"]]) + len(h[h["CH"] < h["CV"]])
            cf = v["CV"].sum() + h["CH"].sum() # Carreras a Favor
            cc = v["CH"].sum() + h["CV"].sum() # Carreras en Contra
            
            res.append({
                "Equipo": eq, "JJ": ganados + perdidos, "G": ganados, "P": perdidos,
                "AVG": round(ganados/(ganados+perdidos), 3) if (ganados+perdidos) > 0 else 0,
                "CF": cf, "CC": cc, "DIF": cf - cc
            })
        
        st.table(pd.DataFrame(res).sort_values(by=["AVG", "DIF", "G"], ascending=False))
    else: st.warning("No hay resultados suficientes para el Standing.")

elif menu == "🏆 LÍDERES":
    st.header("🥇 Líderes de la Temporada")
    jor_max = df_g["Jornada"].max() if not df_g.empty else 1
    if st.session_state.admin:
        with st.expander("⚙️ AJUSTES DE FILTRO"):
            min_vb = st.slider("Mínimo VB (Bateo):", 0, 100, int(jor_max * 3.1))
            min_dec = st.slider("Mínimo G+P (Pitcheo):", 0, 20, 1)
    else:
        min_vb, min_dec = int(jor_max * 3), 1

    df_l = df_j.copy()
    df_l["AVG_N"] = (df_l["H"] / df_l["VB"]).fillna(0)
    # Cálculo de Bases Totales (TB)
    df_l["TB"] = (df_l["H"] - df_l["2B"] - df_l["3B"] - df_l["HR"]) + (df_l["2B"]*2) + (df_l["3B"]*3) + (df_l["HR"]*4)
    
    t1, t2 = st.tabs(["⚾ BATEO", "🎯 PITCHEO"])
    with t1:
        c1, c2, c3 = st.columns(3)
        c1.write("### AVG"); c1.dataframe(df_l[df_l["VB"] >= min_vb].nlargest(10, 'AVG_N')[['Nombre', 'H', 'VB']], hide_index=True)
        c2.write("### Hits (H)"); c2.dataframe(df_l.nlargest(10, 'H')[['Nombre', 'H']], hide_index=True)
        c3.write("### Bases Totales (TB)"); c3.dataframe(df_l.nlargest(10, 'TB')[['Nombre', 'TB']], hide_index=True)
        st.divider()
        c4, c5, c6 = st.columns(3)
        c4.write("### Home Runs"); c4.dataframe(df_l.nlargest(10, 'HR')[['Nombre', 'HR']], hide_index=True)
        c5.write("### Bases x Bola (BB)"); c5.dataframe(df_l.nlargest(10, 'BB')[['Nombre', 'BB']], hide_index=True)
        c6.write("### Extrabases (2B+3B)"); c6.dataframe(df_l.nlargest(10, '2B')[['Nombre', '2B', '3B']], hide_index=True)

elif menu == "📜 HISTORIAL":
    st.header("📜 Ficha de Jugador")
    if not df_j.empty:
        js = st.selectbox("Seleccione Jugador:", sorted(df_j["Nombre"].unique()))
        d = df_j[df_j["Nombre"]==js].iloc[0]
        tb_calc = (d['H'] - d['2B'] - d['3B'] - d['HR']) + (d['2B']*2) + (d['3B']*3) + (d['HR']*4)
        c1, c2, c3 = st.columns(3)
        c1.metric("Promedio (AVG)", f"{(d['H']/d['VB'] if d['VB']>0 else 0):.3f}")
        c2.metric("Bases Totales (TB)", int(tb_calc))
        c3.metric("Bases x Bola (BB)", int(d['BB']))

elif menu == "✍️ REGISTRAR":
    if st.session_state.admin:
        tj, tr = st.tabs(["JUGADORES", "RESULTADOS"])
        with tj:
            with st.form("rj"):
                n = st.text_input("Nombre")
                e = st.selectbox("Equipo", df_e["Nombre"].unique()) if not df_e.empty else "N/A"
                v1, v2, v3, v4 = st.columns(4)
                vb, h, bb = v1.number_input("VB",0), v2.number_input("H (TOTAL)",0), v3.number_input("BB",0)
                d2, d3, hr = v1.number_input("2B",0), v2.number_input("3B",0), v3.number_input("HR",0)
                if st.form_submit_button("Guardar"):
                    df_j = pd.concat([df_j[df_j["Nombre"]!=n], pd.DataFrame([{"Nombre":n,"Equipo":e,"VB":vb,"H":h,"2B":d2,"3B":d3,"HR":hr,"BB":bb}])], ignore_index=True)
                    df_j.to_csv(J_FILE, index=False); st.rerun()
        with tr:
            with st.form("rs"):
                j, v, cv = st.number_input("Jornada",1), st.selectbox("Visitante", df_e["Nombre"].unique()), st.number_input("Carreras Vis",0)
                hc, ch = st.selectbox("Home Club", df_e["Nombre"].unique()), st.number_input("Carreras HC",0)
                if st.form_submit_button("Guardar Resultado"):
                    pd.concat([df_g, pd.DataFrame([{"Jornada":j,"Visitante":v,"CV":cv,"HomeClub":hc,"CH":ch}])], ignore_index=True).to_csv(G_FILE, index=False); st.rerun()

elif menu == "🗑️ BORRAR":
    if st.session_state.admin:
        sel = st.selectbox("Eliminar jugador:", sorted(df_j["Nombre"].unique()))
        if st.button("Borrar Permanentemente", type="primary"):
            df_j[df_j["Nombre"]!=sel].to_csv(J_FILE, index=False); st.rerun()

elif menu == "💾 RESPALDO":
    if st.session_state.admin:
        st.download_button("Descargar Jugadores 2026", df_j.to_csv(index=False), "jugadores_2026.csv")
        st.download_button("Descargar Resultados 2026", df_g.to_csv(index=False), "resultados_2026.csv")
