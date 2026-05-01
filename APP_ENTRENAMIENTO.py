import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date
import time

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Registro de Entrenamiento", layout="centered")

st.title("🏃🏽‍♂️ Registro Diario de Entrenamiento")
st.write("Completa los datos y se sincronizarán en tiempo real con Google Sheets.")

# --- CONEXIÓN A GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- ENTRADA DE DATOS (SIN FORM) ---
# Al quitar el formulario, las opciones aparecerán apenas marques el checkbox
atleta = st.text_input("Nombre del Atleta", placeholder="Ej: Juan Pérez")
fecha = st.date_input("Fecha", date.today())

col1, col2 = st.columns(2)
with col1:
    distancia = st.number_input("Distancia Real (km)", min_value=0.0, step=0.1)
    tiempo = st.text_input("Tiempo Real", placeholder="ej: 00:55:00")
with col2:
    sensacion = st.selectbox("Sensación", ["Excelente", "Bien", "Cansado", "Con Dolor"])
    cumplimiento = st.radio("¿Cumpliste el objetivo?", ["Sí", "No"])

# --- SECCIÓN DINÁMICA DE SERIES ---
hubo_series = st.checkbox("¿Hiciste series de velocidad?")
series_tiempos = []

if hubo_series:
    # Esto aparecerá INSTANTÁNEAMENTE al marcar el checkbox anterior
    num_rep = st.slider("Número de repeticiones", 1, 12, 5)
    cols = st.columns(4)
    for i in range(num_rep):
        with cols[i % 4]:
            t = st.text_input(f"S{i+1}", key=f"rep_{i}")
            series_tiempos.append(t)

st.divider() # Una línea visual antes del botón

# --- BOTÓN DE GUARDADO ---
enviado = st.button("Guardar Entrenamiento")

if enviado:
    if not atleta:
        st.error("Por favor, ingresa el nombre del atleta.")
    else:
        fecha_str = fecha.strftime("%Y-%m-%d")
        
        # 1. Preparar datos
        nuevo_reg = {
            "Fecha": [fecha_str],
            "Atleta": [atleta],
            "Distancia": [distancia],
            "Tiempo": [tiempo],
            "Sensacion": [sensacion],
            "Cumplimiento": [cumplimiento]
        }
        
        # Llenamos las 12 columnas de series posibles
        for i in range(1, 13):
            valor = series_tiempos[i-1] if hubo_series and i <= len(series_tiempos) else ""
            nuevo_reg[f"Serie_{i}"] = [valor]
        
        df_nuevo = pd.DataFrame(nuevo_reg)

        # 2. Proceso de Guardado
        try:
            # Leemos datos actuales (sin caché)
            existente = conn.read(ttl=0)
            
            # Verificación anti-duplicados
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
                st.warning(f"⚠️ Ya existe un registro igual para {atleta}. No se ha guardado de nuevo.")
            else:
                # Unimos y actualizamos
                df_final = pd.concat([existente, df_nuevo], ignore_index=True)
                df_final = df_final.dropna(how='all')
                conn.update(data=df_final)
                
                st.success(f"¡Excelente trabajo, {atleta}! Registrado en la nube.")
                st.balloons()
                
                # Esperamos un par de segundos y refrescamos para limpiar la pantalla
                time.sleep(2)
                st.rerun()
                
        except Exception as e:
            st.error(f"Error al conectar con Google: {e}")
