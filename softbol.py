import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN DE RUTAS ---
CARPETA_DATOS = "datos_liga"
if not os.path.exists(CARPETA_DATOS):
    os.makedirs(CARPETA_DATOS)

def ruta(archivo):
    return os.path.join(CARPETA_DATOS, archivo)

# Columnas estrictas
COLS_J = ["Nombre", "Edad", "Equipo", "VB", "H", "H2", "H3", "HR"]

# --- 2. FUNCIÓN DE CARGA SEGURA (ELIMINA EL KEYERROR) ---
def cargar_datos_seguros():
    path = ruta("data_jugadores.csv")
    if os.path.exists(path):
        try:
            df = pd.read_csv(path)
            # Limpieza total de nombres de columnas
            df.columns = df.columns.str.strip()
            # Asegurar que cada columna requerida exista con ceros
            for col in COLS_J:
                if col not in df.columns:
                    df[col] = 0
            # Retornar solo las columnas necesarias en el orden correcto
            return df[COLS_J]
        except:
            return pd.DataFrame(columns=COLS_J)
    return pd.DataFrame(columns=COLS_J)

# Inicializar sesión
if 'jugadores' not in st.session_state:
    st.session_state.jugadores = cargar_datos_seguros()
if 'equipos' not in st.session_state:
    st.session_state.equipos = pd.read_csv(ruta("data_equipos.csv")) if os.path.exists(ruta("data_equipos.csv")) else pd.DataFrame(columns=["Nombre"])

# --- 3. INTERFAZ ---
st.sidebar.title("⚾ LIGA SOFTBOL 2026")
menu = st.sidebar.radio("MENÚ:", ["🏆 TOP 10 LÍDERES", "🏃 Bateo", "👥 Equipos"])

# ==========================================
# SECCIÓN LÍDERES (DONDE OCURRE EL ERROR)
# ==========================================
if menu == "🏆 TOP 10 LÍDERES":
    st.header("🏆 Líderes de Bateo")
    
    # RE-VALIDACIÓN ANTES DEL CÁLCULO
    df_b = st.session_state.jugadores.copy()
    
    # Verificación extra: Si 'VB' no está, la creamos aquí mismo para que no falle la línea 68
    if 'VB' not in df_b.columns:
        for col in COLS_J: df_b[col] = 0

    # Convertir a números para evitar errores de tipo
    for c in ['H', 'H2', 'H3', 'HR', 'VB']:
        df_b[c] = pd.to_numeric(df_b[c], errors='coerce').fillna(0)

    if not df_b.empty:
        # Cálculo con protección contra división por cero y KeyError
        hits = df_b['H'] + df_b['H2'] + df_b['H3'] + df_b['HR']
        df_b['AVG'] = (hits / df_b['VB'].replace(0, 1)).fillna(0).round(3)
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🥇 Top AVG")
            st.table(df_b.sort_values("AVG", ascending=False).head(10)[["Nombre", "AVG"]])
        with c2:
            st.subheader("🥇 Top HR")
            st.table(df_b.sort_values("HR", ascending=False).head(10)[["Nombre", "HR"]])
    else:
        st.info("No hay datos registrados.")

# ==========================================
# SECCIÓN REGISTRO
# ==========================================
elif menu == "🏃 Bateo":
    st.header("Registrar Estadísticas")
    with st.form("nuevo_b"):
        nom = st.text_input("Nombre")
        # Evitar error si no hay equipos
        lista_eq = st.session_state.equipos['Nombre'].tolist() if not st.session_state.equipos.empty else ["General"]
        eq = st.selectbox("Equipo", lista_eq)
        
        c1, c2, c3, c4, c5 = st.columns(5)
        vb_in = c1.number_input("VB", 1)
        h1_in = c2.number_input("H1", 0)
        h2_in = c3.number_input("H2", 0)
        h3_in = c4.number_input("H3", 0)
        hr_in = c5.number_input("HR", 0)
        
        if st.form_submit_button("Guardar"):
            nueva_fila = pd.DataFrame([{"Nombre": nom, "Edad": 0, "Equipo": eq, "VB": vb_in, "H": h1_in, "H2": h2_in, "H3": h3_in, "HR": hr_in}])
            st.session_state.jugadores = pd.concat([st.session_state.jugadores, nueva_fila], ignore_index=True)
            # Guardar físicamente
            st.session_state.jugadores.to_csv(ruta("data_jugadores.csv"), index=False)
            st.success("¡Datos guardados!")
            st.rerun()

    st.subheader("Base de Datos Actual")
    st.dataframe(st.session_state.jugadores)

elif menu == "👥 Equipos":
    nombre_e = st.text_input("Nombre del Equipo")
    if st.button("Agregar"):
        nuevo_e = pd.DataFrame([{"Nombre": nombre_e}])
        st.session_state.equipos = pd.concat([st.session_state.equipos, nuevo_e], ignore_index=True)
        st.session_state.equipos.to_csv(ruta("data_equipos.csv"), index=False)
        st.rerun()
    st.table(st.session_state.equipos)
