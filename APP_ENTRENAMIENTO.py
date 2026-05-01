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

# --- ESTILO CSS PERSONALIZADO (Para tipografía y centrado) ---
st.markdown("""
    <style>
    /* Importar fuentes modernas */
    @import url('https://fonts.googleapis.com/css2?family=Archivo+Black&family=Montserrat:wght@400;700&display=swap');

    /* Título Principal Estilo Archivo Black */
    .main-title {
        font-family: 'Archivo Black', sans-serif;
        color: #2E7D32;
        font-size: 3rem !important;
        text-align: center;
        margin-bottom: 0;
    }
    
    /* Fuente general de la app */
    html, body, [class*="css"]  {
        font-family: 'Montserrat', sans-serif;
    }
    
    /* Ajuste para que el logo en sidebar no tenga márgenes raros */
    [data-testid="stSidebarNav"] {
        padding-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN A GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- DISEÑO DE LA INTERFAZ (BARRA LATERAL) ---
with st.sidebar:
    # Usamos columnas para centrar el logo y que no se vea pequeño
    col_l1, col_l2, col_l3 = st.columns([1, 5, 1])
    with col_l2:
        try:
            # use_container_width hace que el logo se adapte al ancho de la barra
            st.image("logo.png", use_container_width=True)
        except:
            # Fallback a la imagen generada (Asegúrate que el nombre sea exacto)
            st.image("Gemini_Generated_Image_v1o06fv1o06fv1o0.png", use_container_width=True)
    
    st.markdown("<h2 style='text-align: center; font-family: Archivo Black;'>Zancada Maestra</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-weight: bold;'>Coach JAZ</p>", unsafe_allow_html=True)
    st.divider()
    
    opcion = st.radio("Menú Principal:", ["📝 Registrar Entrenamiento", "📊 Panel de Control"])
    st.divider()
    st.caption("© 2026 Zancada Maestra - Paipa, Boyacá")

# ---------------------------------------------------------
# OPCIÓN 1: REGISTRO DE ENTRENAMIENTO
# ---------------------------------------------------------
if opcion == "📝 Registrar Entrenamiento":
    st.markdown("<h1 class='main-title'>¡BIENVENIDO, ATLETA! ⚡</h1>", unsafe_allow_html=True)
    
    st.info("""
    **"La disciplina de hoy es tu victoria de mañana."**  
    Registra tus marcas con precisión. Con el apoyo del **Coach JAZ**, vamos a transformar tus límites en metas alcanzadas. 
    ¡A darle con toda! 🏃🏽‍♂️💨
    """)
    
    st.subheader("Formulario de Seguimiento")
    st.write("---")

    col_a, col_b = st.columns(2)
    with col_a:
        atleta_input = st.text_input("Nombre del Atleta", placeholder="Escribe tu nombre...")
        fecha_input = st.date_input("Fecha de la sesión", date.today())
    with col_b:
        distancia = st.number_input("Distancia Real (km)", min_value=0.0, step=0.1)
        tiempo = st.text_input("Tiempo Total (HH:MM:SS)", placeholder="ej: 00:45:30")

    col_c, col_d = st.columns(2)
    with col_c:
        sensacion = st.selectbox("¿Cómo te sentiste?", ["Excelente", "Bien", "Cansado", "Con Dolor"])
    with col_d:
        cumplimiento = st.radio("¿Cumpliste el objetivo?", ["Sí", "No"], horizontal=True)

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
            st.error("Atleta, por favor ingresa tu nombre.")
        else:
            fecha_str = fecha_input.strftime("%Y-%m-%d")
            
            mensajes_coach = {
                "Excelente": f"¡Esa es la actitud de un campeón! 🏆 ¡A seguir rompiendo marcas, {atleta_input}!",
                "Bien": "¡Buen trabajo! La constancia es el secreto del éxito. ¡Vamos por más!",
                "Cansado": "El descanso también es entrenamiento. Recupera bien, te quiero al 100% mañana. 🛌",
                "Con Dolor": "⚠️ ¡Cuidado! Escucha a tu cuerpo. Reporta esta molestia al Coach JAZ de inmediato."
            }
            msg_final = mensajes_coach.get(sensacion, "¡Registro completado!")

            nuevo_reg = {
                "Fecha": [fecha_str], "Atleta": [atleta_input], "Distancia": [distancia],
                "Tiempo": [tiempo], "Sensacion": [sensacion], "Cumplimiento": [cumplimiento]
            }
            for i in range(1, 13):
                valor = series_tiempos[i-1] if hubo_series and i <= len(series_tiempos) else ""
                nuevo_reg[f"Serie_{i}"] = [valor]
            
            try:
                df_nuevo = pd.DataFrame(nuevo_reg)
                existente = conn.read(ttl=0)
                
                es_duplicado = False
                if not existente.empty:
                    existente['Distancia'] = pd.to_numeric(existente['Distancia'], errors='coerce')
                    duplicados = existente[
                        (existente['Atleta'].astype(str) == atleta_input) & 
                        (existente['Fecha'].astype(str) == fecha_str) & 
                        (existente['Distancia'] == float(distancia))
                    ]
                    if not duplicados.empty:
                        es_duplicado = True

                if es_duplicado:
                    st.warning("⚠️ Este entrenamiento ya fue registrado anteriormente.")
                else:
                    df_final = pd.concat([existente, df_nuevo], ignore_index=True)
                    conn.update(data=df_final)
                    
                    if sensacion == "Con Dolor":
                        st.warning(msg_final)
                    else:
                        st.success(msg_final)
                        st.balloons()
                    
                    time.sleep(3)
                    st.rerun()
            except Exception as e:
                st.error(f"Error de conexión: {e}")

# ---------------------------------------------------------
# OPCIÓN 2: PANEL DE CONTROL
# ---------------------------------------------------------
else:
    st.markdown("<h1 class='main-title'>PANEL DE CONTROL</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Análisis estratégico por <b>Coach JAZ</b></p>", unsafe_allow_html=True)
    st.divider()

    try:
        df = conn.read(ttl=0)
        if df.empty:
            st.info("Aún no hay datos para analizar.")
        else:
            df['Fecha'] = pd.to_datetime(df['Fecha'])
            df['Distancia'] = pd.to_numeric(df['Distancia'], errors='coerce')

            atleta_sel = st.sidebar.selectbox("Filtrar Atleta:", ["Todos"] + list(df['Atleta'].unique()))
            df_plot = df.copy() if atleta_sel == "Todos" else df[df['Atleta'] == atleta_sel]

            k1, k2, k3 = st.columns(3)
            with k1: st.metric("Kilómetros Totales", f"{df_plot['Distancia'].sum():.1f} km")
            with k2: st.metric("Sesiones", len(df_plot))
            with k3: 
                fav = df_plot['Sensacion'].mode()[0] if not df_plot.empty else "N/A"
                st.metric("Estado Físico", fav)

            st.write("---")

            fig_evol = px.line(df_plot, x='Fecha', y='Distancia', color='Atleta', markers=True, 
                               title="Evolución del Kilometraje", template="plotly_white")
            fig_evol.update_traces(line_color='#2E7D32')
            st.plotly_chart(fig_evol, use_container_width=True)

            if atleta_sel != "Todos":
                st.subheader("⏱️ Detalle de Series")
                cols_s = [f"Serie_{i}" for i in range(1, 13)]
                df_s = df_plot[df_plot[cols_s].notna().any(axis=1)]
                
                if not df_s.empty:
                    f_sel = st.selectbox("Fecha de entrenamiento:", df_s['Fecha'].dt.date.unique())
                    fila = df_s[df_s['Fecha'].dt.date == f_sel].iloc[0]
                    
                    x_val, y_val = [], []
                    for c in cols_s:
                        if fila[c] and str(fila[c]).strip() != "":
                            x_val.append(c.replace("_", " "))
                            y_val.append(fila[c])
                    
                    if y_val:
                        fig_s = px.bar(x=x_val, y=y_val, title=f"Series del {f_sel}", 
                                       text_auto=True, color_discrete_sequence=['#2E7D32'])
                        st.plotly_chart(fig_s, use_container_width=True)
    except Exception as e:
        st.error(f"Error al cargar el panel: {e}")
