import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import date
import time

# --- 1. CONFIGURACIÓN DE IDENTIDAD Y PÁGINA ---
st.set_page_config(
    page_title="CORRIENDO ANDO | Coach JAZ", 
    page_icon="🏃🏽‍♂️", 
    layout="wide"
)

# --- 2. ESTILO CSS PERSONALIZADO (Look de Alto Rendimiento) ---
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
    
    [data-testid="stSidebarNav"] { padding-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONEXIÓN A GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 4. DISEÑO DE LA BARRA LATERAL (Navegación e Identidad) ---
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
    
    # Menú Principal con las 3 opciones requeridas
    opcion = st.radio("Menú Principal:", [
        "📝 Registrar Entrenamiento", 
        "📅 Mi Plan Semanal", 
        "📊 Panel de Control"
    ])
    st.divider()
    st.caption("© 2026 Corriendo Ando - Paipa, Boyacá")

# ---------------------------------------------------------
# OPCIÓN 1: REGISTRO DE ENTRENAMIENTO
# ---------------------------------------------------------
if opcion == "📝 Registrar Entrenamiento":
    st.markdown("<h1 class='main-title'>¡BIENVENIDO, ATLETA! ⚡</h1>", unsafe_allow_html=True)
    
    st.info("""
    **"La disciplina de hoy es tu victoria de mañana."** Registra tu sesión en **Corriendo Ando**. 
    Detalla tu trabajo de fuerza y las series asignadas para que el **Coach JAZ** pueda evaluar tu progreso. ¡Vamos con toda! 🏃🏽‍♂️💨
    """)
    
    st.subheader("Formulario de Seguimiento")
    st.write("---")

    col_a, col_b = st.columns(2)
    with col_a:
        atleta_input = st.text_input("Nombre del Atleta", placeholder="Escribe tu nombre completo...")
        fecha_input = st.date_input("Fecha de la sesión", date.today())
        jornada = st.radio("Jornada del entrenamiento:", ["Mañana", "Tarde"], horizontal=True)
        
    with col_b:
        distancia = st.number_input("Distancia Real Alcanzada (km)", min_value=0.0, step=0.1)
        tiempo = st.text_input("Tiempo Total (HH:MM:SS)", placeholder="ej: 00:45:30")

    st.markdown("### 🏋️‍♂️ Trabajo de Fuerza")
    col_gym1, col_gym2 = st.columns([1, 2])
    with col_gym1:
        hizo_gym = st.selectbox("¿Realizaste ejercicios de fuerza?", ["No", "Sí"])
    
    detalle_gym = ""
    if hizo_gym == "Sí":
        with col_gym2:
            detalle_gym = st.text_area("Detalles de la rutina:", placeholder="Ej: Ejercicios de core, sentadillas, cargas pesadas...")

    st.write("---")
    
    hubo_series = st.checkbox("¿Realizaste series de velocidad en esta sesión?")
    series_tiempos = []
    tipo_velocidad = ""

    if hubo_series:
        st.markdown("### ⏱️ Series de Velocidad")
        tipo_velocidad = st.text_input("Tipo de trabajo asignado:", placeholder="Ej: 10x400m, Cuestas explosivas, Fartlek 3-2-1...")
        
        num_rep = st.slider("Número de repeticiones realizadas", 1, 12, 5)
        cols = st.columns(4)
        for i in range(num_rep):
            with cols[i % 4]:
                t = st.text_input(f"Serie {i+1}", key=f"rep_{i}", placeholder="0:00")
                series_tiempos.append(t)
        st.write("---")

    col_c, col_d = st.columns(2)
    with col_c:
        sensacion = st.selectbox("¿Cómo estuvo tu sensación física?", ["Excelente", "Bien", "Cansado", "Con Dolor"])
    with col_d:
        cumplimiento = st.radio("¿Cumpliste a cabalidad el objetivo?", ["Sí", "No"], horizontal=True)

    st.write("---")
    enviado = st.button("🚀 Guardar Entrenamiento")

    if enviado:
        if not atleta_input:
            st.error("Por favor, ingresa tu nombre para procesar el registro.")
        else:
            fecha_str = fecha_input.strftime("%Y-%m-%d")
            
            mensajes_coach = {
                "Excelente": f"¡Actitud de campeón! 🏆 ¡A seguir sumando en Corriendo Ando, {atleta_input}!",
                "Bien": "¡Buen trabajo! La constancia es el secreto del éxito. ¡Vamos por más!",
                "Cansado": "El descanso también es entrenamiento. Recupera bien hoy para asimilar la carga. 🛌",
                "Con Dolor": "⚠️ ¡Cuidado! Escucha a tu cuerpo. Reporta esta molestia al Coach JAZ de inmediato."
            }
            msg_final = mensajes_coach.get(sensacion, "¡Registro completado con éxito!")

            nuevo_reg = {
                "Fecha": [fecha_str], 
                "Atleta": [atleta_input], 
                "Jornada": [jornada],
                "Distancia": [distancia], 
                "Tiempo": [tiempo], 
                "Gimnasio": [hizo_gym],
                "Detalle_Gimnasio": [detalle_gym], 
                "Tipo_Velocidad": [tipo_velocidad],
                "Sensacion": [sensacion], 
                "Cumplimiento": [cumplimiento]
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
                        (existente['Jornada'].astype(str) == jornada) &
                        (existente['Distancia'] == float(distancia))
                    ]
                    if not duplicados.empty: es_duplicado = True

                if es_duplicado:
                    st.warning(f"⚠️ Este entrenamiento de la jornada de la {jornada} ya se encuentra registrado.")
                else:
                    df_final = pd.concat([existente, df_nuevo], ignore_index=True)
                    conn.update(data=df_final)
                    st.success(msg_final)
                    st.balloons()
                    time.sleep(3)
                    st.rerun()
            except Exception as e:
                st.error(f"Error al intentar conectar con la base de datos: {e}")

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
            lista_atletas = df_planes['Atleta'].dropna().unique()
            atleta_plan = st.selectbox("Selecciona tu nombre para cargar tu planificación:", [""] + list(lista_atletas))

            if atleta_plan:
                st.write(f"### Hoja de ruta para: **{atleta_plan}**")
                st.divider()
                
                df_mi_plan = df_planes[df_planes['Atleta'] == atleta_plan]
                dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
                
                for dia in dias_semana:
                    plan_dia = df_mi_plan[df_mi_plan['Dia'] == dia]
                    
                    if not plan_dia.empty:
                        with st.expander(f"🗓️ {dia}", expanded=True):
                            col_m, col_t = st.columns(2)
                            
                            plan_manana = plan_dia[plan_dia['Jornada'] == "Mañana"]
                            plan_tarde = plan_dia[plan_dia['Jornada'] == "Tarde"]
                            
                            with col_m:
                                st.markdown("🌅 **Jornada Mañana:**")
                                if not plan_manana.empty:
                                    st.success(plan_manana.iloc[0]['Entrenamiento'])
                                else:
                                    st.write("*Descanso / Sesión Libre*")
                                    
                            with col_t:
                                st.markdown("🌇 **Jornada Tarde:**")
                                if not plan_tarde.empty:
                                    st.info(plan_tarde.iloc[0]['Entrenamiento'])
                                else:
                                    st.write("*Descanso / Sesión Libre*")
    except Exception as e:
        st.error(f"Error técnico al leer la hoja de planificación: {e}")
        st.caption("Verifica que la pestaña se llame exactamente 'Planes' y tenga los encabezados: Atleta, Dia, Jornada, Entrenamiento.")

# ---------------------------------------------------------
# OPCIÓN 3: PANEL DE CONTROL (Privado para el Entrenador)
# ---------------------------------------------------------
else:
    st.markdown("<h1 class='main-title'>ÁREA RESTRINGIDA</h1>", unsafe_allow_html=True)
    st.sidebar.divider()
    st.sidebar.subheader("🔐 Acceso Entrenador")
    password = st.sidebar.text_input("Llave Maestra:", type="password")

    if password == "CoachJaz2026":
        st.success("Acceso concedido. Panel estratégico de Corriendo Ando activado.")
        st.markdown("<h1 class='main-title'>CORRIENDO ANDO - ESTRATEGIA</h1>", unsafe_allow_html=True)
        st.write("---")
        
        try:
            df = conn.read(ttl=0)
            if df.empty:
                st.info("No se registran datos históricos en la base de datos principal.")
            else:
                df['Fecha'] = pd.to_datetime(df['Fecha'])
                df['Distancia'] = pd.to_numeric(df['Distancia'], errors='coerce')

                atleta_sel = st.sidebar.selectbox("Seleccionar Atleta a evaluar:", ["Todos"] + list(df['Atleta'].unique()))
                j_sel = st.sidebar.multiselect("Filtrar por Jornadas:", ["Mañana", "Tarde"], default=["Mañana", "Tarde"])
                
                df_plot = df[df['Jornada'].isin(j_sel)]
                if atleta_sel != "Todos":
                    df_plot = df_plot[df_plot['Atleta'] == atleta_sel]

                # Métricas clave (KPIs)
                k1, k2, k3 = st.columns(3)
                with k1: st.metric("Kilómetros Acumulados", f"{df_plot['Distancia'].sum():.1f} km")
                with k2: st.metric("Sesiones Registradas", len(df_plot))
                with k3: 
                    gym_ses = len(df_plot[df_plot['Gimnasio'] == "Sí"])
                    st.metric("Estabilidad en Fuerza (Gym)", gym_ses)

                # Sistema Automatizado de Logros (Medallero)
                if atleta_sel != "Todos":
                    st.divider()
                    st.subheader(f"🏅 Rendimiento e Insignias de {atleta_sel}")
                    tot_km = df_plot['Distancia'].sum()
                    tot_ses = len(df_plot)
                    m1, m2, m3, m4 = st.columns(4)
                    with m1:
                        if tot_ses >= 1: st.markdown("🥈 **Primera Zancada**\n\n*¡Proceso iniciado!*")
                    with m2:
                        if tot_ses >= 5: st.markdown("🔥 **Constancia Pura**\n\n*5 entrenamientos completados*")
                        else: st.caption(f"{tot_ses}/5 entrenamientos para 🔥")
                    with m3:
                        if tot_km >= 100: st.markdown("🚀 **Centurión**\n\n*100 kilómetros superados*")
                        else: st.caption(f"{tot_km:.1f}/100 km acumulados para 🚀")
                    with m4:
                        if gym_ses >= 10: st.markdown("💪 **Hércules**\n\n*10 entrenamientos de fuerza*")
                        else: st.caption(f"{gym_ses}/10 sesiones de fuerza para 💪")

                st.divider()
                fig = px.line(df_plot, x='Fecha', y='Distancia', color='Jornada', markers=True, 
                              title="Curva de Distribución de Volumen por Sesión", template="plotly_white")
                fig.update_traces(line_color='#2E7D32')
                st.plotly_chart(fig, use_container_width=True)

                # Desglose Técnico de Series de Velocidad
                if atleta_sel != "Todos":
                    st.subheader("⏱️ Análisis de Intervalos y Velocidad")
                    cols_s = [f"Serie_{i}" for i in range(1, 13)]
                    df_s = df_plot[df_plot[cols_s].notna().any(axis=1)]
                    
                    if not df_s.empty:
                        f_sel = st.selectbox("Selecciona la fecha del trabajo específico:", df_s['Fecha'].dt.date.unique())
                        fila = df_s[df_s['Fecha'].dt.date == f_sel].iloc[0]
                        
                        st.info(f"📋 **Trabajo Programado por el Coach:** {fila['Tipo_Velocidad'] if fila['Tipo_Velocidad'] else 'Trabajo estándar / No especificado'}")
                        
                        x_val, y_val = [], []
                        for c in cols_s:
                            if fila[c] and str(fila[c]).strip() != "":
                                x_val.append(c.replace("_", " "))
                                y_val.append(fila[c])
                        if y_val:
                            fig_s = px.bar(x=x_val, y=y_val, text_auto=True, color_discrete_sequence=['#2E7D32'],
                                           labels={'x': 'Repeticiones', 'y': 'Tiempos Registrados'})
                            st.plotly_chart(fig_s, use_container_width=True)

                # Desglose de Gimnasio
                if atleta_sel != "Todos" and gym_ses > 0:
                    with st.expander("Ver Historial Detallado de Rutinas de Fuerza"):
                        st.table(df_plot[df_plot['Gimnasio'] == "Sí"][['Fecha', 'Jornada', 'Detalle_Gimnasio']])
        except Exception as e:
            st.error(f"Ocurrió un error al compilar los datos estratégicos: {e}")
            
    elif password == "":
        st.warning("Por favor, introduce la credencial en el panel lateral para desbloquear el análisis táctico.")
    else:
        st.error("Credencial incorrecta. Acceso denegado.")
