import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN DE LIGA ---
ANIO_ACTUAL = 2026
MAX_JUGADORES = 25
MAX_REFUERZOS = 3
DATA_DIR = "liga_softbol_final_2026"
if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)

JUGADORES_FILE = os.path.join(DATA_DIR, "jugadores_master.csv")
EQUIPOS_FILE = os.path.join(DATA_DIR, "equipos_master.csv")

# --- 2. MOTOR DE DATOS (PROTECCIÓN TOTAL) ---
def cargar_jugadores():
    cols = ["Nombre", "Equipo", "Categoria", "VB", "H", "2B", "3B", "HR", "G", "P"]
    if os.path.exists(JUGADORES_FILE):
        try:
            df = pd.read_csv(JUGADORES_FILE)
            for c in cols:
                if c not in df.columns: df[c] = "Softbolista" if c == "Categoria" else 0
        except: df = pd.DataFrame(columns=cols)
    else: df = pd.DataFrame(columns=cols)
    
    # Limpiar nombres vacíos para evitar el error TypeError en sorted
    df = df.dropna(subset=['Nombre'])
    
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
    st.title(f"🥎 Temporada {ANIO_ACTUAL}")
    if not st.session_state.admin:
        with st.expander("🔐 Acceso Admin"):
            u = st.text_input("Usuario"); p = st.text_input("Clave", type="password")
            if st.button("Entrar"):
                if u == "admin" and p == "123": st.session_state.admin = True; st.rerun()
    else:
        st.success("Admin Activo")
        if st.button("Cerrar Sesión"): st.session_state.admin = False; st.rerun()
    
    menu = st.radio("Menú:", ["🏆 LÍDERES", "📜 HISTORIAL ACUMULADO", "📋 ROSTERS", "🏘️ EQUIPOS", "✍️ REGISTRAR", "🗑️ BORRAR", "💾 RESPALDO"])

# --- 5. SECCIÓN: HISTORIAL ACUMULADO (LO QUE ME PEDISTE) ---
if menu == "📜 HISTORIAL ACUMULADO":
    st.header("📜 Historial de Carrera del Jugador")
    if df_j.empty:
        st.info("No hay datos registrados.")
    else:
        # El sorted ahora es seguro gracias a la limpieza en cargar_jugadores()
        lista_nombres = sorted(df_j["Nombre"].unique().tolist())
        j_sel = st.selectbox("Selecciona un jugador para ver su trayectoria:", lista_nombres)
        
        datos = df_j[df_j["Nombre"] == j_sel].iloc[0]
        
        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("Equipo Actual", datos['Equipo'])
        c2.metric("Categoría", datos['Categoria'])
        avg = (datos['H'] / datos['VB']) if datos['VB'] > 0 else 0
        c3.metric("Promedio Carrera (AVG)", f"{avg:.3f}")
        
        st.subheader("📊 Totales Acumulados")
        col_b1, col_b2, col_b3, col_b4, col_b5 = st.columns(5)
        col_b1.metric("Turnos (VB)", int(datos['VB']))
        col_b2.metric("Hits (H)", int(datos['H']))
        col_b3.metric("Dobles (2B)", int(datos['2B']))
        col_b4.metric("Triples (3B)", int(datos['3B']))
        col_b5.metric("Home Runs (HR)", int(datos['HR']))
        
        st.subheader("🎯 Desempeño en Pitcheo")
        col_p1, col_p2 = st.columns(2)
        col_p1.metric("Juegos Ganados (G)", int(datos['G']), delta_color="normal")
        col_p2.metric("Juegos Perdidos (P)", int(datos['P']), delta_color="inverse")

