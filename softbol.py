import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN DE LIGA 2026 ---
ANIO_INICIO_LIGA = 2024
ANIO_ACTUAL = 2026
MAX_JUGADORES = 25
MAX_REFUERZOS = 3

DATA_DIR = "liga_softbol_final_2026"
if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)

JUGADORES_FILE = os.path.join(DATA_DIR, "jugadores_v11.csv")
EQUIPOS_FILE = os.path.join(DATA_DIR, "equipos_v11.csv")

# --- 2. MOTOR DE DATOS (PROTECCIÓN TOTAL) ---
def cargar_jugadores():
    cols_obligatorias = ["Nombre", "Equipo", "Categoria", "VB", "H", "2B", "3B", "HR", "G", "P"]
    if os.path.exists(JUGADORES_FILE):
        try:
            df = pd.read_csv(JUGADORES_FILE)
            for col in cols_obligatorias:
                if col not in df.columns: 
                    df[col] = "Softbolista" if col == "Categoria" else 0
        except: df = pd.DataFrame(columns=cols_obligatorias)
    else: df = pd.DataFrame(columns=cols_obligatorias)
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
    
    st.divider()
    menu = st.radio("Menú:", ["🏆 LÍDERES", "📋 ROSTERS", "📜 HISTORIAL", "🏘️ EQUIPOS", "✍️ REGISTRAR", "🗑️ BORRAR", "💾 RESPALDO"])

# --- 5. LÍDERES (TOP 10) ---
if menu == "🏆 LÍDERES":
    st.header("🥇 Líderes Departamentales")
    t1, t2 = st.tabs(["⚾ BATEO", "🎯 PITCHEO"])
    with t1:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Hits (H)"); st.table(df_j.nlargest(10, 'H')[['Nombre', 'H', 'Equipo']])
            st.subheader("Dobles (2B)"); st.table(df_j.nlargest(10, '2B')[['Nombre', '2B', 'Equipo']])
        with c2:
            st.subheader("Home Runs (HR)"); st.table(df_j.nlargest(10, 'HR')[['Nombre', 'HR', 'Equipo']])
            st.subheader("Triples (3B)"); st.table(df_j.nlargest(10, '3B')[['Nombre', '3B', 'Equipo']])
    with t2:
        c1, c2 = st.columns(2)
        with c1: st.subheader("Ganados (G)"); st.table(df_j.nlargest(10, 'G')[['Nombre', 'G', 'Equipo']])
        with c2: st.subheader("Perdidos (P)"); st.table(df_j.nlargest(10, 'P')[['Nombre', 'P', 'Equipo']])

# --- 6. REGISTRAR CON CALCULADORA AUTOMÁTICA ---
elif menu == "✍️ REGISTRAR":
    if st.session_state.admin:
        st.header("✍️ Anotación Rápida")
        lista_j = ["NUEVO JUGADOR"] + sorted(df_j["Nombre"].unique().tolist())
        seleccion = st.selectbox("Seleccionar Jugador:", lista_j)
        
        if 'vals' not in st.session_state or st.session_state.get('last_sel') != seleccion:
            if seleccion != "NUEVO JUGADOR":
                st.session_state.vals = df_j[df_j["Nombre"] == seleccion].iloc[0].to_dict()
            else:
                st.session_state.vals = {"Nombre": "", "Equipo": None, "Categoria": "Softbolista", "VB": 0, "H": 0, "2B": 0, "3B": 0, "HR": 0, "G": 0, "P": 0}
            st.session_state.last_sel = seleccion

        st.subheader("➕ Sumar acciones de hoy:")
        c1, c2, c3, c4, c5 = st.columns(5)
        if c1.button("Sencillo (+1H, +1VB)"): st.session_state.vals["H"]+=1; st.session_state.vals["VB"]+=1; st.rerun()
        if c2.button("Doble (+1H, +1 2B, +1VB)"): st.session_state.vals["H"]+=1; st.session_state.vals["2B"]+=1; st.session_state.vals["VB"]+=1; st.rerun()
        if c3.button("Triple (+1H, +1 3B, +1VB)"): st.session_state.vals["H"]+=1; st.session_state.vals["3B"]+=1; st.session_state.vals["VB"]+=1; st.rerun()
        if c4.button("Home Run (+1H, +1HR, +1VB)"): st.session_state.vals["H"]+=1; st.session_state.vals["HR"]+=1; st.session_state.vals["VB"]+=1; st.rerun()
        if c5.button("Out (+1VB)"): st.session_state.vals["VB"]+=1; st.rerun()

        with st.form("form_final", clear_on_submit=True):
            nom_f = st.text_input("Confirmar Nombre:", value=st.session_state.vals["Nombre"])
            eq_f = st.selectbox("Equipo:", df_e[df_e["Fin"] == 0]["Nombre"].unique() if not df_e.empty else ["Crea un equipo"])
            cat_f = st.radio("Categoría:", ["Novato", "Softbolista", "Refuerzo"], index=["Novato", "Softbolista", "Refuerzo"].index(st.session_state.vals["Categoria"]))
            
            st.write("### Totales Acumulados")
            v1, v2, v3, v4, v5 = st.columns(5)
            vb = v1.number_input("VB", value=int(st.session_state.vals["VB"]))
            h = v2.number_input("H", value=int(st.session_state.vals["H"]))
            d2 = v3.number_input("2B", value=int(st.session_state.vals["2B"]))
            d3 = v4.number_input("3B", value=int(st.session_state.vals["3B"]))
            hr = v5.number_input("HR", value=int(st.session_state.vals["HR"]))
            
            p1, p2 = st.columns(2)
            gan = p1.number_input("G", value=int(st.session_state.vals["G"]))
            per = p2.number_input("P", value=int(st.session_state.vals["P"]))
            
            if st.form_submit_button("💾 GUARDAR CAMBIOS"):
                df_j = df_j[df_j["Nombre"] != nom_f]
                nueva = pd.DataFrame([{"Nombre": nom_f, "Equipo": eq_f, "Categoria": cat_f, "VB": vb, "H": h, "2B": d2, "3B": d3, "HR": hr, "G": gan, "P": per}])
                pd.concat([df_j, nueva], ignore_index=True).to_csv(JUGADORES_FILE, index=False)
                st.success("Guardado"); st.rerun()

