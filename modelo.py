from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
from plan_estudios import PLAN_LSI_2023

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
    id_materia: str (ej. '401')
    historial_alumno: dict con el estado de sus materias {'203': 'Aprobada', '304': 'Regular'}
    notas_alumno: dict con las calificaciones ingresadas
    trabaja: str ('No' o 'Si')
    dedicacion: str ('Bajo' o 'Alto')
    """
    materia_info = PLAN_LSI_2023[id_materia]
    
    # 1. CONTROL DETERMINÍSTICO DE REQUISITOS (Según la Resolución Oficial)
    for req in materia_info["aprobadas"]:
        if historial_alumno.get(req) != "Aprobada":
            return {"Insuficiente": 1.0, "Regular": 0.0, "Promocion": 0.0, "Observacion": f"No cumple con la correlativa Aprobada obligatoria: {req}"}
            
    for req in materia_info["regulares"]:
        if historial_alumno.get(req) not in ["Regular", "Aprobada"]:
            return {"Insuficiente": 1.0, "Regular": 0.0, "Promocion": 0.0, "Observacion": f"No cumple con la correlativa Regular obligatoria: {req}"}

    # 2. MODELADO PROBABILÍSTICO DINÁMICO (Si cumple los requisitos)
    
    # Unificamos todas las correlativas de la materia para rastrear el rendimiento previo
    correlativas_totales = list(set(materia_info["aprobadas"] + materia_info["regulares"]))
    
    # Filtramos cuáles de esas materias previas ya están aprobadas con nota en el sistema
    correlativas_con_nota = [m for m in correlativas_totales if historial_alumno.get(m) == "Aprobada" and m in notas_alumno]
    
    if correlativas_con_nota:
        # El alumno tiene finales rendidos en las previas. Tomamos la materia con la nota más alta.
        materia_base_id = max(correlativas_con_nota, key=lambda m: notas_alumno.get(m, 6))
        nota_base = notas_alumno[materia_base_id]
        base_academica = clasificar_base_academica(nota_base)
        texto_materia_base = f"{materia_base_id} - {PLAN_LSI_2023[materia_base_id]['nombre']}"
        tiene_nodo_base = True
    elif correlativas_totales:
        # Tiene materias previas obligatorias pero solo en condición de cursado Regular (sin nota de examen final)
        nota_base = "Regularizada (Sin Final)"
        base_academica = "Media"
        texto_materia_base = "Correlativas en condición Regular"
        tiene_nodo_base = True
    else:
        # Materias de primer año, primer cuatrimestre (no poseen requerimientos de correlativas)
        nota_base = "No aplica"
        base_academica = "No aplica"
        texto_materia_base = None
        tiene_nodo_base = False

    evidencia_ia = {'Trabaja': trabaja, 'Dedicacion': dedicacion}
    
    # Construcción dinámica de la topología de la Red Bayesiana
    estructura = [('Trabaja', 'Condicion_Final'), ('Dedicacion', 'Condicion_Final')]
    if tiene_nodo_base:
        estructura.append(('Base_Academica', 'Condicion_Final'))
        evidencia_ia['Base_Academica'] = base_academica
        
    modelo = DiscreteBayesianNetwork(estructura)
    
    # Definición de CPDs base para los contextos de entrada
    cpd_trabaja = TabularCPD(variable='Trabaja', variable_card=2, values=[[0.7], [0.3]], state_names={'Trabaja': ['No', 'Si']})
    cpd_dedicacion = TabularCPD(variable='Dedicacion', variable_card=2, values=[[0.4], [0.6]], state_names={'Dedicacion': ['Bajo', 'Alto']})
    modelo.add_cpds(cpd_trabaja, cpd_dedicacion)
    
    if tiene_nodo_base:
        cpd_base = TabularCPD(variable='Base_Academica', variable_card=2, values=[[0.5], [0.5]], state_names={'Base_Academica': ['Media', 'Alta']})
        modelo.add_cpds(cpd_base)
        
        # Tabla probabilística balanceada para nodos con base académica
        cpd_condicion = TabularCPD(
            variable='Condicion_Final', variable_card=3,
            values=[
                # Insuficiente
                [0.55, 0.65, 0.25, 0.40, 0.35, 0.50, 0.05, 0.15],
                # Regular
                [0.40, 0.32, 0.60, 0.50, 0.45, 0.42, 0.45, 0.55],
                # Promocion
                [0.05, 0.03, 0.15, 0.10, 0.20, 0.08, 0.50, 0.30]
            ],
            evidence=['Base_Academica', 'Dedicacion', 'Trabaja'], evidence_card=[2, 2, 2],
            state_names={'Condicion_Final': ['Insuficiente', 'Regular', 'Promocion'],
                         'Base_Academica': ['Media', 'Alta'], 'Dedicacion': ['Bajo', 'Alto'], 'Trabaja': ['No', 'Si']}
        )
    else:
        # Tabla probabilística para asignaturas sin dependencias
        cpd_condicion = TabularCPD(
            variable='Condicion_Final', variable_card=3,
            values=[
                # Insuficiente
                [0.45, 0.60, 0.10, 0.25], 
                # Regular
                [0.50, 0.38, 0.45, 0.55], 
                # Promocion
                [0.05, 0.02, 0.45, 0.20]  
            ],
            evidence=['Dedicacion', 'Trabaja'], evidence_card=[2, 2],
            state_names={'Condicion_Final': ['Insuficiente', 'Regular', 'Promocion'],
                         'Dedicacion': ['Bajo', 'Alto'], 'Trabaja': ['No', 'Si']}
        )
        
    modelo.add_cpds(cpd_condicion)
    
    # Motor de inferencia
    inferencia = VariableElimination(modelo)
    resultado = inferencia.query(variables=['Condicion_Final'], evidence=evidencia_ia)
    
    # Armado de la observación de diagnóstico para el Chatbot
    if texto_materia_base:
        observacion_final = f"Cumple con las correlativas de la Res. 2024-723-CS. Evaluando rendimiento con base en: {texto_materia_base}."
    else:
        observacion_final = "Materia del primer cuatrimestre de la carrera. Análisis basado puramente en contexto de dedicación y trabajo."

    return {
        "Insuficiente": resultado.values[0],
        "Regular": resultado.values[1],
        "Promocion": resultado.values[2],
        "BaseAcademica": base_academica,
        "NotaBase": str(nota_base),
        "Observacion": observacion_final
    }