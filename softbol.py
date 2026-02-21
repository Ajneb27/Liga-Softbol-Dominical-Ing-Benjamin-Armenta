import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN DE RUTAS ---
DATA_DIR = "liga_softbol_2026_final"
if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)

JUGADORES_FILE = os.path.join(DATA_DIR, "jugadores_stats.csv")
EQUIPOS_FILE = os.path.join(DATA_DIR, "equipos_lista.csv")
CONFIG_FILE = os.path.join(DATA_DIR, "config_admin.csv")

ANIO_ACTUAL = 2026 

# --- 2. MOTOR DE DATOS (REPARACIÓN AUTOMÁTICA DE COLUMNAS) ---
def cargar_base_datos():
    # LISTA MAESTRA DE COLUMNAS (Incluye 3B y P)
    cols_obligatorias = ["Nombre", "Equipo", "VB", "H", "2B", "3B", "HR", "G", "P"]
    
    if os.path.exists(JUGADORES_FILE):
        try:
            df = pd.read_csv(JUGADORES_FILE)
            # PROTECCIÓN: Si falta 3B o cualquier otra, se crea con 0
            for col in cols_obligatorias:
                if col not in df.columns: 
                    df[col] = 0
        except: 
            df = pd.DataFrame(columns=cols_obligatorias)
    else: 
        df = pd.DataFrame(columns=cols_obligatorias)
    
    # FORZAR NÚMEROS (Evita que desaparezcan los líderes)
    for c in ["VB", "H", "2B", "3B", "HR", "G", "P"]:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
    return df

def cargar_equipos():
    if os.path.exists(EQUIPOS_FILE):
        df = pd.read_csv(EQUIPOS_FILE)
        if "Debut" not in df.columns: df["Debut"] = ANIO_ACTUAL
        return df
    return pd.DataFrame(columns=["Nombre", "Debut"])

# --- 3. INICIALIZACIÓN ---
if 'admin_sesion' not in st.session_state: st.session_state.admin_sesion = False
df_j = cargar_base_datos()
df_e = cargar_equipos()

st.set_page_config(page_title="Softbol Pro 2026", layout="wide")

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.title("🥎 Liga Softbol 2026")
    if not st.session_state.admin_sesion:
        with st.expander("🔐 Login Admin"):
            u = st.text_input("Usuario")
            p = st.text_input("Clave", type="password")
            if st.button("Entrar"):
                if u == "admin" and p == "123": 
                    st.session_state.admin_sesion = True
                    st.rerun()
    else:
        if st.button("Cerrar Sesión"):
            st.session_state.admin_sesion = False
            st.rerun()
    
    st.divider()
    menu = st.radio("Menú:", ["🏆 LÍDERES", "📜 HISTORIAL JUGADOR", "📋 ROSTERS", "🏘️ EQUIPOS", "✍️ REGISTRAR", "💾 RESPALDO"])

# --- 5. SECCIÓN: LÍDERES (TOP 10) ---
if menu == "🏆 LÍDERES":
    st.header("🔝 Líderes Departamentales")
    t_b, t_p = st.tabs(["⚾ Bateo", "🎯 Pitcheo"])
    with t_b:
        c1, c2, c3 = st.columns(3)
        with c1: 
            st.subheader("Hits (H)"); st.table(df_j.nlargest(10, 'H')[['Nombre', 'H']])
            st.subheader("Home Runs (HR)"); st.table(df_j.nlargest(10, 'HR')[['Nombre', 'HR']])
        with c2: 
            st.subheader("Dobles (2B)"); st.table(df_j.nlargest(10, '2B')[['Nombre', '2B']])
        with c3: 
            # AQUÍ SE MUESTRAN LOS TRIPLES REPARADOS
            st.subheader("Triples (3B)"); st.table(df_j.nlargest(10, '3B')[['Nombre', '3B']])
    with t_p:
        c1, c2 = st.columns(2)
        with c1: st.subheader("Ganados (G)"); st.table(df_j.nlargest(10, 'G')[['Nombre', 'G']])
        with c2: st.subheader("Perdidos (P)"); st.table(df_j.nlargest(10, 'P')[['Nombre', 'P']])

