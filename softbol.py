import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN E IDENTIDAD ---
NOMBRE_LIGA = "LIGA DE SOFTBOL DOMINICAL"
ANIO_INICIO_LIGA = 2024
ANIO_ACTUAL = 2026

DATA_DIR = "liga_softbol_final_2026"
if not os.path.exists(DATA_DIR): 
    os.makedirs(DATA_DIR)

JUGADORES_FILE = os.path.join(DATA_DIR, "jugadores_master.csv")
EQUIPOS_FILE = os.path.join(DATA_DIR, "equipos_master.csv")

# --- 2. MOTOR DE DATOS ---
def cargar_jugadores():
    cols_obligatorias = ["Nombre", "Equipo", "Categoria", "VB", "H", "2B", "3B", "HR", "G", "P"]
    if os.path.exists(JUGADORES_FILE):
        try:
            df = pd.read_csv(JUGADORES_FILE)
            for c in cols_obligatorias:
                if c not in df.columns: 
                    df[c] = "Softbolista" if c == "Categoria" else 0
        except: 
            df = pd.DataFrame(columns=cols_obligatorias)
    else: 
        df = pd.DataFrame(columns=cols_obligatorias)
    
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

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .gold-header { color: #d4af37; font-weight: bold; border-bottom: 3px solid #d4af37; padding-bottom: 10px; margin-bottom: 20px; }
    .stMetric { background-color: white; border-radius: 10px; border-left: 5px solid #d4af37; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

if 'admin' not in st.session_state: 
    st.session_state.admin = False

df_j = cargar_jugadores()
df_e = cargar_equipos()

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.title(f"🏆 {NOMBRE_LIGA}")
    if not st.session_state.admin:
        with st.expander("🔐 Acceso Administrador"):
            u = st.text_input("Usuario")
            p = st.text_input("Clave", type="password")
            if st.button("Entrar"):
                if u == "admin" and p == "123": 
                    st.session_state.admin = True
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")
    else:
        st.success("Modo Admin: ACTIVADO")
        if st.button("Cerrar Sesión"): 
            st.session_state.admin = False
            st.rerun()
    
    st.divider()
    menu = st.radio("Secciones:", ["🏠 INICIO", "🏆 LÍDERES", "📋 ROSTERS", "📜 HISTORIAL", "🏘️ EQUIPOS", "✍️ REGISTRAR", "🗑️ BORRAR", "💾 RESPALDO"])

# --- 5. LÓGICA DE NAVEGACIÓN ---

if menu == "🏠 INICIO":
    st.markdown(f"<h1 class='gold-header'>{NOMBRE_LIGA}</h1>", unsafe_allow_html=True)
    st.write(f"### Bienvenidos a la plataforma oficial de estadísticas.")
    st.write(f"Uniendo a la familia deportiva desde Agosto de {ANIO_INICIO_LIGA}.")
    st.info("Utilice el menú lateral para navegar por las estadísticas de los jugadores y equipos.")

elif menu == "🏆 LÍDERES":
    st.markdown("<h1 class='gold-header'>🥇 Cuadro de Honor Departamental</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["⚾ BATEO ACUMULADO", "🎯 PITCHEO ACUMULADO"])
    
    with t1:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Hits (H)")
            st.dataframe(df_j.nlargest(10, 'H')[['Nombre', 'Equipo', 'H']], hide_index=True, use_container_width=True)
            st.subheader("Dobles (2B)")
            st.dataframe(df_j.nlargest(10, '2B')[['Nombre', 'Equipo', '2B']], hide_index=True, use_container_width=True)
        with c2:
            st.subheader("Home Runs (HR)")
            st.dataframe(df_j.nlargest(10, 'HR')[['Nombre', 'Equipo', 'HR']], hide_index=True, use_container_width=True)
            st.subheader("Triples (3B)")
            st.dataframe(df_j.nlargest(10, '3B')[['Nombre', 'Equipo', '3B']], hide_index=True, use_container_width=True)

    with t2:
        c1, c2 = st.columns(2)
        with c1: 
            st.subheader("Ganados (G)")
            st.dataframe(df_j.sort_values('G', ascending=False).head(10)[['Nombre', 'Equipo', 'G']], hide_index=True, use_container_width=True)
        with c2: 
            st.subheader("Perdidos (P)")
            st.dataframe(df_j.sort_values('P', ascending=False).head(10)[['Nombre', 'Equipo', 'P']], hide_index=True, use_container_width=True)

elif menu == "📋 ROSTERS":
    st.markdown("<h1 class='gold-header'>📋 Rosters por Equipo</h1>", unsafe_allow_html=True)
    if not df_e.empty:
        lista_e = df_e[df_e["Fin"] == 0]["Nombre"].unique()
        eq_sel = st.selectbox("Seleccione un Equipo:", lista_e)
        roster = df_j[df_j["Equipo"] == eq_sel]
        st.dataframe(roster, hide_index=True, use_container_width=True)
    else:
        st.warning("No hay equipos registrados.")

elif menu == "📜 HISTORIAL":
    st.markdown("<h1 class='gold-header'>📜 Historial de Carrera</h1>", unsafe_allow_html=True)
    if not df_j.empty:
        j_s = st.selectbox("Seleccionar Jugador:", sorted(df_j["Nombre"].unique().tolist()))
        d = df_j[df_j["Nombre"] == j_s].iloc[0]
        
        st.header(f"Ficha Técnica: {d['Nombre']}")
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Equipo", d['Equipo'])
        col_m2.metric("Categoría", d['Categoria'])
        avg = (d['H'] / d['VB']) if d['VB'] > 0 else 0
        col_m3.metric("Promedio (AVG)", f"{avg:.3f}")
        
        st.divider()
        st.write("### 📊 Totales Acumulados")
        c1, c2 = st.columns(2)
        with c1:
            st.info(f"**BATEO:** VB: {int(d['VB'])} | H: {int(d['H'])} | 2B: {int(d['2B'])} | 3B: {int(d['3B'])} | HR: {int(d['HR'])}")
        with c2:
            st.success(f"**PITCHEO:** Juegos Ganados: {int(d['G'])} | Juegos Perdidos: {int(d['P'])}")
    else: 
        st.info("No hay datos de jugadores disponibles.")

elif menu == "✍️ REGISTRAR":
    if st.session_state.admin:
        st.markdown("<h1 class='gold-header'>✍️ Registro y Actualización</h1>", unsafe_allow_html=True)
        
        sel = st.selectbox("Jugador:", ["NUEVO JUGADOR"] + sorted(df_j["Nombre"].unique().tolist()))
        
        if 'vals' not in st.session_state or st.session_state.get('last_sel') != sel:
            if sel != "NUEVO JUGADOR": 
                st.session_state.vals = df_j[df_j["Nombre"] == sel].iloc[0].to_dict()
            else: 
                st.session_state.vals = {"Nombre": "", "Equipo": None, "Categoria": "Softbolista", "VB": 0, "H": 0, "2B": 0, "3B": 0, "HR": 0, "G": 0, "P": 0}
            st.session_state.last_sel = sel

        st.write("### Acciones Rápidas (Sumar un turno)")
        c1, c2, c3, c4 = st.columns(4)
        if c1.button("H (+1)"): st.session_state.vals["H"]+=1; st.session_state.vals["VB"]+=1; st.rerun()
        if c2.button("HR (+1)"): st.session_state.vals["H"]+=1; st.session_state.vals["HR"]+=1; st.session_state.vals["VB"]+=1; st.rerun()
        if c3.button("G (+1)"): st.session_state.vals["G"]+=1; st.rerun()
        if c4.button("P (+1)"): st.session_state.vals["P"]+=1; st.rerun()

        with st.form("f_reg", clear_on_submit=False):
            col1, col2 = st.columns(2)
            nom_f = col1.text_input("Nombre:", value=st.session_state.vals["Nombre"])
            
            # --- SELECTOR DE CATEGORÍA ---
            cats = ["Novato", "Softbolista", "Refuerzo"]
            try:
                idx_cat = cats.index(st.session_state.vals["Categoria"])
            except:
                idx_cat = 1
            cat_f = col2.selectbox("Categoría:", cats, index=idx_cat)
            
            eq_f = st.selectbox("Equipo:", df_e[df_e["Fin"] == 0]["Nombre"].unique() if not df_e.empty else ["Sin Equipo"])
            
            st.write("Estadísticas:")
            v1, v2, v3, v4, v5 = st.columns(5)
            vb = v1.number_input("VB", value=int(st.session_state.vals["VB"]))
            h = v2.number_input("H", value=int(st.session_state.vals["H"]))
            d2 = v3.number_input("2B", value=int(st.session_state.vals["2B"]))
            d3 = v4.number_input("3B", value=int(st.session_state.vals["3B"]))
            hr = v5.number_input("HR", value=int(st.session_state.vals["HR"]))
            
            g_f = st.number_input("G", value=int(st.session_state.vals["G"]))
            p_f = st.number_input("P", value=int(st.session_state.vals["P"]))
            
            if st.form_submit_button("💾 GUARDAR DATOS"):
                if nom_f:
                    df_j = df_j[df_j["Nombre"] != nom_f]
                    nueva = pd.DataFrame([{"Nombre": nom_f, "Equipo": eq_f, "Categoria": cat_f, "VB": vb, "H": h, "2B": d2, "3B": d3, "HR": hr, "G": g_f, "P": p_f}])
                    pd.concat([df_j, nueva], ignore_index=True).to_csv(JUGADORES_FILE, index=False)
                    st.success("¡Datos guardados!")
                    st.rerun()
                else:
                    st.error("El nombre es obligatorio")
    else: 
        st.warning("Acceso restringido a administradores.")

elif menu == "🏘️ EQUIPOS":
    st.markdown("<h1 class='gold-header'>🏘️ Gestión de Equipos</h1>", unsafe_allow_html=True)
    if st.session_state.admin:
        with st.form("eq"):
            n = st.text_input("Nombre del Equipo:")
            d = st.number_input("Año de Debut:", 2024, 2030, 2024)
            f = st.number_input("Año de Retiro (0 si activo):", 0, 2030, 0)
            if st.form_submit_button("Añadir Equipo"):
                nuevo_e = pd.DataFrame([{"Nombre": n, "Debut": d, "Fin": f}])
                pd.concat([df_e, nuevo_e], ignore_index=True).to_csv(EQUIPOS_FILE, index=False)
                st.success("Equipo registrado.")
                st.rerun()
    
    if not df_e.empty:
        df_v = df_e.copy()
        df_v["Estado"] = df_v["Fin"].apply(lambda x: "Activo" if x == 0 else f"Retirado en {x}")
        st.table(df_v)

elif menu == "🗑️ BORRAR":
    if st.session_state.admin:
        st.markdown("<h1 class='gold-header'>🗑️ Eliminar Registros</h1>", unsafe_allow_html=True)
        j_del = st.selectbox("Seleccione Jugador para borrar:", [""] + sorted(df_j["Nombre"].tolist()))
        if st.button("❌ Confirmar Eliminación Permanente"):
            if j_del != "":
                df_j = df_j[df_j["Nombre"] != j_del]
                df_j.to_csv(JUGADORES_FILE, index=False)
                st.success(f"{j_del} ha sido eliminado.")
                st.rerun()
    else: 
        st.warning("Acceso restringido.")

elif menu == "💾 RESPALDO":
    st.markdown("<h1 class='gold-header'>💾 Gestión de Copias de Seguridad</h1>", unsafe_allow_html=True)
    st.download_button("📥 Descargar Base de Datos (CSV)", df_j.to_csv(index=False), "respaldo_jugadores.csv", "text/csv")
    
    st.divider()
    st.write("### Restaurar Datos")
    f = st.file_uploader("Subir archivo CSV", type="csv")
    if f: 
        df_nuevo = pd.read_csv(f)
        df_nuevo.to_csv(JUGADORES_FILE, index=False)
        st.success("Base de datos restaurada con éxito.")
        st.rerun()
