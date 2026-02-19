import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="LIGA SOFTBOL 2026", layout="wide")

# Estilo para asegurar que los botones se vean y funcionen
st.markdown("""
    <style>
    div.stButton > button { background-color: #D32F2F; color: white; font-weight: bold; border-radius: 5px; }
    h1 { color: #B71C1C; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE ARCHIVOS (PERSISTENCIA TOTAL) ---
DATOS_DIR = "datos_liga"
FOTOS_DIR = "galeria_liga"
for d in [DATOS_DIR, FOTOS_DIR]:
    if not os.path.exists(d): os.makedirs(d)

ARCHIVOS = {
    "jugadores": ["Nombre", "Equipo", "VB", "H", "H2", "H3", "HR"],
    "equipos": ["Nombre"],
    "calendario": ["Fecha", "Hora", "Campo", "Local", "Visitante", "Score"],
    "accesos": ["Equipo", "Password"]
}

def cargar_datos(tipo):
    p = os.path.join(DATOS_DIR, f"data_{tipo}.csv")
    if os.path.exists(p):
        return pd.read_csv(p)
    return pd.DataFrame(columns=ARCHIVOS[tipo])

def guardar_datos(tipo, df):
    p = os.path.join(DATOS_DIR, f"data_{tipo}.csv")
    df.to_csv(p, index=False)
    st.session_state[tipo] = df # Actualiza la memoria RAM de la app

# Cargar todo al inicio
for t in ARCHIVOS:
    if t not in st.session_state:
        st.session_state[t] = cargar_datos(t)

# --- 3. LOGIN ---
if 'rol' not in st.session_state: st.session_state.rol = "Invitado"
if 'eq_gestion' not in st.session_state: st.session_state.eq_gestion = None

with st.sidebar:
    st.title("⚾ LIGA 2026")
    if st.session_state.rol == "Invitado":
        pwd = st.text_input("Clave:", type="password")
        if st.button("Entrar"):
            if pwd == "softbol2026": 
                st.session_state.rol = "Admin"; st.rerun()
            elif pwd in st.session_state.accesos["Password"].values:
                f = st.session_state.accesos[st.session_state.accesos["Password"] == pwd].iloc[0]
                st.session_state.rol = "Delegado"; st.session_state.eq_gestion = f["Equipo"]; st.rerun()
    else:
        st.write(f"Usuario: {st.session_state.rol}")
        if st.button("Salir"):
            st.session_state.rol = "Invitado"; st.rerun()

menu = st.sidebar.radio("Ir a:", ["🏠 Inicio", "📊 Standings", "🔍 Buscador"] + 
                       (["🏃 Admin"] if st.session_state.rol == "Admin" else []) +
                       (["📋 Mi Equipo"] if st.session_state.rol == "Delegado" else []))

# --- 4. SECCIONES ---

if menu == "🏠 Inicio":
    st.header("⚾ BIENVENIDOS A LA LIGA")
    st.subheader("📅 Próximos Juegos")
    st.table(st.session_state.calendario)

elif menu == "📊 Standings":
    st.header("📊 Posiciones Actuales")
    # Lógica de cálculo simplificada para evitar errores de actualización
    cal = st.session_state.calendario
    cal = cal[cal['Score'].str.contains('-', na=False)]
    if not cal.empty:
        stats = []
        for eq in st.session_state.equipos["Nombre"]:
            jg = jp = 0
            for _, f in cal[(cal['Local']==eq) | (cal['Visitante']==eq)].iterrows():
                s = f['Score'].split('-')
                if f['Local'] == eq:
                    if int(s[0]) > int(s[1]): jg += 1
                    else: jp += 1
                else:
                    if int(s[1]) > int(s[0]): jg += 1
                    else: jp += 1
            stats.append({"Equipo": eq, "JG": jg, "JP": jp})
        st.table(pd.DataFrame(stats).sort_values("JG", ascending=False))

elif menu == "📋 Mi Equipo":
    eq = st.session_state.eq_gestion
    st.subheader(f"Gestión: {eq}")
    
    # AGREGAR
    with st.expander("Añadir Jugador"):
        nom = st.text_input("Nombre:")
        if st.button("Guardar"):
            nuevo = pd.DataFrame([[nom, eq, 0,0,0,0,0]], columns=ARCHIVOS["jugadores"])
            df_actual = pd.concat([st.session_state.jugadores, nuevo], ignore_index=True)
            guardar_datos("jugadores", df_actual)
            st.success("Añadido"); st.rerun()

    # ELIMINAR
    mis_j = st.session_state.jugadores[st.session_state.jugadores["Equipo"] == eq]
    eliminar = st.selectbox("Dar de baja:", ["--"] + mis_j["Nombre"].tolist())
    if st.button("Confirmar Baja") and eliminar != "--":
        df_actual = st.session_state.jugadores[st.session_state.jugadores["Nombre"] != eliminar]
        guardar_datos("jugadores", df_actual)
        st.rerun()

elif menu == "🏃 Admin":
    t1, t2 = st.tabs(["Equipos", "Resultados"])
    with t1:
        ne = st.text_input("Nombre de Equipo:")
        if st.button("Registrar Equipo"):
            df = pd.concat([st.session_state.equipos, pd.DataFrame([[ne]], columns=["Nombre"])], ignore_index=True)
            guardar_datos("equipos", df); st.rerun()
            
    with t2:
        idx = st.selectbox("Juego:", st.session_state.calendario.index)
        sc = st.text_input("Score (ej: 10-5):")
        if st.button("Actualizar Marcador"):
            st.session_state.calendario.at[idx, "Score"] = sc
            guardar_datos("calendario", st.session_state.calendario)
            st.success("Marcador Guardado"); st.rerun()
