# ---------------------------------------------------------
# OPCIÓN 2: MI PLAN SEMANAL (Visualización para Atletas)
# ---------------------------------------------------------
elif opcion == "📅 Mi Plan Semanal":
    st.markdown("<h1 class='main-title'>TU PLAN SEMANAL 📅</h1>", unsafe_allow_html=True)
    st.info("Consulta las directrices asignadas para tu semana. Sigue la ruta trazada por el Coach JAZ.")

    try:
        df_planes = conn.read(worksheet="Planes", ttl=0)
        
        if df_planes.empty:
            st.warning("Aún no se registran planes en la pestaña 'Planes' de la base de datos.")
        else:
            # Limpiamos espacios en blanco alrededor de los nombres de los atletas
            df_planes['Atleta'] = df_planes['Atleta'].astype(str).str.strip()
            
            lista_atletas = df_planes['Atleta'].dropna().unique()
            # Quitamos textos vacíos de la lista
            lista_atletas = [a for a in lista_atletas if a not forcing_str == 'nan' and a != '']
            
            atleta_plan = st.selectbox("Selecciona tu nombre para cargar tu planificación:", [""] + list(lista_atletas))

            if atleta_plan:
                st.write(f"### Hoja de ruta para: **{atleta_plan}**")
                st.divider()
                
                # Filtramos el plan del atleta seleccionado
                df_mi_plan = df_planes[df_planes['Atleta'] == atleta_plan].copy()
                
                # Limpieza de columnas para evitar fallos por tildes o mayúsculas
                df_mi_plan['Dia'] = df_mi_plan['Dia'].astype(str).str.strip().str.capitalize()
                df_mi_plan['Jornada'] = df_mi_plan['Jornada'].astype(str).str.strip().str.capitalize()
                
                # Mapeo por si en el Sheets escribieron los días sin tilde
                reemplazos_dias = {"Miercoles": "Miércoles", "Sabado": "Sábado"}
                df_mi_plan['Dia'] = df_mi_plan['Dia'].replace(reemplazos_dias)

                dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
                
                for dia in dias_semana:
                    plan_dia = df_mi_plan[df_mi_plan['Dia'] == dia]
                    
                    if not plan_dia.empty:
                        with st.expander(f"🗓️ {dia}", expanded=True):
                            col_m, col_t = st.columns(2)
                            
                            # Filtramos ignorando si escribieron minúsculas o mayúsculas en el Sheets
                            plan_manana = plan_dia[plan_dia['Jornada'] == "Mañana"]
                            plan_tarde = plan_dia[plan_dia['Jornada'] == "Tarde"]
                            
                            with col_m:
                                st.markdown("🌅 **Jornada Mañana:**")
                                if not plan_manana.empty and str(plan_manana.iloc[0]['Entrenamiento']).strip() != "nan":
                                    st.success(plan_manana.iloc[0]['Entrenamiento'])
                                else:
                                    st.write("*Descanso / Sesión Libre*")
                                    
                            with col_t:
                                st.markdown("🌇 **Jornada Tarde:**")
                                if not plan_tarde.empty and str(plan_tarde.iloc[0]['Entrenamiento']).strip() != "nan":
                                    st.info(plan_tarde.iloc[0]['Entrenamiento'])
                                else:
                                    st.write("*Descanso / Sesión Libre*")
                    else:
                        # Si quieres que aparezcan todos los días de la semana, incluso los que no programaste nada:
                        with st.expander(f"🗓️ {dia}", expanded=False):
                            col_m, col_t = st.columns(2)
                            with col_m:
                                st.markdown("🌅 **Jornada Mañana:**\n\n*Descanso / Sesión Libre*")
                            with col_t:
                                st.markdown("🌇 **Jornada Tarde:**\n\n*Descanso / Sesión Libre*")
                                
    except Exception as e:
        st.error(f"Error técnico al leer la hoja de planificación: {e}")
