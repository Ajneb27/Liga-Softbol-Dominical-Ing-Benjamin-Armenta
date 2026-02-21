import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN DE RUTAS ---
DATA_DIR = "liga_softbol_2026_final"
if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)

JUGADORES_FILE = os.path.join(DATA_DIR, "jugadores_stats.csv")
EQUIPOS_FILE = os.path.join(DATA_DIR, "equipos_lista.csv")
ANIO_ACTUAL = 2026 

# --- 2. MOTOR DE DATOS PROTEGIDO ---
def cargar_base_datos():
    cols_obligatorias = ["Nombre", "Equipo", "VB", "H", "2B", "3B", "HR", "G", "P"]
    if os.path.exists(JUGADORES_FILE):
        try:
            df = pd.read_csv(JUGADORES_FILE)
            for col in cols_obligatorias:
                if col not in df.columns: df[col] = 0
        except: df = pd.DataFrame(columns=cols_obligatorias)
    else: df = pd.DataFrame(columns=cols_obligatorias)
    
    for c in ["VB", "H", "2B", "3B", "HR", "G", "P"]:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
    return df

def cargar_equipos():
    if os.path.exists(EQUIPOS_FILE):
        df = pd.read_csv(EQUIPOS_FILE)
        # Asegurar columnas de tiempo
        if "Debut" not in df.columns: df["Debut"] = ANIO_ACTUAL
        if "Fin" not in df.columns: df["Fin"] = 0 # 0 significa que sigue activo
        return df
    return pd.DataFrame(columns=["Nombre", "Debut", "Fin"])

# --- 3. INICIALIZACIÓN ---
if 'admin_sesion' not in st.session_state: st.session_state.admin_sesion = False
df_j = cargar_base_datos()
df_e = cargar_equipos()

st.set_page_config(page_title="Liga Softbol 2026", layout="wide")

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.title("🥎 Softbol Pro 2026")
    if not st.session_state.admin_sesion:
        with st.expander("🔐 Login Admin"):
            u = st.text_input("Usuario"); p = st.text_input("Clave", type="password")
            if st.button("Entrar"):
                if u == "admin" and p == "123":
                    st.session_state.admin_sesion = True
                    st.rerun()
    else:
        if st.button("Cerrar Sesión"):
            st.session_state.admin_sesion = False
            st.rerun()
    
    st.divider()
    menu = st.radio("Menú:", ["🏆 LÍDERES", "📋 ROSTERS", "🏘️ EQUIPOS", "📜 HISTORIAL JUGADOR", "✍️ REGISTRAR", "💾 RESPALDO"])

# --- 5. SECCIÓN EQUIPOS (DEBUT Y RETIRO) ---
if menu == "🏘️ EQUIPOS":
    st.header("🏘️ Gestión de Equipos y Trayectoria")
    
    if st.session_state.admin_sesion:
        with st.form("form_equipos"):
            col_e1, col_e2 = st.columns(2)
            nombre_e = col_e1.text_input("Nombre del Equipo:")
            anio_d = col_e2.number_input("Año de Debut:", 1980, ANIO_ACTUAL, ANIO_ACTUAL)
            
            st.info("Nota: Si el equipo sigue participando, deja el 'Año de Retiro' en 0.")
            anio_f = st.number_input("Año de Retiro (0 si está Activo):", 0, ANIO_ACTUAL, 0)
            
            if st.form_submit_button("💾 Guardar/Actualizar Equipo"):
                if nombre_e:
                    # Actualizar si existe, si no, añadir
                    df_e = df_e[df_e["Nombre"] != nombre_e]
                    nuevo_eq = pd.DataFrame([{"Nombre": nombre_e, "Debut": anio_d, "Fin": anio_f}])
                    df_e = pd.concat([df_e, nuevo_eq], ignore_index=True)
                    df_e.to_csv(EQUIPOS_FILE, index=False)
                    st.success(f"Equipo {nombre_e} actualizado.")
                    st.rerun()

    st.subheader("Historial de Equipos en la Liga")
    if not df_e.empty:
        df_display = df_e.copy()
        
        # Lógica de cálculo de temporadas
        def calcular_temporadas(row):
            fin = row['Fin'] if row['Fin'] > 0 else ANIO_ACTUAL
            return int(fin - row['Debut'] + 1)

        df_display["Estatus"] = df_display["Fin"].apply(lambda x: "🔴 Retirado" if x > 0 else "🟢 Activo")
        df_display["Temporadas"] = df_display.apply(calcular_temporadas, axis=1)
        
        st.dataframe(df_display[["Nombre", "Debut", "Fin", "Estatus", "Temporadas"]].sort_values("Debut"), use_container_width=True)

