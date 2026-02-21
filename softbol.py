import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN ---
ANIO_ACTUAL = 2026
MAX_JUGADORES = 25
MAX_REFUERZOS = 3
DATA_DIR = "liga_softbol_final_2026"
if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)

JUGADORES_FILE = os.path.join(DATA_DIR, "jugadores_v9.csv")
EQUIPOS_FILE = os.path.join(DATA_DIR, "equipos_v9.csv")

# --- 2. MOTOR DE DATOS ---
def cargar_jugadores():
    cols = ["Nombre", "Equipo", "Categoria", "VB", "H", "2B", "3B", "HR", "G", "P"]
    if os.path.exists(JUGADORES_FILE):
        df = pd.read_csv(JUGADORES_FILE)
        for col in cols:
            if col not in df.columns: df[col] = 0
    else: df = pd.DataFrame(columns=cols)
    for c in ["VB", "H", "2B", "3B", "HR", "G", "P"]:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
    return df

def cargar_equipos():
    df = pd.read_csv(EQUIPOS_FILE) if os.path.exists(EQUIPOS_FILE) else pd.DataFrame(columns=["Nombre", "Debut", "Fin"])
    if "Fin" not in df.columns: df["Fin"] = 0
    return df

# --- 3. INICIALIZACIÓN ---
st.set_page_config(page_title="Softbol Pro 2026", layout="wide")
if 'admin' not in st.session_state: st.session_state.admin = False

df_j = cargar_jugadores()
df_e = cargar_equipos()

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.title(f"🥎 Liga {ANIO_ACTUAL}")
    if not st.session_state.admin:
        with st.expander("🔐 Admin"):
            u = st.text_input("Usuario"); p = st.text_input("Clave", type="password")
            if st.button("Entrar"):
                if u == "admin" and p == "123": st.session_state.admin = True; st.rerun()
    else:
        if st.button("Cerrar Sesión"): st.session_state.admin = False; st.rerun()
    
    menu = st.radio("Menú:", ["🏆 LÍDERES", "📋 ROSTERS", "📜 HISTORIAL", "🏘️ EQUIPOS", "✍️ REGISTRAR", "💾 RESPALDO"])

