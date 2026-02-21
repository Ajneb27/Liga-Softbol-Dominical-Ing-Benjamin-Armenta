import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN DE LIGA 2026 ---
ANIO_INICIO_LIGA = 2024
ANIO_ACTUAL = 2026
MAX_JUGADORES = 25
MAX_REFUERZOS = 3

DATA_DIR = "liga_softbol_reglas_2026"
if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)

JUGADORES_FILE = os.path.join(DATA_DIR, "jugadores_v3.csv")
EQUIPOS_FILE = os.path.join(DATA_DIR, "equipos_v3.csv")

# --- 2. MOTOR DE DATOS ---
def cargar_jugadores():
    cols = ["Nombre", "Equipo", "Categoria", "VB", "H", "2B", "3B", "HR", "G", "P"]
    if os.path.exists(JUGADORES_FILE):
        df = pd.read_csv(JUGADORES_FILE)
        for c in cols:
            if c not in df.columns: df[c] = "Softbolista" if c == "Categoria" else 0
    else:
        df = pd.DataFrame(columns=cols)
    for c in ["VB", "H", "2B", "3B", "HR", "G", "P"]:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
    return df

def cargar_equipos():
    return pd.read_csv(EQUIPOS_FILE) if os.path.exists(EQUIPOS_FILE) else pd.DataFrame(columns=["Nombre", "Debut", "Fin"])

# --- 3. INICIALIZACIÓN ---
st.set_page_config(page_title="Liga Softbol Pro 2026", layout="wide")
if 'admin' not in st.session_state: st.session_state.admin = False

df_j = cargar_jugadores()
df_e = cargar_equipos()

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.title(f"🥎 Temporada 2026")
    if not st.session_state.admin:
        with st.expander("🔐 Admin"):
            u = st.text_input("Usuario"); p = st.text_input("Password", type="password")
            if st.button("Entrar"):
                if u == "admin" and p == "123":
                    st.session_state.admin = True
                    st.rerun()
    else:
        if st.button("Cerrar Sesión"):
            st.session_state.admin = False
            st.rerun()
    
    st.divider()
    menu = st.radio("Menú:", ["🏆 LÍDERES", "📋 ROSTERS", "📜 HISTORIAL", "🏘️ EQUIPOS", "✍️ REGISTRAR", "💾 RESPALDO"])

# --- 5. LÓGICA DE SECCIONES ---