# --- 6. SECCIÓN LÍDERES (PROTEGIDA) ---
elif menu == "🏆 LÍDERES":
    st.header("🔝 Líderes Departamentales")
    t1, t2 = st.tabs(["⚾ Bateo", "🎯 Pitcheo"])
    with t1:
        c1, c2, c3 = st.columns(3)
        c1.subheader("Hits (H)"); c1.table(df_j.nlargest(10, 'H')[['Nombre', 'H']])
        c1.subheader("Home Runs (HR)"); c1.table(df_j.nlargest(10, 'HR')[['Nombre', 'HR']])
        c2.subheader("Dobles (2B)"); c2.table(df_j.nlargest(10, '2B')[['Nombre', '2B']])
        c3.subheader("Triples (3B)"); c3.table(df_j.nlargest(10, '3B')[['Nombre', '3B']])
    with t2:
        c1, c2 = st.columns(2)
        c1.subheader("Ganados (G)"); c1.table(df_j.nlargest(10, 'G')[['Nombre', 'G']])
        c2.subheader("Perdidos (P)"); c2.table(df_j.nlargest(10, 'P')[['Nombre', 'P']])

# --- 7. SECCIONES RESTANTES (REGISTRAR, RESPALDO, ROSTER) ---
elif menu == "✍️ REGISTRAR":
    if st.session_state.admin_sesion:
        # Solo mostrar equipos ACTIVOS para registrar nuevos jugadores
        equipos_activos = df_e[df_e["Fin"] == 0]["Nombre"].unique()
        if len(equipos_activos) == 0: st.error("No hay equipos activos para registrar.")
        else:
            with st.form("reg"):
                nom = st.text_input("Nombre:")
                eq = st.selectbox("Equipo:", equipos_activos)
                v1, v2, v3, v4, v5 = st.columns(5)
                h_i = v1.number_input("H", 0); d2_i = v2.number_input("2B", 0); d3_i = v3.number_input("3B", 0); hr_i = v4.number_input("HR", 0); vb_i = v5.number_input("VB", 0)
                p1, p2 = st.columns(2)
                g_i = p1.number_input("G", 0); p_i = p2.number_input("P", 0)
                if st.form_submit_button("Guardar"):
                    df_j = df_j[df_j["Nombre"] != nom]
                    n = pd.DataFrame([{"Nombre": nom, "Equipo": eq, "VB": vb_i, "H": h_i, "2B": d2_i, "3B": d3_i, "HR": hr_i, "G": g_i, "P": p_i}])
                    pd.concat([df_j, n], ignore_index=True).to_csv(JUGADORES_FILE, index=False)
                    st.success("Guardado"); st.rerun()

elif menu == "💾 RESPALDO":
    st.download_button("📥 Descargar", df_j.to_csv(index=False), "liga_2026.csv")
    f = st.file_uploader("📤 Restaurar", type="csv")
    if f: pd.read_csv(f).to_csv(JUGADORES_FILE, index=False); st.rerun()

elif menu == "📋 ROSTERS":
    if not df_e.empty:
        eq = st.selectbox("Equipo:", df_e["Nombre"].unique())
        st.dataframe(df_j[df_j["Equipo"] == eq], use_container_width=True)

elif menu == "📜 HISTORIAL JUGADOR":
    if not df_j.empty:
        j = st.selectbox("Buscar:", sorted(df_j["Nombre"].unique()))
        d = df_j[df_j["Nombre"] == j].iloc[0]
        st.write(f"**Equipo:** {d['Equipo']} | **AVG:** {(d['H']/d['VB'] if d['VB']>0 else 0):.3f}")
        st.write(f"**Stats:** H:{int(d['H'])} | 2B:{int(d['2B'])} | 3B:{int(d['3B'])} | HR:{int(d['HR'])} | G:{int(d['G'])} | P:{int(d['P'])}")
