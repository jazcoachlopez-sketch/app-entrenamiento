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
    st.info("La disciplina de hoy es tu victoria de mañana. Registra tu sesión en Corriendo Ando. ¡Vamos con toda! 🏃🏽‍♂️💨")
    
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

    st.markdown("### ⏱️ Series de Velocidad")
    tipo_velocidad = st.text_input("Tipo de trabajo asignado:", placeholder="Ej: 10x400m, Cuestas explosivas...")
    num_rep = st.slider("Número de repeticiones realizadas", 1, 12, 5)
    
    # Cálculo promedio
    def time_to_sec(t):
        try:
            m, s = map(int, t.split(':'))
            return m * 60 + s
        except: return 0
    
    cols = st.columns(4)
    tiempos_series = []
    for i in range(num_rep):
        t = cols[i % 4].text_input(f"Serie {i+1}", key=f"rep_{i}", placeholder="0:00")
        if t: tiempos_series.append(time_to_sec(t))

    if tiempos_series:
        promedio = sum(tiempos_series) / len(tiempos_series)
        m, s = divmod(int(promedio), 60)
        st.info(f"⚡ **Promedio de ritmo:** {m:02d}:{s:02d} min/rep")

    st.write("---")
    enviado = st.button("🚀 Guardar Entrenamiento")

    if enviado:
        if not atleta_input:
            st.error("Por favor, ingresa tu nombre.")
        else:
            fecha_str = fecha_input.strftime("%Y-%m-%d")
            nuevo_reg = {"Fecha": [fecha_str], "Atleta": [atleta_input], "Jornada": [jornada], "Distancia": [distancia], "Tiempo": [tiempo], "Tipo_Velocidad": [tipo_velocidad]}
            try:
                existente = conn.read(ttl=0)
                conn.update(data=pd.concat([existente, pd.DataFrame(nuevo_reg)], ignore_index=True))
                st.success("¡Registro completado!")
                st.balloons()
                time.sleep(2)
                st.rerun()
            except Exception as e: st.error(f"Error: {e}")

# ---------------------------------------------------------
# OPCIÓN 2: MI PLAN SEMANAL
# ---------------------------------------------------------
elif opcion == "📅 Mi Plan Semanal":
    st.markdown("<h1 class='main-title'>TU PLAN SEMANAL 📅</h1>", unsafe_allow_html=True)
    st.info("Visualiza tu ruta de entrenamiento. Privacidad garantizada.")

    try:
        df_planes = conn.read(worksheet="Planes", ttl=0)
        lista_atletas = [a for a in df_planes['Atleta'].unique() if str(a).lower() != 'nan' and str(a).strip() != '']
        atleta_plan = st.selectbox("Selecciona tu nombre:", [""] + list(lista_atletas))

        if atleta_plan:
            df_mi_plan = df_planes[df_planes['Atleta'] == atleta_plan].copy()
            if 'Codigo' not in df_mi_plan.columns:
                st.error("⚠️ Coach: Falta la columna 'Codigo' en tu pestaña 'Planes'.")
            else:
                codigos_validos = [str(c).strip() for c in df_mi_plan['Codigo'].unique() if str(c).lower() not in ['nan', 'none', '']]
                if not codigos_validos:
                    st.warning(f"Coach, no has asignado un código a {atleta_plan}.")
                else:
                    codigo_real = codigos_validos[0]
                    codigo_input = st.text_input("🔑 Ingresa tu código de acceso:", type="password")
                    
                    if codigo_input and codigo_input.strip() == codigo_real:
                        st.success("Acceso concedido.")
                        
                        # INFO ADICIONAL
                        comp = df_mi_plan['Proxima_Competencia'].iloc[0] if 'Proxima_Competencia' in df_mi_plan.columns else "No definida"
                        obj = df_mi_plan['Objetivo_Plan'].iloc[0] if 'Objetivo_Plan' in df_mi_plan.columns else "No definido"
                        obs = df_mi_plan['Observacion_Coach'].iloc[0] if 'Observacion_Coach' in df_mi_plan.columns else "Sin observaciones."
                        
                        col1, col2 = st.columns(2)
                        col1.info(f"🏆 **Próxima Competencia:** {comp}")
                        col2.info(f"🎯 **Objetivo:** {obj}")
                        
                        st.write(f"### 🗓️ Calendario de: **{atleta_plan}**")
                        
                        df_mi_plan['Dia'] = df_mi_plan['Dia'].astype(str).str.strip().str.capitalize()
                        df_mi_plan['Jornada'] = df_mi_plan['Jornada'].astype(str).str.strip().str.capitalize()
                        df_mi_plan['Dia'] = df_mi_plan['Dia'].replace({"Miercoles": "Miércoles", "Sabado": "Sábado"})
                        dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
                        
                        html_cal = """
                        <div style="overflow-x:auto; margin-top: 10px;">
                        <table style="width:100%; border-collapse: collapse; font-family: 'Montserrat', sans-serif; font-size: 0.95em; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                            <tr style="background-color: #2E7D32; color: white; text-align: center;">
                                <th style="padding: 12px; border: 1px solid #ddd; width: 10%;">Jornada</th>
                        """
                        for dia in dias_semana: html_cal += f"<th style='padding: 12px; border: 1px solid #ddd; min-width: 140px; text-align: center;'>{dia}</th>"
                        html_cal += "</tr>"

                        for j in ["Mañana", "Tarde"]:
                            html_cal += f"<tr><td style='padding: 12px; border: 1px solid #ddd; font-weight: bold; background-color: #f9f9f9; text-align: center;'>{j}</td>"
                            for dia in dias_semana:
                                plan = df_mi_plan[(df_mi_plan['Dia'] == dia) & (df_mi_plan['Jornada'] == j)]
                                if not plan.empty:
                                    fecha_val = plan.iloc[0]['Fecha']
                                    texto = str(plan.iloc[0]['Entrenamiento']).replace("\n", "<br>")
                                    html_cal += f"<td style='padding: 12px; border: 1px solid #ddd; background-color: #e8f5e9;'><b>{fecha_val}</b><br>{texto}</td>"
                                else:
                                    html_cal += "<td style='padding: 12px; border: 1px solid #ddd; background-color: #ffffff; color: #888; text-align: center;'><i>🛋️ Libre</i></td>"
                            html_cal += "</tr>"
                        html_cal += "</table></div>"
                        st.markdown(html_cal, unsafe_allow_html=True)
                        
                        st.markdown("---")
                        st.subheader("📝 Observaciones del Coach")
                        st.warning(obs)
                        
                    elif codigo_input: st.error("❌ Código incorrecto.")
    except Exception as e: st.error(f"Error técnico: {e}")

# ---------------------------------------------------------
# OPCIÓN 3: PANEL DE CONTROL
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
            if df.empty: st.info("No se registran datos.")
            else:
                df['Fecha'] = pd.to_datetime(df['Fecha'])
                atleta_sel = st.sidebar.selectbox("Seleccionar Atleta:", ["Todos"] + list(df['Atleta'].unique()))
                if atleta_sel != "Todos": df = df[df['Atleta'] == atleta_sel]

                c1, c2, c3 = st.columns(3)
                c1.metric("Kilómetros Acumulados", f"{df['Distancia'].sum():.1f} km")
                c2.metric("Sesiones", len(df))
                
                st.plotly_chart(px.line(df, x='Fecha', y='Distancia', color='Atleta', title="Curva de Volumen", template="plotly_white"), use_container_width=True)
                st.table(df)
        except Exception as e: st.error(f"Error técnico: {e}")
