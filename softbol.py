import streamlit as st
import pandas as pd
import os
import urllib.parse

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="LIGA SOFTBOL BENJAMIN ARMENTA", page_icon="⚾", layout="wide", initial_sidebar_state="collapsed")

# Carpetas de almacenamiento
CARPETA_DATOS = "datos_liga"
CARPETA_FOTOS = "galeria_liga"
for c in [CARPETA_DATOS, CARPETA_FOTOS]:
    if not os.path.exists(c): os.makedirs(c)

def ruta(archivo): return os.path.join(CARPETA_DATOS, archivo)

# --- 2. CARGA DE DATOS ---
COLS_J = ["Nombre", "Equipo", "VB", "H", "H2", "H3", "HR"]
COLS_P = ["Nombre", "Equipo", "JG", "JP", "IP", "CL"]
COLS_CAL = ["Fecha", "Hora", "Campo", "Local", "Visitante", "Score"]

def cargar_datos(archivo, columnas):
    path = ruta(archivo)
    if os.path.exists(path):
        df = pd.read_csv(path)
        for col in columnas:
            if col not in df.columns: df[col] = "" if col == "Score" else 0
        return df[columnas]
    return pd.DataFrame(columns=columnas)

st.session_state.jugadores = cargar_datos("data_jugadores.csv", COLS_J)
st.session_state.pitchers = cargar_datos("data_pitchers.csv", COLS_P)
st.session_state.equipos = cargar_datos("data_equipos.csv", ["Nombre"])
st.session_state.calendario = cargar_datos("data_calendario.csv", COLS_CAL)

# --- 3. SIDEBAR / LOGIN ---
if 'autenticado' not in st.session_state: st.session_state.autenticado = False
with st.sidebar:
    st.title("⚾ MENÚ LIGA")
    if not st.session_state.autenticado:
        with st.form("login"):
            pwd = st.text_input("Contraseña:", type="password")
            if st.form_submit_button("Entrar"):
                if pwd == "softbol2026": st.session_state.autenticado = True; st.rerun()
    else:
        st.success("🔓 MODO ADMIN")
        if st.button("Cerrar Sesión"): st.session_state.autenticado = False; st.rerun()

menu = st.sidebar.radio("IR A:", ["🏠 Inicio", "🏆 LÍDERES", "📅 Programación (Admin)", "🖼️ Galería", "📊 Standings", "📋 Rosters", "🏃 Admin Stats"])

# ==========================================
# SECCIÓN: INICIO (GALERÍA + ROL + SCORES)
# ==========================================
if menu == "🏠 Inicio":
    st.markdown("<h1 style='text-align: center;'>⚾ LIGA BENJAMIN ARMENTA 2026</h1>", unsafe_allow_html=True)
    st.divider()

    # Galería Dinámica (Top 3 fotos)
    fotos = sorted(os.listdir(CARPETA_FOTOS), reverse=True)
    if fotos:
        st.subheader("📸 Galería Reciente")
        cols_gal = st.columns(3)
        for i, foto in enumerate(fotos[:3]):
            with cols_gal[i]: st.image(os.path.join(CARPETA_FOTOS, foto), use_container_width=True)
    
    st.divider()

    # Rol de Juegos y Resultados
    st.subheader("📅 Programación y Resultados")
    if not st.session_state.calendario.empty:
        # Estilo para resaltar la columna Score
        st.dataframe(st.session_state.calendario, use_container_width=True, hide_index=True)
    else:
        st.info("No hay juegos programados aún.")

# ==========================================
# SECCIÓN: PROGRAMACIÓN ADMIN (CON SCORE)
# ==========================================
elif menu == "📅 Programación (Admin)":
    if not st.session_state.autenticado: st.warning("Inicia sesión como administrador.")
    else:
        st.header("⚙️ Editar Rol de Juegos")
        with st.form("f_cal"):
            c1, c2, c3 = st.columns(3)
            f = c1.date_input("Fecha"); h = c2.text_input("Hora"); cp = c3.text_input("Campo")
            loc = st.selectbox("Local", st.session_state.equipos["Nombre"].tolist())
            vis = st.selectbox("Visitante", st.session_state.equipos["Nombre"].tolist())
            sc = st.text_input("Score (ej: 5 - 2)", help="Dejar vacío si no se ha jugado")
            if st.form_submit_button("Añadir / Actualizar Juego"):
                nuevo = pd.DataFrame([[f, h, cp, loc, vis, sc]], columns=COLS_CAL)
                st.session_state.calendario = pd.concat([st.session_state.calendario, nuevo], ignore_index=True)
                st.session_state.calendario.to_csv(ruta("data_calendario.csv"), index=False)
                st.rerun()
        
        if st.button("🗑️ Borrar Todo el Calendario"):
            if os.path.exists(ruta("data_calendario.csv")): os.remove(ruta("data_calendario.csv")); st.rerun()

# ==========================================
# SECCIÓN: ROSTER + COMPARTIR WHATSAPP
# ==========================================
elif menu == "📋 Rosters":
    if not st.session_state.equipos.empty:
        eq_s = st.selectbox("Selecciona Equipo:", st.session_state.equipos["Nombre"].tolist())
        df_r = st.session_state.jugadores[st.session_state.jugadores["Equipo"] == eq_s].copy()
        
        if not df_r.empty:
            df_r['AVG'] = ((df_r['H']+df_r['H2']+df_r['H3']+df_r['HR'])/df_r['VB'].replace(0,1)).fillna(0)
            st.dataframe(df_r[["Nombre", "VB", "H", "H2", "H3", "HR", "AVG"]].style.format({"AVG": "{:.3f}"}), use_container_width=True)
            
            # Botón Compartir
            texto = f"Estadísticas del Equipo {eq_s} - Liga Benjamin Armenta ⚾"
            link_wa = f"https://wa.me{urllib.parse.quote(texto)}"
            st.markdown(f'[📲 Compartir Roster en WhatsApp]({link_wa})')
    else: st.warning("Crea equipos primero.")

# ==========================================
# SECCIÓN: GALERÍA (GESTIÓN)
# ==========================================
elif menu == "🖼️ Galería":
    st.header("📸 Galería de Fotos")
    if st.session_state.autenticado:
        subida = st.file_uploader("Subir Fotos:", accept_multiple_files=True)
        if st.button("Guardar Fotos"):
            for img in subida:
                with open(os.path.join(CARPETA_FOTOS, img.name), "wb") as f: f.write(img.getbuffer())
            st.rerun()
    
    fotos = os.listdir(CARPETA_FOTOS)
    cols = st.columns(4)
    for i, f in enumerate(fotos):
        with cols[i % 4]: 
            st.image(os.path.join(CARPETA_FOTOS, f), use_container_width=True)
            if st.session_state.autenticado:
                if st.button(f"Eliminar {i}"): os.remove(os.path.join(CARPETA_FOTOS, f)); st.rerun()

# (Nota: Se deben incluir las secciones de LÍDERES, STANDINGS y ADMIN STATS de los códigos anteriores para que la app esté completa)
