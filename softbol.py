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

JUGADORES_FILE = os.path.join(DATA_DIR, "jugadores_v5.csv")
EQUIPOS_FILE = os.path.join(DATA_DIR, "equipos_v5.csv")

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
st.set_page_config(page_title="Liga Softbol Pro 2026", layout="wide")
if 'admin' not in st.session_state: st.session_state.admin = False

df_j = cargar_jugadores()
df_e = cargar_equipos()

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.title(f"🥎 Temporada 2026")
    if not st.session_state.admin:
        with st.expander("🔐 Acceso Administrador"):
            u = st.text_input("Usuario"); p = st.text_input("Password", type="password")
            if st.button("Entrar"):
                if u == "admin" and p == "123":
                    st.session_state.admin = True
                    st.rerun()
    else:
        st.success("Admin Activo")
        if st.button("Cerrar Sesión"):
            st.session_state.admin = False
            st.rerun()
    
    st.divider()
    menu_options = ["🏆 LÍDERES", "📋 ROSTERS", "📜 HISTORIAL", "🏘️ EQUIPOS", "✍️ REGISTRAR"]
    if st.session_state.admin: menu_options += ["🗑️ BORRAR", "💾 RESPALDO"]
    menu = st.radio("Secciones:", menu_options)

# --- 5. SECCIÓN LÍDERES (TODOS LOS DEPARTAMENTOS) ---
if menu == "🏆 LÍDERES":
    st.header("🥇 Líderes de la Temporada (Top 10)")
    cat_f = st.multiselect("Filtrar Categoría:", ["Novato", "Softbolista", "Refuerzo"], default=["Novato", "Softbolista", "Refuerzo"])
    df_f = df_j[df_j["Categoria"].isin(cat_f)]
    
    t_bat, t_pit = st.tabs(["⚾ BATEO", "🎯 PITCHEO"])
    with t_bat:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Hits (H)"); st.table(df_f.nlargest(10, 'H')[['Nombre', 'H', 'Equipo']])
            st.subheader("Dobles (2B)"); st.table(df_f.nlargest(10, '2B')[['Nombre', '2B', 'Equipo']])
        with c2:
            st.subheader("Home Runs (HR)"); st.table(df_f.nlargest(10, 'HR')[['Nombre', 'HR', 'Equipo']])
            st.subheader("Triples (3B)"); st.table(df_f.nlargest(10, '3B')[['Nombre', '3B', 'Equipo']])
    with t_pit:
        c1, c2 = st.columns(2)
        with c1: st.subheader("Ganados (G)"); st.table(df_f.nlargest(10, 'G')[['Nombre', 'G', 'Equipo']])
        with c2: st.subheader("Perdidos (P)"); st.table(df_f.nlargest(10, 'P')[['Nombre', 'P', 'Equipo']])

# --- 6. SECCIÓN REGISTRAR (CON AUTO-BORRADO) ---
elif menu == "✍️ REGISTRAR":
    if st.session_state.admin:
        st.header("✍️ Registro de Jugadores")
        with st.form("reg_form", clear_on_submit=True):
            nom = st.text_input("Nombre Completo:")
            eq = st.selectbox("Equipo:", df_e[df_e["Fin"] == 0]["Nombre"].unique() if not df_e.empty else ["Crea un equipo"])
            cat = st.radio("Categoría:", ["Novato", "Softbolista", "Refuerzo"], horizontal=True)
            tipo = st.radio("Anotar:", ["Bateo", "Pitcheo"], horizontal=True)
            v1, v2, v3, v4, v5 = st.columns(5)
            if tipo == "Bateo":
                vb=v1.number_input("VB",0); h=v2.number_input("H",0); d2=v3.number_input("2B",0); d3=v4.number_input("3B",0); hr=v5.number_input("HR",0); g,p=0,0
            else:
                g=v1.number_input("G",0); p=v2.number_input("P",0); vb,h,d2,d3,hr=0,0,0,0,0
            
            if st.form_submit_button("💾 Guardar y Limpiar"):
                if nom and eq != "Crea un equipo":
                    ros = df_j[df_j["Equipo"] == eq]
                    if (nom not in ros["Nombre"].values) and (len(ros) >= MAX_JUGADORES): st.error("❌ Equipo lleno")
                    elif (nom not in ros["Nombre"].values) and (cat == "Refuerzo") and (len(ros[ros["Categoria"]=="Refuerzo"]) >= MAX_REFUERZOS): st.error("❌ Límite refuerzos")
                    else:
                        df_j = df_j[df_j["Nombre"] != nom]
                        nueva = pd.DataFrame([{"Nombre": nom, "Equipo": eq, "Categoria": cat, "VB": vb, "H": h, "2B": d2, "3B": d3, "HR": hr, "G": g, "P": p}])
                        pd.concat([df_j, nueva], ignore_index=True).to_csv(JUGADORES_FILE, index=False)
                        st.success(f"✅ {nom} Guardado."); st.rerun()
    else: st.warning("Inicia sesión")