# --- 5. SECCIÓN REGISTRAR (CALCULADORA AUTOMÁTICA) ---
if menu == "✍️ REGISTRAR":
    if st.session_state.admin:
        st.header("✍️ Anotación de Juego")
        
        # Selector de Jugador para cargar datos
        lista_j = ["NUEVO JUGADOR"] + sorted(df_j["Nombre"].unique().tolist())
        seleccion = st.selectbox("Seleccionar Jugador:", lista_j)
        
        # Cargar valores actuales
        if 'vals' not in st.session_state or st.session_state.get('last_sel') != seleccion:
            if seleccion != "NUEVO JUGADOR":
                row = df_j[df_j["Nombre"] == seleccion].iloc[0]
                st.session_state.vals = row.to_dict()
            else:
                st.session_state.vals = {"Nombre": "", "Equipo": None, "Categoria": "Softbolista", "VB": 0, "H": 0, "2B": 0, "3B": 0, "HR": 0, "G": 0, "P": 0}
            st.session_state.last_sel = seleccion

        # PANEL DE INCREMENTO RÁPIDO
        st.subheader("➕ Sumar acciones de hoy:")
        c1, c2, c3, c4, c5 = st.columns(5)
        if c1.button("Sencillo (+1 H, +1 VB)"):
            st.session_state.vals["H"] += 1; st.session_state.vals["VB"] += 1
        if c2.button("Doble (+1 H, +1 2B, +1 VB)"):
            st.session_state.vals["H"] += 1; st.session_state.vals["2B"] += 1; st.session_state.vals["VB"] += 1
        if c3.button("Triple (+1 H, +1 3B, +1 VB)"):
            st.session_state.vals["H"] += 1; st.session_state.vals["3B"] += 1; st.session_state.vals["VB"] += 1
        if c4.button("Home Run (+1 H, +1 HR, +1 VB)"):
            st.session_state.vals["H"] += 1; st.session_state.vals["HR"] += 1; st.session_state.vals["VB"] += 1
        if c5.button("Out (+1 VB)"):
            st.session_state.vals["VB"] += 1

        # FORMULARIO FINAL PARA REVISAR Y GUARDAR
        with st.form("form_final"):
            nom_f = st.text_input("Nombre:", value=st.session_state.vals["Nombre"])
            eq_f = st.selectbox("Equipo:", df_e[df_e["Fin"] == 0]["Nombre"].unique(), 
                               index=list(df_e["Nombre"].unique()).index(st.session_state.vals["Equipo"]) if st.session_state.vals["Equipo"] in df_e["Nombre"].unique() else 0)
            
            st.write("### Totales Acumulados (Revisar)")
            v1, v2, v3, v4, v5 = st.columns(5)
            vb = v1.number_input("VB", value=int(st.session_state.vals["VB"]))
            h = v2.number_input("H", value=int(st.session_state.vals["H"]))
            d2 = v3.number_input("2B", value=int(st.session_state.vals["2B"]))
            d3 = v4.number_input("3B", value=int(st.session_state.vals["3B"]))
            hr = v5.number_input("HR", value=int(st.session_state.vals["HR"]))
            
            st.write("### Pitcheo")
            p1, p2 = st.columns(2)
            gan = p1.number_input("G", value=int(st.session_state.session_state.vals["G"] if "G" in st.session_state.vals else 0))
            per = p2.number_input("P", value=int(st.session_state.session_state.vals["P"] if "P" in st.session_state.vals else 0))
            
            if st.form_submit_button("💾 GUARDAR TODOS LOS CAMBIOS"):
                df_j = df_j[df_j["Nombre"] != nom_f]
                nueva = pd.DataFrame([{"Nombre": nom_f, "Equipo": eq_f, "Categoria": st.session_state.vals["Categoria"], "VB": vb, "H": h, "2B": d2, "3B": d3, "HR": hr, "G": gan, "P": per}])
                pd.concat([df_j, nueva], ignore_index=True).to_csv(JUGADORES_FILE, index=False)
                st.success("¡Datos sincronizados!"); st.rerun()
    else: st.warning("Inicia sesión")

# --- 6. SECCIÓN LÍDERES ---
elif menu == "🏆 LÍDERES":
    st.header("🥇 Líderes de la Liga")
    t1, t2 = st.tabs(["⚾ BATEO", "🎯 PITCHEO"])
    with t1:
        c1, c2, c3 = st.columns(3)
        c1.write("**HITS**"); c1.table(df_j.nlargest(10, 'H')[['Nombre', 'H']])
        c1.write("**HOME RUNS**"); c1.table(df_j.nlargest(10, 'HR')[['Nombre', 'HR']])
        c2.write("**DOBLES (2B)**"); c2.table(df_j.nlargest(10, '2B')[['Nombre', '2B']])
        c3.write("**TRIPLES (3B)**"); c3.table(df_j.nlargest(10, '3B')[['Nombre', '3B']])
    with t2:
        st.subheader("Ganados"); st.table(df_j.nlargest(10, 'G')[['Nombre', 'G']])

# --- 7. OTRAS SECCIONES ---
elif menu == "📋 ROSTERS":
    if not df_e.empty:
        eq = st.selectbox("Equipo:", df_e["Nombre"].unique())
        st.dataframe(df_j[df_j["Equipo"] == eq], use_container_width=True)

elif menu == "🏘️ EQUIPOS":
    if st.session_state.admin:
        with st.form("add_eq"):
            n=st.text_input("Equipo:"); d=st.number_input("Debut:", 2024, 2026, 2024)
            if st.form_submit_button("Añadir"):
                pd.concat([df_e, pd.DataFrame([{"Nombre": n, "Debut": d, "Fin": 0}])], ignore_index=True).to_csv(EQUIPOS_FILE, index=False); st.rerun()
    st.table(df_e)

elif menu == "💾 RESPALDO":
    st.download_button("📥 Descargar", df_j.to_csv(index=False), "liga_softbol.csv")
    f = st.file_uploader("📤 Restaurar", type="csv")
    if f: pd.read_csv(f).to_csv(JUGADORES_FILE, index=False); st.rerun()
