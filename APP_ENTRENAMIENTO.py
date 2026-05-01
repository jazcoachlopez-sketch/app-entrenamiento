import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import date
import time

# --- CONFIGURACIÓN DE IDENTIDAD Y PÁGINA ---
st.set_page_config(
    page_title="Zancada Maestra | Coach JAZ", 
    page_icon="⚡", 
    layout="wide"
)

# --- CONEXIÓN A GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- DISEÑO DE LA INTERFAZ (BARRA LATERAL) ---
with st.sidebar:
    st.image("descarga.png", width=100)
    st.title("Zancada Maestra")
    st.markdown(f"**Coach:** JAZ")
    st.divider()
    opcion = st.radio("Menú Principal:", ["📝 Registrar Entrenamiento", "📊 Panel de Control"])
    st.divider()
    st.caption("© 2026 Zancada Maestra - Paipa, Boyacá")

# ---------------------------------------------------------
# OPCIÓN 1: REGISTRO DE ENTRENAMIENTO
# ---------------------------------------------------------
if opcion == "📝 Registrar Entrenamiento":
    st.title("¡Bienvenido, atleta! ⚡")
    
    # Cuadro motivacional
    st.info("""
    **"La disciplina de hoy es tu victoria de mañana."**  
    Cada kilómetro cuenta y cada segundo te acerca a tu mejor versión. Registra tus marcas con honestidad; con el apoyo del **Coach JAZ**, vamos a transformar tus límites en metas alcanzadas. 
    
    ¡A darle con toda! 🏃🏽‍♂️💨
    """)
    
    st.subheader("Formulario de Seguimiento")
    st.write("---")

    # Inputs principales
    col_a, col_b = st.columns(2)
    with col_a:
        atleta_input = st.text_input("Nombre del Atleta", placeholder="Escribe tu nombre aquí...")
        fecha_input = st.date_input("Fecha de la sesión", date.today())
    with col_b:
        distancia = st.number_input("Distancia Real (km)", min_value=0.0, step=0.1)
        tiempo = st.text_input("Tiempo Total (HH:MM:SS)", placeholder="ej: 00:45:30")

    col_c, col_d = st.columns(2)
    with col_c:
        sensacion = st.selectbox("¿Cómo te sentiste?", ["Excelente", "Bien", "Cansado", "Con Dolor"])
    with col_d:
        cumplimiento = st.radio("¿Cumpliste el objetivo de la sesión?", ["Sí", "No"], horizontal=True)

    # Sección de Series
    st.write("---")
    hubo_series = st.checkbox("¿Realizaste series de velocidad?")
    series_tiempos = []

    if hubo_series:
        num_rep = st.slider("Número de repeticiones", 1, 12, 5)
        cols = st.columns(4)
        for i in range(num_rep):
            with cols[i % 4]:
                t = st.text_input(f"Serie {i+1}", key=f"rep_{i}", placeholder="0:00")
                series_tiempos.append(t)

    st.write("---")
    enviado = st.button("🚀 Guardar Entrenamiento")

    if enviado:
        if not atleta_input:
            st.error("Atleta, por favor ingresa tu nombre para continuar.")
        else:
            fecha_str = fecha_input.strftime("%Y-%m-%d")
            
            # 1. Preparar Diccionario de Datos
            nuevo_reg = {
                "Fecha": [fecha_str],
                "Atleta": [atleta_input],
                "Distancia": [distancia],
                "Tiempo": [tiempo],
                "Sensacion": [sensacion],
                "Cumplimiento": [cumplimiento]
            }
            # Agregar las 12 columnas de series
            for i in range(1, 13):
                valor = series_tiempos[i-1] if hubo_series and i <= len(series_tiempos) else ""
                nuevo_reg[f"Serie_{i}"] = [valor]
            
            df_nuevo = pd.DataFrame(nuevo_reg)

            # 2. Guardar en Google Sheets
            try:
                # Lectura en vivo sin caché
                existente = conn.read(ttl=0)
                
                # Validación de duplicados (Mismo atleta, fecha y distancia)
                es_duplicado = False
                if not existente.empty:
                    # Asegurar que la distancia sea numérica para comparar
                    existente['Distancia'] = pd.to_numeric(existente['Distancia'], errors='coerce')
                    duplicados = existente[
                        (existente['Atleta'].astype(str) == atleta_input) & 
                        (existente['Fecha'].astype(str) == fecha_str) & 
                        (existente['Distancia'] == float(distancia))
                    ]
                    if not duplicados.empty:
                        es_duplicado = True

                if es_duplicado:
                    st.warning(f"⚠️ Ya existe un registro igual para {atleta_input} en esta fecha.")
                else:
                    df_final = pd.concat([existente, df_nuevo], ignore_index=True)
                    df_final = df_final.dropna(how='all')
                    conn.update(data=df_final)
                    
                    st.success(f"¡Excelente, {atleta_input}! Tu progreso ha sido registrado.")
                    st.balloons()
                    time.sleep(2)
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Error al conectar con la base de datos: {e}")