# --- 7. SECCIÓN BORRAR (NUEVA) ---
elif menu == "🗑️ BORRAR":
    st.header("🗑️ Gestión de Eliminación")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Eliminar Jugador")
        j_sel = st.selectbox("Selecciona Jugador:", [""] + sorted(df_j["Nombre"].unique().tolist()))
        if st.button("❌ Eliminar Jugador") and j_sel != "":
            df_j = df_j[df_j["Nombre"] != j_sel]
            df_j.to_csv(JUGADORES_FILE, index=False)
            st.success(f"{j_sel} eliminado."); st.rerun()
    with col2:
        st.subheader("Eliminar Equipo")
        e_sel = st.selectbox("Selecciona Equipo:", [""] + sorted(df_e["Nombre"].unique().tolist()))
        if st.button("❌ Eliminar Equipo") and e_sel != "":
            df_e = df_e[df_e["Nombre"] != e_sel]
            df_j = df_j[df_j["Equipo"] != e_sel] # Borra jugadores de ese equipo
            df_e.to_csv(EQUIPOS_FILE, index=False); df_j.to_csv(JUGADORES_FILE, index=False)
            st.success(f"Equipo {e_sel} eliminado."); st.rerun()

# --- 8. RESTO DE SECCIONES ---
elif menu == "📋 ROSTERS":
    if not df_e.empty:
        eq = st.selectbox("Equipo:", df_e["Nombre"].unique())
        r = df_j[df_j["Equipo"] == eq]
        st.write(f"**Jugadores:** {len(r)}/{MAX_JUGADORES} | **Refuerzos:** {len(r[r['Categoria']=='Refuerzo'])}/{MAX_REFUERZOS}")
        st.dataframe(r, use_container_width=True)

elif menu == "🏘️ EQUIPOS":
    if st.session_state.admin:
        with st.form("add_eq", clear_on_submit=True):
            n=st.text_input("Nombre:"); d=st.number_input("Debut:", 2024, 2026, 2024); f=st.number_input("Fin (0=Activo):", 0, 2026, 0)
            if st.form_submit_button("Añadir"):
                pd.concat([df_e, pd.DataFrame([{"Nombre": n, "Debut": d, "Fin": f}])], ignore_index=True).to_csv(EQUIPOS_FILE, index=False); st.rerun()
    df_v = df_e.copy()
    df_v["Temporadas"] = df_v.apply(lambda r: (r['Fin'] if r['Fin']>0 else ANIO_ACTUAL) - r['Debut'] + 1, axis=1)
    st.table(df_v)

elif menu == "💾 RESPALDO":
    st.download_button("📥 Descargar CSV", df_j.to_csv(index=False), "liga_softbol.csv")
    f = st.file_uploader("📤 Restaurar", type="csv")
    if f: pd.read_csv(f).to_csv(JUGADORES_FILE, index=False); st.rerun()

elif menu == "📜 HISTORIAL":
    if not df_j.empty:
        j = st.selectbox("Jugador:", sorted(df_j["Nombre"].unique()))
        d = df_j[df_j["Nombre"] == j].iloc
        st.subheader(f"Ficha: {d['Nombre']}")
        st.write(f"**AVG:** {(d['H']/d['VB'] if d['VB']>0 else 0):.3f} | **Categoría:** {d['Categoria']}")
        st.write(f"**Stats:** H:{int(d['H'])} | 2B:{int(d['2B'])} | 3B:{int(d['3B'])} | HR:{int(d['HR'])} | G:{int(d['G'])} | P:{int(d['P'])}")
