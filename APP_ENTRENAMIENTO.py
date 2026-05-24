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
            st.image("logo.png", use_container_width=True)
        except:
            st.image("https://cdn-icons-png.flaticon.com/512/7159/7159044.png", use_container_width=True)
    
    st.markdown("<h2 style='text-align: center; font-family: Archivo Black;'>CORRIENDO ANDO</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-weight: bold;'>Coach JAZ</p>", unsafe_allow_html=True)
    st.divider()
    
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
    
    st.info("La disciplina de hoy es tu victoria de mañana. Registra tu sesión en Corriendo Ando. Detalla tu trabajo de fuerza y las series asignadas. ¡Vamos con toda! 🏃🏽‍♂️💨")
    
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
            detalle_gym = st.text_area("Detalles de la rutina:", placeholder="Ej: Ejercicios de core, sentadillas...")

    st.write("---")
    
    hubo_series = st.checkbox("¿Realizaste series de velocidad en esta sesión?")
    series_tiempos = []
    tipo_velocidad = ""

    if hubo_series:
        st.markdown("### ⏱️ Series de Velocidad")
        tipo_velocidad = st.text_input("Tipo de trabajo asignado:", placeholder="Ej: 10x400m, Cuestas explosivas...")
        
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
                "Cansado": "El descanso también es entrenamiento. Recupera bien hoy. 🛌",
                "Con Dolor": "⚠️ ¡Cuidado! Escucha a tu cuerpo. Reporta esta molestia al Coach JAZ de inmediato."
            }
            msg_final = mensajes_coach.get(sensacion, "¡Registro completado con éxito!")

            nuevo_reg = {
                "Fecha": [fecha_str], "Atleta": [atleta_input], "Jornada": [jornada],
                "Distancia": [distancia], "Tiempo": [tiempo], "Gimnasio": [hizo_gym],
                "Detalle_Gimnasio": [detalle_gym], "Tipo_Velocidad": [tipo_velocidad],
                "Sensacion": [sensacion], "Cumplimiento": [cumplimiento]
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
                    if not duplicados.empty:
                        es_duplicado = True

                if es_duplicado:
                    st.warning(f"⚠️ Este entrenamiento de la {jornada} ya se encuentra registrado.")
                else:
                    df_final = pd.concat([existente, df_nuevo], ignore_index=True)
                    conn.update(data=df_final)
                    st.success(msg_final)
                    st.balloons()
                    time.sleep(3)
                    st.rerun()
            except Exception as e:
                st.error(f"Error al intentar conectar: {e}")

# ---------------------------------------------------------
# OPCIÓN 2: MI PLAN SEMANAL (Visualización con FECHA)
# ---------------------------------------------------------
elif opcion == "📅 Mi Plan Semanal":
    st.markdown("<h1 class='main-title'>TU PLAN SEMANAL 📅</h1>", unsafe_allow_html=True)
    
    try:
        df_planes = conn.read(worksheet="Planes", ttl=0)
        
        if df_planes.empty:
            st.warning("Aún no se registran planes en la pestaña 'Planes'.")
        else:
            df_planes['Atleta'] = df_planes['Atleta'].astype(str).str.strip()
            lista_atletas = [a for a in df_planes['Atleta'].unique() if str(a).lower() != 'nan' and str(a).strip() != '']
            
            atleta_plan = st.selectbox("Selecciona tu nombre:", [""] + list(lista_atletas))

            if atleta_plan:
                df_mi_plan = df_planes[df_planes['Atleta'] == atleta_plan].copy()
                
                # Validación de código
                codigos_validos = [str(c).strip() for c in df_mi_plan['Codigo'].unique() if str(c).lower() not in ['nan', 'none', '']]
                
                if not codigos_validos:
                    st.warning(f"Coach, no has asignado un código a {atleta_plan}.")
                else:
                    codigo_real = codigos_validos[0]
                    codigo_input = st.text_input("🔑 Ingresa tu código de acceso:", type="password")
                    
                    if codigo_input and codigo_input.strip() == codigo_real:
                        st.success("Acceso concedido.")
                        
                        # --- PREPARACIÓN DE DATOS ---
                        # Asumimos que tienes una columna 'Fecha' en tu Google Sheets
                        df_mi_plan['Dia'] = df_mi_plan['Dia'].astype(str).str.strip().str.capitalize()
                        
                        # Creamos una tabla más detallada
                        st.write(f"### 🗓️ Plan detallado para: **{atleta_plan}**")
                        
                        # Ajustamos las columnas a mostrar
                        columnas_mostrar = ['Fecha', 'Dia', 'Jornada', 'Entrenamiento']
                        if 'Entrenamiento' in df_mi_plan.columns:
                            # Filtramos para que solo muestre lo del atleta y ordenamos si es necesario
                            st.table(df_mi_plan[columnas_mostrar])
                        else:
                            st.error("No se encuentra la columna 'Entrenamiento' en tu hoja.")
                            
                    elif codigo_input:
                        st.error("❌ Código incorrecto.")
                
    except Exception as e:
        st.error(f"Error: {e}")

# ---------------------------------------------------------
# OPCIÓN 3: PANEL DE CONTROL (Privado)
# ---------------------------------------------------------
else:
    st.markdown("<h1 class='main-title'>ÁREA RESTRINGIDA</h1>", unsafe_allow_html=True)
    st.sidebar.divider()
    st.sidebar.subheader("🔐 Acceso Entrenador")
    password = st.sidebar.text_input("Llave Maestra:", type="password")

    if password == "CoachJaz2026":
        st.success("Acceso concedido.")
        st.markdown("<h1 class='main-title'>CORRIENDO ANDO - ESTRATEGIA</h1>", unsafe_allow_html=True)
        st.write("---")
        
        try:
            df = conn.read(ttl=0)
            if df.empty:
                st.info("No se registran datos.")
            else:
                df['Fecha'] = pd.to_datetime(df['Fecha'])
                df['Distancia'] = pd.to_numeric(df['Distancia'], errors='coerce')

                atleta_sel = st.sidebar.selectbox("Seleccionar Atleta:", ["Todos"] + list(df['Atleta'].unique()))
                j_sel = st.sidebar.multiselect("Filtrar Jornadas:", ["Mañana", "Tarde"], default=["Mañana", "Tarde"])
                
                df_plot = df[df['Jornada'].isin(j_sel)]
                if atleta_sel != "Todos":
                    df_plot = df_plot[df_plot['Atleta'] == atleta_sel]

                k1, k2, k3 = st.columns(3)
                with k1: st.metric("Kilómetros Acumulados", f"{df_plot['Distancia'].sum():.1f} km")
                with k2: st.metric("Sesiones", len(df_plot))
                with k3: 
                    gym_ses = len(df_plot[df_plot['Gimnasio'] == "Sí"])
                    st.metric("Sesiones Gym", gym_ses)

                if atleta_sel != "Todos":
                    st.divider()
                    st.subheader(f"🏅 Insignias de {atleta_sel}")
                    tot_km = df_plot['Distancia'].sum()
                    tot_ses = len(df_plot)
                    m1, m2, m3, m4 = st.columns(4)
                    with m1:
                        if tot_ses >= 1: st.markdown("🥈 **Primera Zancada**")
                    with m2:
                        if tot_ses >= 5: st.markdown("🔥 **Constancia Pura**")
                    with m3:
                        if tot_km >= 100: st.markdown("🚀 **Centurión**")
                    with m4:
                        if gym_ses >= 10: st.markdown("💪 **Hércules**")

                st.divider()
                fig = px.line(df_plot, x='Fecha', y='Distancia', color='Jornada', markers=True, 
                              title="Curva de Volumen", template="plotly_white")
                fig.update_traces(line_color='#2E7D32')
                st.plotly_chart(fig, use_container_width=True)

                if atleta_sel != "Todos":
                    st.subheader("⏱️ Análisis de Intervalos")
                    cols_s = [f"Serie_{i}" for i in range(1, 13)]
                    df_s = df_plot[df_plot[cols_s].notna().any(axis=1)]
                    
                    if not df_s.empty:
                        f_sel = st.selectbox("Fecha de trabajo:", df_s['Fecha'].dt.date.unique())
                        fila = df_s[df_s['Fecha'].dt.date == f_sel].iloc[0]
                        
                        st.info(f"📋 **Trabajo:** {fila['Tipo_Velocidad'] if fila['Tipo_Velocidad'] else 'No especificado'}")
                        
                        x_val, y_val = [], []
                        for c in cols_s:
                            if fila[c] and str(fila[c]).strip() != "":
                                x_val.append(c.replace("_", " "))
                                y_val.append(fila[c])
                        if y_val:
                            st.plotly_chart(px.bar(x=x_val, y=y_val, text_auto=True, color_discrete_sequence=['#2E7D32']), use_container_width=True)

                if atleta_sel != "Todos" and gym_ses > 0:
                    with st.expander("Historial de Fuerza"):
                        st.table(df_plot[df_plot['Gimnasio'] == "Sí"][['Fecha', 'Jornada', 'Detalle_Gimnasio']])
        except Exception as e:
            st.error(f"Error técnico: {e}")
            
    elif password == "":
        st.warning("Introduce la llave en el menú.")
    else:
        st.error("Credencial incorrecta.")
