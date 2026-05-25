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
    @import url('https://fonts.googleapis.com/css2?family=Archivo+Black&family=Montserrat:wght=400;700&display=swap');
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

# Inicialización segura del estado de guardado
if 'guardando_entrenamiento' not in st.session_state:
    st.session_state.guardando_entrenamiento = False

def activar_guardado():
    st.session_state.guardando_entrenamiento = True

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
# OPCIÓN 1: REGISTRO DE ENTRENAMIENTO (ESTRUCTURADO)
# ---------------------------------------------------------
if opcion == "📝 Registrar Entrenamiento":
    st.markdown("<h1 class='main-title'>¡BIENVENIDO, ATLETA! ⚡</h1>", unsafe_allow_html=True)
    st.info("La disciplina de hoy es tu victoria de mañana. Registra tu sesión en Corriendo Ando. ¡Vamos con toda! 跑")
    
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

    # SECCIÓN 1: DATOS DE IDENTIFICACIÓN
    col_base1, col_base2, col_base3 = st.columns(3)
    with col_base1:
        atleta_input = st.selectbox("Selecciona tu Nombre:", [""] + sorted(list(lista_atletas_roster)))
    with col_base2:
        fecha_input = st.date_input("Fecha de la sesión", date.today())
    with col_base3:
        jornada = st.radio("Jornada del entrenamiento:", ["Mañana", "Tarde"], horizontal=True)

    st.write("---")

    # SECCIÓN 2: TRABAJOS DE FONDO / RESISTENCIA (ABAJO DE DATOS BASE)
    st.markdown("### 🏃‍♂️ Trabajo de Fondo / Resistencia")
    col_fondo1, col_fondo2 = st.columns(2)
    with col_fondo1:
        distancia = st.number_input("Distancia Real Alcanzada (km)", min_value=0.0, step=0.1, help="Kilómetros totales recorridos")
    with col_fondo2:
        tiempo = st.text_input("Tiempo Total Acumulado (HH:MM:SS)", placeholder="ej: 00:45:30")

    st.write("---")

    # SECCIÓN 3: TRABAJOS DE VELOCIDAD
    st.markdown("### ⏱️ Series de Velocidad (Si aplica)")
    tipo_entrenamiento_input = st.text_input("Tipo de Entrenamiento (ej: 10x400m, Cuestas explosivas, Fartlek):", placeholder="Deja vacío si sólo realizaste fondo continuo")
    num_rep = st.slider("Número de repeticiones realizadas", 1, 20, 5)
    
    cols = st.columns(4)
    tiempos_series = []
    for i in range(num_rep):
        t = cols[i % 4].text_input(f"Serie {i+1} (MM:SS)", key=f"rep_{i}", placeholder="0:00")
        if t: tiempos_series.append(t)

    # Cálculo del promedio continuo
    tiempos_sec = [time_to_sec(t) for t in tiempos_series if t]
    prom_val = sum(tiempos_sec) / len(tiempos_sec) if tiempos_sec else 0
    if tiempos_sec: 
        st.info(f"⚡ **Promedio de ritmo en series:** {sec_to_time(prom_val)} min/rep")

    st.write("---")

    # PROCESAMIENTO SEGURO DEL BOTÓN DE GUARDADO
    if st.session_state.guardando_entrenamiento:
        st.button("⌛ Guardando entrenamiento...", disabled=True)
        
        if not atleta_input or atleta_input == "":
            st.error("❌ Por favor, selecciona tu nombre de la lista desplegable antes de guardar.")
            st.session_state.guardando_entrenamiento = False
            st.rerun()
        else:
            try:
                fecha_str = fecha_input.strftime("%Y-%m-%d")
                existente = conn.read(ttl=0)
                es_duplicado = False
                
                if not existente.empty:
                    existente.columns = existente.columns.astype(str).str.strip().str.replace(" ", "_")
                    duplicados = existente[
                        (existente['Fecha'].astype(str) == fecha_str) & 
                        (existente['Atleta'].astype(str) == atleta_input) & 
                        (existente['Jornada'].astype(str) == jornada) & 
                        (existente['Tipo_Entrenamiento'].astype(str) == tipo_entrenamiento_input)
                    ]
                    if not duplicados.empty:
                        es_duplicado = True
                
                if es_duplicado:
                    st.warning("⚠️ Este entrenamiento ya fue registrado hace unos instantes.")
                    time.sleep(2)
                else:
                    nuevo_reg = {
                        "Fecha": [fecha_str], 
                        "Atleta": [atleta_input], 
                        "Jornada": [jornada], 
                        "Distancia": [distancia], 
                        "Tiempo": [tiempo], 
                        "Tipo_Entrenamiento": [tipo_entrenamiento_input], 
                        "Promedio_Ritmo": [sec_to_time(prom_val)]
                    }
                    for i in range(20):
                        nuevo_reg[f"Serie_{i+1}"] = [tiempos_series[i] if i < len(tiempos_series) else ""]
                        
                    df_final = pd.concat([existente, pd.DataFrame(nuevo_reg)], ignore_index=True)
                    conn.update(data=df_final)
                    st.success("¡Entrenamiento guardado con éxito!")
                    st.balloons()
                    time.sleep(1.5)
                
            except Exception as e:
                st.error(f"Error técnico al guardar: {e}")
            
            st.session_state.guardando_entrenamiento = False
            st.rerun()
    else:
        st.button("🚀 Guardar Entrenamiento", on_click=activar_guardado)

# ---------------------------------------------------------
# OPCIÓN 2: MI PLAN SEMANAL
# ---------------------------------------------------------
elif opcion == "📅 Mi Plan Semanal":
    st.markdown("<h1 class='main-title'>TU PLAN SEMANAL 📅</h1>", unsafe_allow_html=True)
    try:
        df_planes = conn.read(worksheet="Planes", ttl=0)
        if not df_planes.empty:
            df_planes.columns = df_planes.columns.astype(str).str.strip().str.replace(" ", "_")
            
        lista_atletas = [a for a in df_planes['Atleta'].unique() if str(a).lower() != 'nan' and str(a).strip() != '']
        atleta_plan = st.selectbox("Selecciona tu nombre:", [""] + list(lista_atletas))

        if atleta_plan:
            df_
