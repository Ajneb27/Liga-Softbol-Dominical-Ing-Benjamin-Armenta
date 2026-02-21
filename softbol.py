import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN E IDENTIDAD ---
NOMBRE_LIGA = "LIGA DE SOFTBOL DOMINICAL"
ANIO_INICIO_LIGA = 2024
ANIO_ACTUAL = 2026

DATA_DIR = "liga_softbol_final_2026"
if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)

JUGADORES_FILE = os.path.join(DATA_DIR, "jugadores_master.csv")
EQUIPOS_FILE = os.path.join(DATA_DIR, "equipos_master.csv")

# --- 2. MOTOR DE DATOS ---
def cargar_jugadores():
    cols = ["Nombre", "Equipo", "Categoria", "VB", "H", "2B", "3B", "HR", "G", "P"]
    if os.path.exists(JUGADORES_FILE):
        try:
            df = pd.read_csv(JUGADORES_FILE)
            for c in cols:
                if c not in df.columns: df[c] = "Softbolista" if c == "Categoria" else 0
        except: df = pd.DataFrame(columns=cols)
    else: df = pd.DataFrame(columns=cols)
    df = df.dropna(subset=['Nombre'])
    for c in ["VB", "H", "2B", "3B", "HR", "G", "P"]:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
    return df

def cargar_equipos():
    if os.path.exists(EQUIPOS_FILE):
        df = pd.read_csv(EQUIPOS_FILE)
        if "Debut" not in df.columns: df["Debut"] = ANIO_INICIO_LIGA
        if "Fin" not in df.columns: df["Fin"] = 0
        return df
    return pd.DataFrame(columns=["Nombre", "Debut", "Fin"])

# --- 3. INICIALIZACIÓN ---
st.set_page_config(page_title=NOMBRE_LIGA, layout="wide", page_icon="🥎")
if 'admin' not in st.session_state: st.session_state.admin = False

df_j = cargar_jugadores()
df_e = cargar_equipos()

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.title(f"🥎 {NOMBRE_LIGA}")
    if not st.session_state.admin:
        with st.expander("🔐 Acceso Admin"):
            u = st.text_input("Usuario"); p = st.text_input("Clave", type="password")
            if st.button("Entrar"):
                if u == "admin" and p == "123": st.session_state.admin = True; st.rerun()
    else:
        st.success("Admin Activo")
        if st.button("Cerrar Sesión"): st.session_state.admin = False; st.rerun()
    
    st.divider()
    opciones_menu = ["🏠 INICIO / PORTADA", "🏆 LÍDERES", "📋 ROSTERS", "📜 HISTORIAL JUGADOR", "🏘️ EQUIPOS"]
    if st.session_state.admin:
        opciones_menu += ["✍️ REGISTRAR", "🗑️ BORRAR", "💾 RESPALDO"]
    
    menu = st.radio("Navegación:", opciones_menu)

# --- 5. SECCIÓN 🏠 INICIO / PORTADA ---
if menu == "🏠 INICIO / PORTADA":
    st.title(f"Bienvenido a la {NOMBRE_LIGA}")
    st.image("https://cdn-icons-png.flaticon.com", width=100)
    st.write(f"Desde **Agosto de {ANIO_INICIO_LIGA}**, uniendo familias a través del diamante.")
    st.divider()
    st.header("📜 Nuestra Historia")
    st.write("Esta liga nació para fomentar el deporte dominical y la sana competencia. Hoy somos una comunidad apasionada por el softbol.")

# --- 6. SECCIÓN 🏆 LÍDERES ---
elif menu == "🏆 LÍDERES":
    st.header("🥇 Líderes Departamentales")
    t1, t2 = st.tabs(["⚾ Bateo", "🎯 Pitcheo"])
    with t1:
        c1, c2 = st.columns(2)
        c1.write("**Hits (H)**"); c1.table(df_j.nlargest(10, 'H')[['Nombre', 'H']])
        c2.write("**Home Runs (HR)**"); c2.table(df_j.nlargest(10, 'HR')[['Nombre', 'HR']])
    with t2:
        c1, c2 = st.columns(2)
        c1.write("**Ganados (G)**"); c1.table(df_j.sort_values('G', ascending=False).head(10)[['Nombre', 'G']])
        c2.write("**Perdidos (P)**"); c2.table(df_j.sort_values('P', ascending=False).head(10)[['Nombre', 'P']])

# --- 7. SECCIÓN 📜 HISTORIAL JUGADOR (CORREGIDA) ---
elif menu == "📜 HISTORIAL JUGADOR":
    st.header("📜 Ficha del Jugador")
    if not df_j.empty:
        j_s = st.selectbox("Selecciona Jugador:", sorted(df_j["Nombre"].unique().tolist()))
        d = df_j[df_j["Nombre"] == j_s].iloc[0] # Uso de .iloc[0] para evitar TypeError
        st.subheader(f"Jugador: {d['Nombre']}")
        st.write(f"**Equipo:** {d['Equipo']} | **Categoría:** {d['Categoria']}")
        st.write(f"**Acumulado:** H: {int(d['H'])} | 2B: {int(d['2B'])} | 3B: {int(d['3B'])} | HR: {int(d['HR'])}")
        st.write(f"**Pitcheo:** G: {int(d['G'])} | P: {int(d['P'])}")