if menu == "✍️ REGISTRAR":
    if st.session_state.admin:
        st.header("✍️ Registro con Validación de Reglas")
        st.info(f"Reglas: Máximo {MAX_JUGADORES} jugadores y {MAX_REFUERZOS} refuerzos por equipo.")
        
        with st.form("form_reg_validado", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            nombre_n = col_a.text_input("Nombre Completo:")
            equipo_n = col_b.selectbox("Equipo:", df_e[df_e["Fin"] == 0]["Nombre"].unique() if not df_e.empty else ["Crea un equipo"])
            categoria_n = st.radio("Categoría:", ["Novato", "Softbolista", "Refuerzo"], horizontal=True)
            
            tipo_stat = st.radio("Tipo:", ["Bateo", "Pitcheo"], horizontal=True)
            c1, c2, c3 = st.columns(3)
            if tipo_stat == "Bateo":
                vb_n = c1.number_input("VB", 0); h_n = c2.number_input("H", 0); hr_n = c3.number_input("HR", 0)
                d2_n, d3_n, g_n, p_n = 0, 0, 0, 0
            else:
                g_n = c1.number_input("G", 0); p_n = c2.number_input("P", 0)
                vb_n, h_n, hr_n, d2_n, d3_n = 0, 0, 0, 0, 0
            
            if st.form_submit_button("💾 Guardar Jugador"):
                if nombre_n and equipo_n != "Crea un equipo":
                    # --- VALIDACIONES ---
                    roster_actual = df_j[df_j["Equipo"] == equipo_n]
                    es_nuevo = nombre_n not in roster_actual["Nombre"].values
                    
                    num_jugadores = len(roster_actual)
                    num_refuerzos = len(roster_actual[roster_actual["Categoria"] == "Refuerzo"])
                    
                    if es_nuevo and num_jugadores >= MAX_JUGADORES:
                        st.error(f"❌ Error: El equipo {equipo_n} ya tiene el máximo de {MAX_JUGADORES} jugadores.")
                    elif es_nuevo and categoria_n == "Refuerzo" and num_refuerzos >= MAX_REFUERZOS:
                        st.error(f"❌ Error: El equipo {equipo_n} ya tiene el máximo de {MAX_REFUERZOS} refuerzos.")
                    else:
                        # Guardar Datos
                        df_j = df_j[df_j["Nombre"] != nombre_n]
                        nueva_f = pd.DataFrame([{"Nombre": nombre_n, "Equipo": equipo_n, "Categoria": categoria_n, 
                                                 "VB": vb_n, "H": h_n, "2B": d2_n, "3B": d3_n, "HR": hr_n, "G": g_n, "P": p_n}])
                        pd.concat([df_j, nueva_f], ignore_index=True).to_csv(JUGADORES_FILE, index=False)
                        st.success(f"✅ {nombre_n} registrado exitosamente.")
                else:
                    st.error("Faltan datos obligatorios.")
    else: st.warning("Inicia sesión.")

elif menu == "📋 ROSTERS":
    st.header("📋 Consulta de Rosters")
    if not df_e.empty:
        eq_s = st.selectbox("Equipo:", df_e["Nombre"].unique())
        roster_view = df_j[df_j["Equipo"] == eq_s]
        
        # Resumen de reglas en el Roster
        nj = len(roster_view)
        nr = len(roster_view[roster_view["Categoria"] == "Refuerzo"])
        st.write(f"**Jugadores:** {nj}/{MAX_JUGADORES} | **Refuerzos:** {nr}/{MAX_REFUERZOS}")
        
        st.dataframe(roster_view[["Nombre", "Categoria", "VB", "H", "HR", "G", "P"]], use_container_width=True)

elif menu == "🏆 LÍDERES":
    st.header("🔝 Líderes Departamentales 2026")
    cat_f = st.multiselect("Categoría:", ["Novato", "Softbolista", "Refuerzo"], default=["Novato", "Softbolista", "Refuerzo"])
    df_f = df_j[df_j["Categoria"].isin(cat_f)]
    t1, t2 = st.tabs(["Bateo", "Pitcheo"])
    with t1:
        c1, c2 = st.columns(2)
        c1.write("**Hits**"); c1.table(df_f.nlargest(10, 'H')[['Nombre', 'H', 'Equipo']])
        c2.write("**Home Runs**"); c2.table(df_f.nlargest(10, 'HR')[['Nombre', 'HR', 'Equipo']])

elif menu == "📜 HISTORIAL":
    if not df_j.empty:
        j = st.selectbox("Jugador:", sorted(df_j["Nombre"].unique()))
        d = df_j[df_j["Nombre"] == j].iloc
        st.subheader(f"Ficha: {d['Nombre']}")
        st.write(f"**Categoría:** {d['Categoria']} | **Equipo:** {d['Equipo']}")
        st.metric("Promedio (AVG)", f"{(d['H']/d['VB'] if d['VB']>0 else 0):.3f}")

elif menu == "🏘️ EQUIPOS":
    if st.session_state.admin:
        with st.form("add_eq", clear_on_submit=True):
            n_e = st.text_input("Nombre Equipo:")
            d_e = st.number_input("Año Debut:", 2024, 2026, 2024)
            if st.form_submit_button("Añadir"):
                pd.concat([df_e, pd.DataFrame([{"Nombre": n_e, "Debut": d_e, "Fin": 0}])], ignore_index=True).to_csv(EQUIPOS_FILE, index=False)
                st.rerun()
    df_v = df_e.copy()
    df_v["Temporadas"] = df_v.apply(lambda r: (r['Fin'] if r['Fin']>0 else ANIO_ACTUAL) - r['Debut'] + 1, axis=1)
    st.table(df_v)

elif menu == "💾 RESPALDO":
    st.download_button("📥 Descargar CSV", df_j.to_csv(index=False), "liga_2026.csv")
    f = st.file_uploader("📤 Restaurar", type="csv")
    if f: pd.read_csv(f).to_csv(JUGADORES_FILE, index=False); st.rerun()