# --- 6. SECCIÓN: HISTORIAL JUGADOR ---
elif menu == "📜 HISTORIAL JUGADOR":
    st.header("📜 Ficha Técnica")
    if df_j.empty: st.info("No hay jugadores.")
    else:
        jugador_sel = st.selectbox("Buscar Jugador:", sorted(df_j["Nombre"].unique()))
        datos = df_j[df_j["Nombre"] == jugador_sel].iloc[0]
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            st.metric("Promedio (AVG)", f"{(datos['H']/datos['VB'] if datos['VB']>0 else 0):.3f}")
            st.write(f"**Equipo:** {datos['Equipo']}")
        with col_f2:
            st.write(f"**Hits:** {int(datos['H'])} | **2B:** {int(datos['2B'])} | **3B:** {int(datos['3B'])} | **HR:** {int(datos['HR'])}")
            st.write(f"**Récord Pitcheo:** {int(datos['G'])}G - {int(datos['P'])}P")

# --- 7. SECCIÓN: REGISTRAR (INCLUYE 3B) ---
elif menu == "✍️ REGISTRAR":
    if st.session_state.admin_sesion:
        modo = st.radio("Tipo:", ["Bateo", "Pitcheo"], horizontal=True)
        with st.form("reg_full"):
            nom = st.text_input("Nombre:")
            eq = st.selectbox("Equipo:", df_e["Nombre"])
            if modo == "Bateo":
                v1, v2, v3, v4, v5 = st.columns(5)
                vb = v1.number_input("VB", 0); h = v2.number_input("H", 0)
                d2 = v3.number_input("2B", 0); d3 = v4.number_input("3B", 0); hr = v5.number_input("HR", 0)
                g, p = 0, 0
            else:
                p1, p2 = st.columns(2)
                g = p1.number_input("G", 0); p = p2.number_input("P", 0)
                vb, h, d2, d3, hr = 0, 0, 0, 0, 0
            
            if st.form_submit_button("Guardar"):
                df_j = df_j[df_j["Nombre"] != nom]
                nueva = pd.DataFrame([{"Nombre": nom, "Equipo": eq, "VB": vb, "H": h, "2B": d2, "3B": d3, "HR": hr, "G": g, "P": p}])
                pd.concat([df_j, nueva], ignore_index=True).to_csv(JUGADORES_FILE, index=False)
                st.success("Guardado"); st.rerun()

# --- 8. SECCIONES RESTANTES ---
elif menu == "🏘️ EQUIPOS":
    st.header("Equipos")
    if st.session_state.admin_sesion:
        with st.form("eq"):
            ne = st.text_input("Nombre:"); de = st.number_input("Debut:", 1980, 2026, 2026)
            if st.form_submit_button("Añadir"):
                df_e = pd.concat([df_e, pd.DataFrame([{"Nombre": ne, "Debut": de}])], ignore_index=True)
                df_e.to_csv(EQUIPOS_FILE, index=False); st.rerun()
    df_e["Temporadas"] = 2026 - df_e["Debut"] + 1
    st.table(df_e)

elif menu == "💾 RESPALDO":
    st.download_button("📥 Descargar", df_j.to_csv(index=False), "respaldo.csv")
    f = st.file_uploader("📤 Restaurar", type="csv")
    if f: pd.read_csv(f).to_csv(JUGADORES_FILE, index=False); st.rerun()

elif menu == "📋 ROSTERS":
    if not df_e.empty:
        eq = st.selectbox("Equipo:", df_e["Nombre"])
        st.dataframe(df_j[df_j["Equipo"] == eq], use_container_width=True)
