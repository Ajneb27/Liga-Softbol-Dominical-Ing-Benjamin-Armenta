import streamlit as st
import pandas as pd
import os

# 1. CONFIGURACIÓN INICIAL
st.set_page_config(page_title="SISTEMA LIGA", layout="wide")

# Nombre de la carpeta de datos
FOLDER = "datos_liga_v2"
if not os.path.exists(FOLDER):
    os.makedirs(FOLDER)

# 2. FUNCIÓN MAESTRA DE CARGA/GUARDADO
def procesar_datos(nombre_tabla):
    ruta = os.path.join(FOLDER, f"{nombre_tabla}.csv")
    
    # Si el archivo NO existe, creamos uno con datos de prueba
    if not os.path.exists(ruta):
        if nombre_tabla == "equipos":
            df = pd.DataFrame({"Nombre": ["Equipo de Prueba 1", "Equipo de Prueba 2"]})
        else:
            df = pd.DataFrame(columns=["Nombre", "Equipo", "VB", "H"])
        df.to_csv(ruta, index=False)
    
    # Intentar leer el archivo
    try:
        return pd.read_csv(ruta)
    except Exception as e:
        st.error(f"Error cargando {nombre_tabla}: {e}")
        return pd.DataFrame()

# 3. CARGAR EN MEMORIA
if "equipos" not in st.session_state:
    st.session_state.equipos = procesar_datos("equipos")
if "jugadores" not in st.session_state:
    st.session_state.jugadores = procesar_datos("jugadores")

# 4. INTERFAZ DE USUARIO
st.title("⚾ LIGA DE SOFTBOL - REINICIO TOTAL")

# Barra lateral para acciones
with st.sidebar:
    st.header("⚙️ Herramientas")
    if st.button("🔄 Forzar Recarga (Limpiar todo)"):
        st.cache_data.clear()
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

tab1, tab2 = st.tabs(["📊 Ver Datos", "➕ Añadir Equipos"])

with tab1:
    st.subheader("Equipos Registrados")
    if st.session_state.equipos.empty:
        st.warning("No hay equipos en la base de datos.")
    else:
        st.table(st.session_state.equipos)
    
    st.subheader("Lista de Jugadores")
    st.dataframe(st.session_state.jugadores, use_container_width=True)

with tab2:
    st.subheader("Registrar Nuevo Equipo")
    nuevo_eq = st.text_input("Nombre del Equipo:")
    if st.button("Guardar Equipo"):
        if nuevo_eq:
            # Crear el nuevo DataFrame
            nuevo_df = pd.concat([st.session_state.equipos, pd.DataFrame([{"Nombre": nuevo_eq}])], ignore_index=True)
            # Guardar físicamente
            ruta_eq = os.path.join(FOLDER, "equipos.csv")
            nuevo_df.to_csv(ruta_eq, index=False)
            # Actualizar memoria
            st.session_state.equipos = nuevo_df
            st.success(f"¡{nuevo_eq} guardado con éxito!")
            st.rerun()
        else:
            st.error("Escribe un nombre válido.")
