import streamlit as st
import pandas as pd
from plan_estudios import PLAN_LSI_2023
from modelo import evaluar_situacion_materia

# Configuración de la página de Streamlit
st.set_page_config(page_title="Tutor AI - LSI 2023", page_icon="🎓", layout="wide")

st.title("🎓 Sistema Experto de Orientación Académica (LSI 2023)")
st.caption("Trabajo Práctico Integrador - Inteligencia Artificial (FaCENA-UNNE)")

# --- BARRA LATERAL: Configuración del Historial del Alumno ---
st.sidebar.header("👤 Perfil y Estado del Alumno")

# Variables de contexto
trabaja = st.sidebar.radio("¿Realiza actividad laboral?", ["No", "Si"])
dedicacion = st.sidebar.radio("Dedicación al estudio fuera de clases:", ["Baja", "Alta"])

st.sidebar.markdown("---")
st.sidebar.subheader("Historial de Materias")
st.sidebar.info("Marcá el estado actual de tus materias previas para calcular las correlatividades automáticamente.")

# Diccionario para almacenar el estado del historial en la sesión de Streamlit
if "historial" not in st.session_state:
    st.session_state.historial = {cod: "No Cursada" for cod in PLAN_LSI_2023.keys()}

# Renderizar selectores para cada materia en la barra lateral
for cod, info in PLAN_LSI_2023.items():
    # Evitamos que se pueda marcar a sí misma en este bucle de configuración simple
    estado = st.sidebar.selectbox(
        f"{cod} - {info['nombre']}",
        ["No Cursada", "Regular", "Aprobada"],
        index=["No Cursada", "Regular", "Aprobada"].index(st.session_state.historial[cod]),
        key=f"sidebar_{cod}"
    )
    st.session_state.historial[cod] = estado


# --- ÁREA PRINCIPAL: Interfaz del Chatbot ---

# Filtrar las materias que NO están aprobadas para el menú desplegable del chat
materias_pendientes = {
    cod: info["nombre"] 
    for cod, info in PLAN_LSI_2023.items() 
    if st.session_state.historial[cod] != "Aprobada"
}

# Inicializar el contenedor de mensajes del chat si no existe
if "mensajes_chat" not in st.session_state:
    st.session_state.mensajes_chat = [
        {"role": "assistant", "content": "¡Hola! Soy tu Asistente de LSI. Configura tu perfil en la barra lateral y selecciona abajo qué materia pendiente deseas auditar hoy."}
    ]

# Mostrar el historial de la conversación
for msg in st.session_state.mensajes_chat:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "data_grafico" in msg:
            # Si el mensaje guardado tenía un gráfico, lo vuelve a renderizar
            st.bar_chart(msg["data_grafico"])

# Formulario interactivo simulando la entrada del chat
if materias_pendientes:
    with st.container():
        st.write("---")
        # El menú desplegable dinámico que filtra las aprobadas
        materia_seleccionada = st.selectbox(
            "Seleccioná la materia que querés consultar:",
            options=list(materias_pendientes.keys()),
            format_func=lambda x: f"{x} - {materias_pendientes[x]}"
        )
        
        btn_consultar = st.button("Consultar con el Sistema Experto")
        
        if btn_consultar:
            # 1. Agregar consulta del usuario al chat
            nombre_mat = materias_pendientes[materia_seleccionada]
            st.session_state.mensajes_chat.append(
                {"role": "user", "content": f"Quiero consultar mis posibilidades para la materia: {materia_seleccionada} - {nombre_mat}"}
            )
            
            # 2. Llamar al motor probabilístico/determinístico
            resultado = evaluar_situacion_materia(
                materia_seleccionada, 
                st.session_state.historial, 
                trabaja, 
                dedicacion
            )
            
            # 3. Formatear la respuesta del asistente
            respuesta_bot = f"**Análisis para {nombre_mat}:**\n\n"
            respuesta_bot += f"*Observación:* {resultado['Observacion']}\n\n"
            
            df_grafico = None
            if "No cumple" not in resultado['Observacion']:
                respuesta_bot += "**Predicción de condición final:**\n"
                respuesta_bot += f"- 🔴 **Insuficiente (Libre/Abandono):** {resultado['Insuficiente']*100:.1f}%\n"
                respuesta_bot += f"- 🟡 **Regular:** {resultado['Regular']*100:.1f}%\n"
                respuesta_bot += f"- 🟢 **Promoción (Aprobada):** {resultado['Promocion']*100:.1f}%\n"
                
                # Crear estructura de datos para el gráfico de barras de Streamlit
                df_grafico = pd.DataFrame({
                    "Probabilidad": [resultado['Insuficiente'], resultado['Regular'], resultado['Promocion']]
                }, index=["Insuficiente", "Regular", "Promoción"])
            
            # Guardar respuesta en el historial de estados
            nuevo_mensaje = {"role": "assistant", "content": respuesta_bot}
            if df_grafico is not None:
                nuevo_mensaje["data_grafico"] = df_grafico
                
            st.session_state.mensajes_chat.append(nuevo_mensaje)
            
            # Forzar actualización de pantalla para mostrar los nuevos mensajes
            st.rerun()
else:
    st.success("¡Felicitaciones! Según el historial de la barra lateral, ya aprobaste todas las materias cargadas en el sistema.")