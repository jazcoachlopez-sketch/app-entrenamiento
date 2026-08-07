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
        try: 
            st.image("logo.png", use_container_width=True)
        except: 
            st.image("https://cdn-icons-png.flaticon.com/512/7159/7159044.png", use_container_width=True)
            
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

    # SECCIÓN 1: DATOS DE IDENTIFICACIÓN
    col_base1, col_base2, col_base3 = st.columns(3)
    with col_base1:
        atleta_input = st.selectbox("Selecciona tu Nombre:", [""] + sorted(list(lista_atletas_roster)))
    with col_base2:
        fecha_input = st.date_input("Fecha de la sesión", date.today())
    with col_base3:
        jornada = st.radio("Jornada del entrenamiento:", ["Mañana", "Tarde"], horizontal=True)

    st.write("---")

    # SECCIÓN 2: TRABAJOS DE FONDO / RESISTENCIA
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
    num_rep = st.slider("Número de repeticiones realizadas", 1, 30, 5)
    
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
            df_mi = df_planes[df_planes['Atleta'] == atleta_plan].copy()
            codigo_real = str(df_mi['Codigo'].iloc[0]).strip()
            codigo_input = st.text_input("🔑 Código de acceso:", type="password")
            
            if codigo_input and codigo_input.strip() == codigo_real:
                st.success("Acceso concedido.")
                
                comp = df_mi['Proxima_Competencia'].iloc[0] if 'Proxima_Competencia' in df_mi.columns else "No definida"
                obj = df_mi['Objetivo_Plan'].iloc[0] if 'Objetivo_Plan' in df_mi.columns else "No definido"
                obs = df_mi['Observacion_Coach'].iloc[0] if 'Observacion_Coach' in df_mi.columns else "Sin observaciones."
                
                col1, col2 = st.columns(2)
                col1.info(f"🏆 **Competencia:** {comp}")
                col2.info(f"🎯 **Objetivo:** {obj}")
                
                st.write(f"### 🗓️ Calendario de: **{atleta_plan}**")
                df_mi['Dia'] = df_mi['Dia'].astype(str).str.strip().str.capitalize()
                df_mi['Jornada'] = df_mi['Jornada'].astype(str).str.strip().str.capitalize()
                df_mi['Dia'] = df_mi['Dia'].replace({"Miercoles": "Miércoles", "Sabado": "Sábado"})
                dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
                
                html_cal = '<div style="overflow-x:auto; margin-top: 10px;">'
                html_cal += '<table style="width:100%; border-collapse: collapse; font-family: \'Montserrat\', sans-serif; font-size: 0.95em; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">'
                html_cal += '<tr style="background-color: #2E7D32; color: white; text-align: center;">'
                html_cal += '<th style="padding: 12px; border: 1px solid #ddd; width: 10%;">Jornada</th>'
                
                for d in dias_semana: 
                    html_cal += f"<th style='padding: 12px; border: 1px solid #ddd; min-width: 140px; text-align: center;'>{d}</th>"
                html_cal += "</tr>"

                for j in ["Mañana", "Tarde"]:
                    html_cal += f"<tr><td style='padding: 12px; border: 1px solid #ddd; font-weight: bold; background-color: #f9f9f9; text-align: center;'>{j}</td>"
                    for dia in dias_semana:
                        plan = df_mi[(df_mi['Dia'] == dia) & (df_mi['Jornada'] == j)]
                        if not plan.empty:
                            f_val = plan.iloc[0]['Fecha'] if 'Fecha' in plan.columns else ""
                            e_val = plan.iloc[0]['Entrenamiento'] if 'Entrenamiento' in plan.columns else ""
                            html_cal += (
                                f"<td style='padding: 12px; border: 1px solid #ddd; background-color: #e8f5e9;'>"
                                f"<b>{f_val}</b><br>{e_val}</td>"
                            )
                        else: 
                            html_cal += (
                                "<td style='padding: 12px; border: 1px solid #ddd; background-color: #ffffff; "
                                "color: #888; text-align: center;'><i>🛋️ Libre</i></td>"
                            )
                    html_cal += "</tr>"
                html_cal += "</table></div>"
                
                st.markdown(html_cal, unsafe_allow_html=True)
                
                st.markdown("---")
                st.subheader("📝 Observaciones del Coach")
                st.warning(obs)

                st.divider()
                st.subheader("📈 Tus Resultados Registrados")
                df_hist = conn.read(ttl=0)
                
                if not df_hist.empty:
                    df_hist.columns = df_hist.columns.astype(str).str.strip().str.replace(" ", "_")
                    df_filtro = df_hist[df_hist['Atleta'].astype(str).str.strip() == atleta_plan.strip()].copy()
                    
                    if not df_filtro.empty:
                        columnas_principales = ["Fecha", "Jornada", "Tipo_Entrenamiento", "Distancia", "Tiempo", "Promedio_Ritmo"]
                        columnas_series = [f"Serie_{i}" for i in range(1, 21)]
                        
                        for col in columnas_principales + columnas_series:
                            if col not in df_filtro.columns: 
                                df_filtro[col] = ""
                                
                        columnas_finales = columnas_principales + columnas_series
                        df_ordenado = df_filtro[columnas_finales].sort_values(by="Fecha", ascending=False)
                        
                        df_visual = df_ordenado.rename(columns={
                            "Tipo_Entrenamiento": "Tipo de Entrenamiento",
                            "Promedio_Ritmo": "Ritmo Promedio",
                            "Distancia": "Distancia (km)",
                            "Tiempo": "Tiempo Total"
                        })
                        st.dataframe(df_visual, use_container_width=True)
                    else: 
                        st.info("Aún no tienes entrenamientos registrados.")
                else: 
                    st.info("No se registran datos en la base de datos principal.")
                    
            elif codigo_input: 
                st.error("❌ Código incorrecto.")
    except Exception as e: 
        st.error(f"Error técnico: {e}")

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
        st.markdown("<h1 class='main-title'>CORRIENDO ANDO - ESTRATEGIA Y CONTROL</h1>", unsafe_allow_html=True)
        st.write("---")
        
        try:
            df = conn.read(ttl=0)
            if df.empty:
                st.info("No hay datos de entrenamientos registrados aún.")
            else:
                df.columns = df.columns.astype(str).str.strip().str.replace(" ", "_")
                if 'Distancia' in df.columns:
                    df['Distancia'] = pd.to_numeric(df['Distancia'], errors='coerce').fillna(0)
                
                lista_atletas_registrados = sorted([a for a in df['Atleta'].dropna().unique() if str(a).strip() != ''])
                atleta_sel = st.sidebar.selectbox("Filtrar por Atleta:", ["Todos los Atletas"] + lista_atletas_registrados)
                
                df_filtrado = df.copy()
                if atleta_sel != "Todos los Atletas":
                    df_filtrado = df_filtrado[df_filtrado['Atleta'] == atleta_sel]

                k1, k2, k3 = st.columns(3)
                k1.metric("Km Totales Acumulados", f"{df_filtrado['Distancia'].sum():.1f} km")
                k2.metric("Sesiones Registradas", len(df_filtrado))
                prom_km = df_filtrado['Distancia'].mean() if len(df_filtrado) > 0 else 0
                k3.metric("Promedio Km / Sesión", f"{prom_km:.1f} km")

                st.write("---")
                st.subheader("📋 Registro Completo de Entrenamientos")
                
                columnas_principales = ["Fecha", "Atleta", "Jornada", "Tipo_Entrenamiento", "Distancia", "Tiempo", "Promedio_Ritmo"]
                columnas_series = [f"Serie_{i}" for i in range(1, 21)]
                
                for col in columnas_principales + columnas_series:
                    if col not in df_filtrado.columns:
                        df_filtrado[col] = ""

                df_tabla = df_filtrado[columnas_principales + columnas_series].copy()
                df_tabla = df_tabla.sort_values(by="Fecha", ascending=False)
                
                df_tabla_renombrada = df_tabla.rename(columns={
                    "Tipo_Entrenamiento": "Tipo de Entrenamiento",
                    "Promedio_Ritmo": "Ritmo Promedio",
                    "Distancia": "Distancia (km)",
                    "Tiempo": "Tiempo Total"
                })
                
                st.dataframe(df_tabla_renombrada, use_container_width=True, hide_index=True)

                st.write("---")
                st.subheader("📈 Evolución del Volumen (Kilómetros)")
                if 'Fecha' in df_filtrado.columns and not df_filtrado.empty:
                    df_graf = df_filtrado.copy()
                    df_graf['Fecha'] = pd.to_datetime(df_graf['Fecha'], errors='coerce')
                    df_graf = df_graf.dropna(subset=['Fecha']).sort_values('Fecha')
                    
                    fig = px.line(
                        df_graf, 
                        x='Fecha', 
                        y='Distancia', 
                        color='Atleta' if atleta_sel == "Todos los Atletas" else None,
                        markers=True,
                        title="Kilómetros recorridos por sesión",
                        template="plotly_white",
                        labels={"Distancia": "Distancia (km)", "Fecha": "Fecha de Sesión"}
                    )
                    fig.update_traces(line_color='#2E7D32' if atleta_sel != "Todos los Atletas" else None)
                    st.plotly_chart(fig, use_container_width=True)

                if atleta_sel != "Todos los Atletas" and not df_filtrado.empty:
                    st.write("---")
                    st.subheader(f"⏱️ Inspección de Series de {atleta_sel}")
                    
                    series_cols = [f"Serie_{i}" for i in range(1, 21) if f"Serie_{i}" in df_filtrado.columns]
                    df_con_series = df_filtrado[df_filtrado[series_cols].notna().any(axis=1)]
                    
                    if not df_con_series.empty:
                        fechas_disponibles = df_con_series['Fecha'].astype(str).unique()
                        fecha_sel = st.selectbox("Selecciona la fecha a analizar:", fechas_disponibles)
                        
                        sesion = df_con_series[df_con_series['Fecha'].astype(str) == fecha_sel].iloc[0]
                        st.info(f"📋 **Trabajo asignado:** {sesion.get('Tipo_Entrenamiento', 'Sin especificar')} | **Ritmo Promedio:** {sesion.get('Promedio_Ritmo', 'N/A')}")
                        
                        s_x, s_y = [], []
                        for col in series_cols:
                            val = sesion.get(col, "")
                            if str(val).strip() != "" and str(val).lower() != "nan":
                                s_x.append(col.replace("_", " "))
                                s_y.append(str(val))
                        
                        if s_x:
                            fig_series = px.bar(
                                x=s_x, y=s_y, text_auto=True, color_discrete_sequence=['#2E7D32'],
                                labels={"x": "Repetición", "y": "Tiempo (MM:SS)"}, title="Tiempos por Serie"
                            )
                            st.plotly_chart(fig_series, use_container_width=True)
                        else:
                            st.caption("No hay repeticiones registradas para esta fecha.")
        except Exception as e:
            st.error(f"Error técnico al cargar el panel: {e}")
