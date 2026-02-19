import streamlit as st
import pandas as pd

# Configuración estilo "Liga Pro"
st.set_page_config(page_title="Liga Softbol Pro 2026", layout="wide", page_icon="🥎")

# Estilo visual personalizado (Colores de la página de Culiacán)
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { background-color: #d32f2f; color: white; border-radius: 5px; }
    h1 { color: #1a237e; font-family: 'Arial Black'; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏆 Sistema de Liga de Softbol v1.0")

# Menú lateral (Navegación como en la web)
menu = st.sidebar.selectbox("MENÚ PRINCIPAL", ["Inicio", "Tabla de Posiciones", "Registrar Juego"])

# Base de datos simulada (En un futuro esto será un archivo real)
if 'datos_liga' not in st.session_state:
    st.session_state.datos_liga = pd.DataFrame(columns=["Equipo", "JJ", "JG", "JP", "CF", "CC"])

# --- SECCIÓN: TABLA DE POSICIONES ---
if menu == "Tabla de Posiciones":
    st.header("📊 Tabla de Posiciones Actualizada")
    if not st.session_state.datos_liga.empty:
        df = st.session_state.datos_liga.copy()
        # Cálculo de Porcentaje (PCT)
        df['PCT'] = (df['JG'] / df['JJ']).fillna(0).map("{:.3f}".format)
        # Ordenar por juegos ganados
        st.table(df.sort_values(by="JG", ascending=False))
    else:
        st.info("Aún no hay juegos registrados. Ve a 'Registrar Juego'.")

# --- SECCIÓN: REGISTRAR JUEGO ---
elif menu == "Registrar Juego":
    st.header("📝 Anotar Resultado del Encuentro")
    with st.form("registro_juego"):
        col1, col2 = st.columns(2)
        with col1:
            equipo_local = st.text_input("Equipo Local")
            carreras_local = st.number_input("Carreras Local", min_value=0, step=1)
        with col2:
            equipo_visita = st.text_input("Equipo Visita")
            carreras_visita = st.number_input("Carreras Visita", min_value=0, step=1)
        
        btn_juego = st.form_submit_button("Finalizar Juego")

    if btn_juego:
        # Lógica para actualizar tabla
        st.success(f"¡Resultado guardado: {equipo_local} vs {equipo_visita}!")
        # (Aquí podrías agregar la lógica para sumar JG y JP automáticamente)

elif menu == "Inicio":
    st.subheader("Bienvenido a la plataforma de gestión de la liga.")
    st.image("https://images.unsplash.com", caption="Softbol 2026")
