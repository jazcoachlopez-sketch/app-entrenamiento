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

# --- 2. ESTILO CSS PERSONALIZADO ---
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

# --- 4. DISEÑO DE LA BARRA LATERAL ---
with st.sidebar:
    col_l1, col_l2, col_l3 = st.columns([1, 5, 1])
    with col_l2:
        try:
            st.image("Gemini_Generated_Image_pm4871pm4871pm48.png", use_container_width=True)
        except:
            st.image("https://cdn-icons-png.flaticon.com/512/7159/7159044.png", use_container_width=True)
    
    st.markdown("<h2 style='text-align: center; font-family: Archivo Black;'>CORRIENDO ANDO</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-weight: bold;'>Coach JAZ</p>", unsafe_allow_html=True)
    st.divider()
    
    opcion = st.radio("Menú Principal:", ["📝 Registrar Entrenamiento", "📊 Panel de Control"])
    st.divider()
    st.caption("© 2026 Corriendo Ando - Paipa, Boyacá")

# ---------------------------------------------------------
# OPCIÓN 1: REGISTRO DE ENTRENAMIENTO
# ---------------------------------------------------------
if opcion == "📝 Registrar Entrenamiento":
    st.markdown("<h1 class='main-title'>¡BIENVENIDO, ATLETA! ⚡</h1>", unsafe_allow_html=True)
    
    st.info("""
    **"La disciplina de hoy es tu victoria de mañana."** Registra tu sesión en **Corriendo Ando**. Detalla tu trabajo de fuerza y las series asignadas. 
    ¡Con el apoyo del **Coach JAZ**, vamos por más! 🏃🏽‍♂️💨
    """)
    
    st.subheader("Formulario de Seguimiento")
    st.write("---")

    col_a, col_b = st.columns(2)
    with col_a:
        atleta_input = st.text_input("Nombre del Atleta", placeholder="Escribe tu nombre...")
        fecha_input = st.date_input("Fecha de la sesión", date.today())
        jornada = st.radio("Jornada:", ["Mañana", "Tarde"], horizontal=True)
        
    with col_b:
        distancia = st.number_input("Distancia Real (km)", min_value=0.0, step=0.1)
        tiempo = st.text_input("Tiempo Total (HH:MM:SS)", placeholder="ej: 00:45:30")

    st.markdown("### 🏋️‍♂️ Trabajo de Fuerza")
    col_gym1, col_gym2 = st.columns([1, 2])
    with col_gym1:
        hizo_gym = st.selectbox("¿Realizaste ejercicios de fuerza?", ["No", "Sí"])
    
    detalle_gym = ""
    if hizo_gym == "Sí":
        with col_gym2:
            detalle_gym = st.text_area("Detalles del gimnasio:", placeholder="Ej: Core, Sentadillas...")

    st.write("---")
    
    hubo_series = st.checkbox("¿Realizaste series de velocidad?")
    series_tiempos = []
    tipo_velocidad = ""

    if hubo_series:
        st.markdown("### ⏱️ Series de Velocidad")
        tipo_velocidad = st.text_input("Tipo de trabajo asignado", placeholder="Ej: 10x400m, Cuestas...")
        
        num_rep = st.slider("Número de repeticiones", 1, 12, 5)
        cols = st.columns(4)
        for i in range(num_rep):
            with cols[i % 4]:
                t = st.text_input(f"Serie {i+1}", key=f"rep_{i}", placeholder="0:00")
                series_tiempos.append(t)
        st.write("---")

    col_c, col_d = st.columns(2)
    with col_c:
        sensacion = st.selectbox("¿Cómo te sentiste?", ["Excelente", "Bien", "Cansado", "Con Dolor"])
    with col_d:
        cumplimiento = st.radio("¿Cumpliste el objetivo?", ["Sí", "No"], horizontal=True)

    st.write("---")
    enviado = st.button("🚀 Guardar Entrenamiento")

    if enviado:
        if not atleta_input:
            st.error("Por favor, ingresa tu nombre.")
        else:
            # CORRECCIÓN AQUÍ: Usamos fecha_input que es la variable definida arriba
            fecha_str = fecha_input.strftime("%Y-%m-%d")
            
            mensajes_coach = {
                "Excelente": f"¡Actitud de campeón! 🏆 ¡A seguir sumando en Corriendo Ando, {atleta_input}!",
                "Bien": "¡Buen trabajo! La constancia es el secreto. ¡Vamos por más!",
                "Cansado": "El descanso también es entrenamiento. Recupera bien hoy. 🛌",
                "Con Dolor": "⚠️ ¡Cuidado! Escucha a tu cuerpo. Reporta esto al Coach JAZ de inmediato."
            }
            msg_final = mensajes_coach.get(sensacion, "¡Registro completado!")

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
            # Llenamos las 12 series posibles
            for i in range(1, 13):
                valor = series_tiempos[i-1] if hubo_series and i <= len(series_tiempos) else ""
                nuevo_reg[f"Serie_{i}"] = [valor]
            
            try:
                df_nuevo = pd.DataFrame(nuevo_reg)
                existente = conn.read(ttl=0)
                
                # Validación Duplicados
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
                    st.warning(f"⚠️ Ya registraste este entrenamiento de la {jornada}.")
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
# OPCIÓN 2: PANEL DE CONTROL (PRIVADO)
# ---------------------------------------------------------
else:
    st.markdown("<h1 class='main-title'>ÁREA PRIVADA</h1>", unsafe_allow_html=True)
    st.sidebar.divider()
    st.sidebar.subheader("🔐 Acceso Entrenador")
    password = st.sidebar.text_input("Llave Maestra:", type="password")

    if password == "CoachJaz2026":
        st.success("Acceso concedido. Bienvenido, Coach JAZ.")
        
        try:
            df = conn.read(ttl=0)
            if df.empty:
                st.info("Aún no hay datos para mostrar.")
            else:
                df['Fecha'] = pd.to_datetime(df['Fecha'])
                df['Distancia'] = pd.to_numeric(df['Distancia'], errors='coerce')

                atleta_sel = st.sidebar.selectbox("Seleccionar Atleta:", ["Todos"] + list(df['Atleta'].unique()))
                j_sel = st.sidebar.multiselect("Jornadas:", ["Mañana", "Tarde"], default=["Mañana", "Tarde"])
                
                df_plot = df[df['Jornada'].isin(j_sel)]
                if atleta_sel != "Todos":
                    df_plot = df_plot[df_plot['Atleta'] == atleta_sel]

                k1, k2, k3 = st.columns(3)
                with k1: st.metric("KM Totales", f"{df_plot['Distancia'].sum():.1f} km")
                with k2: st.metric("Sesiones", len(df_plot))
                with k3: 
                    gym_ses = len(df_plot[df_plot['Gimnasio'] == "Sí"])
                    st.metric("Sesiones de Fuerza", gym_ses)

                st.divider()
                fig = px.line(df_plot, x='Fecha', y='Distancia', color='Jornada', markers=True, 
                              title="Evolución de Volumen", template="plotly_white")
                fig.update_traces(line_color='#2E7D32')
                st.plotly_chart(fig, use_container_width=True)

                if atleta_sel != "Todos":
                    st.subheader("⏱️ Detalle de Series")
                    cols_s = [f"Serie_{i}" for i in range(1, 13)]
                    df_s = df_plot[df_plot[cols_s].notna().any(axis=1)]
                    
                    if not df_s.empty:
                        f_sel = st.selectbox("Elegir fecha de series:", df_s['Fecha'].dt.date.unique())
                        fila = df_s[df_s['Fecha'].dt.date == f_sel].iloc[0]
                        st.info(f"**Trabajo Asignado:** {fila['Tipo_Velocidad'] if fila['Tipo_Velocidad'] else 'No especificado'}")
                        x_val, y_val = [], []
                        for c in cols_s:
                            if fila[c] and str(fila[c]).strip() != "":
                                x_val.append(c.replace("_", " "))
                                y_val.append(fila[c])
                        if y_val:
                            st.plotly_chart(px.bar(x=x_val, y=y_val, text_auto=True), use_container_width=True)
        except Exception as e:
            st.error(f"Error: {e}")
            
    elif password == "":
        st.warning("Ingresa la clave en la barra lateral para ver estadísticas.")
    else:
        st.error("Llave Maestra incorrecta.")
