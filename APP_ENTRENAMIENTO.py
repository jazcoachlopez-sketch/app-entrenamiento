import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import date
import time

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="App Entrenamiento - Coach", layout="wide")

# --- CONEXIÓN A GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- MENÚ DE PESTAÑAS ---
tab_registro, tab_panel = st.tabs(["📝 Registro de Atletas", "📊 Panel de Control"])

# ---------------------------------------------------------
# PESTAÑA 1: REGISTRO
# ---------------------------------------------------------
with tab_registro:
    st.title("🏃🏽‍♂️ Registro Diario")
    st.write("Completa los datos de tu sesión de hoy.")

    atleta_input = st.text_input("Nombre del Atleta", placeholder="Ej: Juan Pérez", key="reg_atleta")
    fecha_input = st.date_input("Fecha", date.today(), key="reg_fecha")

    col1, col2 = st.columns(2)
    with col1:
        distancia = st.number_input("Distancia Real (km)", min_value=0.0, step=0.1)
        tiempo = st.text_input("Tiempo Real", placeholder="ej: 00:55:00")
    with col2:
        sensacion = st.selectbox("Sensación", ["Excelente", "Bien", "Cansado", "Con Dolor"])
        cumplimiento = st.radio("¿Cumpliste el objetivo?", ["Sí", "No"])

    hubo_series = st.checkbox("¿Hiciste series de velocidad?")
    series_tiempos = []

    if hubo_series:
        num_rep = st.slider("Número de repeticiones", 1, 12, 5)
        cols = st.columns(4)
        for i in range(num_rep):
            with cols[i % 4]:
                t = st.text_input(f"S{i+1}", key=f"rep_{i}")
                series_tiempos.append(t)

    enviado = st.button("Guardar Entrenamiento")

    if enviado:
        if not atleta_input:
            st.error("Por favor, ingresa el nombre.")
        else:
            fecha_str = fecha_input.strftime("%Y-%m-%d")
            nuevo_reg = {
                "Fecha": [fecha_str],
                "Atleta": [atleta_input],
                "Distancia": [distancia],
                "Tiempo": [tiempo],
                "Sensacion": [sensacion],
                "Cumplimiento": [cumplimiento]
            }
            for i in range(1, 13):
                valor = series_tiempos[i-1] if hubo_series and i <= len(series_tiempos) else ""
                nuevo_reg[f"Serie_{i}"] = [valor]
            
            df_nuevo = pd.DataFrame(nuevo_reg)

            try:
                existente = conn.read(ttl=0)
                # Anti-duplicados
                es_duplicado = False
                if not existente.empty:
                    # Asegurar tipos de datos para comparar
                    existente['Distancia'] = pd.to_numeric(existente['Distancia'], errors='coerce')
                    duplicados = existente[
                        (existente['Atleta'].astype(str) == atleta_input) & 
                        (existente['Fecha'].astype(str) == fecha_str) & 
                        (existente['Distancia'] == float(distancia))
                    ]
                    if not duplicados.empty:
                        es_duplicado = True

                if es_duplicado:
                    st.warning("⚠️ Este entrenamiento ya fue registrado.")
                else:
                    df_final = pd.concat([existente, df_nuevo], ignore_index=True)
                    conn.update(data=df_final)
                    st.success("¡Datos guardados!")
                    st.balloons()
                    time.sleep(2)
                    st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

# ---------------------------------------------------------
# PESTAÑA 2: PANEL DE CONTROL (VISUALIZACIÓN)
# ---------------------------------------------------------
with tab_panel:
    st.title("📊 Análisis de Rendimiento")
    
    try:
        df = conn.read(ttl=0)
        
        if df.empty or len(df.columns) < 2:
            st.info("Aún no hay datos suficientes para mostrar estadísticas.")
        else:
            # Limpieza básica de datos
            df['Fecha'] = pd.to_datetime(df['Fecha'])
            df['Distancia'] = pd.to_numeric(df['Distancia'], errors='coerce')

            # Filtros superiores
            atleta_sel = st.selectbox("Selecciona un Atleta para filtrar:", ["Todos"] + list(df['Atleta'].unique()))
            
            df_plot = df.copy()
            if atleta_sel != "Todos":
                df_plot = df[df['Atleta'] == atleta_sel]

            # KPIs Rápidos
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Total Kilómetros", f"{df_plot['Distancia'].sum():.1f} km")
            with c2:
                st.metric("Sesiones Registradas", len(df_plot))
            with c3:
                sensacion_fav = df_plot['Sensacion'].mode()[0] if not df_plot.empty else "N/A"
                st.metric("Sensación Predominante", sensacion_fav)

            st.divider()

            # Gráfica 1: Evolución de Distancia
            fig_dist = px.line(df_plot, x='Fecha', y='Distancia', color='Atleta',
                               title="Evolución de Kilometraje", markers=True,
                               labels={'Distancia': 'Km recorridos', 'Fecha': 'Día'})
            st.plotly_chart(fig_dist, use_container_width=True)

            # Gráfica 2: Análisis de Series (Si el atleta seleccionado tiene series)
            st.subheader("⏱️ Análisis de Series de Velocidad")
            # Tomamos las columnas Serie_1 a Serie_12
            columnas_series = [f"Serie_{i}" for i in range(1, 13)]
            
            if atleta_sel != "Todos":
                entrenamiento_series = df_plot[df_plot[columnas_series].notna().any(axis=1)]
                
                if not entrenamiento_series.empty:
                    # Seleccionar una fecha para ver sus series
                    fecha_series = st.selectbox("Selecciona una fecha de entrenamiento:", 
                                               entrenamiento_series['Fecha'].dt.date.unique())
                    
                    datos_fecha = entrenamiento_series[entrenamiento_series['Fecha'].dt.date == fecha_series].iloc[0]
                    
                    # Preparar datos para gráfica de barras
                    tiempos_series = []
                    nombres_series = []
                    for col in columnas_series:
                        if datos_fecha[col]: # Si hay tiempo registrado
                            tiempos_series.append(datos_fecha[col])
                            nombres_series.append(col)
                    
                    if tiempos_series:
                        fig_series = px.bar(x=nombres_series, y=tiempos_series, 
                                           title=f"Tiempos de Series - {fecha_series}",
                                           labels={'x': 'Número de Serie', 'y': 'Tiempo (min/seg)'},
                                           text_auto=True)
                        st.plotly_chart(fig_series, use_container_width=True)
                else:
                    st.write("Este atleta no tiene registros de series de velocidad.")
            else:
                st.write("Selecciona un atleta específico para ver el detalle de sus series.")

    except Exception as e:
        st.error(f"Error al cargar el panel: {e}")
