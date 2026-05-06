import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import date
import time

# --- CONFIGURACIÓN DE IDENTIDAD Y PÁGINA ---
st.set_page_config(
    page_title="CORRIENDO ANDO | Coach JAZ", 
    page_icon="🏃🏽‍♂️", 
    layout="wide"
)

# --- ESTILO CSS PERSONALIZADO ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Archivo+Black&family=Montserrat:wght@400;700&display=swap');

    .main-title {
        font-family: 'Archivo Black', sans-serif;
        color: #2E7D32;
        font-size: 3rem !important;
        text-align: center;
        margin-bottom: 0;
    }
    
    html, body, [class*="css"]  {
        font-family: 'Montserrat', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN A GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- DISEÑO DE LA INTERFAZ (BARRA LATERAL) ---
with st.sidebar:
    col_l1, col_l2, col_l3 = st.columns([1, 5, 1])
    with col_l2:
        try:
            st.image("logo.png", use_container_width=True)
        except:
            st.image("https://cdn-icons-png.flaticon.com/512/7159/7159044.png", use_container_width=True)
    
    st.markdown("<h2 style='text-align: center; font-family: Archivo Black;'>CORRIENDO ANDO</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-weight: bold;'>Coach JAZ</p>", unsafe_allow_html=True)
    st.divider()
    
    opcion = st.sidebar.radio("Menú Principal:", ["📝 Registrar Entrenamiento", "📊 Panel de Control"])
    st.divider()
    st.caption("© 2026 Corriendo Ando - Paipa, Boyacá")

# ---------------------------------------------------------
# OPCIÓN 1: REGISTRO DE ENTRENAMIENTO
# ---------------------------------------------------------
if opcion == "📝 Registrar Entrenamiento":
    st.markdown("<h1 class='main-title'>¡BIENVENIDO, ATLETA! ⚡</h1>", unsafe_allow_html=True)
    
    st.info("""
    **"La disciplina de hoy es tu victoria de mañana."**  
    Registra tu sesión en **Corriendo Ando**. No olvides reportar tu trabajo de fuerza, es clave para tu rendimiento. 
    ¡A darle con toda! 🏃🏽‍♂️💨
    """)
    
    st.subheader("Formulario de Seguimiento")
    st.write("---")

    col_a, col_b = st.columns(2)
    with col_a:
        atleta_input = st.text_input("Nombre del Atleta", placeholder="Tu nombre...")
        fecha_input = st.date_input("Fecha de la sesión", date.today())
        jornada = st.radio("Jornada:", ["Mañana", "Tarde"], horizontal=True)
        
    with col_b:
        distancia = st.number_input("Distancia Real (km)", min_value=0.0, step=0.1)
        tiempo = st.text_input("Tiempo Total (HH:MM:SS)", placeholder="ej: 00:45:30")

    # --- SECCIÓN DE GIMNASIO / FUERZA ---
    st.markdown("### 🏋️‍♂️ Trabajo de Fuerza")
    col_gym1, col_gym2 = st.columns([1, 2])
    with col_gym1:
        hizo_gym = st.selectbox("¿Realizaste ejercicios de fuerza?", ["No", "Sí"])
    
    detalle_gym = ""
    if hizo_gym == "Sí":
        with col_gym2:
            detalle_gym = st.text_area("Cuéntame qué hiciste:", placeholder="Ej: Sentadillas 4x12, Plancha 3 min, Fortalecimiento de core...")

    st.write("---")
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
                "Excelente": f"¡Esa es la actitud de un campeón! 🏆 ¡A seguir sumando en Corriendo Ando, {atleta_input}!",
                "Bien": "¡Buen trabajo! La fuerza te hará más rápido. ¡Vamos por más!",
                "Cansado": "El descanso también es entrenamiento. Recupera bien hoy. 🛌",
                "Con Dolor": "⚠️ ¡Cuidado! Escucha a tu cuerpo. Reporta esta molestia al Coach JAZ."
            }
            msg_final = mensajes_coach.get(sensacion, "¡Registro completado!")

            nuevo_reg = {
                "Fecha": [fecha_str], 
                "Atleta": [atleta_input], 
                "Jornada": [jornada],
                "Distancia": [distancia],
                "Tiempo": [tiempo], 
                "Gimnasio": [hizo_gym],        # NUEVO DATO
                "Detalle_Gimnasio": [detalle_gym], # NUEVO DATO
                "Sensacion": [sensacion], 
                "Cumplimiento": [cumplimiento]
            }
            for i in range(1, 13):
                valor = series_tiempos[i-1] if hubo_series and i <= len(series_tiempos) else ""
                nuevo_reg[f"Serie_{i}"] = [valor]
            
            try:
                df_nuevo = pd.DataFrame(nuevo_reg)
                existente = conn.read(ttl=0)
                
                # Validación anti-duplicados
                es_duplicado = False
                if not existente.empty:
                    existente['Distancia'] = pd.to_numeric(existente['Distancia'], errors='coerce')
                    duplicados = existente[
                        (existente['Atleta'].astype(str) == atleta_input) & 
                        (existente['Fecha'].astype(str) == fecha_str) & 
                        (existente['Jornada'].astype(str) == jornada) &
                        (existente['Distancia'] == float(distancia))
                    ]
                    if not duplicados.empty:
                        es_duplicado = True

                if es_duplicado:
                    st.warning("⚠️ Este entrenamiento ya fue registrado.")
                else:
                    df_final = pd.concat([existente, df_nuevo], ignore_index=True)
                    conn.update(data=df_final)
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
    st.markdown("<h1 class='main-title'>CORRIENDO ANDO - PANEL</h1>", unsafe_allow_html=True)
    st.divider()

    try:
        df = conn.read(ttl=0)
        if df.empty:
            st.info("Aún no hay datos.")
        else:
            df['Fecha'] = pd.to_datetime(df['Fecha'])
            df['Distancia'] = pd.to_numeric(df['Distancia'], errors='coerce')

            atleta_sel = st.sidebar.selectbox("Seleccionar Atleta:", ["Todos"] + list(df['Atleta'].unique()))
            df_plot = df.copy() if atleta_sel == "Todos" else df[df['Atleta'] == atleta_sel]

            # KPIs
            k1, k2, k3 = st.columns(3)
            with k1: st.metric("Kilómetros Totales", f"{df_plot['Distancia'].sum():.1f} km")
            with k2: st.metric("Sesiones", len(df_plot))
            with k3:
                # Conteo de sesiones de gimnasio
                sesiones_gym = len(df_plot[df_plot['Gimnasio'] == "Sí"])
                st.metric("Sesiones de Fuerza", sesiones_gym)

            st.write("---")
            # Mostrar tabla de detalles de fuerza si existe un atleta seleccionado
            if atleta_sel != "Todos" and sesiones_gym > 0:
                with st.expander("Ver bitácora de Gimnasio/Fuerza"):
                    st.table(df_plot[df_plot['Gimnasio'] == "Sí"][['Fecha', 'Jornada', 'Detalle_Gimnasio']])

            fig_evol = px.line(df_plot, x='Fecha', y='Distancia', color='Jornada', markers=True, title="Progreso de Distancia")
            st.plotly_chart(fig_evol, use_container_width=True)

    except Exception as e:
        st.error(f"Error al cargar el panel: {e}")
