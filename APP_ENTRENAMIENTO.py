import streamlit as st
import pandas as pd
import os
from datetime import date

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Registro de Entrenamiento", layout="centered")

st.title("🏃🏽‍♂️ Registro Diario de Entrenamiento")
st.write("Registra los datos de tu ejecución de hoy.")

# --- ARCHIVO DE GUARDADO ---
archivo_datos = "registros_atletas.xlsx"

# --- FORMULARIO ---
with st.form("registro_diario"):
    # Identificación básica
    atleta = st.text_input("Nombre del Atleta", placeholder="Ej: Juan Pérez")
    fecha = st.date_input("Fecha de entrenamiento", date.today())
    
    st.subheader("Datos de Ejecución")
    col1, col2 = st.columns(2)
    with col1:
        distancia = st.number_input("Distancia Real (km)", min_value=0.0, step=0.1)
        tiempo = st.text_input("Tiempo Real", placeholder="ej: 00:55:00")
    with col2:
        sensacion = st.selectbox("Sensación general", ["Excelente", "Bien", "Cansado", "Con Dolor"])
        cumplimiento = st.radio("¿Cumpliste el objetivo planificado?", ["Sí", "No"])
        
    st.subheader("Trabajos de Velocidad (Opcional)")
    st.write("Si hoy tuviste pista o intervalos, registra tus series.")
    hubo_series = st.checkbox("Habilitar registro de repeticiones")
    
    # Manejo de las series
    series_tiempos = []
    if hubo_series:
        num_repeticiones = st.slider("Número de repeticiones realizadas", 1, 12, 5)
        cols = st.columns(4)
        for i in range(num_repeticiones):
            with cols[i % 4]:
                tiempo_rep = st.text_input(f"Serie {i+1}", key=f"rep_{i}")
                # Guardamos el tiempo (incluso si está vacío para mantener el orden)
                series_tiempos.append(tiempo_rep)
                
    # Botón para enviar
    enviado = st.form_submit_button("Guardar Entrenamiento")
    
    # --- LÓGICA DE GUARDADO EN EXCEL ---
    if enviado:
        if not atleta:
            st.error("Por favor, ingresa el nombre del atleta.")
        else:
            # 1. Creamos la base del registro
            nuevo_registro = {
                "Fecha": fecha.strftime("%Y-%m-%d"),
                "Atleta": atleta,
                "Distancia_Real_km": distancia,
                "Tiempo_Real": tiempo,
                "Sensacion": sensacion,
                "Cumplimiento": cumplimiento
            }
            
            # 2. Agregamos exactamente 12 columnas para las series (vacías por defecto)
            for i in range(1, 13):
                nuevo_registro[f"Serie_{i}"] = ""
                
            # 3. Llenamos las columnas con las series que el atleta realmente hizo
            if hubo_series:
                for idx, tiempo_rep in enumerate(series_tiempos):
                    # Solo llenamos hasta la cantidad que haya hecho
                    nuevo_registro[f"Serie_{idx+1}"] = tiempo_rep
            
            # 4. Convertimos a DataFrame y guardamos
            df_nuevo = pd.DataFrame([nuevo_registro])
            
            try:
                if os.path.isfile(archivo_datos):
                    df_existente = pd.read_excel(archivo_datos)
                    df_final = pd.concat([df_existente, df_nuevo], ignore_index=True)
                    df_final.to_excel(archivo_datos, index=False)
                else:
                    df_nuevo.to_excel(archivo_datos, index=False)
                    
                st.success(f"¡Excelente trabajo, {atleta}! Datos guardados en Excel correctamente.")
            
            except Exception as e:
                st.error(f"Hubo un error al guardar: {e}. Si el Excel está abierto, ciérralo y vuelve a intentar.")