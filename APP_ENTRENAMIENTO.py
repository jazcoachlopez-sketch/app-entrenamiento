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
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONEXIÓN ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNCIONES ---
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

# --- BARRA LATERAL ---
with st.sidebar:
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
    with col_b:
        jornada = st.radio("Jornada:", ["Mañana", "Tarde"], horizontal=True)
        tipo_entreno = st.selectbox("Tipo de Entrenamiento:", ["Velocidad", "Resistencia/Fondo"])

    tiempos_series = []
    distancia = 0.0
    tiempo = ""
    prom_val = 0

    if tipo_entreno == "Velocidad":
        st.markdown("### ⏱️ Series de Velocidad")
        num_rep = st.slider("Número de repeticiones", 1, 20, 5)
        cols = st.columns(4)
        for i in range(num_rep):
            t = cols[i % 4].text_input(f"Serie {i+1} (MM:SS)", key=f"rep_{i}")
            if t: tiempos_series.append(t)
        
        tiempos_sec = [time_to_sec(t) for t in tiempos_series if t]
        prom_val = sum(tiempos_sec) / len(tiempos_sec) if tiempos_sec else 0
        if tiempos_sec: st.info(f"⚡ **Promedio:** {sec_to_time(prom_val)} min/rep")
    else:
        st.markdown("### 🏃‍♂️ Carrera de Fondo")
        distancia = st.number_input("Distancia (km)", min_value=0.0, step=0.1)
        tiempo = st.text_input("Tiempo Total (HH:MM:SS)")

    if st.button("🚀 Guardar Entrenamiento"):
        try:
            nuevo_reg = {
                "Fecha": [fecha_input.strftime("%Y-%m-%d")], "Atleta": [atleta_input], 
                "Jornada": [jornada], "Tipo_Entrenamiento": [tipo_entreno],
                "Distancia": [distancia], "Tiempo": [tiempo], 
                "Promedio_Ritmo": [sec_to_time(prom_val) if tipo_entreno == "Velocidad" else ""]
            }
            for i in range(20):
                nuevo_reg[f"Serie_{i+1}"] = [tiempos_series[i] if (tipo_entreno == "Velocidad" and i < len(tiempos_series)) else ""]
            
            existente = conn.read(ttl=0)
            conn.update(data=pd.concat([existente, pd.DataFrame(nuevo_reg)], ignore_index=True))
            st.success("¡Guardado correctamente!")
            st.rerun()
        except Exception as e: st.error(f"Error: {e}")

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
            codigo_input = st.text_input("🔑 Código de acceso:", type="password")
            
            if codigo_input and codigo_input.strip() == str(df_mi['Codigo'].iloc[0]).strip():
                # PLAN
                c1, c2 = st.columns(2)
                c1.info(f"🏆 Competencia: {df_mi['Proxima_Competencia'].iloc[0]}")
                c2.info(f"🎯 Objetivo: {df_mi['Objetivo_Plan'].iloc[0]}")
                
                # Calendario
                df_mi['Dia'] = df_mi['Dia'].astype(str).str.strip().str.capitalize()
                dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
                html_cal = "<div style='overflow-x:auto;'><table style='width:100%; border-collapse: collapse;'>"
                html_cal += "<tr style='background-color: #2E7D32; color: white;'><th>Jornada</th>"
                for d in dias: html_cal += f"<th>{d}</th>"
                html_cal += "</tr>"
                for j in ["Mañana", "Tarde"]:
                    html_cal += f"<tr><td><b>{j}</b></td>"
                    for d in dias:
                        p = df_mi[(df_mi['Dia'] == d) & (df_mi['Jornada'] == j)]
                        val = f"<b>{p.iloc[0]['Fecha']}</b><br>{p.iloc[0]['Entrenamiento']}" if not p.empty else "-"
                        html_cal += f"<td style='padding:10px; border:1px solid #ddd; background:#f1f8e9;'>{val}</td>"
                    html_cal += "</tr>"
                html_cal += "</table></div>"
                st.markdown(html_cal, unsafe_allow_html=True)
                
                # HISTORIAL
                st.divider()
                st.subheader("📈 Tus Resultados Registrados")
                df_hist = conn.read(ttl=0)
                df_filtro = df_hist[df_hist['Atleta'].astype(str).str.strip() == atleta_plan.strip()]
                if not df_filtro.empty:
                    st.dataframe(df_filtro.sort_values(by="Fecha", ascending=False), use_container_width=True)
                else: st.info("Aún no tienes registros.")
            elif codigo_input: st.error("Código incorrecto.")
    except Exception as e: st.error(f"Error: {e}")

# ---------------------------------------------------------
# OPCIÓN 3: PANEL DE CONTROL
# ---------------------------------------------------------
else:
    st.markdown("<h1 class='main-title'>ÁREA RESTRINGIDA</h1>", unsafe_allow_html=True)
    pwd = st.sidebar.text_input("Llave Maestra:", type="password")
    if pwd == "CoachJaz2026":
        df = conn.read(ttl=0)
        st.table(df)
