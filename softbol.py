import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN DE LIGA ---
ANIO_ACTUAL = 2026
DATA_DIR = "liga_softbol_final_2026"
if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)

JUGADORES_FILE = os.path.join(DATA_DIR, "jugadores_master.csv")
EQUIPOS_FILE = os.path.join(DATA_DIR, "equipos_master.csv")

# --- 2. MOTOR DE DATOS (PROTECCIÓN TOTAL) ---
def cargar_jugadores():
    # LISTA MAESTRA: Asegura que todas las columnas existan SIEMPRE
    cols_obligatorias = ["Nombre", "Equipo", "Categoria", "VB", "H", "2B", "3B", "HR", "G", "P"]
    if os.path.exists(JUGADORES_FILE):
        try:
            df = pd.read_csv(JUGADORES_FILE)
            for c in cols_obligatorias:
                if c not in df.columns: df[c] = "Softbolista" if c == "Categoria" else 0
        except: df = pd.DataFrame(columns=cols_obligatorias)
    else: df = pd.DataFrame(columns=cols_obligatorias)
    
    df = df.dropna(subset=['Nombre']) # Evita el error de ordenamiento
    
    # CONVERSIÓN NUMÉRICA CRÍTICA: Si no es número, los líderes no aparecen
    for c in ["VB", "H", "2B", "3B", "HR", "G", "P"]:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
    return df

def cargar_equipos():
    df = pd.read_csv(EQUIPOS_FILE) if os.path.exists(EQUIPOS_FILE) else pd.DataFrame(columns=["Nombre", "Debut", "Fin"])
    return df

# --- 3. INICIALIZACIÓN ---
st.set_page_config(page_title="Softbol Pro 2026", layout="wide")
if 'admin' not in st.session_state: st.session_state.admin = False

df_j = cargar_jugadores()
df_e = cargar_equipos()

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.title(f"🥎 Temporada {ANIO_ACTUAL}")
    if not st.session_state.admin:
        with st.expander("🔐 Acceso Admin"):
            u = st.text_input("Usuario"); p = st.text_input("Clave", type="password")
            if st.button("Entrar"):
                if u == "admin" and p == "123": st.session_state.admin = True; st.rerun()
    else:
        st.success("Admin Activo")
        if st.button("Cerrar Sesión"): st.session_state.admin = False; st.rerun()
    
    menu = st.radio("Menú:", ["🏆 LÍDERES", "📋 ROSTERS", "📜 HISTORIAL ACUMULADO", "🏘️ EQUIPOS", "✍️ REGISTRAR", "💾 RESPALDO"])

# --- 5. SECCIÓN: LÍDERES (CORREGIDA) ---
if menu == "🏆 LÍDERES":
    st.header("🥇 Líderes Departamentales")
    t1, t2 = st.tabs(["⚾ BATEO", "🎯 PITCHEO"])
    
    with t1:
        c1, c2 = st.columns(2)
        with c1:
            st.write("**HITS (H)**")
            st.table(df_j.nlargest(10, 'H', keep='all')[['Nombre', 'H']])
            st.write("**DOBLES (2B)**")
            st.table(df_j.nlargest(10, '2B', keep='all')[['Nombre', '2B']])
        with c2:
            st.write("**HOME RUNS (HR)**")
            st.table(df_j.nlargest(10, 'HR', keep='all')[['Nombre', 'HR']])
            st.write("**TRIPLES (3B)**")
            st.table(df_j.nlargest(10, '3B', keep='all')[['Nombre', '3B']])
            
    with t2:
        # SECCIÓN DE PITCHEO BLINDADA
        st.subheader("Líderes de Pitcheo")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.write("**JUEGOS GANADOS (G)**")
            # nlargest puede fallar si todos son 0, aquí lo forzamos a mostrar
            top_g = df_j.sort_values(by='G', ascending=False).head(10)
            st.table(top_g[['Nombre', 'Equipo', 'G']])
            
        with col_p2:
            st.write("**JUEGOS PERDIDOS (P)**")
            top_p = df_j.sort_values(by='P', ascending=False).head(10)
            st.table(top_p[['Nombre', 'Equipo', 'P']])

