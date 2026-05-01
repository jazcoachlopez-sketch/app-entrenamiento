import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Registro de Entrenamiento", layout="centered")

st.title("🏃🏽‍♂️ Registro Diario de Entrenamiento")
st.write("Registra tus datos de hoy. La información se sincroniza con Google Sheets.")

# --- CONEXIÓN A GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FORMULARIO ---
# Agregamos clear_on_submit=True para que el formulario se limpie al guardar
with st.form("registro_diario", clear_on_submit=True):
    atleta = st.text_input("Nombre del Atleta", placeholder="Ej: Juan Pérez")
    fecha = st.date_input("Fecha", date.today())
    
    col1, col2 = st.columns(2)
    with col1:
        distancia = st.number_input("Distancia Real (km)", min_value=0.0, step=0.1)
        tiempo = st.text_input("Tiempo Real", placeholder="ej: 00:55:00")
    with col2:
        sensacion = st.selectbox("Sensación", ["Excelente", "Bien", "Cansado", "Con Dolor"])
        cumplimiento = st.radio("¿Cumpliste el objetivo?", ["Sí", "No"])
        
    hubo_series = st.checkbox("¿Hiciste series de velocidad?")
    series_tiempos = []
    if hubo_series:
        num_rep = st.slider("Número de repeticiones", 1, 12, 5)
        cols = st.columns(4)
        for i in range(num_rep):
            with cols[i % 4]:
                t = st.text_input(f"S{i+1}", key=f"rep_{i}")
                series_tiempos.append(t)
                
    enviado = st.form_submit_button("Guardar Entrenamiento")

    if enviado:
        if not atleta:
            st.error("Por favor, ingresa el nombre del atleta.")
        else:
            # 1. Preparar datos para el registro
            fecha_str = fecha.strftime("%Y-%m-%d")
            nuevo_reg = {
                "Fecha": [fecha_str],
                "Atleta": [atleta],
                "Distancia": [distancia],
                "Tiempo": [tiempo],
                "Sensacion": [sensacion],
                "Cumplimiento": [cumplimiento]
            }
            for i in range(1, 13):
                valor = series_tiempos[i-1] if hubo_series and i <= len(series_tiempos) else ""
                nuevo_reg[f"Serie_{i}"] = [valor]
            
            df_nuevo = pd.DataFrame(nuevo_reg)

            # 2. Enviar a Google Sheets con verificación de duplicados
            try:
                # Leemos la hoja "en vivo"
                existente = conn.read(ttl=0)
                
                # --- LÓGICA ANTI-DUPLICADOS ---
                # Verificamos si existe una fila con el mismo Atleta, Fecha y Distancia
                # Esto evita guardar el mismo entrenamiento dos veces por error
                es_duplicado = False
                if not existente.empty:
                    duplicados = existente[
                        (existente['Atleta'].astype(str) == atleta) & 
                        (existente['Fecha'].astype(str) == fecha_str) & 
                        (existente['Distancia'].astype(float) == float(distancia))
                    ]
                    if not duplicados.empty:
                        es_duplicado = True

                if es_duplicado:
                    st.warning(f"⚠️ Atención: Ya existe un registro para {atleta} en esta fecha con esa distancia. No se ha duplicado la información.")
                else:
                    # Si no es duplicado, acumulamos y subimos
                    df_final = pd.concat([existente, df_nuevo], ignore_index=True)
                    df_final = df_final.dropna(how='all')
                    conn.update(data=df_final)
                    
                    st.success(f"¡Excelente trabajo, {atleta}! Datos guardados correctamente.")
                    st.balloons() # Un pequeño festejo visual para el atleta
                
            except Exception as e:
                st.error(f"Error al conectar con Google: {e}")
