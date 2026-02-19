import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN DE ARCHIVOS ---
CARPETA_DATOS = "datos_liga"
if not os.path.exists(CARPETA_DATOS):
    os.makedirs(CARPETA_DATOS)

def ruta(archivo):
    return os.path.join(CARPETA_DATOS, archivo)

COLS_J = ["Nombre", "Edad", "Equipo", "VB", "H", "H2", "H3", "HR"]

def cargar_jugadores():
    path = ruta("data_jugadores.csv")
    if os.path.exists(path):
        df = pd.read_csv(path)
        df.columns = df.columns.str.strip()
        for col in COLS_J:
            if col not in df.columns: df[col] = 0
        # Aseguramos que todo sea numérico excepto Nombre y Equipo
        cols_num = ["VB", "H", "H2", "H3", "HR"]
        df[cols_num] = df[cols_num].apply(pd.to_numeric, errors='coerce').fillna(0)
        return df[COLS_J]
    return pd.DataFrame(columns=COLS_J)

# Inicializar sesión
if 'jugadores' not in st.session_state:
    st.session_state.jugadores = cargar_jugadores()
if 'equipos' not in st.session_state:
    st.session_state.equipos = pd.read_csv(ruta("data_equipos.csv")) if os.path.exists(ruta("data_equipos.csv")) else pd.DataFrame(columns=["Nombre"])

# --- 2. INTERFAZ ---
st.sidebar.title("⚾ LIGA SOFTBOL 2026")
menu = st.sidebar.radio("MENÚ:", ["🏆 TOP 10 LÍDERES", "🏃 Bateo", "👥 Equipos"])

# ==========================================
# SECCIÓN: TOP 10 LÍDERES (CÁLCULO DE AVG)
# ==========================================
if menu == "🏆 TOP 10 LÍDERES":
    st.header("🏆 Líderes de Bateo")
    
    if not st.session_state.jugadores.empty:
        # Hacemos una copia para calcular sin afectar la base original
        df_lideres = st.session_state.jugadores.copy()
        
        # FÓRMULA: Hits Totales = H (Sencillos) + H2 + H3 + HR
        hits_totales = df_lideres['H'] + df_lideres['H2'] + df_lideres['H3'] + df_lideres['HR']
        
        # CÁLCULO DE AVG: Hits / VB (Vueltas al Bate)
        # Usamos .replace(0, 1) para evitar error si VB es cero
        df_lideres['AVG'] = hits_totales / df_lideres['VB'].replace(0, 1)
        
        # FORMATO: Redondear a 3 decimales (Milésimas)
        df_lideres['AVG'] = df_lideres['AVG'].round(3)
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🥇 Top Average (AVG)")
            # Mostramos la tabla formateada
            tabla_avg = df_lideres.sort_values("AVG", ascending=False).head(10)[["Nombre", "AVG"]]
            st.table(tabla_avg.style.format({"AVG": "{:.3f}"})) # Fuerza el .000
            
            st.subheader("🥇 Home Runs (HR)")
            st.table(df_lideres.sort_values("HR", ascending=False).head(10)[["Nombre", "HR"]])
        with c2:
            st.subheader("🥇 Triples (H3)")
            st.table(df_lideres.sort_values("H3", ascending=False).head(10)[["Nombre", "H3"]])
            
            st.subheader("🥇 Dobles (H2)")
            st.table(df_lideres.sort_values("H2", ascending=False).head(10)[["Nombre", "H2"]])
    else:
        st.info("Aún no hay jugadores registrados.")

# ==========================================
# SECCIÓN: REGISTRO DE BATEO
# ==========================================
elif menu == "🏃 Bateo":
    st.header("Registrar Estadísticas")
    with st.form("nuevo_b"):
        nom = st.text_input("Nombre del Jugador")
        lista_eq = st.session_state.equipos['Nombre'].tolist() if not st.session_state.equipos.empty else ["Independiente"]
        eq = st.selectbox("Equipo", lista_eq)
        
        c1, c2, c3, c4, c5 = st.columns(5)
        vb_in = c1.number_input("VB (Turnos)", min_value=1, value=1)
        h1_in = c2.number_input("H (Sencillos)", 0)
        h2_in = c3.number_input("H2 (Dobles)", 0)
        h3_in = c4.number_input("H3 (Triples)", 0)
        hr_in = c5.number_input("HR (Jonrones)", 0)
        
        if st.form_submit_button("Guardar Registro"):
            nueva_fila = pd.DataFrame([{"Nombre": nom, "Edad": 0, "Equipo": eq, "VB": vb_in, "H": h1_in, "H2": h2_in, "H3": h3_in, "HR": hr_in}])
            st.session_state.jugadores = pd.concat([st.session_state.jugadores, nueva_fila], ignore_index=True)
            st.session_state.jugadores.to_csv(ruta("data_jugadores.csv"), index=False)
            st.success(f"¡{nom} registrado con éxito!")
            st.rerun()

    st.subheader("Registros actuales")
    st.dataframe(st.session_state.jugadores, use_container_width=True)

# ==========================================
# SECCIÓN: EQUIPOS
# ==========================================
elif menu == "👥 Equipos":
    st.header("Gestión de Equipos")
    nombre_e = st.text_input("Nombre del Nuevo Equipo")
    if st.button("Registrar Equipo"):
        if nombre_e:
            nuevo_e = pd.DataFrame([{"Nombre": nombre_e}])
            st.session_state.equipos = pd.concat([st.session_state.equipos, nuevo_e], ignore_index=True)
            st.session_state.equipos.to_csv(ruta("data_equipos.csv"), index=False)
            st.rerun()
    st.table(st.session_state.equipos)
