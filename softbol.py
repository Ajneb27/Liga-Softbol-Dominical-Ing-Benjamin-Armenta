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

df_j = cargar_csv(J_FILE, ["Nombre", "Equipo", "Categoria", "VB", "H", "2B", "3B", "HR", "G", "P"])
df_e = cargar_csv(E_FILE, ["Nombre", "Debut", "Fin", "Logo"])
df_g = cargar_csv(G_FILE, ["Jornada", "Visitante", "CV", "HomeClub", "CH"])
df_c = cargar_csv(C_FILE, ["Tipo", "Jornada", "Fecha", "Hora", "Visitante", "HomeClub", "Campo"])

# --- 3. BARRA LATERAL ---
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
        if st.button("❌ Cerrar Sesión"):
            st.session_state.admin = False
            st.rerun()

    st.divider()
    menu = st.radio("Secciones:", ["🏠 INICIO", "📊 STANDING", "🏆 LÍDERES", "📋 ROSTERS", "📜 HISTORIAL", "🏘️ EQUIPOS", "✍️ REGISTRAR", "🗑️ BORRAR", "💾 RESPALDO"])

# --- 4. SECCIONES ---

if menu == "🏠 INICIO":
    st.markdown(f"<h1 style='color:#d4af37;'>{NOMBRE_LIGA}</h1>", unsafe_allow_html=True)
    tab_reg, tab_play = st.tabs(["📅 TEMPORADA REGULAR", "🔥 PLAYOFFS"])
    with tab_reg:
        if not df_c.empty: st.dataframe(df_c[df_c["Tipo"] == "Regular"], hide_index=True, use_container_width=True)
        else: st.info("No hay calendario disponible.")
    with tab_play:
        playoffs = df_c[df_c["Tipo"] != "Regular"]
        if not playoffs.empty:
            c1, c2 = st.columns(2)
            c1.subheader("Semifinales"); c1.table(playoffs[playoffs["Tipo"] == "Semifinal"])
            c2.subheader("Gran Final"); c2.table(playoffs[playoffs["Tipo"] == "Final"])
        else: st.warning("Playoffs no programados.")

elif menu == "📊 STANDING":
    st.header("📊 Tabla de Posiciones")
    if not df_g.empty and not df_e.empty:
        stats = []
        for eq in df_e["Nombre"].unique():
            v, h = df_g[df_g["Visitante"] == eq], df_g[df_g["HomeClub"] == eq]
            g = len(v[v["CV"] > v["CH"]]) + len(h[h["CH"] > h["CV"]])
            p = len(v[v["CV"] < v["CH"]]) + len(h[h["CH"] < h["CV"]])
            stats.append({"Equipo": eq, "JJ": g+p, "G": g, "P": p, "AVG": round(g/(g+p), 3) if (g+p)>0 else 0})
        st.table(pd.DataFrame(stats).sort_values(by=["AVG", "G"], ascending=False))

elif menu == "🏆 LÍDERES":
    st.header("🥇 Líderes 2026")
    cat_f = st.selectbox("Categoría:", ["TODOS", "Novato", "Softbolista", "Refuerzo"])
    df_l = df_j.copy() if cat_f == "TODOS" else df_j[df_j["Categoria"] == cat_f].copy()
    df_l["AVG_NUM"] = (df_l["H"] / df_l["VB"]).fillna(0)
    df_l["AVG"] = df_l["AVG_NUM"].apply(lambda x: f"{x:.3f}")

    t_bat, t_pit = st.tabs(["⚾ BATEO", "🎯 PITCHEO"])
    with t_bat:
        c1, c2, c3 = st.columns(3)
        c1.write("### Average"); c1.dataframe(df_l[df_l["VB"]>0].nlargest(10,'AVG_NUM')[['Nombre','AVG']], hide_index=True)
        c2.write("### Hits"); c2.dataframe(df_l.nlargest(10,'H')[['Nombre','H']], hide_index=True)
        c3.write("### Home Runs"); c3.dataframe(df_l.nlargest(10,'HR')[['Nombre','HR']], hide_index=True)
        st.divider()
        c4, c5 = st.columns(2)
        c4.write("### Dobles (2B)"); c4.dataframe(df_l.nlargest(10,'2B')[['Nombre','2B']], hide_index=True)
        c5.write("### Triples (3B)"); c5.dataframe(df_l.nlargest(10,'3B')[['Nombre','3B']], hide_index=True)
    with t_pit:
        st.write("### Juegos Ganados")
        st.dataframe(df_l.nlargest(10,'G')[['Nombre','Equipo','G','P']], hide_index=True)

