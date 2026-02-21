import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN GLOBAL 2026 ---
ANIO_ACTUAL = 2026
TEMPORADA_NOMBRE = "2025-2026"  # Formato para temporadas que abarcan 2 años

DATA_DIR = "liga_softbol_pro_2026"
if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)

JUGADORES_FILE = os.path.join(DATA_DIR, "jugadores.csv")
EQUIPOS_FILE = os.path.join(DATA_DIR, "equipos.csv")

# --- 2. MOTOR DE DATOS (PROTECCIÓN TOTAL) ---
def cargar_jugadores():
    cols = ["Nombre", "Equipo", "VB", "H", "2B", "3B", "HR", "G", "P"]
    if os.path.exists(JUGADORES_FILE):
        try:
            df = pd.read_csv(JUGADORES_FILE)
            for c in cols:
                if c not in df.columns: df[c] = 0
        except: df = pd.DataFrame(columns=cols)
    else:
        df = pd.DataFrame(columns=cols)
    
    # Forzar conversión numérica para que no fallen los Líderes
    for c in ["VB", "H", "2B", "3B", "HR", "G", "P"]:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
    return df

def cargar_equipos():
    cols = ["Nombre", "Debut", "Fin"]
    if os.path.exists(EQUIPOS_FILE):
        try:
            df = pd.read_csv(EQUIPOS_FILE)
            if "Debut" not in df.columns: df["Debut"] = ANIO_ACTUAL
            if "Fin" not in df.columns: df["Fin"] = 0
            return df
        except: return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

# --- 3. INICIALIZACIÓN ---
st.set_page_config(page_title=f"Liga Softbol {TEMPORADA_NOMBRE}", layout="wide")

if 'admin' not in st.session_state: st.session_state.admin = False

df_j = cargar_jugadores()
df_e = cargar_equipos()

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.title(f"🥎 Temporada {TEMPORADA_NOMBRE}")
    if not st.session_state.admin:
        with st.expander("🔐 Login Admin"):
            u = st.text_input("Usuario")
            p = st.text_input("Password", type="password")
            if st.button("Entrar"):
                if u == "admin" and p == "123":
                    st.session_state.admin = True
                    st.rerun()
    else:
        st.success("Admin: Conectado")
        if st.button("Cerrar Sesión"):
            st.session_state.admin = False
            st.rerun()
    
    st.divider()
    menu = st.radio("Menú:", ["🏆 LÍDERES", "📋 ROSTERS", "📜 HISTORIAL JUGADOR", "🏘️ EQUIPOS", "✍️ REGISTRAR", "🗑️ BORRAR", "💾 RESPALDO"])

# --- 5. LÓGICA DE SECCIONES ---

if menu == "🏆 LÍDERES":
    st.header(f"🔝 Líderes Departamentales {TEMPORADA_NOMBRE}")
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

elif menu == "📋 ROSTERS":
    st.header("👥 Rosters por Equipo")
    if df_e.empty: st.warning("No hay equipos. Agrégalos en '🏘️ EQUIPOS'.")
    else:
        eq_sel = st.selectbox("Selecciona Equipo:", df_e[df_e["Fin"] == 0]["Nombre"].unique())
        roster = df_j[df_j["Equipo"] == eq_sel]
        if roster.empty: st.info("Sin jugadores registrados.")
        else: st.dataframe(roster, use_container_width=True)

elif menu == "📜 HISTORIAL JUGADOR":
    st.header("📜 Ficha del Jugador")
    if df_j.empty: st.info("No hay datos.")
    else:
        j_sel = st.selectbox("Buscar Jugador:", sorted(df_j["Nombre"].unique()))
        d = df_j[df_j["Nombre"] == j_sel].iloc[0]
        c1, c2 = st.columns(2)
        with c1:
            avg = (d['H']/d['VB']) if d['VB'] > 0 else 0
            st.metric("Promedio (AVG)", f"{avg:.3f}")
            st.write(f"**Equipo:** {d['Equipo']}")
        with c2:
            st.write(f"**Bateo:** H:{int(d['H'])} | 2B:{int(d['2B'])} | 3B:{int(d['3B'])} | HR:{int(d['HR'])}")
            st.write(f"**Pitcheo:** G:{int(d['G'])} | P:{int(d['P'])}")

