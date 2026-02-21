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

# --- 2. MOTOR DE DATOS (PROTECCIÓN TOTAL) ---
def cargar_jugadores():
    cols_obligatorias = ["Nombre", "Equipo", "Categoria", "VB", "H", "2B", "3B", "HR", "G", "P"]
    if os.path.exists(JUGADORES_FILE):
        try:
            df = pd.read_csv(JUGADORES_FILE)
            for c in cols_obligatorias:
                if c not in df.columns: df[c] = "Softbolista" if c == "Categoria" else 0
        except: df = pd.DataFrame(columns=cols_obligatorias)
    else: df = pd.DataFrame(columns=cols_obligatorias)
    
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

# --- 3. INICIALIZACIÓN Y ESTILO ---
st.set_page_config(page_title=NOMBRE_LIGA, layout="wide", page_icon="🥎")

# CORRECCIÓN DEL ERROR DE ESTILO (unsafe_allow_html)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .gold-header { color: #d4af37; font-weight: bold; border-bottom: 3px solid #d4af37; padding-bottom: 10px; margin-bottom: 20px; }
    .stMetric { background-color: white; border-radius: 10px; border-left: 5px solid #d4af37; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

if 'admin' not in st.session_state: st.session_state.admin = False

df_j = cargar_jugadores()
df_e = cargar_equipos()

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.title(f"🏆 {NOMBRE_LIGA}")
    if not st.session_state.admin:
        with st.expander("🔐 Acceso Administrador"):
            u = st.text_input("Usuario"); p = st.text_input("Clave", type="password")
            if st.button("Entrar"):
                if u == "admin" and p == "123": st.session_state.admin = True; st.rerun()
    else:
        st.success("Modo Admin: ACTIVADO")
        if st.button("Cerrar Sesión"): st.session_state.admin = False; st.rerun()
    
    st.divider()
    menu = st.radio("Secciones:", ["🏠 INICIO", "🏆 LÍDERES", "📋 ROSTERS", "📜 HISTORIAL", "🏘️ EQUIPOS", "✍️ REGISTRAR", "🗑️ BORRAR", "💾 RESPALDO"])

# --- 5. SECCIÓN 🏆 LÍDERES (ACUMULADOS) ---
if menu == "🏆 LÍDERES":
    st.markdown("<h1 class='gold-header'>🥇 Cuadro de Honor Departamental</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["⚾ BATEO ACUMULADO", "🎯 PITCHEO ACUMULADO"])
    
    with t1:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Hits (H)"); st.dataframe(df_j.nlargest(10, 'H')[['Nombre', 'Equipo', 'H']], hide_index=True)
            st.subheader("Dobles (2B)"); st.dataframe(df_j.nlargest(10, '2B')[['Nombre', 'Equipo', '2B']], hide_index=True)
        with c2:
            st.subheader("Home Runs (HR)"); st.dataframe(df_j.nlargest(10, 'HR')[['Nombre', 'Equipo', 'HR']], hide_index=True)
            st.subheader("Triples (3B)"); st.dataframe(df_j.nlargest(10, '3B')[['Nombre', 'Equipo', '3B']], hide_index=True)
    with t2:
        c1, c2 = st.columns(2)
        with c1: st.subheader("Ganados (G)"); st.dataframe(df_j.sort_values('G', ascending=False).head(10)[['Nombre', 'Equipo', 'G']], hide_index=True)
        with c2: st.subheader("Perdidos (P)"); st.dataframe(df_j.sort_values('P', ascending=False).head(10)[['Nombre', 'Equipo', 'P']], hide_index=True)

# --- 6. SECCIÓN 📜 HISTORIAL (ACUMULADO TOTAL) ---
elif menu == "📜 HISTORIAL":
    st.markdown("<h1 class='gold-header'>📜 Historial de Carrera</h1>", unsafe_allow_html=True)
    if not df_j.empty:
        j_s = st.selectbox("Seleccionar Jugador:", sorted(df_j["Nombre"].unique().tolist()))
        d = df_j[df_j["Nombre"] == j_s].iloc[0] # Uso de iloc[0] para evitar errores
        
        st.header(f"Ficha Técnica: {d['Nombre']}")
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Equipo", d['Equipo'])
        col_m2.metric("Categoría", d['Categoria'])
        avg = (d['H'] / d['VB']) if d['VB'] > 0 else 0
        col_m3.metric("Promedio (AVG)", f"{avg:.3f}")
        
        st.divider()
        st.write("### 📊 Totales en la Liga")
        c1, c2 = st.columns(2)
        with c1:
            st.info(f"**BATEO:** VB: {int(d['VB'])} | H: {int(d['H'])} | 2B: {int(d['2B'])} | 3B: {int(d['3B'])} | HR: {int(d['HR'])}")
        with c2:
            st.success(f"**PITCHEO:** Juegos Ganados: {int(d['G'])} | Juegos Perdidos: {int(d['P'])}")
    else: st.info("No hay datos de jugadores.")

# --- 7. SECCIÓN ✍️ REGISTRAR (CALCULADORA) ---
elif menu == "✍️ REGISTRAR":
    if st.session_state.admin:
        st.header("✍️ Anotación de Estadísticas")
        sel = st.selectbox("Jugador:", ["NUEVO JUGADOR"] + sorted(df_j["Nombre"].unique().tolist()))
        if 'vals' not in st.session_state or st.session_state.get('last_sel') != sel:
            if sel != "NUEVO JUGADOR": st.session_state.vals = df_j[df_j["Nombre"] == sel].iloc[0].to_dict()
            else: st.session_state.vals = {"Nombre": "", "Equipo": None, "Categoria": "Softbolista", "VB": 0, "H": 0, "2B": 0, "3B": 0, "HR": 0, "G": 0, "P": 0}
            st.session_state.last_sel = sel

        st.write("Sumar hoy:")
        c1, c2, c3, c4 = st.columns(4)
        if c1.button("H (+1)"): st.session_state.vals["H"]+=1; st.session_state.vals["VB"]+=1; st.rerun()
        if c2.button("HR (+1)"): st.session_state.vals["H"]+=1; st.session_state.vals["HR"]+=1; st.session_state.vals["VB"]+=1; st.rerun()
        if c3.button("G (+1)"): st.session_state.vals["G"]+=1; st.rerun()
        if c4.button("P (+1)"): st.session_state.vals["P"]+=1; st.rerun()

        with st.form("f_reg", clear_on_submit=True):
            nom_f = st.text_input("Nombre:", value=st.session_state.vals["Nombre"])
            eq_f = st.selectbox("Equipo:", df_e[df_e["Fin"] == 0]["Nombre"].unique() if not df_e.empty else ["Crea equipo"])
            v1, v2, v3, v4, v5 = st.columns(5)
            vb = v1.number_input("VB", value=int(st.session_state.vals["VB"])); h = v2.number_input("H", value=int(st.session_state.vals["H"]))
            d2 = v3.number_input("2B", value=int(st.session_state.vals["2B"])); d3 = v4.number_input("3B", value=int(st.session_state.vals["3B"]))
            hr = v5.number_input("HR", value=int(st.session_state.vals["HR"]))
            g_f = st.number_input("G", value=int(st.session_state.vals["G"])); p_f = st.number_input("P", value=int(st.session_state.vals["P"]))
            if st.form_submit_button("💾 GUARDAR"):
                df_j = df_j[df_j["Nombre"] != nom_f]
                nueva = pd.DataFrame([{"Nombre": nom_f, "Equipo": eq_f, "Categoria": st.session_state.vals["Categoria"], "VB": vb, "H": h, "2B": d2, "3B": d3, "HR": hr, "G": g_f, "P": p_f}])
                pd.concat([df_j, nueva], ignore_index=True).to_csv(JUGADORES_FILE, index=False); st.success("¡Guardado!"); st.rerun()
    else: st.warning("Solo administradores.")

# --- SECCIONES RESTANTES ---
elif menu == "🏘️ EQUIPOS":
    if st.session_state.admin:
        with st.form("eq"):
            n=st.text_input("Equipo:"); d=st.number_input("Debut:", 2024, 2026, 2024); f=st.number_input("Fin:", 0, 2026, 0)
            if st.form_submit_button("Añadir"):
                pd.concat([df_e, pd.DataFrame([{"Nombre": n, "Debut": d, "Fin": f}])], ignore_index=True).to_csv(EQUIPOS_FILE, index=False); st.rerun()
    if not df_e.empty:
        df_v = df_e.copy()
        df_v["Temporadas"] = df_v.apply(lambda r: (r['Fin'] if r['Fin']>0 else ANIO_ACTUAL) - r['Debut'] + 1, axis=1)
        st.table(df_v.sort_values("Temporadas", ascending=False))

elif menu == "💾 RESPALDO":
    st.download_button("📥 Descargar", df_j.to_csv(index=False), "respaldo.csv")
    f = st.file_uploader("Subir CSV", type="csv")
    if f: pd.read_csv(f).to_csv(JUGADORES_FILE, index=False); st.rerun()

elif menu == "🏠 INICIO":
    st.title(NOMBRE_LIGA)
    st.write(f"Uniendo a la familia deportiva desde Agosto de {ANIO_INICIO_LIGA}.")

elif menu == "📋 ROSTERS":
    if not df_e.empty:
        eq = st.selectbox("Equipo:", df_e[df_e["Fin"] == 0]["Nombre"].unique())
        st.dataframe(df_j[df_j["Equipo"] == eq], use_container_width=True)

elif menu == "🗑️ BORRAR":
    if st.session_state.admin:
        j_del = st.selectbox("Borrar:", [""] + sorted(df_j["Nombre"].tolist()))
        if st.button("❌ Eliminar") and j_del != "":
            df_j = df_j[df_j["Nombre"] != j_del]; df_j.to_csv(JUGADORES_FILE, index=False); st.rerun()
