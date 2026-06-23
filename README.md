## Sistema Experto Híbrido de Orientación Académica

**Trabajo Integrador - Inteligencia Artificial (2026)**
**Licenciatura en Sistemas de Información - FaCENA, UNNE**

Este repositorio contiene el código fuente de un agente de software inteligente diseñado para asistir en la toma de decisiones académicas. El sistema transiciona de una arquitectura basada puramente en reglas lógicas (validación de correlativas) hacia un motor probabilístico basado en Redes Bayesianas, modelando la incertidumbre del desempeño universitario mediante variables de contexto.

# Autoras
Navarro Milagros Valentina (LU 54308)
Rodriguez Ojeda Lourdes (LU 55718) 

## Requisitos Previos
Instalar las dependencias necesarias, ejecutando el comando:
pip install -r requirements.txt

Para comprobar matemáticamente la eficacia de la Red Bayesiana (entrenada mediante el Estimador de Máxima Verosimilitud)
y visualizar las métricas del modelo (Accuracy, Matriz de Confusión), ejecute:
python evaluacion.py

Para lanzar el Chatbot interactivo y probar el sistema experto desde el navegador, 
utilice el framework Streamlit ejecutando el siguiente comando:
streamlit run app.py