elif menu == "🏘️ EQUIPOS":
    st.header("🏘️ Gestión de Equipos")
    if st.session_state.admin:
        with st.form("eq_form"):
            n_eq = st.text_input("Nombre del Equipo:")
            d_eq = st.number_input("Año Debut:", 1980, ANIO_ACTUAL, ANIO_ACTUAL)
            f_eq = st.number_input("Año Retiro (0 si está Activo):", 0, ANIO_ACTUAL, 0)
            if st.form_submit_button("Guardar Equipo"):
                df_e = df_e[df_e["Nombre"] != n_eq]
                df_e = pd.concat([df_e, pd.DataFrame([{"Nombre": n_eq, "Debut": d_eq, "Fin": f_eq}])], ignore_index=True)
                df_e.to_csv(EQUIPOS_FILE, index=False); st.rerun()
    
    if not df_e.empty:
        df_view = df_e.copy()
        df_view["Estatus"] = df_view["Fin"].apply(lambda x: "🟢 Activo" if x == 0 else "🔴 Retirado")
        df_view["Temporadas"] = df_view.apply(lambda r: (r['Fin'] if r['Fin']>0 else ANIO_ACTUAL) - r['Debut'] + 1, axis=1)
        st.table(df_view)

elif menu == "✍️ REGISTRAR":
    if not st.session_state.admin: st.warning("Inicia sesión como administrador.")
    elif df_e.empty: st.error("Crea un equipo primero.")
    else:
        tipo = st.radio("Modo:", ["Bateo", "Pitcheo"], horizontal=True)
        with st.form("reg_form"):
            nom = st.text_input("Nombre del Jugador:")
            eq = st.selectbox("Equipo:", df_e[df_e["Fin"] == 0]["Nombre"].unique())
            c1, c2, c3, c4, c5 = st.columns(5)
            if tipo == "Bateo":
                vb = c1.number_input("VB", 0); h = c2.number_input("H", 0); d2 = c3.number_input("2B", 0); d3 = c4.number_input("3B", 0); hr = c5.number_input("HR", 0)
                g, p = 0, 0
            else:
                g = c1.number_input("G", 0); p = c2.number_input("P", 0)
                vb, h, d2, d3, hr = 0, 0, 0, 0, 0
            if st.form_submit_button("💾 Guardar"):
                df_j = df_j[df_j["Nombre"] != nom]
                df_j = pd.concat([df_j, pd.DataFrame([{"Nombre": nom, "Equipo": eq, "VB": vb, "H": h, "2B": d2, "3B": d3, "HR": hr, "G": g, "P": p}])], ignore_index=True)
                df_j.to_csv(JUGADORES_FILE, index=False); st.success("Guardado"); st.rerun()

elif menu == "🗑️ BORRAR":
    if st.session_state.admin:
        st.header("🗑️ Eliminar Datos")
        j_borrar = st.selectbox("Selecciona Jugador:", [""] + list(df_j["Nombre"].unique()))
        if st.button("❌ Borrar Jugador") and j_borrar:
            df_j = df_j[df_j["Nombre"] != j_borrar]
            df_j.to_csv(JUGADORES_FILE, index=False); st.rerun()
        
        e_borrar = st.selectbox("Selecciona Equipo:", [""] + list(df_e["Nombre"].unique()))
        if st.button("❌ Borrar Equipo") and e_borrar:
            df_e = df_e[df_e["Nombre"] != e_borrar]
            df_j = df_j[df_j["Equipo"] != e_borrar]
            df_e.to_csv(EQUIPOS_FILE, index=False); df_j.to_csv(JUGADORES_FILE, index=False); st.rerun()

elif menu == "💾 RESPALDO":
    st.header("💾 Centro de Respaldo")
    st.download_button("📥 Descargar CSV", df_j.to_csv(index=False), "respaldo_liga.csv")
    f = st.file_uploader("📤 Restaurar CSV", type="csv")
    if f: pd.read_csv(f).to_csv(JUGADORES_FILE, index=False); st.success("Restaurado"); st.rerun()