# --- 6. SECCIÓN: HISTORIAL ACUMULADO ---
elif menu == "📜 HISTORIAL ACUMULADO":
    st.header("📜 Historial de Carrera")
    if not df_j.empty:
        j_sel = st.selectbox("Selecciona Jugador:", sorted(df_j["Nombre"].unique().tolist()))
        d = df_j[df_j["Nombre"] == j_sel].iloc[0] # Arreglado el acceso a datos
        
        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("Equipo", d['Equipo'])
        c2.metric("Categoría", d['Categoria'])
        avg = (d['H'] / d['VB']) if d['VB'] > 0 else 0
        c3.metric("Promedio (AVG)", f"{avg:.3f}")
        
        st.subheader("Estadísticas Acumuladas")
        st.write(f"**Bateo:** VB: {int(d['VB'])} | H: {int(d['H'])} | 2B: {int(d['2B'])} | 3B: {int(d['3B'])} | HR: {int(d['HR'])}")
        st.write(f"**Pitcheo:** Juegos Ganados (G): {int(d['G'])} | Juegos Perdidos (P): {int(d['P'])}")

# --- 7. REGISTRAR (INCLUYE GANADOS/PERDIDOS) ---
elif menu == "✍️ REGISTRAR":
    if st.session_state.admin:
        st.header("✍️ Anotación")
        lista_op = ["NUEVO JUGADOR"] + sorted(df_j["Nombre"].unique().tolist())
        sel = st.selectbox("Elegir Jugador:", lista_op)
        
        if 'vals' not in st.session_state or st.session_state.get('last_sel') != sel:
            if sel != "NUEVO JUGADOR":
                st.session_state.vals = df_j[df_j["Nombre"] == sel].iloc[0].to_dict()
            else:
                st.session_state.vals = {"Nombre": "", "Equipo": None, "Categoria": "Softbolista", "VB": 0, "H": 0, "2B": 0, "3B": 0, "HR": 0, "G": 0, "P": 0}
            st.session_state.last_sel = sel

        st.write("### 🎯 Sumar al Pitcheo")
        cp1, cp2 = st.columns(2)
        if cp1.button("Ganó Juego (+1 G)"): st.session_state.vals["G"]+=1; st.rerun()
        if cp2.button("Perdió Juego (+1 P)"): st.session_state.vals["P"]+=1; st.rerun()

        with st.form("form_f"):
            nom_f = st.text_input("Nombre:", value=st.session_state.vals["Nombre"])
            eq_f = st.selectbox("Equipo:", df_e["Nombre"].unique() if not df_e.empty else ["Crea equipo"])
            v1, v2, v3, v4, v5 = st.columns(5)
            vb = v1.number_input("VB", value=int(st.session_state.vals["VB"]))
            h = v2.number_input("H", value=int(st.session_state.vals["H"]))
            d2 = v3.number_input("2B", value=int(st.session_state.vals["2B"]))
            d3 = v4.number_input("3B", value=int(st.session_state.vals["3B"]))
            hr = v5.number_input("HR", value=int(st.session_state.vals["HR"]))
            g_f = st.number_input("Ganados (G)", value=int(st.session_state.vals["G"]))
            p_f = st.number_input("Perdidos (P)", value=int(st.session_state.vals["P"]))
            
            if st.form_submit_button("💾 GUARDAR"):
                df_j = df_j[df_j["Nombre"] != nom_f]
                nueva = pd.DataFrame([{"Nombre": nom_f, "Equipo": eq_f, "Categoria": st.session_state.vals["Categoria"], "VB": vb, "H": h, "2B": d2, "3B": d3, "HR": hr, "G": g_f, "P": p_f}])
                pd.concat([df_j, nueva], ignore_index=True).to_csv(JUGADORES_FILE, index=False)
                st.success("Guardado"); st.rerun()

# --- 8. OTRAS SECCIONES ---
elif menu == "🏘️ EQUIPOS":
    if st.session_state.admin:
        with st.form("eq"):
            n=st.text_input("Equipo:"); d=st.number_input("Debut:", 2024, 2026, 2024)
            if st.form_submit_button("Añadir"):
                pd.concat([df_e, pd.DataFrame([{"Nombre": n, "Debut": d, "Fin": 0}])], ignore_index=True).to_csv(EQUIPOS_FILE, index=False); st.rerun()
    st.table(df_e)

elif menu == "💾 RESPALDO":
    st.download_button("📥 Descargar", df_j.to_csv(index=False), "respaldo.csv")
    f = st.file_uploader("Subir", type="csv")
    if f: pd.read_csv(f).to_csv(JUGADORES_FILE, index=False); st.rerun()