# --- 6. SECCIÓN REGISTRAR (CALCULADORA) ---
elif menu == "✍️ REGISTRAR":
    if st.session_state.admin:
        st.header("✍️ Anotación de Juego")
        lista_opciones = ["NUEVO JUGADOR"] + sorted(df_j["Nombre"].unique().tolist())
        seleccion = st.selectbox("Seleccionar Jugador:", lista_opciones)
        
        if 'vals' not in st.session_state or st.session_state.get('last_sel') != seleccion:
            if seleccion != "NUEVO JUGADOR":
                st.session_state.vals = df_j[df_j["Nombre"] == seleccion].iloc[0].to_dict()
            else:
                st.session_state.vals = {"Nombre": "", "Equipo": None, "Categoria": "Softbolista", "VB": 0, "H": 0, "2B": 0, "3B": 0, "HR": 0, "G": 0, "P": 0}
            st.session_state.last_sel = seleccion

        st.write("### ➕ Acciones del día (se sumarán al total)")
        c1, c2, c3, c4, c5 = st.columns(5)
        if c1.button("H (+1)"): st.session_state.vals["H"]+=1; st.session_state.vals["VB"]+=1; st.rerun()
        if c2.button("2B (+1)"): st.session_state.vals["H"]+=1; st.session_state.vals["2B"]+=1; st.session_state.vals["VB"]+=1; st.rerun()
        if c3.button("3B (+1)"): st.session_state.vals["H"]+=1; st.session_state.vals["3B"]+=1; st.session_state.vals["VB"]+=1; st.rerun()
        if c4.button("HR (+1)"): st.session_state.vals["H"]+=1; st.session_state.vals["HR"]+=1; st.session_state.vals["VB"]+=1; st.rerun()
        if c5.button("K/Out (+1 VB)"): st.session_state.vals["VB"]+=1; st.rerun()

        with st.form("form_final"):
            nom_f = st.text_input("Nombre:", value=st.session_state.vals["Nombre"])
            eq_f = st.selectbox("Equipo:", df_e[df_e["Fin"] == 0]["Nombre"].unique() if not df_e.empty else ["Crea un equipo"])
            v1, v2, v3, v4, v5 = st.columns(5)
            vb = v1.number_input("VB Total", value=int(st.session_state.vals["VB"]))
            h = v2.number_input("H Total", value=int(st.session_state.vals["H"]))
            d2 = v3.number_input("2B Total", value=int(st.session_state.vals["2B"]))
            d3 = v4.number_input("3B Total", value=int(st.session_state.vals["3B"]))
            hr = v5.number_input("HR Total", value=int(st.session_state.vals["HR"]))
            p1, p2 = st.columns(2)
            g = p1.number_input("G Total", value=int(st.session_state.vals["G"]))
            p = p2.number_input("P Total", value=int(st.session_state.vals["P"]))
            
            if st.form_submit_button("💾 GUARDAR"):
                df_j = df_j[df_j["Nombre"] != nom_f]
                nueva = pd.DataFrame([{"Nombre": nom_f, "Equipo": eq_f, "Categoria": st.session_state.vals["Categoria"], "VB": vb, "H": h, "2B": d2, "3B": d3, "HR": hr, "G": g, "P": p}])
                pd.concat([df_j, nueva], ignore_index=True).to_csv(JUGADORES_FILE, index=False)
                st.success("¡Datos actualizados!"); st.rerun()

# --- 7. LÍDERES (TOP 10) ---
elif menu == "🏆 LÍDERES":
    st.header("🥇 Líderes Departamentales")
    t1, t2 = st.tabs(["⚾ BATEO", "🎯 PITCHEO"])
    with t1:
        c1, c2 = st.columns(2)
        c1.write("**HITS**"); c1.table(df_j.nlargest(10, 'H')[['Nombre', 'H']])
        c2.write("**HOME RUNS**"); c2.table(df_j.nlargest(10, 'HR')[['Nombre', 'HR']])
        st.write("**DOBLES (2B)**"); st.table(df_j.nlargest(10, '2B')[['Nombre', '2B']])

# --- 8. EQUIPOS ---
elif menu == "🏘️ EQUIPOS":
    st.header("🏘️ Gestión de Equipos")
    if st.session_state.admin:
        with st.form("eq_f"):
            n=st.text_input("Nombre:"); d=st.number_input("Debut:", 2024, 2026, 2024)
            if st.form_submit_button("Añadir"):
                pd.concat([df_e, pd.DataFrame([{"Nombre": n, "Debut": d, "Fin": 0}])], ignore_index=True).to_csv(EQUIPOS_FILE, index=False); st.rerun()
    
    df_v = df_e.copy()
    df_v["Temporadas"] = df_v.apply(lambda r: (r['Fin'] if r['Fin']>0 else ANIO_ACTUAL) - r['Debut'] + 1, axis=1)
    st.table(df_v.sort_values("Temporadas", ascending=False))

# --- 9. BORRAR ---
elif menu == "🗑️ BORRAR":
    if st.session_state.admin:
        j_b = st.selectbox("Borrar Jugador:", [""] + sorted(df_j["Nombre"].unique().tolist()))
        if st.button("❌ Eliminar") and j_b:
            df_j = df_j[df_j["Nombre"] != j_b]; df_j.to_csv(JUGADORES_FILE, index=False); st.rerun()

# --- 10. RESPALDO ---
elif menu == "💾 RESPALDO":
    st.download_button("📥 Descargar", df_j.to_csv(index=False), "respaldo.csv")
    f = st.file_uploader("Subir CSV", type="csv")
    if f: pd.read_csv(f).to_csv(JUGADORES_FILE, index=False); st.rerun()
