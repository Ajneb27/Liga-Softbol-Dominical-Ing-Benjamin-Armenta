import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN E IDENTIDAD ---
NOMBRE_LIGA = "LIGA DE SOFTBOL DOMINICAL"
ANIO_INICIO_LIGA = 2024
ANIO_ACTUAL = 2026

DATA_DIR = "liga_softbol_final_2026"
if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)

JUGADORES_FILE = os.path.join(DATA_DIR, "jugadores_master.csv")
EQUIPOS_FILE = os.path.join(DATA_DIR, "equipos_master.csv")

# --- 2. MOTOR DE DATOS ---
def cargar_jugadores():
    cols = ["Nombre", "Equipo", "Categoria", "VB", "H", "2B", "3B", "HR", "G", "P"]
    if os.path.exists(JUGADORES_FILE):
        try:
            df = pd.read_csv(JUGADORES_FILE)
            for c in cols:
                if c not in df.columns: df[c] = "Softbolista" if c == "Categoria" else 0
        except: df = pd.DataFrame(columns=cols)
    else: df = pd.DataFrame(columns=cols)
    df = df.dropna(subset=['Nombre'])
    for c in ["VB", "H", "2B", "3B", "HR", "G", "P"]:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
    return df

def cargar_equipos():
    if os.path.exists(EQUIPOS_FILE):
        df = pd.read_csv(EQUIPOS_FILE)
        if "Debut" not in df.columns: df["Debut"] = ANIO_INICIO_LIGA
        if "Fin" not in df.columns: df["Fin"] = 0
        return df
    return pd.DataFrame(columns=["Nombre", "Debut", "Fin"])

# --- 3. INICIALIZACIÓN ---
st.set_page_config(page_title=NOMBRE_LIGA, layout="wide", page_icon="🥎")
if 'admin' not in st.session_state: st.session_state.admin = False

df_j = cargar_jugadores()
df_e = cargar_equipos()

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.title(f"🥎 {NOMBRE_LIGA}")
    if not st.session_state.admin:
        with st.expander("🔐 Acceso Admin"):
            u = st.text_input("Usuario"); p = st.text_input("Clave", type="password")
            if st.button("Entrar"):
                if u == "admin" and p == "123": st.session_state.admin = True; st.rerun()
    else:
        st.success("Admin Activo")
        if st.button("Cerrar Sesión"): st.session_state.admin = False; st.rerun()
    
    st.divider()
    menu = st.radio("Navegación:", ["🏠 INICIO / PORTADA", "🏆 LÍDERES", "📋 ROSTERS", "📜 HISTORIAL JUGADOR", "🏘️ EQUIPOS", "✍️ REGISTRAR", "💾 RESPALDO"])

# --- 5. SECCIÓN 🏠 INICIO / PORTADA ---
if menu == "🏠 INICIO / PORTADA":
    col_logo, col_titulo = st.columns([1, 3])
    
    with col_logo:
        # Aquí puedes poner el link de tu logo real o usar un placeholder
        st.image("https://cdn-icons-png.flaticon.com", width=150)
    
    with col_titulo:
        st.title(f"Bienvenido a la {NOMBRE_LIGA}")
        st.subheader("Compromiso, Deporte y Familia")

    st.divider()
    
    col_hist, col_info = st.columns(2)
    
    with col_hist:
        st.header("📜 Nuestra Historia")
        st.write(f"""
        Fundada en **Agosto de {ANIO_INICIO_LIGA}**, la **{NOMBRE_LIGA}** nació con el firme propósito de 
        fomentar la convivencia sana y la competencia deportiva de alto nivel entre amigos y familias.
        
        Lo que empezó como una reunión dominical de entusiastas, hoy se ha convertido en una de las ligas 
        más respetadas de la región, destacando por su organización, transparencia estadística y el 
        gran nivel de sus refuerzos y novatos por igual.
        """)
        
    with col_info:
        st.header("📊 Resumen de la Liga")
        c1, c2 = st.columns(2)
        c1.metric("Equipos Registrados", len(df_e))
        c2.metric("Jugadores Activos", len(df_j))
        
        st.info("📅 ¡Te esperamos cada domingo en el diamante para vivir la pasión del softbol!")

# --- 6. SECCIÓN 🏆 LÍDERES ---
elif menu == "🏆 LÍDERES":
    st.header("🥇 Cuadro de Honor Departamental")
    t1, t2 = st.tabs(["⚾ Bateo", "🎯 Pitcheo"])
    with t1:
        c1, c2 = st.columns(2)
        c1.subheader("Hits (H)"); c1.table(df_j.nlargest(10, 'H')[['Nombre', 'H', 'Equipo']])
        c1.subheader("Home Runs (HR)"); c1.table(df_j.nlargest(10, 'HR')[['Nombre', 'HR', 'Equipo']])
        c2.subheader("Dobles (2B)"); c2.table(df_j.nlargest(10, '2B')[['Nombre', '2B', 'Equipo']])
        c2.subheader("Triples (3B)"); c2.table(df_j.nlargest(10, '3B')[['Nombre', '3B', 'Equipo']])
    with t2:
        c1, c2 = st.columns(2)
        c1.subheader("Ganados (G)"); c1.table(df_j.sort_values('G', ascending=False).head(10)[['Nombre', 'G', 'Equipo']])
        c2.subheader("Perdidos (P)"); c2.table(df_j.sort_values('P', ascending=False).head(10)[['Nombre', 'P', 'Equipo']])

