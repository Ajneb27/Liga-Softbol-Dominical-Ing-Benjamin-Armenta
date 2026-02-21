import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN ---
DATA_DIR = "datos_liga_pro"
if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)

EQUIPOS_FILE = os.path.join(DATA_DIR, "equipos.csv")
JUGADORES_FILE = os.path.join(DATA_DIR, "jugadores.csv")
CONFIG_FILE = os.path.join(DATA_DIR, "config.csv")

# Credenciales iniciales
if not os.path.exists(CONFIG_FILE):
    pd.DataFrame([{"user": "admin", "pass": "123"}]).to_csv(CONFIG_FILE, index=False)

# --- 2. FUNCIONES DE DATOS ---
def cargar_csv(ruta, columnas):
    if os.path.exists(ruta): return pd.read_csv(ruta)
    return pd.DataFrame(columns=columnas)

# --- 3. ESTADO DE SESIÓN ---
if 'admin' not in st.session_state: st.session_state.admin = False

df_e = cargar_csv(EQUIPOS_FILE, ["Nombre"])
# Columnas: Nombre, Equipo, VB, H, 2B, 3B, HR, G (Ganados), P (Perdidos)
df_j = cargar_csv(JUGADORES_FILE, ["Nombre", "Equipo", "VB", "H", "2B", "3B", "HR", "G", "P"])

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.title("🥎 Liga Softbol Pro")
    if not st.session_state.admin:
        u = st.text_input("Usuario")
        p = st.text_input("Password", type="password")
        if st.button("Login Admin"):
            conf = pd.read_csv(CONFIG_FILE)
            if u == conf.iloc[0]['user'] and p == str(conf.iloc[0]['pass']):
                st.session_state.admin = True
                st.rerun()
    else:
        st.success("Admin Activo")
        if st.button("Cerrar Sesión"):
            st.session_state.admin = False
            st.rerun()
    
    menu = st.radio("Menú", ["🏆 Líderes (Top 10)", "📊 Tabla Completa", "🏘️ Equipos", "👤 Registro/Editar", "💾 Respaldo"])

# --- 5. SECCIONES ---

if menu == "🏆 Líderes (Top 10)":
    st.header("🔝 Los 10 Mejores de la Liga")
    if df_j.empty:
        st.info("No hay datos suficientes.")
    else:
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Hits", "2B", "3B", "HR", "Ganados", "Perdidos"])
        with tab1: st.table(df_j.nlargest(10, 'H')[['Nombre', 'Equipo', 'H']])
        with tab2: st.table(df_j.nlargest(10, '2B')[['Nombre', 'Equipo', '2B']])
        with tab3: st.table(df_j.nlargest(10, '3B')[['Nombre', 'Equipo', '3B']])
        with tab4: st.table(df_j.nlargest(10, 'HR')[['Nombre', 'Equipo', 'HR']])
        with tab5: st.table(df_j.nlargest(10, 'G')[['Nombre', 'Equipo', 'G']])
        with tab6: st.table(df_j.nlargest(10, 'P')[['Nombre', 'Equipo', 'P']])

elif menu == "📊 Tabla Completa":
    st.header("Estadísticas Generales")
    df_show = df_j.copy()
    df_show['AVG'] = (df_show['H'] / df_show['VB']).fillna(0.000)
    st.dataframe(df_show, use_container_width=True)

elif menu == "👤 Registro/Editar":
    if not st.session_state.admin:
        st.warning("Acceso solo para administradores.")
    else:
        st.header("Añadir o Actualizar Jugador")
        with st.form("registro"):
            nombre = st.text_input("Nombre del Jugador")
            equipo = st.selectbox("Equipo", df_e["Nombre"])
            c1, c2, c3, c4 = st.columns(4)
            vb = c1.number_input("VB", min_value=0)
            h = c2.number_input("Hits", min_value=0)
            d2 = c3.number_input("2B", min_value=0)
            d3 = c4.number_input("3B", min_value=0)
            
            c5, c6, c7, c8 = st.columns(4)
            hr = c5.number_input("HR", min_value=0)
            g = c6.number_input("G (Pitcher)", min_value=0)
            p = c7.number_input("P (Pitcher)", min_value=0)
            
            if st.form_submit_button("Guardar Jugador"):
                # Si el jugador ya existe, lo actualizamos, si no, lo añadimos
                df_j = df_j[df_j['Nombre'] != nombre] # Elimina versión vieja si existe
                nueva_fila = pd.DataFrame([{"Nombre": nombre, "Equipo": equipo, "VB": vb, "H": h, "2B": d2, "3B": d3, "HR": hr, "G": g, "P": p}])
                df_j = pd.concat([df_j, nueva_fila], ignore_index=True)
                df_j.to_csv(JUGADORES_FILE, index=False)
                st.success(f"¡{nombre} actualizado!")
                st.rerun()

elif menu == "💾 Respaldo":
    st.header("💾 Centro de Respaldo")
    # Botón para descargar el archivo actual de la nube
    csv = df_j.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar CSV de Jugadores", csv, "respaldo_liga.csv", "text/csv")
    
    # Opción para subir un respaldo si se borra la app
    archivo = st.file_uploader("📤 Restaurar desde archivo CSV", type="csv")
    if archivo:
        df_restaurado = pd.read_csv(archivo)
        df_restaurado.to_csv(JUGADORES_FILE, index=False)
        st.success("¡Datos restaurados correctamente!")
        st.rerun()

# --- Gestión de Equipos (Simplificada) ---
elif menu == "🏘️ Equipos":
    if not st.session_state.admin: st.warning("Solo Admin")
    else:
        eq_n = st.text_input("Nuevo Equipo")
        if st.button("Añadir"):
            df_e = pd.concat([df_e, pd.DataFrame([{"Nombre": eq_n}])], ignore_index=True)
            df_e.to_csv(EQUIPOS_FILE, index=False)
            st.rerun()
        st.table(df_e)
