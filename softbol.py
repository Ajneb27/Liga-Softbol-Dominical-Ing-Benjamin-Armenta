import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN HISTÓRICA ---
# La liga inició en Agosto 2024. Estamos en Febrero 2026.
ANIO_INICIO_LIGA = 2024
ANIO_ACTUAL = 2026
TEMPORADA_LABEL = "2024-2026" 

DATA_DIR = "liga_softbol_historia"
if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)

JUGADORES_FILE = os.path.join(DATA_DIR, "jugadores.csv")
EQUIPOS_FILE = os.path.join(DATA_DIR, "equipos.csv")

# --- 2. MOTOR DE DATOS (PROTECCIÓN DE DEPARTAMENTOS) ---
def cargar_jugadores():
    cols = ["Nombre", "Equipo", "VB", "H", "2B", "3B", "HR", "G", "P"]
    if os.path.exists(JUGADORES_FILE):
        try:
            df = pd.read_csv(JUGADORES_FILE)
            for c in cols:
                if c not in df.columns: df[c] = 0
        except: df = pd.DataFrame(columns=cols)
    else: df = pd.DataFrame(columns=cols)
    
    for c in ["VB", "H", "2B", "3B", "HR", "G", "P"]:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
    return df

def cargar_equipos():
    cols = ["Nombre", "Debut", "Fin"]
    if os.path.exists(EQUIPOS_FILE):
        try:
            df = pd.read_csv(EQUIPOS_FILE)
            if "Debut" not in df.columns: df["Debut"] = ANIO_INICIO_LIGA
            if "Fin" not in df.columns: df["Fin"] = 0
            return df
        except: return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

# --- 3. INICIALIZACIÓN ---
st.set_page_config(page_title=f"Liga Softbol {TEMPORADA_LABEL}", layout="wide")
if 'admin' not in st.session_state: st.session_state.admin = False

df_j = cargar_jugadores()
df_e = cargar_equipos()

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.title(f"🥎 Ciclo {TEMPORADA_LABEL}")
    st.info(f"Inicio: Agosto {ANIO_INICIO_LIGA}")
    if not st.session_state.admin:
        with st.expander("🔐 Admin"):
            u = st.text_input("Usuario")
            p = st.text_input("Password", type="password")
            if st.button("Entrar"):
                if u == "admin" and p == "123":
                    st.session_state.admin = True
                    st.rerun()
    else:
        if st.button("Cerrar Sesión"):
            st.session_state.admin = False
            st.rerun()
    
    st.divider()
    menu = st.radio("Navegación:", ["🏆 LÍDERES", "📋 ROSTERS", "📜 HISTORIAL JUGADOR", "🏘️ EQUIPOS", "✍️ REGISTRAR", "🗑️ BORRAR", "💾 RESPALDO"])

# --- 5. LÓGICA DE SECCIONES ---

if menu == "🏆 LÍDERES":
    st.header(f"🔝 Líderes Departamentales ({TEMPORADA_LABEL})")
    t1, t2 = st.tabs(["⚾ BATEO", "🎯 PITCHEO"])
    with t1:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.subheader("Hits (H)"); st.table(df_j.nlargest(10, 'H')[['Nombre', 'H']])
            st.subheader("Home Runs (HR)"); st.table(df_j.nlargest(10, 'HR')[['Nombre', 'HR']])
        with c2:
            st.subheader("Dobles (2B)"); st.table(df_j.nlargest(10, '2B')[['Nombre', '2B']])
        with c3:
            st.subheader("Triples (3B)"); st.table(df_j.nlargest(10, '3B')[['Nombre', '3B']])
    with t2:
        c1, c2 = st.columns(2)
        with c1: st.subheader("Ganados (G)"); st.table(df_j.nlargest(10, 'G')[['Nombre', 'G']])
        with c2: st.subheader("Perdidos (P)"); st.table(df_j.nlargest(10, 'P')[['Nombre', 'P']])

