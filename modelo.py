import pandas as pd
from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.estimators import BayesianEstimator
from pgmpy.inference import VariableElimination
from plan_estudios import PLAN_LSI_2023
from pgmpy.estimators import MaximumLikelihoodEstimator

# Cargar el dataset de entrenamiento en memoria una sola vez al iniciar la app
try:
    DF_ENTRENAMIENTO = pd.read_csv('dataset_entrenamiento_lsi.csv')
except FileNotFoundError:
    DF_ENTRENAMIENTO = None

def discretizar_contexto(horas_trabajo, horas_estudio):
    """
    Convierte las variables numéricas continuas a los estados binarios 
    ('No'/'Si' y 'Bajo'/'Alto') que espera la Red Bayesiana.
    """
    if horas_trabajo == 0:
        estado_trabajo = "No"
    else:
        estado_trabajo = "Si"
        
    if horas_estudio < 10:
        estado_estudio = "Bajo"
    else:
        estado_estudio = "Alto"
        
    return estado_trabajo, estado_estudio

def clasificar_base_academica(nota):
    if nota >= 8:
        return "Alta"
    else:
        return "Media"

def evaluar_situacion_materia(id_materia, historial_alumno, notas_alumno, trabaja, dedicacion):
    """
    Motor de Inferencia Híbrido:
    1. Filtro determinístico (Res. 2024-723-CS).
    2. Red Bayesiana entrenada con datos históricos.
    """
    materia_info = PLAN_LSI_2023[id_materia]
    
    # 1. CONTROL DETERMINÍSTICO DE REQUISITOS
    for req in materia_info["aprobadas"]:
        if historial_alumno.get(req) != "Aprobada":
            return {"Insuficiente": 1.0, "Regular": 0.0, "Promocion": 0.0, "Observacion": f"No cumple con la correlativa Aprobada obligatoria: {req}"}
            
    for req in materia_info["regulares"]:
        if historial_alumno.get(req) not in ["Regular", "Aprobada"]:
            return {"Insuficiente": 1.0, "Regular": 0.0, "Promocion": 0.0, "Observacion": f"No cumple con la correlativa Regular obligatoria: {req}"}

    # 2. PREPARACIÓN DE VARIABLES PARA LA IA
    correlativas_totales = list(set(materia_info["aprobadas"] + materia_info["regulares"]))
    correlativas_con_nota = [m for m in correlativas_totales if historial_alumno.get(m) == "Aprobada" and m in notas_alumno]
    
    if correlativas_con_nota:
        materia_base_id = max(correlativas_con_nota, key=lambda m: notas_alumno.get(m, 6))
        nota_base = notas_alumno[materia_base_id]
        base_academica = clasificar_base_academica(nota_base)
        texto_materia_base = f"{materia_base_id} - {PLAN_LSI_2023[materia_base_id]['nombre']}"
        tiene_nodo_base = True
    elif correlativas_totales:
        nota_base = "Regularizada (Sin Final)"
        base_academica = "Media"
        texto_materia_base = "Correlativas en condición Regular"
        tiene_nodo_base = True
    else:
        nota_base = "No aplica"
        base_academica = "No aplica"
        texto_materia_base = None
        tiene_nodo_base = False

    evidencia_ia = {'Trabaja': trabaja, 'Dedicacion': dedicacion}
    
    # 3. CONSTRUCCIÓN Y ENTRENAMIENTO DEL MODELO PROBABILÍSTICO
    if DF_ENTRENAMIENTO is None:
        return {"Insuficiente": 0.0, "Regular": 0.0, "Promocion": 0.0, "BaseAcademica": "Error", "NotaBase": "Error", "Observacion": "Falta archivo dataset_entrenamiento_lsi.csv"}

    estructura = [('Trabaja', 'Condicion_Final'), ('Dedicacion', 'Condicion_Final')]
    if tiene_nodo_base:
        estructura.append(('Base_Academica', 'Condicion_Final'))
        evidencia_ia['Base_Academica'] = base_academica
        
    modelo = DiscreteBayesianNetwork(estructura)
    
    # ---------------------------------------------------------
    # SOLUCIÓN: Entrenamiento por Máxima Verosimilitud (MLE)
    # ---------------------------------------------------------
    estimador = MaximumLikelihoodEstimator(modelo, DF_ENTRENAMIENTO)
    modelo.add_cpds(*estimador.get_parameters())
    # ---------------------------------------------------------

    # 4. INFERENCIA
    inferencia = VariableElimination(modelo)
    resultado = inferencia.query(variables=['Condicion_Final'], evidence=evidencia_ia)
    
    if texto_materia_base:
        observacion_final = f"Cumple correlativas. Predicción basada en aprendizaje automático sobre dataset histórico. Base: {texto_materia_base}."
    else:
        observacion_final = "Materia de primer año. Predicción basada en aprendizaje automático sobre dataset histórico."

    # Mapeo dinámico de los resultados del estimador
    # pgmpy devuelve los estados en orden alfabético interno, así que buscamos sus valores exactos.
    probabilidades = dict(zip(resultado.state_names['Condicion_Final'], resultado.values))

    return {
        "Insuficiente": probabilidades.get('Insuficiente', 0.0),
        "Regular": probabilidades.get('Regular', 0.0),
        "Promocion": probabilidades.get('Promocion', 0.0),
        "BaseAcademica": base_academica,
        "NotaBase": str(nota_base),
        "Observacion": observacion_final
    }