# --- 8. SECCIÓN 🗑️ BORRAR (REINTEGRADA) ---
elif menu == "🗑️ BORRAR":
    if st.session_state.admin:
        st.header("🗑️ Gestión de Eliminación")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Borrar Jugador")
            j_del = st.selectbox("Seleccionar Jugador:", [""] + sorted(df_j["Nombre"].tolist()))
            if st.button("❌ Eliminar Jugador") and j_del != "":
                df_j = df_j[df_j["Nombre"] != j_del]
                df_j.to_csv(JUGADORES_FILE, index=False)
                st.success(f"Jugador {j_del} eliminado."); st.rerun()
        with col2:
            st.subheader("Borrar Equipo")
            e_del = st.selectbox("Seleccionar Equipo:", [""] + sorted(df_e["Nombre"].tolist()))
            if st.button("❌ Eliminar Equipo") and e_del != "":
                df_e = df_e[df_e["Nombre"] != e_del]
                df_j = df_j[df_j["Equipo"] != e_del] # Limpieza automática de jugadores
                df_e.to_csv(EQUIPOS_FILE, index=False); df_j.to_csv(JUGADORES_FILE, index=False)
                st.success(f"Equipo {e_del} eliminado."); st.rerun()

# --- 9. SECCIÓN ✍️ REGISTRAR ---
elif menu == "✍️ REGISTRAR":
    if st.session_state.admin:
        st.header("✍️ Anotación de Juego")
        sel = st.selectbox("Elegir Jugador:", ["NUEVO JUGADOR"] + sorted(df_j["Nombre"].unique().tolist()))
        if 'vals' not in st.session_state or st.session_state.get('last_sel') != sel:
            if sel != "NUEVO JUGADOR": st.session_state.vals = df_j[df_j["Nombre"] == sel].iloc[0].to_dict()
            else: st.session_state.vals = {"Nombre": "", "Equipo": None, "Categoria": "Softbolista", "VB": 0, "H": 0, "2B": 0, "3B": 0, "HR": 0, "G": 0, "P": 0}
            st.session_state.last_sel = sel
        
        with st.form("f_reg", clear_on_submit=True):
            nom_f = st.text_input("Nombre:", value=st.session_state.vals["Nombre"])
            eq_f = st.selectbox("Equipo:", df_e["Nombre"].unique() if not df_e.empty else ["Crea equipo"])
            cat_f = st.radio("Categoría:", ["Novato", "Softbolista", "Refuerzo"], index=0)
            v1, v2, v3, v4 = st.columns(4)
            h = v1.number_input("H Total", value=int(st.session_state.vals["H"]))
            hr = v2.number_input("HR Total", value=int(st.session_state.vals["HR"]))
            g = v3.number_input("G Total", value=int(st.session_state.vals["G"]))
            p = v4.number_input("P Total", value=int(st.session_state.vals["P"]))
            if st.form_submit_button("💾 GUARDAR"):
                df_j = df_j[df_j["Nombre"] != nom_f]
                nueva = pd.DataFrame([{"Nombre": nom_f, "Equipo": eq_f, "Categoria": cat_f, "H": h, "HR": hr, "G": g, "P": p, "VB": h, "2B": 0, "3B": 0}])
                pd.concat([df_j, nueva], ignore_index=True).to_csv(JUGADORES_FILE, index=False); st.success("Guardado"); st.rerun()

# --- 10. EQUIPOS, ROSTERS Y RESPALDO ---
elif menu == "🏘️ EQUIPOS":
    if st.session_state.admin:
        with st.form("eq"):
            n=st.text_input("Equipo:"); d=st.number_input("Debut:", 2024, 2026, 2024); f=st.number_input("Fin:", 0, 2026, 0)
            if st.form_submit_button("Añadir"):
                pd.concat([df_e, pd.DataFrame([{"Nombre": n, "Debut": d, "Fin": f}])], ignore_index=True).to_csv(EQUIPOS_FILE, index=False); st.rerun()
    st.table(df_e)

elif menu == "📋 ROSTERS":
    if not df_e.empty:
        eq = st.selectbox("Equipo:", df_e["Nombre"].unique())
        st.dataframe(df_j[df_j["Equipo"] == eq], use_container_width=True)

elif menu == "💾 RESPALDO":
    st.download_button("📥 Descargar CSV", df_j.to_csv(index=False), "liga.csv")
    f = st.file_uploader("Subir", type="csv")
    if f: pd.read_csv(f).to_csv(JUGADORES_FILE, index=False); st.rerun()
