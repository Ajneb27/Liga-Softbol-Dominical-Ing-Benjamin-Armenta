# ==========================================
# SECCIÓN: 🏆 TOP 10 LÍDERES (COMPLETO)
# ==========================================
elif menu == "🏆 LÍDERES":
    t_b, t_p = st.tabs(["🥖 Departamentos de Bateo", "🔥 Departamentos de Pitcheo"])
    
    with t_b:
        df_b = st.session_state.jugadores.copy()
        if not df_b.empty:
            # Cálculos necesarios
            df_b['H_T'] = df_b['H'] + df_b['H2'] + df_b['H3'] + df_b['HR']
            df_b['AVG'] = (df_b['H_T'] / df_b['VB'].replace(0, 1)).fillna(0)
            
            # Fila 1: AVG y Hits Totales
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("🥇 Porcentaje (AVG)")
                st.table(df_b.sort_values("AVG", ascending=False).head(10)[["Nombre", "AVG"]].style.format({"AVG": "{:.3f}"}))
            with c2:
                st.subheader("🥇 Hits Totales (H)")
                st.table(df_b.sort_values("H_T", ascending=False).head(10)[["Nombre", "H_T"]])
            
            # Fila 2: Jonrones y Dobles
            c3, c4 = st.columns(2)
            with c3:
                st.subheader("🥇 Jonrones (HR)")
                st.table(df_b.sort_values("HR", ascending=False).head(10)[["Nombre", "HR"]])
            with c4:
                st.subheader("🥇 Dobles (H2)")
                st.table(df_b.sort_values("H2", ascending=False).head(10)[["Nombre", "H2"]])
            
            # Fila 3: Triples
            st.subheader("🥇 Triples (H3)")
            st.table(df_b.sort_values("H3", ascending=False).head(10)[["Nombre", "H3"]])
        else:
            st.info("No hay datos de bateadores registrados.")

    with t_p:
        df_p = st.session_state.pitchers.copy()
        if not df_p.empty:
            # Cálculo de Efectividad (ERA) basado en 7 entradas
            df_p['EFE'] = ((df_p['CL'] * 7) / df_p['IP'].replace(0, 1)).fillna(0)
            
            # Fila 1: Efectividad y Ganados
            cp1, cp2 = st.columns(2)
            with cp1:
                st.subheader("🥇 Efectividad (EFE)")
                # Solo mostrar pitchers con innings lanzados para la efectividad
                st.table(df_p[df_p['IP'] > 0].sort_values("EFE", ascending=True).head(10)[["Nombre", "EFE"]].style.format({"EFE": "{:.2f}"}))
            with cp2:
                st.subheader("🥇 Ganados (JG)")
                st.table(df_p.sort_values("JG", ascending=False).head(10)[["Nombre", "JG"]])
            
            # Fila 2: Perdidos e Innings
            cp3, cp4 = st.columns(2)
            with cp3:
                st.subheader("🥇 Perdidos (JP)")
                st.table(df_p.sort_values("JP", ascending=False).head(10)[["Nombre", "JP"]])
            with cp4:
                st.subheader("🥇 Innings (IP)")
                st.table(df_p.sort_values("IP", ascending=False).head(10)[["Nombre", "IP"]])
        else:
            st.info("No hay datos de pitchers registrados.")