# --- 7. SECCIÓN 🏘️ EQUIPOS (TRAYECTORIA) ---
elif menu == "🏘️ EQUIPOS":
    st.header("🏘️ Equipos y Trayectoria")
    if st.session_state.admin:
        with st.form("eq_f", clear_on_submit=True):
            n=st.text_input("Equipo:"); d=st.number_input("Debut:", 2024, ANIO_ACTUAL, 2024); f=st.number_input("Retiro (0 si activo):", 0, ANIO_ACTUAL, 0)
            if st.form_submit_button("Añadir"):
                df_e = df_e[df_e["Nombre"] != n]
                df_e = pd.concat([df_e, pd.DataFrame([{"Nombre": n, "Debut": d, "Fin": f}])], ignore_index=True)
                df_e.to_csv(EQUIPOS_FILE, index=False); st.rerun()
    
    if not df_e.empty:
        df_v = df_e.copy()
        df_v["Temporadas"] = df_v.apply(lambda r: (r['Fin'] if r['Fin']>0 else ANIO_ACTUAL) - r['Debut'] + 1, axis=1)
        df_v["Estatus"] = df_v["Fin"].apply(lambda x: "🟢 Activo" if x == 0 else f"🔴 Retirado ({x})")
        st.table(df_v.sort_values("Temporadas", ascending=False)[["Nombre", "Debut", "Estatus", "Temporadas"]])

# --- 8. SECCIÓN ✍️ REGISTRAR ---
elif menu == "✍️ REGISTRAR":
    if st.session_state.admin:
        st.header("✍️ Anotación de Juego")
        sel = st.selectbox("Elegir Jugador:", ["NUEVO JUGADOR"] + sorted(df_j["Nombre"].unique().tolist()))
        if 'vals' not in st.session_state or st.session_state.get('last_sel') != sel:
            if sel != "NUEVO JUGADOR": st.session_state.vals = df_j[df_j["Nombre"] == sel].iloc.to_dict()
            else: st.session_state.vals = {"Nombre": "", "Equipo": None, "Categoria": "Softbolista", "VB": 0, "H": 0, "2B": 0, "3B": 0, "HR": 0, "G": 0, "P": 0}
            st.session_state.last_sel = sel

        c1, c2, c3, c4 = st.columns(4)
        if c1.button("H (+1)"): st.session_state.vals["H"]+=1; st.session_state.vals["VB"]+=1; st.rerun()
        if c2.button("HR (+1)"): st.session_state.vals["H"]+=1; st.session_state.vals["HR"]+=1; st.session_state.vals["VB"]+=1; st.rerun()
        if c3.button("G (+1)"): st.session_state.vals["G"]+=1; st.rerun()
        if c4.button("P (+1)"): st.session_state.vals["P"]+=1; st.rerun()

        with st.form("f_reg", clear_on_submit=True):
            nom_f = st.text_input("Nombre:", value=st.session_state.vals["Nombre"])
            eq_f = st.selectbox("Equipo:", df_e[df_e["Fin"] == 0]["Nombre"].unique() if not df_e.empty else ["Crea equipo"])
            cat_f = st.radio("Categoría:", ["Novato", "Softbolista", "Refuerzo"], index=["Novato", "Softbolista", "Refuerzo"].index(st.session_state.vals["Categoria"]))
            v1, v2, v3, v4, v5 = st.columns(5)
            vb = v1.number_input("VB", value=int(st.session_state.vals["VB"]))
            h = v2.number_input("H", value=int(st.session_state.vals["H"]))
            d2 = v3.number_input("2B", value=int(st.session_state.vals["2B"]))
            d3 = v4.number_input("3B", value=int(st.session_state.vals["3B"]))
            hr = v5.number_input("HR", value=int(st.session_state.vals["HR"]))
            g_f = st.number_input("G", value=int(st.session_state.vals["G"]))
            p_f = st.number_input("P", value=int(st.session_state.vals["P"]))
            if st.form_submit_button("💾 GUARDAR"):
                df_j = df_j[df_j["Nombre"] != nom_f]
                nueva = pd.DataFrame([{"Nombre": nom_f, "Equipo": eq_f, "Categoria": cat_f, "VB": vb, "H": h, "2B": d2, "3B": d3, "HR": hr, "G": g_f, "P": p_f}])
                pd.concat([df_j, nueva], ignore_index=True).to_csv(JUGADORES_FILE, index=False); st.success("Guardado"); st.rerun()

# --- 9. HISTORIAL ACUMULADO ---
elif menu == "📜 HISTORIAL JUGADOR":
    st.header("📜 Historial y Ficha del Jugador")
    if not df_j.empty:
        j_s = st.selectbox("Selecciona Jugador:", sorted(df_j["Nombre"].unique().tolist()))
        d = df_j[df_j["Nombre"] == j_s].iloc
        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("Equipo", d['Equipo']); c2.metric("Categoría", d['Categoria'])
        avg = (d['H'] / d['VB']) if d['VB'] > 0 else 0
        c3.metric("AVG Acumulado", f"{avg:.3f}")
        st.write(f"**Bateo Carrera:** VB: {int(d['VB'])} | H: {int(d['H'])} | 2B: {int(d['2B'])} | 3B: {int(d['3B'])} | HR: {int(d['HR'])}")
        st.write(f"**Pitcheo Carrera:** G: {int(d['G'])} | P: {int(d['P'])}")

# --- 10. RESPALDO Y ROSTERS ---
elif menu == "📋 ROSTERS":
    if not df_e.empty:
        eq = st.selectbox("Equipo:", df_e[df_e["Fin"] == 0]["Nombre"].unique())
        st.dataframe(df_j[df_j["Equipo"] == eq], use_container_width=True)

elif menu == "💾 RESPALDO":
    st.download_button("📥 Descargar", df_j.to_csv(index=False), "respaldo_liga.csv")
    f = st.file_uploader("Subir", type="csv")
    if f: pd.read_csv(f).to_csv(JUGADORES_FILE, index=False); st.rerun()