# ---------------------------------------------------------
# OPCIÓN 2: PANEL DE CONTROL (VISUALIZACIÓN)
# ---------------------------------------------------------
else:
    st.title("📊 Panel de Control - Zancada Maestra")
    st.markdown(f"Análisis estratégico de rendimiento por el **Coach JAZ**")
    st.divider()

    try:
        # Cargar datos
        df = conn.read(ttl=0)
        
        if df.empty or len(df.columns) < 2:
            st.info("Aún no hay datos registrados para mostrar el análisis.")
        else:
            # Limpieza de datos para gráficas
            df['Fecha'] = pd.to_datetime(df['Fecha'])
            df['Distancia'] = pd.to_numeric(df['Distancia'], errors='coerce')

            # Filtros en la barra lateral (Sidebar)
            st.sidebar.subheader("Configuración de Vista")
            atleta_sel = st.sidebar.selectbox("Filtrar por Atleta:", ["Todos"] + list(df['Atleta'].unique()))
            
            df_plot = df.copy()
            if atleta_sel != "Todos":
                df_plot = df[df['Atleta'] == atleta_sel]

            # Indicadores Clave (KPIs)
            kpi1, kpi2, kpi3 = st.columns(3)
            with kpi1:
                st.metric("Distancia Total", f"{df_plot['Distancia'].sum():.1f} km")
            with kpi2:
                st.metric("Sesiones Totales", len(df_plot))
            with kpi3:
                # Calcular la sensación más frecuente
                if not df_plot.empty:
                    fav = df_plot['Sensacion'].mode()[0]
                    st.metric("Estado de Ánimo", fav)

            st.write("---")

            # Gráfica de Evolución
            fig_evolucion = px.line(
                df_plot, x='Fecha', y='Distancia', color='Atleta',
                title="Progresión de Kilometraje Diario",
                markers=True,
                template="plotly_white",
                color_discrete_sequence=px.colors.qualitative.Dark2
            )
            st.plotly_chart(fig_evolucion, use_container_width=True)

            # Detalle de Series de Velocidad
            st.subheader("⏱️ Análisis de Tiempos en Series")
            columnas_series = [f"Serie_{i}" for i in range(1, 13)]
            
            if atleta_sel != "Todos":
                # Filtrar solo entrenamientos que tengan series registradas
                mask = df_plot[columnas_series].notna().any(axis=1) & (df_plot[columnas_series] != "")
                entrenamientos_con_series = df_plot[mask]
                
                if not entrenamientos_con_series.empty:
                    fecha_sel = st.selectbox(
                        "Selecciona una fecha de entrenamiento para analizar las series:", 
                        entrenamientos_con_series['Fecha'].dt.date.unique()
                    )
                    
                    # Obtener la fila específica
                    fila = entrenamientos_con_series[entrenamientos_con_series['Fecha'].dt.date == fecha_sel].iloc[0]
                    
                    # Preparar datos para la gráfica de barras
                    eje_x = []
                    eje_y = []
                    for col in columnas_series:
                        if fila[col] and str(fila[col]).strip() != "":
                            eje_x.append(col.replace("_", " "))
                            eje_y.append(fila[col])
                    
                    if eje_y:
                        fig_barras = px.bar(
                            x=eje_x, y=eje_y, 
                            title=f"Desempeño de Series - {fecha_sel}",
                            labels={'x': 'Repetición', 'y': 'Tiempo'},
                            text_auto=True,
                            color_discrete_sequence=['#2E7D32']
                        )
                        st.plotly_chart(fig_barras, use_container_width=True)
                else:
                    st.info("Este atleta aún no tiene series de velocidad registradas.")
            else:
                st.write("👉 *Selecciona un atleta en el menú lateral para ver el detalle de sus series.*")

    except Exception as e:
        st.error(f"Error al cargar los datos del panel: {e}")