elif menu == "📋 ROSTERS":
    if not df_e.empty:
        eq_s = st.selectbox("Equipo:", df_e["Nombre"].unique())
        df_roster = df_j[df_j["Equipo"] == eq_s].copy()
        df_roster["AVG"] = (df_roster["H"] / df_roster["VB"]).fillna(0).apply(lambda x: f"{x:.3f}")
        st.dataframe(df_roster, use_container_width=True, hide_index=True)

elif menu == "📜 HISTORIAL":
    st.header("📜 Historial de Jugadores")
    j_sel = st.selectbox("Buscar Jugador:", sorted(df_j["Nombre"].unique()) if not df_j.empty else ["No hay jugadores"])
    
    if not df_j.empty and j_sel != "No hay jugadores":
        # Corregido: Usar .iloc[0] para obtener la serie de datos
        d = df_j[df_j["Nombre"] == j_sel].iloc[0]
        avg = d['H'] / d['VB'] if d['VB'] > 0 else 0
        
        st.subheader(f"Ficha Técnica: {d['Nombre']}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Equipo", d['Equipo'])
        c2.metric("Categoría", d['Categoria'])
        c3.metric("Average", f"{avg:.3f}")
        
        st.divider()
        col_b, col_p = st.columns(2)
        with col_b:
            st.write("### ⚾ Bateo")
            st.write(f"**VB:** {int(d['VB'])} | **H:** {int(d['H'])}")
            st.write(f"**2B:** {int(d['2B'])} | **3B:** {int(d['3B'])} | **HR:** {int(d['HR'])}")
        with col_p:
            st.write("### 🎯 Pitcheo")
            st.write(f"**Ganados:** {int(d['G'])}")
            st.write(f"**Perdidos:** {int(d['P'])}")

elif menu == "🏘️ EQUIPOS":
    st.header("🏘️ Equipos y Antigüedad")
    if st.session_state.admin:
        with st.form("nuevo_e"):
            n_e = st.text_input("Nombre del Equipo")
            a_d = st.number_input("Año de Debut", 1980, ANIO_ACTUAL, ANIO_ACTUAL)
            if st.form_submit_button("Registrar"):
                pd.concat([df_e, pd.DataFrame([{"Nombre":n_e, "Debut":a_d}])], ignore_index=True).to_csv(E_FILE, index=False)
                st.rerun()
    if not df_e.empty:
        df_resumen = df_e.copy()
        df_resumen["Antigüedad"] = ANIO_ACTUAL - df_resumen["Debut"]
        st.dataframe(df_resumen[["Nombre", "Debut", "Antigüedad"]], hide_index=True, use_container_width=True)

elif menu == "✍️ REGISTRAR":
    if st.session_state.admin:
        tj, tr, tc = st.tabs(["JUGADORES", "RESULTADOS", "CALENDARIO"])
        with tj:
            if not df_e.empty:
                with st.form("reg_j"):
                    nom = st.text_input("Nombre"); cat = st.selectbox("Cat", ["Novato", "Softbolista", "Refuerzo"])
                    eq = st.selectbox("Equipo", df_e["Nombre"].unique())
                    v1, v2, v3, v4, v5 = st.columns(5)
                    vb, h, d2, d3, hr = v1.number_input("VB",0), v2.number_input("H",0), v3.number_input("2B",0), v4.number_input("3B",0), v5.number_input("HR",0)
                    gp, pp = st.number_input("G",0), st.number_input("P",0)
                    if st.form_submit_button("Guardar"):
                        df_j = pd.concat([df_j[df_j["Nombre"] != nom], pd.DataFrame([{"Nombre":nom,"Equipo":eq,"Categoria":cat,"VB":vb,"H":h,"2B":d2,"3B":d3,"HR":hr,"G":gp,"P":pp}])], ignore_index=True)
                        df_j.to_csv(J_FILE, index=False); st.rerun()
            else: st.error("Registre un equipo primero.")
        # ... Resto de sub-tabs (tr, tc) se mantienen igual ...

elif menu == "🗑️ BORRAR":
    if st.session_state.admin:
        st.header("🗑️ Borrar Jugador Específico")
        if not df_j.empty:
            j_borrar = st.selectbox("Seleccione Jugador:", sorted(df_j["Nombre"].unique()))
            if st.button("Confirmar Borrado", type="primary"):
                df_j[df_j["Nombre"] != j_borrar].to_csv(J_FILE, index=False)
                st.success(f"{j_borrar} eliminado."); st.rerun()
    else: st.error("Acceso administrador requerido.")

elif menu == "💾 RESPALDO":
    if st.session_state.admin:
        st.download_button("Bajar Jugadores", df_j.to_csv(index=False), "jugadores.csv")
