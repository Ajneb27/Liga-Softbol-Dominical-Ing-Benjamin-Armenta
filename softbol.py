import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="LIGA SOFTBOL", page_icon="⚾", layout="wide")
st.markdown("""
    <style>
        th{background-color:#D32F2F!important;color:white!important;}
        h1,h2{color:#B71C1C;}
        .stButton>button {width: 100%;}
    </style>
""", unsafe_allow_html=True)

DATOS_DIR = "datos_liga"
if not os.path.exists(DATOS_DIR): 
    os.makedirs(DATOS_DIR)

def path_archivo(n): 
    return os.path.join(DATOS_DIR, n)

# --- 2. FUNCIONES DE CARGA Y GUARDADO MEJORADAS ---
def cargar(archivo, columnas_default):
    p = path_archivo(archivo)
    if os.path.exists(p):
        try:
            df = pd.read_csv(p)
            # Limpiar espacios en nombres de columnas
            df.columns = df.columns.str.strip()
            return df
        except:
            return pd.DataFrame(columns=columnas_default)
    return pd.DataFrame(columns=columnas_default)

def guardar(df, archivo):
    df.to_csv(path_archivo(archivo), index=False)

# --- 3. INICIALIZACIÓN DE DATOS ---
# Definimos las columnas para evitar errores de "KeyError"
df_e = cargar("data_equipos.csv", ["Nombre"])
df_j = cargar("data_jugadores.csv", ["Nombre", "Equipo", "VB", "H", "H2", "H3", "HR"])
df_c = cargar("data_calendario.csv", ["Jornada", "Fecha", "Local", "Visitante", "Score"])

# --- 4. LOGIN ---
if 'rol' not in st.session_state: 
    st.session_state.rol = "Invitado"

with st.sidebar:
    st.title("🥎 LIGA DOMINICAL")
    if st.session_state.rol == "Invitado":
        pwd = st.text_input("Clave Admin:", type="password")
        if st.button("ENTRAR"):
            if pwd == "softbol2026": 
                st.session_state.rol = "Admin"
                st.rerun()
            else:
                st.error("Clave incorrecta")
    else:
        st.info(f"Sesión: {st.session_state.rol}")
        if st.button("SALIR"): 
            st.session_state.rol = "Invitado"
            st.rerun()
    
    menu = st.radio("MENÚ:", ["🏠 Inicio", "🏆 LÍDERES", "📊 Standings", "📋 Rosters", "⚙️ Admin General"])

# --- 5. LÓGICA DE NAVEGACIÓN ---

