import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import date
import time

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="CORRIENDO ANDO | Coach JAZ", page_icon="🏃🏽‍♂️", layout="wide")

# --- 2. CONEXIÓN ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 3. BARRA LATERAL ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>CORRIENDO ANDO</h2>", unsafe_allow_html=True)
    opcion = st.radio("Menú Principal:", ["📝 Registrar Entrenamiento", "📅 Mi Plan Semanal", "📊 Panel de Control"])

# ---------------------------------------------------------
# OPCIÓN 1: REGISTRO
# ---------------------------------------------------------
if opcion == "📝 Registrar Entrenamiento":
    st.title("📝 Registrar Entrenamiento")
    atleta = st.text_input("Nombre del Atleta")
    fecha = st.date_input("Fecha", date.today())
    jornada = st.radio("Jornada:", ["Mañana", "Tarde"], horizontal=True)
    distancia = st.number_input("Distancia (km)", min_value=0.0)
    tiempo = st.text_input("Tiempo (HH:MM:SS)")
    gym = st.selectbox("¿Hizo Fuerza?", ["No", "Sí"])
    detalle_gym = st.text_area("Detalle Fuerza")
    hubo_series = st.checkbox("¿Series?")
    tipo_v = st.text_input("Tipo de Velocidad")
    
    if st.button("Guardar"):
        nuevo = pd.DataFrame([{
            "Fecha": fecha.strftime("%Y-%m-%d"), "Atleta": atleta, "Jornada": jornada,
            "Distancia": distancia, "Tiempo": tiempo, "Gimnasio": gym,
            "Detalle_Gimnasio": detalle_gym, "Tipo_Velocidad": tipo_v
        }])
        try:
            existente = conn.read(ttl=0)
            conn.update(data=pd.concat([existente, nuevo], ignore_index=True))
            st.success("Guardado!")
            st.rerun()
        except Exception as e: st.error(e)

# ---------------------------------------------------------
# OPCIÓN 2: PLAN SEMANAL (CON CÓDIGO)
# ---------------------------------------------------------
elif opcion == "📅 Mi Plan Semanal":
    st.title("📅 Mi Plan Semanal")
    try:
        df_planes = conn.read(worksheet="Planes", ttl=0)
        df_planes['Atleta'] = df_planes['Atleta'].astype(str).str.strip()
        lista = [a for a in df_planes['Atleta'].unique() if str(a).lower() != 'nan']
        atleta_sel = st.selectbox("Selecciona tu nombre:", [""] + list(lista))

        if atleta_sel:
            df_mi_plan = df_planes[df_planes['Atleta'] == atleta_sel].copy()
            # Convertimos todo a string y limpiamos espacios
            df_mi_plan['Codigo'] = df_mi_plan['Codigo'].astype(str).str.strip()
            codigos_reales = df_mi_plan['Codigo'].dropna().unique()
            
            codigo_ingresado = st.text_input("🔑 Ingresa tu código:", type="password")
            
            if codigo_ingresado:
                if codigo_ingresado in codigos_reales:
                    st.success("Acceso concedido")
                    # Visualización del calendario...
                    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
                    for dia in dias:
                        with st.expander(f"🗓️ {dia}"):
                            # Aquí iría la tabla HTML que ya tienes
                            st.write("Plan cargado correctamente.")
                else:
                    st.error("❌ Código incorrecto.")
    except Exception as e:
        st.error(f"Error: {e}")

# ---------------------------------------------------------
# OPCIÓN 3: PANEL DE CONTROL
# ---------------------------------------------------------
else:
    st.title("📊 Panel de Control")
    pwd = st.sidebar.text_input("Llave Maestra:", type="password")
    if pwd == "CoachJaz2026":
        st.write("Acceso correcto.")
