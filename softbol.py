import streamlit as st
import pandas as pd
import os
import urllib.parse
from datetime import datetime
import qrcode
from io import BytesIO
from PIL import Image

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(page_title="Liga Softbol Pro 2026", layout="wide", page_icon="🥎")

# URL de tu página para Redes Sociales y QR (CAMBIA ESTO)
URL_MI_PAGINA = "https://tu-liga.streamlit.app" 

# Archivos de Datos
ARCHIVOS = ["data_bateo.csv", "data_pitcheo.csv", "data_juegos.csv", "data_fotos.csv", "data_perfiles.csv", "data_mvp.csv", "data_playoffs.csv", "config.txt", "color_pri.txt", "color_sec.txt", "bg_url.txt"]

def inicializar_archivos():
    if not os.path.exists("config.txt"): 
        with open("config.txt", "w") as f: f.write("softbol2026")
    if not os.path.exists("color_pri.txt"): 
        with open("color_pri.txt", "w") as f: f.write("#1a237e")
    if not os.path.exists("color_sec.txt"): 
        with open("color_sec.txt", "w") as f: f.write("#b71c1c")
    if not os.path.exists("bg_url.txt"): 
        with open("bg_url.txt", "w") as f: f.write("https://images.unsplash.com")

def cargar_datos():
    if 'bateo' not in st.session_state:
        st.session_state.bateo = pd.read_csv("data_bateo.csv") if os.path.exists("data_bateo.csv") else pd.DataFrame(columns=["Nombre", "Equipo", "VB", "H", "2B", "3B", "HR", "RBI"])
    if 'pitcheo' not in st.session_state:
        st.session_state.pitcheo = pd.read_csv("data_pitcheo.csv") if os.path.exists("data_pitcheo.csv") else pd.DataFrame(columns=["Nombre", "Equipo", "JG", "JP", "IP", "CL", "CF", "CC", "K"])
    if 'juegos' not in st.session_state:
        st.session_state.juegos = pd.read_csv("data_juegos.csv") if os.path.exists("data_juegos.csv") else pd.DataFrame(columns=["Fecha", "Hora", "Local", "Visita", "Campo"])
    if 'fotos' not in st.session_state:
        st.session_state.fotos = pd.read_csv("data_fotos.csv") if os.path.exists("data_fotos.csv") else pd.DataFrame(columns=["Titulo", "URL", "Likes"])
    if 'perfiles' not in st.session_state:
        st.session_state.perfiles = pd.read_csv("data_perfiles.csv") if os.path.exists("data_perfiles.csv") else pd.DataFrame(columns=["Nombre", "FotoURL", "Posicion", "Bio"])
    if 'mvp' not in st.session_state:
        st.session_state.mvp = pd.read_csv("data_mvp.csv") if os.path.exists("data_mvp.csv") else pd.DataFrame(columns=["Categoria", "Nombre", "Equipo", "Stat", "FotoURL"])
    if 'playoffs' not in st.session_state:
        st.session_state.playoffs = pd.read_csv("data_playoffs.csv") if os.path.exists("data_playoffs.csv") else pd.DataFrame(columns=["Fase", "Equipo1", "Equipo2", "Resultado", "Estatus"])

def guardar_todo():
    st.session_state.bateo.to_csv("data_bateo.csv", index=False)
    st.session_state.pitcheo.to_csv("data_pitcheo.csv", index=False)
    st.session_state.juegos.to_csv("data_juegos.csv", index=False)
    st.session_state.fotos.to_csv("data_fotos.csv", index=False)
    st.session_state.perfiles.to_csv("data_perfiles.csv", index=False)
    st.session_state.mvp.to_csv("data_mvp.csv", index=False)
    st.session_state.playoffs.to_csv("data_playoffs.csv", index=False)

inicializar_archivos()
cargar_datos()

# --- 2. ESTILO VISUAL DINÁMICO ---
color_p = open("color_pri.txt", "r").read().strip()
color_s = open("color_sec.txt", "r").read().strip()
bg_img = open("bg_url.txt", "r").read().strip()

