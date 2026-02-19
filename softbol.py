import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN DE ARCHIVOS ---
CARPETA_DATOS = "datos_liga"
if not os.path.exists(CARPETA_DATOS): os.makedirs(CARPETA_DATOS)

def ruta(archivo): return os.path.join(CARPETA_DATOS, archivo)

COLS_J = ["Nombre", "Edad", "Equipo", "VB", "H", "H2", "H3", "HR"]

def cargar_jugadores():
    if os.path.exists(ruta("data_jugadores.csv")):
        df = pd.read_csv(ruta("data_jugadores.csv"))
        df.columns = df.columns.str.strip()
        for col in COLS_J:
            if col not in df.columns: df[col] = 0
        # Convertir a números para que el AVG funcione
        for c in ["VB", "H", "H2", "H3", "HR"]:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
        return df[COLS_J]
    return pd.DataFrame(columns=COLS_J)

# Inicializar sesión
if 'jugadores' not in st.session_state: st.session_state.jugadores = cargar_jugadores()
if 'equipos' not in st.session_state:
    st.session_state.equipos = pd.read_csv(ruta("data_equipos.csv")) if os.path.exists(ruta("data_equipos.csv")) else pd.DataFrame(columns=["Nombre"])

# --- 2. INTERFAZ ---
st.sidebar.title("⚾ LIGA SOFTBOL 2026")
menu = st.sidebar.radio("MENÚ:", ["🏆 TOP 10 LÍDERES", "🏃 Bateo", "👥 Equipos"])

# ==========================================
# SECCIÓN: TOP 10 LÍDERES (CON AVG EN MILÉSIMAS)
# ==========================================
if menu == "🏆 TOP 10 LÍDERES":
    st.header("🏆 Cuadro de Honor (Milésimas)")
    df_l = st.session_state.jugadores.copy()
    
    if not df_l.empty:
        # CÁLCULO AUTOMÁTICO DE AVG
        hits = df_l['H'] + df_l['H2'] + df_l['H3'] + df_l['HR']
        df_l['AVG'] = (hits / df_l['VB'].replace(0, 1)).fillna(0)
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🥇 Promedio (AVG)")
            res_avg = df_l.sort_values("AVG", ascending=False).head(10)[["Nombre", "AVG"]]
            # Mostramos con 3 decimales fijos (.333)
            st.table(res_avg.style.format({"AVG": "{:.3f}"}))
            
            st.subheader("🥇 Jonrones (HR)")
            st.table(df_l.sort_values("HR", ascending=False).head(10)[["Nombre", "HR"]])
        with c2:
            st.subheader("🥇 Triples (H3)")
            st.table(df_l.sort_values("H3", ascending=False).head(10)[["Nombre", "H3"]])
            st.subheader("🥇 Dobles (H2)")
            st.table(df_l.sort_values("H2", ascending=False).head(10)[["Nombre", "H2"]])
    else: st.info("No hay datos.")

# ==========================================
# SECCIÓN: BATEO (EDITAR Y BORRAR)
# ==========================================
elif menu == "🏃 Bateo":
    st.header("🏃 Gestión de Bateadores")
    
    tab1, tab2 = st.tabs(["➕ Nuevo / Editar", "🗑️ Borrar Registro"])
    
    with tab1:
        # Selección para editar
        nombres_jugadores = ["-- Nuevo Jugador --"] + st.session_state.jugadores["Nombre"].tolist()
        seleccion = st.selectbox("Selecciona para editar o deja en Nuevo:", nombres_jugadores)
        
        # Valores por defecto
        val_n, val_eq, val_vb, val_h, val_h2, val_h3, val_hr = "", "", 1, 0, 0, 0, 0
        
        if seleccion != "-- Nuevo Jugador --":
            j_edit = st.session_state.jugadores[st.session_state.jugadores["Nombre"] == seleccion].iloc[0]
            val_n, val_eq, val_vb, val_h, val_h2, val_h3, val_hr = j_edit["Nombre"], j_edit["Equipo"], int(j_edit["VB"]), int(j_edit["H"]), int(j_edit["H2"]), int(j_edit["H3"]), int(j_edit["HR"])

        with st.form("form_bateo"):
            nom = st.text_input("Nombre", value=val_n)
            eq = st.selectbox("Equipo", st.session_state.equipos["Nombre"].tolist() if not st.session_state.equipos.empty else ["N/A"])
            c1, c2, c3, c4, c5 = st.columns(5)
            vb = c1.number_input("VB", min_value=1, value=val_vb)
            h = c2.number_input("H1", value=val_h); h2 = c3.number_input("H2", value=val_h2)
            h3 = c4.number_input("H3", value=val_h3); hr = c5.number_input("HR", value=val_hr)
            
            btn_txt = "Actualizar Datos" if seleccion != "-- Nuevo Jugador --" else "Guardar Nuevo"
            if st.form_submit_button(btn_txt):
                if seleccion != "-- Nuevo Jugador --":
                    st.session_state.jugadores = st.session_state.jugadores[st.session_state.jugadores["Nombre"] != seleccion]
                
                nueva = pd.DataFrame([{"Nombre": nom, "Edad": 0, "Equipo": eq, "VB": vb, "H": h, "H2": h2, "H3": h3, "HR": hr}])
                st.session_state.jugadores = pd.concat([st.session_state.jugadores, nueva], ignore_index=True)
                st.session_state.jugadores.to_csv(ruta("data_jugadores.csv"), index=False)
                st.success("¡Operación exitosa!"); st.rerun()

    with tab2:
        if not st.session_state.jugadores.empty:
            borrar_sel = st.selectbox("Selecciona jugador a ELIMINAR:", st.session_state.jugadores["Nombre"].tolist())
            if st.button("Confirmar Borrado ❌"):
                st.session_state.jugadores = st.session_state.jugadores[st.session_state.jugadores["Nombre"] != borrar_sel]
                st.session_state.jugadores.to_csv(ruta("data_jugadores.csv"), index=False)
                st.warning(f"Jugador {borrar_sel} eliminado."); st.rerun()

    st.subheader("📋 Tabla General")
    st.dataframe(st.session_state.jugadores, use_container_width=True)

# ==========================================
# SECCIÓN: EQUIPOS
# ==========================================
elif menu == "👥 Equipos":
    st.header("👥 Equipos")
    n_e = st.text_input("Nombre del Equipo")
    if st.button("Agregar"):
        st.session_state.equipos = pd.concat([st.session_state.equipos, pd.DataFrame([{"Nombre": n_e}])], ignore_index=True)
        st.session_state.equipos.to_csv(ruta("data_equipos.csv"), index=False)
        st.rerun()
    st.table(st.session_state.equipos)
