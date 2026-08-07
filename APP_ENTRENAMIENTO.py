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
        if ':' in str(t_str):
            parts = str(t_str).split(':')
            if len(parts) == 2:
                m, s = map(int, parts)
                return m * 60 + s
            elif len(parts) == 3:
                h, m, s = map(int, parts)
                return h * 3600 + m * 60 + s
        return int(t_str)
    except: return 0

def sec_to_time(sec):
    m = int(sec // 60)
    s = int(sec % 60)
    return f"{m:02d}:{s:02d}"

# Inicialización segura del estado de guardado
if 'guardando_entrenamiento' not in st.session_state:
    st.session_state.guardando_entrenamiento = False

def activar_guardado():
    st.session_state.guardando_entrenamiento = True

# --- 4. BARRA LATERAL ---
with st.sidebar:
    col_l1, col_l2, col_l3 = st.columns([1, 5, 1])
    with col_l2:
        try: st.image("Gemini_Generated_Image_pm4871pm4871pm48.png", use_container_width=True)
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
    st.info("La disciplina de hoy es tu victoria de mañana. Registra tu sesión en Corriendo Ando. ¡Vamos con toda! 🏃🏽‍♂️💨")
    
    st.subheader("Formulario de Seguimiento")
    st.write("---")

    lista_atletas_roster = []
    try:
        df_roster_check = conn.read(worksheet="Planes", ttl=0)
        if not df_roster_check.empty:
            df_roster_check.columns = df_roster_check.columns.astype(str).str.strip().str.replace(" ", "_")
            if 'Atleta' in df_roster_check.columns:
                lista_atletas_roster = [a for a in df_roster_check['Atleta'].unique() if str(a).lower() != 'nan' and str(a).strip() != '']
    except:
        pass

    col_base1, col_base2, col_base3 = st.columns(3)
    with col_base1:
        atleta_input = st.selectbox("Selecciona tu Nombre:", [""] + sorted(list(lista_atletas_roster)))
    with col_base2:
        fecha_input = st.date_input("Fecha de la sesión", date.today())
    with col_base3:
        jornada = st.radio("Jornada del entrenamiento:", ["Mañana", "Tarde"], horizontal=True)

    st.write("---")

    st.markdown("### 🏃‍♂️ Trabajo de Fondo / Resistencia")
    col_fondo1, col_fondo2 = st.columns(2)
    with col_fondo1:
