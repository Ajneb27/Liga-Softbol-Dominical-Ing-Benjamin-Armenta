import streamlit as st
import pandas as pd
import os
import gc  # Importante: Esto limpia la memoria RAM

# --- 1. CONFIGURACIÓN ---
NOMBRE_LIGA = "LIGA DE SOFTBOL 2026"
DATA_DIR = "datos_liga"
if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)

J_FILE = os.path.join(DATA_DIR, "jugadores.csv")
E_FILE = os.path.join(DATA_DIR, "equipos.csv")
G_FILE = os.path.join(DATA_DIR, "juegos.csv")

# --- 2. FUNCIONES DE CARGA (Ligeras) ---
def cargar(archivo, columnas):
    if os.path.exists(archivo):
        return pd.read_csv(archivo)
    return pd.DataFrame(columns=columnas)

# --- 3. INTERFAZ ---
st.set_page_config(page_title=NOMBRE_LIGA, layout="wide")

# Carga de datos al inicio
df_j = cargar(J_FILE, ["Nombre", "Equipo", "VB", "H", "2B", "3B", "HR", "G", "P"])
df_e = cargar(E_FILE, ["Nombre"])
df_g = cargar(G_FILE, ["Visitante", "CV", "HomeClub", "CH"])

if 'admin' not in st.session_state: st.session_state.admin = False

with st.sidebar:
    st.title(NOMBRE_LIGA)
    if not st.session_state.admin:
        with st.expander("🔐 Admin"):
            u = st.text_input("Usuario"); p = st.text_input("Clave", type="password")
            if st.button("Entrar"):
                if u == "admin" and p == "123": st.session_state.admin = True; st.rerun()
    else:
        if st.button("Salir"): st.session_state.admin = False; st.rerun()
    
    menu = st.radio("Ir a:", ["🏠 INICIO", "📊 POSICIONES", "🏆 LÍDERES", "📋 ROSTER", "✍️ REGISTRAR"])

# --- 4. SECCIONES ---
if menu == "🏠 INICIO":
    st.header(f"🥎 {NOMBRE_LIGA}")
    st.write("Bienvenido al sistema de estadísticas.")

elif menu == "📊 POSICIONES":
    st.subheader("Tabla de Posiciones")
    if not df_g.empty:
        res = []
        for eq in df_e["Nombre"].unique():
            v = df_g[df_g["Visitante"] == eq]
            h = df_g[df_g["HomeClub"] == eq]
            gan = len(v[v["CV"] > v["CH"]]) + len(h[h["CH"] > h["CV"]])
            per = len(v[v["CV"] < v["CH"]]) + len(h[h["CH"] < h["CV"]])
            res.append({"Equipo": eq, "G": gan, "P": per, "AVG": round(gan/(gan+per),3) if (gan+per)>0 else 0})
        st.table(pd.DataFrame(res).sort_values("AVG", ascending=False))

elif menu == "🏆 LÍDERES":
    st.subheader("Líderes de Bateo")
    col1, col2 = st.columns(2)
    col1.write("**Hits**")
    col1.table(df_j.nlargest(5, 'H')[['Nombre', 'H']])
    col2.write("**Home Runs**")
    col2.table(df_j.nlargest(5, 'HR')[['Nombre', 'HR']])

elif menu == "📋 ROSTER":
    eq_sel = st.selectbox("Equipo:", df_e["Nombre"].unique())
    roster = df_j[df_j["Equipo"] == eq_sel].copy()
    roster["AVG"] = (roster["H"] / roster["VB"]).fillna(0).apply(lambda x: f"{x:.3f}")
    st.dataframe(roster, hide_index=True)

elif menu == "✍️ REGISTRAR":
    if st.session_state.admin:
        with st.form("reg_form"):
            n = st.text_input("Nombre Jugador")
            e = st.selectbox("Equipo", df_e["Nombre"].unique())
            c1, c2, c3 = st.columns(3)
            vb = c1.number_input("VB", 0); h = c2.number_input("H", 0); hr = c3.number_input("HR", 0)
            if st.form_submit_button("💾 GUARDAR"):
                # Actualizar y guardar
                df_j = pd.concat([df_j[df_j["Nombre"] != n], pd.DataFrame([{"Nombre":n,"Equipo":e,"VB":vb,"H":h,"HR":hr}])], ignore_index=True)
                df_j.to_csv(J_FILE, index=False)
                
                # LIMPIEZA DE MEMORIA (Clave para evitar el error)
                gc.collect() 
                st.success("¡Guardado! La memoria se ha liberado.")
                st.rerun()
    else: st.warning("Inicia sesión como admin.")
