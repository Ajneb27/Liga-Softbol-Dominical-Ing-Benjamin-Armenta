import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN DE CARPETA Y DATOS ---
CARPETA_DATOS = "datos_liga"
if not os.path.exists(CARPETA_DATOS):
    os.makedirs(CARPETA_DATOS)

def ruta(archivo):
    return os.path.join(CARPETA_DATOS, archivo)

# Inicializar bases de datos
if 'equipos' not in st.session_state:
    st.session_state.equipos = pd.read_csv(ruta("data_equipos.csv")) if os.path.exists(ruta("data_equipos.csv")) else pd.DataFrame(columns=["Nombre"])

if 'jugadores' not in st.session_state:
    if os.path.exists(ruta("data_jugadores.csv")):
        df = pd.read_csv(ruta("data_jugadores.csv"))
        # Asegurar columnas H, H2, H3, HR
        for c in ["H", "H2", "H3", "HR"]:
            if c not in df.columns: df[c] = 0
        st.session_state.jugadores = df
    else:
        st.session_state.jugadores = pd.DataFrame(columns=["Nombre", "Edad", "Equipo", "H", "H2", "H3", "HR"])

def guardar_datos():
    st.session_state.equipos.to_csv(ruta("data_equipos.csv"), index=False)
    st.session_state.jugadores.to_csv(ruta("data_jugadores.csv"), index=False)

# --- 2. BARRA LATERAL (LOGIN) ---
st.sidebar.title("⚾ LIGA SOFTBOL 2026")
pwd = st.sidebar.text_input("Contraseña Admin:", type="password")
pass_m = open(ruta("config.txt"), "r").read().strip() if os.path.exists(ruta("config.txt")) else "softbol2026"
es_admin = (pwd == pass_m)

menu = st.sidebar.radio("MENÚ:", ["🏠 Inicio", "👥 Equipos", "🏃 Jugadores y Stats", "📊 Consulta por Equipo"])

# ==========================================
# SECCIÓN: CONSULTA POR EQUIPO (FILTRO DE ROSTER)
# ==========================================
if menu == "📊 Consulta por Equipo":
    st.header("📊 Consulta de Roster y Estadísticas")
    
    # Obtenemos la lista de equipos registrados
    lista_eq = st.session_state.equipos['Nombre'].tolist()
    
    if not lista_eq:
        st.warning("⚠️ No hay equipos registrados todavía. Ve a la sección 'Equipos'.")
    else:
        # AQUÍ ES DONDE SE SELECCIONA EL EQUIPO
        eq_seleccionado = st.selectbox("🎯 Selecciona un equipo para ver su Roster:", ["-- Seleccionar --"] + lista_eq)
        
        if eq_seleccionado != "-- Seleccionar --":
            # Filtramos los jugadores que pertenecen a ese equipo
            roster = st.session_state.jugadores[st.session_state.jugadores['Equipo'] == eq_seleccionado].copy()
            
            if roster.empty:
                st.info(f"El equipo **{eq_seleccionado}** aún no tiene jugadores asignados.")
            else:
                st.subheader(f"Jugadores de {eq_seleccionado}")
                # Calculamos hits totales para la vista rápida
                roster["TOTAL"] = roster["H"] + roster["H2"] + roster["H3"] + roster["HR"]
                
                # Mostramos la tabla filtrada
                st.dataframe(roster[["Nombre", "Edad", "H", "H2", "H3", "HR", "TOTAL"]], use_container_width=True)
                st.write(f"Total de jugadores en el roster: **{len(roster)}**")
        else:
            st.info("Elige un equipo del menú de arriba para ver sus detalles.")

# ==========================================
# (EL RESTO DEL CÓDIGO SE MANTIENE PARA GESTIÓN)
# ==========================================
elif menu == "👥 Equipos":
    st.header("👥 Gestión de Equipos")
    if es_admin:
        with st.form("f_eq"):
            n_eq = st.text_input("Nombre del Nuevo Equipo")
            if st.form_submit_button("Guardar Equipo"):
                if n_eq and n_eq not in st.session_state.equipos['Nombre'].values:
                    st.session_state.equipos = pd.concat([st.session_state.equipos, pd.DataFrame([{"Nombre": n_eq}])], ignore_index=True)
                    guardar_datos(); st.success(f"Equipo {n_eq} listo."); st.rerun()
    st.table(st.session_state.equipos)

elif menu == "🏃 Jugadores y Stats":
    st.header("🏃 Estadísticas de Jugadores")
    # ... (Misma lógica de registro y edición anterior)
    st.dataframe(st.session_state.jugadores, use_container_width=True)