elif menu == "🏘️ EQUIPOS":
    st.header("🏘️ Historial de Equipos")
    if st.session_state.admin:
        with st.form("eq_form"):
            n_eq = st.text_input("Nombre:")
            d_eq = st.number_input("Año Debut:", 2024, ANIO_ACTUAL, 2024)
            f_eq = st.number_input("Año Retiro (0 si sigue Activo):", 0, ANIO_ACTUAL, 0)
            if st.form_submit_button("Guardar Equipo"):
                df_e = df_e[df_e["Nombre"] != n_eq]
                df_e = pd.concat([df_e, pd.DataFrame([{"Nombre": n_eq, "Debut": d_eq, "Fin": f_eq}])], ignore_index=True)
                df_e.to_csv(EQUIPOS_FILE, index=False); st.rerun()
    
    if not df_e.empty:
        df_v = df_e.copy()
        df_v["Estatus"] = df_v["Fin"].apply(lambda x: "🟢 Activo" if x == 0 else "🔴 Retirado")
        # Cálculo: Año fin (o actual) - Año debut + 1
        df_v["Temporadas"] = df_v.apply(lambda r: (r['Fin'] if r['Fin']>0 else ANIO_ACTUAL) - r['Debut'] + 1, axis=1)
        st.table(df_v[["Nombre", "Debut", "Fin", "Estatus", "Temporadas"]])

elif menu == "📜 HISTORIAL JUGADOR":
    st.header("📜 Ficha Técnica")
    if not df_j.empty:
        j_s = st.selectbox("Buscar Jugador:", sorted(df_j["Nombre"].unique()))
        d = df_j[df_j["Nombre"] == j_s].iloc
        c1, c2 = st.columns(2)
        with c1:
            avg = (d['H']/d['VB']) if d['VB'] > 0 else 0
            st.metric("AVG Carrera", f"{avg:.3f}")
            st.write(f"**Equipo:** {d['Equipo']}")
        with c2:
            st.write(f"**Bateo:** H:{int(d['H'])} | 2B:{int(d['2B'])} | 3B:{int(d['3B'])} | HR:{int(d['HR'])}")
            st.write(f"**Pitcheo:** G:{int(d['G'])} | P:{int(d['P'])}")

elif menu == "✍️ REGISTRAR":
    if st.session_state.admin:
        t = st.radio("Tipo:", ["Bateo", "Pitcheo"], horizontal=True)
        with st.form("reg"):
            nom = st.text_input("Jugador:")
            eq = st.selectbox("Equipo:", df_e[df_e["Fin"] == 0]["Nombre"].unique())
            c1, c2, c3, c4, c5 = st.columns(5)
            if t == "Bateo":
                vb = c1.number_input("VB", 0); h = c2.number_input("H", 0); d2 = c3.number_input("2B", 0); d3 = c4.number_input("3B", 0); hr = c5.number_input("HR", 0)
                g, p = 0, 0
            else:
                g = c1.number_input("G", 0); p = c2.number_input("P", 0)
                vb, h, d2, d3, hr = 0, 0, 0, 0, 0
            if st.form_submit_button("💾 Guardar"):
                df_j = df_j[df_j["Nombre"] != nom]
                df_j = pd.concat([df_j, pd.DataFrame([{"Nombre": nom, "Equipo": eq, "VB": vb, "H": h, "2B": d2, "3B": d3, "HR": hr, "G": g, "P": p}])], ignore_index=True)
                df_j.to_csv(JUGADORES_FILE, index=False); st.rerun()
    else: st.warning("Inicia sesión")

elif menu == "💾 RESPALDO":
    st.header("💾 Respaldo")
    st.download_button("📥 Descargar", df_j.to_csv(index=False), "respaldo_softbol.csv")
    f = st.file_uploader("📤 Restaurar", type="csv")
    if f: pd.read_csv(f).to_csv(JUGADORES_FILE, index=False); st.rerun()

elif menu == "📋 ROSTERS":
    if not df_e.empty:
        eq = st.selectbox("Equipo:", df_e[df_e["Fin"] == 0]["Nombre"].unique())
        st.dataframe(df_j[df_j["Equipo"] == eq], use_container_width=True)

elif menu == "🗑️ BORRAR":
    if st.session_state.admin:
        j_b = st.selectbox("Borrar Jugador:", [""] + list(df_j["Nombre"].unique()))
        if st.button("❌ Borrar") and j_b:
            df_j = df_j[df_j["Nombre"] != j_b]
            df_j.to_csv(JUGADORES_FILE, index=False); st.rerun()


