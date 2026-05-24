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

# --- FUNCIONES AUXILIARES ---
def time_to_sec(t_str):
    try:
        if ':' in t_str:
            m, s = map(int, t_str.split(':'))
            return m * 60 + s
        return int(t_str)
    except: return 0

def sec_to_time(sec):
    m = int(sec // 60)
    s = int(sec % 60)
    return f"{m:02d}:{s:02d}"

# --- 4. BARRA LATERAL ---
with st.sidebar:
    col_l1, col_l2, col_l3 = st.columns([1, 5, 1])
    with col_l2:
        try: st.image("logo.png", use_container_width=True)
        except: st.image("https://cdn-icons-png.flaticon.com/512/7159/7159044.png", use_container_width=True)
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
    
    col_a, col_b = st.columns(2)
    with col_a:
        atleta_input = st.text_input("Nombre del Atleta")
        fecha_input = st.date_input("Fecha", date.today())
        jornada = st.radio("Jornada:", ["Mañana", "Tarde"], horizontal=True)
    with col_b:
        distancia = st.number_input("Distancia (km)", min_value=0.0)
        tiempo = st.text_input("Tiempo Total (HH:MM:SS)")

    st.markdown("### ⏱️ Series de Velocidad")
    tipo_v = st.text_input("Tipo de trabajo:")
    num_rep = st.slider("Número de repeticiones", 1, 20, 5)
    
    cols = st.columns(4)
    tiempos_series = []
    
    for i in range(num_rep):
        t = cols[i % 4].text_input(f"Serie {i+1} (MM:SS)", key=f"rep_{i}")
        if t: tiempos_series.append(t)

    # Cálculo promedio
    tiempos_sec = [time_to_sec(t) for t in tiempos_series if t]
    prom_val = sum(tiempos_sec) / len(tiempos_sec) if tiempos_sec else 0
    if tiempos_sec: st.info(f"⚡ **Promedio de ritmo:** {sec_to_time(prom_val)} min/rep")

    if st.button("🚀 Guardar Entrenamiento"):
        try:
            nuevo_reg = {
                "Fecha": [fecha_input.strftime("%Y-%m-%d")], "Atleta": [atleta_input], 
                "Jornada": [jornada], "Distancia": [distancia], "Tiempo": [tiempo], 
                "Tipo_Velocidad": [tipo_v], "Promedio_Ritmo": [sec_to_time(prom_val)]
            }
            # Agregar hasta 20 series
            for i in range(20):
                nuevo_reg[f"Serie_{i+1}"] = [tiempos_series[i] if i < len(tiempos_series) else ""]
                
            existente = conn.read(ttl=0)
            conn.update(data=pd.concat([existente, pd.DataFrame(nuevo_reg)], ignore_index=True))
            st.success("Guardado con éxito!")
            st.rerun()
        except Exception as e: st.error(e)

# ---------------------------------------------------------
# OPCIÓN 2: MI PLAN SEMANAL
# ---------------------------------------------------------
elif opcion == "📅 Mi Plan Semanal":
    st.markdown("<h1 class='main-title'>TU PLAN SEMANAL 📅</h1>", unsafe_allow_html=True)
    try:
        df_planes = conn.read(worksheet="Planes", ttl=0)
        atleta_plan = st.selectbox("Selecciona tu nombre:", [""] + list(df_planes['Atleta'].unique()))

        if atleta_plan:
            df_mi = df_planes[df_planes['Atleta'] == atleta_plan].copy()
            codigo_real = str(df_mi['Codigo'].iloc[0]).strip()
            codigo_input = st.text_input("🔑 Código de acceso:", type="password")
            
            if codigo_input and codigo_input.strip() == codigo_real:
                st.success("Acceso concedido.")
                # Info
                c1, c2 = st.columns(2)
                c1.info(f"🏆 **Competencia:** {df_mi['Proxima_Competencia'].iloc[0]}")
                c2.info(f"🎯 **Objetivo:** {df_mi['Objetivo_Plan'].iloc[0]}")
                
                df_mi['Dia'] = df_mi['Dia'].astype(str).str.strip().str.capitalize()
                dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
                
                html_cal = """<div style="overflow-x:auto;"><table style="width:100%; border-collapse: collapse; font-size: 0.9em; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                    <tr style="background-color: #2E7D32; color: white;"><th style="padding: 12px;">Jornada</th>"""
                for d in dias_semana: html_cal += f"<th style='padding: 12px;'>{d}</th>"
                html_cal += "</tr>"

                for j in ["Mañana", "Tarde"]:
                    html_cal += f"<tr><td style='padding: 12px; font-weight:bold;'>{j}</td>"
                    for dia in dias_semana:
                        plan = df_mi[(df_mi['Dia'] == dia) & (df_mi['Jornada'] == j)]
                        if not plan.empty:
                            html_cal += f"<td style='padding: 12px; border: 1px solid #ddd; background-color: #f1f8e9;'><b>{plan.iloc[0]['Fecha']}</b><br>{plan.iloc[0]['Entrenamiento']}</td>"
                        else: html_cal += "<td style='padding: 12px; border: 1px solid #ddd;'>-</td>"
                    html_cal += "</tr>"
                html_cal += "</table></div>"
                st.markdown(html_cal, unsafe_allow_html=True)
                st.warning(f"📝 **Observación Coach:** {df_mi['Observacion_Coach'].iloc[0]}")
            elif codigo_input: st.error("❌ Código incorrecto.")
    except Exception as e: st.error(f"Error: {e}")

# ---------------------------------------------------------
# OPCIÓN 3: PANEL DE CONTROL
# ---------------------------------------------------------
else:
    st.markdown("<h1 class='main-title'>ÁREA RESTRINGIDA</h1>", unsafe_allow_html=True)
    pwd = st.sidebar.text_input("Llave Maestra:", type="password")
    if pwd == "CoachJaz2026":
        df = conn.read(ttl=0)
        atleta_sel = st.sidebar.selectbox("Atleta:", ["Todos"] + list(df['Atleta'].unique()))
        if atleta_sel != "Todos": df = df[df['Atleta'] == atleta_sel]
        
        c1, c2 = st.columns(2)
        c1.metric("Total km", f"{df['Distancia'].sum():.1f}")
        c2.metric("Sesiones", len(df))
        st.plotly_chart(px.line(df, x='Fecha', y='Distancia', color='Atleta', title="Volumen"), use_container_width=True)
        st.table(df)
