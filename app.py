import streamlit as st
import pandas as pd
from plan_estudios import PLAN_LSI_2023
from modelo import evaluar_situacion_materia, discretizar_contexto

# Configuración de la página de Streamlit
st.set_page_config(page_title="Tutor AI - LSI 2023", page_icon="🎓", layout="wide")

st.title("🎓 Sistema Experto de Orientación Académica (LSI 2023)")
st.caption("Trabajo Práctico Integrador - Inteligencia Artificial (FaCENA-UNNE)")

# --- BARRA LATERAL: Configuración del Historial del Alumno ---
st.sidebar.header("👤 Perfil y Estado del Alumno")

# Variables de contexto
st.sidebar.header("👤 Perfil y Contexto de Estudio")

# 1. Captura de horas de trabajo
trabaja_opcion = st.sidebar.radio("¿Realiza actividad laboral?", ["No", "Si"])
horas_trabajo = 0
if trabaja_opcion == "Si":
    horas_trabajo = st.sidebar.slider(
        "Horas laborales semanales", 
        min_value=1, max_value=48, value=20, step=1,
        help="Indicá tu carga horaria laboral aproximada por semana."
    )

# 2. Captura de horas de estudio
horas_estudio = st.sidebar.slider(
    "Horas semanales de estudio extra-áulico", 
    min_value=1, max_value=40, value=8, step=1,
    help="Horas que estimás dedicarle a la lectura y práctica de esta materia en casa."
)

st.sidebar.markdown("---")
st.sidebar.subheader("📋 Historial de Materias")
st.sidebar.info("Las materias siguientes se desbloquearán automáticamente a medida que apruebes o regularices sus correlativas.")

# Diccionario para almacenar el estado del historial en la sesión de Streamlit
if "historial" not in st.session_state:
    st.session_state.historial = {cod: "No Cursada" for cod in PLAN_LSI_2023.keys()}

# Renderizar solo las materias que están desbloqueadas según sus correlativas
for cod, info in PLAN_LSI_2023.items():
    desbloqueada = True
    
    # 1. Verificamos si cumple con las correlativas Aprobadas
    for req_aprob in info["aprobadas"]:
        if st.session_state.historial.get(req_aprob) != "Aprobada":
            desbloqueada = False
            break
            
    # 2. Verificamos si cumple con las correlativas Regulares (si pasó el filtro anterior)
    if desbloqueada:
        for req_reg in info["regulares"]:
            if st.session_state.historial.get(req_reg) not in ["Regular", "Aprobada"]:
                desbloqueada = False
                break
                
    # 3. Dibujamos el selector SOLO si está desbloqueada
    if desbloqueada:
        nuevo_estado = st.sidebar.selectbox(
            f"{cod} - {info['nombre']}",
            ["No Cursada", "Regular", "Aprobada"],
            index=["No Cursada", "Regular", "Aprobada"].index(st.session_state.historial[cod]),
            key=f"sidebar_{cod}"
        )
        st.session_state.historial[cod] = nuevo_estado
    else:
        # Si la materia queda bloqueada (ej. el usuario desmarcó una correlativa), 
        # forzamos su estado interno a "No Cursada" para mantener la consistencia en cascada.
        st.session_state.historial[cod] = "No Cursada"

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
            nombre_mat = materias_pendientes[materia_seleccionada]
            
            # 1. Aplicamos la discretización de las horas
            estado_trab, estado_estud = discretizar_contexto(horas_trabajo, horas_estudio)
            
            # 2. Mostramos en el chat cómo el sistema interpretó esos números
            st.session_state.mensajes_chat.append(
                {"role": "user", "content": f"Quiero consultar: {materia_seleccionada} - {nombre_mat}.\n\n⏱️ Mi contexto: Trabajo {horas_trabajo}hs semanales | Estudiaré {horas_estudio}hs extra."}
            )
            
            # 3. Llamamos al motor con los estados discretizados ('Alta', 'Part-time', etc.)
            resultado = evaluar_situacion_materia(
                materia_seleccionada, 
                st.session_state.historial, 
                estado_trab,   
                estado_estud   
            )
            
            # 4. Formatear la respuesta del asistente
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