st.markdown(f"""
    <style>
    .stApp {{ background-image: url("{bg_img}"); background-size: cover; background-attachment: fixed; }}
    .block-container {{ background-color: rgba(255, 255, 255, 0.92); padding: 30px; border-radius: 15px; box-shadow: 0px 4px 15px rgba(0,0,0,0.3); }}
    [data-testid="stSidebar"] {{ background-color: {color_p}; }}
    [data-testid="stSidebar"] * {{ color: white !important; }}
    h1, h2, h3 {{ color: {color_s} !important; text-align: center; font-family: 'Arial Black'; }}
    .stButton>button {{ background-color: {color_s}; color: white; border-radius: 8px; width: 100%; font-weight: bold; }}
    .leader-box {{ background: white; padding: 15px; border-radius: 10px; border-top: 5px solid {color_s}; text-align: center; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }}
    .juego-hoy {{ background-color: #ffeb3b; border: 2px solid #f44336; padding: 10px; border-radius: 10px; font-weight: bold; text-align: center; animation: blinker 1.5s linear infinite; }}
    @keyframes blinker {{ 50% {{ opacity: 0.5; }} }}
    .btn-social {{ padding: 8px 15px; border-radius: 5px; text-decoration: none; font-weight: bold; display: inline-block; margin: 5px; color: white !important; font-size: 12px; }}
    .btn-fb {{ background-color: #1877F2; }} .btn-wa {{ background-color: #25D366; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. BARRA LATERAL (LOGIN Y CONTADOR) ---
st.sidebar.title("🥎 LIGA 2026")
pass_admin = open("config.txt", "r").read().strip()
pwd = st.sidebar.text_input("Contraseña Admin:", type="password")
es_admin = (pwd == pass_admin)

# Contador de Visitas Real
st.sidebar.markdown("---")
html_contador = """<div align="center"><img src="https://counter1.optistats.ovh" border="0"><p style="color:white; font-size:12px;">Visitas Totales</p></div>"""
st.sidebar.components.v1.html(html_contador, height=80)

menu = st.sidebar.radio("MENÚ PRINCIPAL:", ["🏆 Standings", "📅 Calendario / Comentarios", "🥖 Bateo Individual", "🔥 Pitcheo Individual", "👤 Perfiles", "📸 Galería", "🔥 PLAYOFFS", "🌟 MVP", "📝 Lineup", "📲 QR", "⚙️ CONFIG"])

# --- 4. SECCIONES DEL SOFTWARE ---

# 4.1 STANDINGS (TABLA DE POSICIONES)
if menu == "🏆 Standings":
    st.header("📊 Tabla de Posiciones Temporada 2026")
    if not st.session_state.pitcheo.empty:
        stnd = st.session_state.pitcheo.groupby('Equipo').agg({'JG': 'sum', 'JP': 'sum', 'CF': 'sum', 'CC': 'sum'}).reset_index()
        stnd['JJ'] = stnd['JG'] + stnd['JP']
        stnd['PCT'] = (stnd['JG'] / stnd['JJ']).fillna(0).round(3)
        stnd['DIF'] = stnd['CF'] - stnd['CC']
        st.table(stnd.sort_values(by=['PCT', 'DIF'], ascending=False))
    else: st.info("Sin datos registrados.")

# 4.2 CALENDARIO Y COMENTARIOS FB
elif menu == "📅 Calendario / Comentarios":
    st.header("🗓️ Rol de Juegos y Foro")
    hoy = datetime.now().strftime("%d/%m/%Y")
    for _, r in st.session_state.juegos.iterrows():
        if r['Fecha'] == hoy: st.markdown(f"<div class='juego-hoy'>🚨 JUEGO HOY: {r['Local']} vs {r['Visita']} | {r['Hora']} | {r['Campo']}</div>", unsafe_allow_html=True)
    
    st.dataframe(st.session_state.juegos, use_container_width=True)
    
    if es_admin:
        with st.expander("➕ Agendar Juego"):
            with st.form("f_j"):
                f, h = st.date_input("Fecha"), st.time_input("Hora")
                l, v, c = st.text_input("Local"), st.text_input("Visita"), st.text_input("Campo")
                if st.form_submit_button("Guardar"):
                    st.session_state.juegos.loc[len(st.session_state.juegos)] = [f.strftime("%d/%m/%Y"), h.strftime("%H:%M"), l, v, c]
                    guardar_todo(); st.rerun()

    st.markdown("### 💬 Comentarios de la Afición")
    componente_fb = f"""<div id="fb-root"></div><script async defer src="https://connect.facebook.net"></script><div class="fb-comments" data-href="{URL_MI_PAGINA}" data-width="100%" data-numposts="5"></div>"""
    st.components.v1.html(componente_fb, height=400, scrolling=True)

# 4.3 BATEO INDIVIDUAL
elif menu == "🥖 Bateo Individual":
    st.header("📊 Líderes de Bateo")
    if not st.session_state.bateo.empty:
        df_b = st.session_state.bateo.copy()
        df_b['H_Tot'] = df_b['H'] + df_b['2B'] + df_b['3B'] + df_b['HR']
        df_b['AVG'] = (df_b['H_Tot'] / df_b['VB']).fillna(0).round(3)
        
        # Cuadro de Honor
        st.subheader("🥇 Top Bateadores")
        c1, c2, c3 = st.columns(3)
        best_h = df_b.loc[df_b['H_Tot'].idxmax()]
        best_hr = df_b.loc[df_b['HR'].idxmax()]
        best_avg = df_b.loc[df_b['AVG'].idxmax()]
        c1.markdown(f"<div class='leader-box'><b>HITS</b><br>{best_h['Nombre']}<br><b>{best_h['H_Tot']}</b></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='leader-box'><b>HR</b><br>{best_hr['Nombre']}<br><b>{best_hr['HR']}</b></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='leader-box'><b>AVG</b><br>{best_avg['Nombre']}<br><b>{best_avg['AVG']:.3f}</b></div>", unsafe_allow_html=True)
        
        st.dataframe(df_b.sort_values(by="AVG", ascending=False), use_container_width=True)

    if es_admin:
        with st.expander("➕ Registrar Bateador"):
            with st.form("r_b"):
                n, eq = st.text_input("Nombre"), st.text_input("Equipo")
                vb, h, hr = st.number_input("VB", 1), st.number_input("H", 0), st.number_input("HR", 0)
                if st.form_submit_button("Guardar"):
                    st.session_state.bateo.loc[len(st.session_state.bateo)] = [n, eq, vb, h, 0, 0, hr, 0]
                    guardar_todo(); st.rerun()

# 4.4 PERFILES Y COMPARTIR
elif menu == "👤 Perfiles":
    st.header("👤 Perfiles y Redes Sociales")
    if not st.session_state.perfiles.empty:
        sel = st.selectbox("Elegir Jugador:", st.session_state.perfiles['Nombre'].unique())
        p = st.session_state.perfiles[st.session_state.perfiles['Nombre'] == sel].iloc[0]
        
        st.image(p['FotoURL'] if p['FotoURL'] else "https://via.placeholder.com", width=150)
        st.subheader(p['Nombre'])
        st.write(f"Posición: {p['Posicion']} | Bio: {p['Bio']}")
        
        # Botones Compartir
        msg = f"Mira las stats de {p['Nombre']} en la Liga 2026: {URL_MI_PAGINA}"
        wa = f"https://api.whatsapp.com{urllib.parse.quote(msg)}"
        fb = f"https://www.facebook.com{urllib.parse.quote(URL_MI_PAGINA)}"
        col1, col2 = st.columns(2)
        col1.markdown(f'<a href="{wa}" target="_blank" class="btn-social btn-wa">🟢 WhatsApp</a>', unsafe_allow_html=True)
        col2.markdown(f'<a href="{fb}" target="_blank" class="btn-social btn-fb">🔵 Facebook</a>', unsafe_allow_html=True)

    if es_admin:
        with st.expander("➕ Crear Perfil"):
            with st.form("f_p"):
                np, fp, pp, bp = st.text_input("Nombre"), st.text_input("URL Foto"), st.text_input("Posición"), st.text_area("Bio")
                if st.form_submit_button("Crear"):
                    st.session_state.perfiles.loc[len(st.session_state.perfiles)] = [np, fp, pp, bp]
                    guardar_todo(); st.rerun()

# 4.5 CONFIGURACIÓN (COLORES, RESET, PASS)
elif menu == "⚙️ CONFIG":
    st.header("⚙️ Ajustes Maestros")
    if es_admin:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🎨 Diseño")
            ncp = st.color_picker("Barra Lateral", color_p)
            ncs = st.color_picker("Títulos/Botones", color_s)
            nbg = st.text_input("Imagen Fondo (URL)", bg_img)
            if st.button("Guardar Diseño"):
                with open("color_pri.txt", "w") as f: f.write(ncp)
                with open("color_sec.txt", "w") as f: f.write(ncs)
                with open("bg_url.txt", "w") as f: f.write(nbg)
                st.rerun()
        with c2:
            st.subheader("🔑 Seguridad")
            npw = st.text_input("Nueva Clave", type="password")
            if st.button("Cambiar Clave"):
                with open("config.txt", "w") as f: f.write(npw)
                st.success("Cambiada.")
        
        st.divider()
        if st.checkbox("BORRAR TODA LA TEMPORADA (RESET)"):
            if st.button("🔥 EJECUTAR RESET TOTAL"):
                for a in ARCHIVOS: 
                    if "csv" in a and os.path.exists(a): os.remove(a)
                st.rerun()
    else: st.error("Ingresa la clave en el menú lateral.")

# 4.6 QR, LINEUP, PLAYOFFS, MVP (Siguen la misma lógica de los bloques previos...)
elif menu == "📲 QR":
    st.header("📲 Generador de Código QR")
    url_q = st.text_input("Link de tu página:", URL_MI_PAGINA)
    if st.button("Generar QR"):
        qr = qrcode.make(url_q)
        buf = BytesIO()
        qr.save(buf, format="PNG")
        st.image(buf.getvalue(), width=300)

elif menu == "📝 Lineup":
    st.header("📋 Generador de Lineup Imprimible")
    equipo_l = st.text_input("Nombre del Equipo")
    jugadores = st.text_area("Lista de jugadores (uno por línea):")
    if jugadores:
        st.markdown(f"""<div style="border:2px dashed black; padding:20px; font-family:monospace;">
        <h3>EQUIPO: {equipo_l.upper()}</h3>
        {"<br>".join([f"{i+1}. {j} __________" for i, j in enumerate(jugadores.split('\n'))])}
        </div>""", unsafe_allow_html=True)

# 4.7 PITCHO INDIVIDUAL (FALTANTE)
elif menu == "🔥 Pitcheo Individual":
    st.header("📊 Líderes de Pitcheo")
    if not st.session_state.pitcheo.empty:
        df_p = st.session_state.pitcheo.copy()
        df_p['ERA'] = ((df_p['CL'] / df_p['IP']) * 7).fillna(0).round(2)
        st.dataframe(df_p, use_container_width=True)
    if es_admin:
        with st.expander("➕ Registrar Pitcher"):
            with st.form("r_p"):
                np, ep = st.text_input("Nombre"), st.text_input("Equipo")
                jg, jp, ip, cl = st.number_input("JG",0), st.number_input("JP",0), st.number_input("IP",0.1), st.number_input("CL",0)
                cf, cc = st.number_input("CF (Equipo)",0), st.number_input("CC (Equipo)",0)
                if st.form_submit_button("Guardar"):
                    st.session_state.pitcheo.loc[len(st.session_state.pitcheo)] = [np, ep, jg, jp, ip, cl, cf, cc, 0]
                    guardar_todo(); st.rerun()

# 4.8 GALERÍA Y MVP (Siguen misma lógica...)
elif menu == "📸 Galería":
    st.header("📸 Galería de la Liga")
    if not st.session_state.fotos.empty:
        cols = st.columns(3)
        for i, f in st.session_state.fotos.iterrows():
            with cols[i % 3]:
                st.image(f['URL'], use_container_width=True)
                if st.button(f"❤️ {f['Likes']} Likes", key=f"lk{i}"):
                    st.session_state.fotos.at[i, 'Likes'] += 1
                    guardar_todo(); st.rerun()
    if es_admin:
        with st.expander("📤 Subir Foto (Link)"):
            tf, uf = st.text_input("Título"), st.text_input("URL Imagen")
            if st.button("Publicar"):
                st.session_state.fotos.loc[len(st.session_state.fotos)] = [tf, uf, 0]
                guardar_todo(); st.rerun()

elif menu == "🌟 MVP":
    st.header("🌟 Jugador Más Valioso")
    if not st.session_state.mvp.empty:
        for _, m in st.session_state.mvp.iterrows():
            st.success(f"🏆 {m['Categoria']}: {m['Nombre']} ({m['Equipo']}) - {m['Stat']}")
    if es_admin:
        with st.form("f_mvp"):
            c_m, n_m, e_m, s_m = st.text_input("Categoría"), st.text_input("Nombre"), st.text_input("Equipo"), st.text_input("Hazaña")
            if st.form_submit_button("Publicar"):
                st.session_state.mvp.loc[len(st.session_state.mvp)] = [c_m, n_m, e_m, s_m, ""]
                guardar_todo(); st.rerun()

elif menu == "🔥 PLAYOFFS":
    st.header("🏆 Bracket de Playoffs")
    st.write("Configura las llaves de Semifinal y Final.")
    if not st.session_state.playoffs.empty:
        st.dataframe(st.session_state.playoffs, use_container_width=True)
    if es_admin:
        with st.form("f_pl"):
            fa, eq1, eq2, res = st.selectbox("Fase", ["Semifinal", "FINAL"]), st.text_input("Equipo 1"), st.text_input("Equipo 2"), st.text_input("Resultado")
            if st.form_submit_button("Actualizar Playoff"):
                st.session_state.playoffs.loc[len(st.session_state.playoffs)] = [fa, eq1, eq2, res, "Activo"]
                guardar_todo(); st.rerun()
