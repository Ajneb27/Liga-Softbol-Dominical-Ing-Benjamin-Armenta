import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN DE CARPETA ---
CARPETA_DATOS = "datos_liga"
if not os.path.exists(CARPETA_DATOS):
    os.makedirs(CARPETA_DATOS)

def ruta(archivo):
    return os.path.join(CARPETA_DATOS, archivo)

# --- 2. INICIALIZAR CONTRASEÑA SI NO EXISTE ---
if not os.path.exists(ruta("config.txt")):
    with open(ruta("config.txt"), "w") as f:
        f.write("softbol2026")

# --- 3. LEER LA CLAVE ACTUAL ---
with open(ruta("config.txt"), "r") as f:
    pass_maestra = f.read().strip()

# --- 4. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Liga Softbol Pro 2026", layout="wide", page_icon="🥎")

# --- 5. BARRA LATERAL (LOGIN MEJORADO) ---
st.sidebar.title("🔐 Acceso de Liga")

# Usamos un formulario para el login para que el "Enter" funcione siempre
with st.sidebar.form("login_form"):
    pwd_input = st.text_input("Contraseña Admin:", type="password")
    boton_login = st.form_submit_button("Entrar / Validar")

# Variable que define si eres admin o no
es_admin = (pwd_input == pass_maestra)

if boton_login:
    if es_admin:
        st.sidebar.success("✅ ¡Acceso Correcto!")
    else:
        st.sidebar.error("❌ Clave Incorrecta")

st.sidebar.markdown("---")
menu = st.sidebar.radio("IR A:", ["🏆 Standings", "🥖 Bateo", "🔥 Pitcheo", "📅 Rol", "⚙️ CONFIG"])

# --- 6. ESTILO VISUAL ---
st.markdown(f"""
    <style>
    .block-container {{ background-color: rgba(255, 255, 255, 0.95); padding: 30px; border-radius: 15px; }}
    [data-testid="stSidebar"] input {{ color: black !important; }}
    h1, h2, h3 {{ color: #b71c1c !important; text-align: center; }}
    </style>
    """, unsafe_allow_html=True)

# --- 7. SECCIÓN DE PRUEBA (Para ver si funciona) ---
if menu == "🥖 Bateo":
    st.header("📊 Registro de Bateo")
    if es_admin:
        st.write("### 🟢 MODO ADMINISTRADOR ACTIVADO")
        with st.form("registro_bateo"):
            nombre = st.text_input("Nombre del Jugador")
            if st.form_submit_button("Guardar Datos"):
                st.success(f"Guardando a {nombre}...")
    else:
        st.info("Solo lectura. Ingresa la clave en la izquierda para editar.")

# --- 8. SECCIÓN CONFIGURACIÓN ---
elif menu == "⚙️ CONFIG":
    st.header("⚙️ Ajustes de Seguridad")
    if es_admin:
        if st.checkbox("👁️ Ver Contraseña Actual"):
            st.info(f"Tu clave es: **{pass_maestra}**")
        
        nueva_p = st.text_input("Nueva Contraseña", type="password")
        if st.button("Cambiar Clave Ahora"):
            with open(ruta("config.txt"), "w") as f:
                f.write(nueva_p)
            st.success("¡Clave cambiada! Úsala la próxima vez.")
    else:
        st.error("Debes validar la contraseña para ver esta sección.")