if menu == "⚙️ Admin General":
    if st.session_state.rol != "Admin":
        st.error("Acceso Denegado. Por favor inicia sesión.")
    else:
        st.title("⚙️ Panel de Control")
        tab1, tab2, tab3 = st.tabs(["🏆 Equipos", "🥖 Jugadores", "📅 Calendario"])

        with tab1:
            st.subheader("Registrar Equipos")
            with st.form("f_equipos", clear_on_submit=True):
                n_e = st.text_input("Nombre del nuevo equipo:")
                if st.form_submit_button("➕ AGREGAR EQUIPO"):
                    if n_e:
                        nuevo_e = pd.DataFrame([{"Nombre": n_e.strip()}])
                        df_res = pd.concat([df_e, nuevo_e], ignore_index=True).drop_duplicates()
                        guardar(df_res, "data_equipos.csv")
                        st.success("Equipo guardado"); st.rerun()
            
            if not df_e.empty:
                st.write("---")
                e_borrar = st.selectbox("Selecciona equipo para ELIMINAR:", df_e["Nombre"].tolist())
                if st.button("🗑️ ELIMINAR EQUIPO SELECCIONADO"):
                    df_res = df_e[df_e["Nombre"] != e_borrar]
                    guardar(df_res, "data_equipos.csv")
                    st.warning(f"Equipo {e_borrar} eliminado"); st.rerun()
                st.table(df_e)

        with tab2:
            st.subheader("Gestión de Jugadores")
            if df_e.empty:
                st.warning("⚠️ Primero debes crear un equipo.")
            else:
                with st.form("f_jugadores", clear_on_submit=True):
                    nom_j = st.text_input("Nombre del Jugador:")
                    eq_j = st.selectbox("Asignar a Equipo:", df_e["Nombre"].tolist())
                    c1, c2, c3, c4 = st.columns(4)
                    vb = c1.number_input("VB (Veces al Bate)", 0)
                    h = c2.number_input("H (Hits)", 0)
                    h2 = c3.number_input("H2 (Dobles)", 0)
                    hr = c4.number_input("HR (Homeruns)", 0)
                    if st.form_submit_button("💾 GUARDAR JUGADOR"):
                        if nom_j:
                            nuevo_j = pd.DataFrame([{"Nombre": nom_j, "Equipo": eq_j, "VB": vb, "H": h, "H2": h2, "H3": 0, "HR": hr}])
                            df_res = pd.concat([df_j, nuevo_j], ignore_index=True)
                            guardar(df_res, "data_jugadores.csv")
                            st.success("Jugador guardado"); st.rerun()
                
                if not df_j.empty:
                    st.write("---")
                    j_borrar = st.selectbox("Selecciona jugador para ELIMINAR:", df_j["Nombre"].tolist())
                    if st.button("🗑️ ELIMINAR JUGADOR"):
                        df_res = df_j[df_j["Nombre"] != j_borrar]
                        guardar(df_res, "data_jugadores.csv")
                        st.rerun()
                    st.dataframe(df_j, use_container_width=True)

        with tab3:
            st.subheader("Calendario (Edición Rápida)")
            ed_cal = st.data_editor(df_c, num_rows="dynamic", use_container_width=True)
            if st.button("💾 GUARDAR TODO EL CALENDARIO"):
                guardar(ed_cal, "data_calendario.csv")
                st.success("Calendario actualizado"); st.rerun()

elif menu == "📋 Rosters":
    st.title("📋 Rosters por Equipo")
    if not df_e.empty:
        eq_sel = st.selectbox("Selecciona Equipo:", df_e["Nombre"].tolist())
        db = df_j[df_j["Equipo"] == eq_sel].copy()
        if not db.empty:
            # Cálculo de AVG evitando división por cero
            db["AVG"] = db.apply(lambda x: x["H"] / x["VB"] if x["VB"] > 0 else 0.0, axis=1)
            # Formatear AVG a 3 decimales
            db_view = db[["Nombre", "VB", "H", "H2", "HR", "AVG"]].sort_values("AVG", ascending=False)
            st.dataframe(db_view.style.format({"AVG": "{:.3f}"}), use_container_width=True, hide_index=True)
        else: 
            st.info("No hay jugadores registrados en este equipo.")
    else: 
        st.warning("No hay equipos registrados.")

elif menu == "🏠 Inicio":
    st.title("⚾ LIGA DOMINICAL 2026")
    if not df_c.empty:
        st.subheader("Próximos Encuentros / Resultados")
        st.table(df_c)
    else:
        st.info("No hay juegos programados en el calendario.")

# --- SECCIONES PENDIENTES (LÍDERES Y STANDINGS) ---
elif menu == "🏆 LÍDERES":
    st.title("🏆 Líderes Individuales")
    if not df_j.empty:
        # Ejemplo rápido de líder de bateo
        df_j["AVG"] = df_j.apply(lambda x: x["H"] / x["VB"] if x["VB"] > 0 else 0.0, axis=1)
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Promedio (AVG)")
            st.table(df_j.nlargest(5, "AVG")[["Nombre", "Equipo", "AVG"]])
        with c2:
            st.subheader("Home Runs (HR)")
            st.table(df_j.nlargest(5, "HR")[["Nombre", "Equipo", "HR"]])
    else:
        st.warning("No hay datos de jugadores.")

elif menu == "📊 Standings":
    st.title("📊 Tabla de Posiciones")
    st.info("Aquí puedes programar la lógica para calcular Ganados/Perdidos desde el calendario.")