# --- 7. EQUIPOS ORDENADOS POR TRAYECTORIA ---
elif menu == "🏘️ EQUIPOS":
    st.header("🏘️ Equipos (Ordenados por Antigüedad)")
    if st.session_state.admin:
        with st.form("eq_f"):
            n=st.text_input("Nombre:"); d=st.number_input("Debut:", 2024, 2026, 2024); f=st.number_input("Fin (0=Activo):", 0, 2026, 0)
            if st.form_submit_button("Añadir"):
                df_e = pd.concat([df_e, pd.DataFrame([{"Nombre": n, "Debut": d, "Fin": f}])], ignore_index=True)
                df_e.to_csv(EQUIPOS_FILE, index=False); st.rerun()
    
    if not df_e.empty:
        df_v = df_e.copy()
        df_v["Temporadas"] = df_v.apply(lambda r: (r['Fin'] if r['Fin']>0 else ANIO_ACTUAL) - r['Debut'] + 1, axis=1)
        df_v["Estatus"] = df_v["Fin"].apply(lambda x: "🟢 Activo" if x == 0 else "🔴 Retirado")
        st.table(df_v.sort_values(by="Temporadas", ascending=False)[["Nombre", "Debut", "Fin", "Estatus", "Temporadas"]])

# --- 8. SECCIÓN BORRAR (ACTUALIZADA) ---
elif menu == "🗑️ BORRAR":
    if st.session_state.admin:
        st.header("🗑️ Centro de Eliminación")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Borrar Jugador")
            j_b = st.selectbox("Selecciona Jugador:", [""] + sorted(list(df_j["Nombre"].unique())))
            if st.button("❌ Eliminar Jugador") and j_b != "":
                df_j = df_j[df_j["Nombre"] != j_b]
                df_j.to_csv(JUGADORES_FILE, index=False)
                st.success(f"Jugador {j_b} eliminado.")
                st.rerun()
        
        with col2:
            st.subheader("Borrar Equipo")
            e_b = st.selectbox("Selecciona Equipo:", [""] + sorted(list(df_e["Nombre"].unique())))
            if st.button("❌ Eliminar Equipo") and e_b != "":
                # Borrar el equipo
                df_e = df_e[df_e["Nombre"] != e_b]
                # Borrar también a sus jugadores vinculados
                df_j = df_j[df_j["Equipo"] != e_b]
                
                df_e.to_csv(EQUIPOS_FILE, index=False)
                df_j.to_csv(JUGADORES_FILE, index=False)
                st.success(f"Equipo {e_b} y sus jugadores eliminados.")
                st.rerun()
    else:
        st.error("Acceso restringido al Administrador.")

# --- 9. SECCIONES RESTANTES ---
elif menu == "📋 ROSTERS":
    if not df_e.empty:
        eq = st.selectbox("Equipo:", df_e["Nombre"].unique())
        r = df_j[df_j["Equipo"] == eq]
        st.write(f"**Jugadores:** {len(r)}/{MAX_JUGADORES}")
        st.dataframe(r, use_container_width=True)

elif menu == "📜 HISTORIAL":
    if not df_j.empty:
        j = st.selectbox("Jugador:", sorted(df_j["Nombre"].unique()))
        d = df_j[df_j["Nombre"] == j].iloc[0]
        st.subheader(f"Ficha: {d['Nombre']}")
        st.write(f"**AVG:** {(d['H']/d['VB'] if d['VB']>0 else 0):.3f} | **Equipo:** {d['Equipo']}")

elif menu == "💾 RESPALDO":
    st.download_button("📥 Descargar", df_j.to_csv(index=False), "respaldo.csv")
    f = st.file_uploader("📤 Restaurar", type="csv")
    if f: pd.read_csv(f).to_csv(JUGADORES_FILE, index=False); st.rerun()
