import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN Y REPARACIÓN ---
CARPETA_DATOS = "datos_liga"
if not os.path.exists(CARPETA_DATOS):
    os.makedirs(CARPETA_DATOS)

def ruta(archivo):
    return os.path.join(CARPETA_DATOS, archivo)

# Estructura obligatoria
COLS_J = ["Nombre", "Edad", "Equipo", "VB", "H", "H2", "H3", "HR"]
COLS_P = ["Nombre", "Equipo", "JG", "JP", "IP", "CL"]

def cargar_y_reparar(nombre_archivo, columnas_esperadas):
    path = ruta(nombre_archivo)
    if os.path.exists(path):
        try:
            df = pd.read_csv(path)
            # 1. Limpiar nombres de columnas (quitar espacios y saltos de línea)
            df.columns = [str(c).strip() for c in df.columns]
            # 2. Agregar columnas que falten
            for col in columnas_esperadas:
                if col not in df.columns:
                    df[col] = 0
            # 3. Forzar que las columnas de números sean realmente números
            for col in columnas_esperadas:
                if col != "Nombre" and col != "Equipo":
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            return df[columnas_esperadas]
        except:
            return pd.DataFrame(columns=columnas_esperadas)
    return pd.DataFrame(columns=columnas_esperadas)

def inicializar_datos():
    if 'equipos' not in st.session_state:
        st.session_state.equipos = cargar_y_reparar("data_equipos.csv", ["Nombre"])
    if 'jugadores' not in st.session_state:
        st.session_state.jugadores = cargar_y_reparar("data_jugadores.csv", COLS_J)
    if 'pitchers' not in st.session_state:
        st.session_state.pitchers = cargar_y_reparar("data_pitchers.csv", COLS_P)

def guardar_datos():
    st.session_state.equipos.to_csv(ruta("data_equipos.csv"), index=False)
    st.session_state.jugadores.to_csv(ruta("data_jugadores.csv"), index=False)
    st.session_state.pitchers.to_csv(ruta("data_pitchers.csv"), index=False)

inicializar_datos()

# --- 2. INTERFAZ Y LÓGICA ---
st.sidebar.title("⚾ LIGA SOFTBOL 2026")
with st.sidebar.form("login"):
    pwd = st.text_input("Contraseña Admin:", type="password")
    st.form_submit_button("Entrar")

es_admin = (pwd == "softbol2026")
menu = st.sidebar.radio("MENÚ:", ["🏆 TOP 10 LÍDERES", "🏃 Bateo", "🔥 Pitcheo", "👥 Equipos"])

if menu == "🏆 TOP 10 LÍDERES":
    st.header("🏆 Líderes de la Liga")
    if not st.session_state.jugadores.empty:
        df_b = st.session_state.jugadores.copy()
        # Cálculo ULTRA seguro de AVG
        # Sumamos hits y dividimos por VB (si VB es 0, usamos 1 para no fallar)
        hits = df_b['H'] + df_b['H2'] + df_b['H3'] + df_b['HR']
        df_b['AVG'] = (hits / df_b['VB'].replace(0, 1)).fillna(0).round(3)
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🥇 Promedio (AVG)")
            st.table(df_b.sort_values("AVG", ascending=False).head(10)[["Nombre", "AVG"]])
        with c2:
            st.subheader("🥇 Jonrones (HR)")
            st.table(df_b.sort_values("HR", ascending=False).head(10)[["Nombre", "HR"]])
    else:
        st.info("No hay datos todavía.")

elif menu == "🏃 Bateo":
    st.header("Registrar Bateador")
    if es_admin:
        with st.form("form_b"):
            n = st.text_input("Nombre")
            eq = st.selectbox("Equipo", st.session_state.equipos['Nombre'] if not st.session_state.equipos.empty else ["N/A"])
            c1, c2, c3, c4, c5 = st.columns(5)
            v = c1.number_input("VB", 1)
            h1 = c2.number_input("H1", 0); h2 = c3.number_input("H2", 0)
            h3 = c4.number_input("H3", 0); hr = c5.number_input("HR", 0)
            if st.form_submit_button("Guardar"):
                nueva = pd.DataFrame([{"Nombre": n, "Edad": 0, "Equipo": eq, "VB": v, "H": h1, "H2": h2, "H3": h3, "HR": hr}])
                st.session_state.jugadores = pd.concat([st.session_state.jugadores, nueva], ignore_index=True)
                guardar_datos(); st.rerun()
    st.dataframe(st.session_state.jugadores)

elif menu == "👥 Equipos":
    if es_admin:
        nuevo_eq = st.text_input("Nuevo Equipo")
        if st.button("Agregar"):
            st.session_state.equipos = pd.concat([st.session_state.equipos, pd.DataFrame([{"Nombre": nuevo_eq}])], ignore_index=True)
            guardar_datos(); st.rerun()
    st.table(st.session_state.equipos)
