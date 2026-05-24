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
    .main-title { font-family: 'Archivo Black', sans-serif; color: #2E7D32; font-size: 3rem !important; text-align: center; margin-bottom: 0; }
    html, body, [class*="css"] { font-family: 'Montserrat', sans-serif; }
    [data-testid="stSidebarNav"] { padding-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONEXIÓN A GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 4. BARRA LATERAL ---
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
    opcion = st.radio("Menú Principal:", ["📝 Registrar Entrenamiento", "📅 Mi Plan Semanal", "📊 Panel de Control"])
    st.divider()
    st.caption("© 2026 Corriendo Ando - Paipa, Boyacá")

# ---------------------------------------------------------
# OPCIÓN 1: REGISTRO DE ENTRENAMIENTO
# ---------------------------------------------------------
if opcion == "📝 Registrar Entrenamiento":
    st.markdown("<h1 class='main-title'>¡BIENVENIDO, ATLETA! ⚡</h1>", unsafe_allow_html=True)
    st.info("Registra tu sesión en Corriendo Ando. Detalla tu trabajo de fuerza y las series asignadas.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        atleta_input = st.text_input("Nombre del Atleta")
        fecha_input = st.date_input("Fecha", date.today())
        jornada = st.radio("Jornada:", ["Mañana", "Tarde"], horizontal=True)
    with col_b:
        distancia = st.number_input("Distancia (km)", min_value=0.0)
        tiempo = st.text_input("Tiempo (HH:MM:SS)")

    hizo_gym = st.selectbox("¿Hizo Fuerza?", ["No", "Sí"])
    detalle_gym = st.text_area("Detalle Fuerza")
    hubo_series = st.checkbox("¿Series de velocidad?")
    tipo_v = st.text_input("Tipo de trabajo")
    
    enviado = st.button("🚀 Guardar Entrenamiento")
    if enviado:
        nuevo = pd.DataFrame([{"Fecha": fecha_input.strftime("%Y-%m-%d"), "Atleta": atleta_input, "Jornada": jornada, "Distancia": distancia, "Tiempo": tiempo, "Gimnasio": hizo_gym, "Detalle_Gimnasio": detalle_gym, "Tipo_Velocidad": tipo_v}])
        try:
            existente = conn.read(ttl=0)
            conn.update(data=pd.concat([existente, nuevo], ignore_index=True))
            st.success("Guardado con éxito!")
            st.rerun()
        except Exception as e: st.error(e)

# ---------------------------------------------------------
# OPCIÓN 2: MI PLAN SEMANAL (CALENDARIO CON FECHA)
# ---------------------------------------------------------
elif opcion == "📅 Mi Plan Semanal":
    st.markdown("<h1 class='main-title'>TU PLAN SEMANAL 📅</h1>", unsafe_allow_html=True)
    try:
        df_planes = conn.read(worksheet="Planes", ttl=0)
        lista_atletas = [a for a in df_planes['Atleta'].unique() if str(a).lower() != 'nan' and str(a).strip() != '']
        atleta_plan = st.selectbox("Selecciona tu nombre:", [""] + list(lista_atletas))

        if atleta_plan:
            df_mi_plan = df_planes[df_planes['Atleta'] == atleta_plan].copy()
            codigo_real = str(df_mi_plan['Codigo'].iloc[0]).strip()
            codigo_input = st.text_input("🔑 Ingresa tu código:", type="password")
            
            if codigo_input and codigo_input.strip() == codigo_real:
                st.write(f"### 🗓️ Calendario de: **{atleta_plan}**")
                df_mi_plan['Dia'] = df_mi_plan['Dia'].astype(str).str.strip().str.capitalize()
                dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
                
                # Construcción del Calendario con Fecha
                html_cal = """
                <div style="overflow-x:auto; margin-top: 10px;">
                <table style="width:100%; border-collapse: collapse; font-family: 'Montserrat', sans-serif; font-size: 0.9em; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                    <tr style="background-color: #2E7D32; color: white; text-align: center;">
                        <th style="padding: 12px; border: 1px solid #ddd; width: 10%;">Jornada</th>
                """
                for dia in dias_semana: html_cal += f"<th style='padding: 12px; border: 1px solid #ddd; min-width: 140px;'>{dia}</th>"
                html_cal += "</tr>"

                for j in ["Mañana", "Tarde"]:
                    html_cal += f"<tr><td style='padding: 12px; font-weight: bold; background-color: #f9f9f9; text-align: center;'>{j}</td>"
                    for dia in dias_semana:
                        plan = df_mi_plan[(df_mi_plan['Dia'] == dia) & (df_mi_plan['Jornada'] == j)]
                        if not plan.empty:
                            fecha_val = plan.iloc[0]['Fecha']
                            texto = str(plan.iloc[0]['Entrenamiento']).replace("\n", "<br>")
                            html_cal += f"<td style='padding: 12px; border: 1px solid #ddd; background-color: #f1f8e9;'><b>{fecha_val}</b><br>{texto}</td>"
                        else:
                            html_cal += "<td style='padding: 12px; border: 1px solid #ddd; color: #888; text-align: center;'><i>Libre</i></td>"
                    html_cal += "</tr>"
                html_cal += "</table></div>"
                st.markdown(html_cal, unsafe_allow_html=True)
            elif codigo_input: st.error("❌ Código incorrecto.")
    except Exception as e: st.error(f"Error: {e}")

# ---------------------------------------------------------
# OPCIÓN 3: PANEL DE CONTROL
# ---------------------------------------------------------
else:
    st.markdown("<h1 class='main-title'>ÁREA RESTRINGIDA</h1>", unsafe_allow_html=True)
    pwd = st.sidebar.text_input("Llave Maestra:", type="password")
    if pwd == "CoachJaz2026":
        st.success("Acceso concedido.")
        df = conn.read(ttl=0)
        atleta_sel = st.sidebar.selectbox("Atleta:", ["Todos"] + list(df['Atleta'].unique()))
        if atleta_sel != "Todos": df = df[df['Atleta'] == atleta_sel]
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total km", f"{df['Distancia'].sum():.1f}")
        c2.metric("Sesiones", len(df))
        c3.metric("Fuerza", len(df[df['Gimnasio'] == "Sí"]))
        
        st.plotly_chart(px.line(df, x='Fecha', y='Distancia', color='Atleta', title="Volumen"), use_container_width=True)
        st.table(df)
