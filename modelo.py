# modelo.py
from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
from plan_estudios import PLAN_LSI_2023

def evaluar_situacion_materia(id_materia, historial_alumno, trabaja, dedicacion):
    """
    id_materia: str (ej. '401')
    historial_alumno: dict con el estado de sus materias {'203': 'Aprobada', '304': 'Regular'}
    trabaja: str ('No' o 'Si')
    dedicacion: str ('Baja' o 'Alta')
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
    # Creamos una red con los nodos padres reales que tiene esa materia según el plan
    nodos_padres = []
    evidencia_ia = {'Trabaja': trabaja, 'Dedicacion': dedicacion}
    
    # Usamos la primera materia correlativa regular como el "indicador de base académica"
    materia_base = materia_info["regulares"][0] if materia_info["regulares"] else None
    
    if materia_base:
        nodos_padres.append('Base_Academica')
        # Mapeamos el estado real del alumno para el motor de inferencia
        evidencia_ia['Base_Academica'] = 'Alta' if historial_alumno.get(materia_base) == 'Aprobada' else 'Media'
    
    # Construcción del grafo de influencia para la materia consultada
    estructura = [('Trabaja', 'Condicion_Final'), ('Dedicacion', 'Condicion_Final')]
    if materia_base:
        estructura.append(('Base_Academica', 'Condicion_Final'))
        
    modelo = BayesianNetwork(estructura)
    
    # Definición de las CPDs genéricas de contexto
    cpd_trabaja = TabularCPD(variable='Trabaja', variable_card=2, values=[[0.7], [0.3]], state_names={'Trabaja': ['No', 'Si']})
    cpd_dedicacion = TabularCPD(variable='Dedicacion', variable_card=2, values=[[0.4], [0.6]], state_names={'Dedicacion': ['Bajo', 'Alto']})
    modelo.add_cpds(cpd_trabaja, cpd_dedicacion)
    
    if materia_base:
        cpd_base = TabularCPD(variable='Base_Academica', variable_card=2, values=[[0.5], [0.5]], state_names={'Base_Academica': ['Media', 'Alta']})
        modelo.add_cpds(cpd_base)
        
        # Tabla de Probabilidad Condicional con 3 salidas: [Insuficiente, Regular, Promocion]
        # Cardinalidad de evidencia: Base_Academica(2) x Dedicacion(2) x Trabaja(2) = 8 combinaciones
        cpd_condicion = TabularCPD(
            variable='Condicion_Final', variable_card=3,
            values=[
                # Insuficiente
                [0.60, 0.45, 0.35, 0.20, 0.40, 0.25, 0.15, 0.05],
                # Regular
                [0.35, 0.50, 0.55, 0.65, 0.45, 0.55, 0.55, 0.45],
                # Promocion
                [0.05, 0.05, 0.10, 0.15, 0.15, 0.20, 0.30, 0.50]
            ],
            evidence=['Base_Academica', 'Dedicacion', 'Trabaja'], evidence_card=[2, 2, 2],
            state_names={'Condicion_Final': ['Insuficiente', 'Regular', 'Promocion'],
                         'Base_Academica': ['Media', 'Alta'], 'Dedicacion': ['Bajo', 'Alto'], 'Trabaja': ['No', 'Si']}
        )
    else:
        # Para materias de primer año sin correlativas previas
        cpd_condicion = TabularCPD(
            variable='Condicion_Final', variable_card=3,
            values=[
                [0.50, 0.30, 0.25, 0.10], # Insuficiente
                [0.45, 0.55, 0.55, 0.45], # Regular
                [0.05, 0.15, 0.20, 0.45]  # Promocion
            ],
            evidence=['Dedicacion', 'Trabaja'], evidence_card=[2, 2],
            state_names={'Condicion_Final': ['Insuficiente', 'Regular', 'Promocion'],
                         'Dedicacion': ['Bajo', 'Alto'], 'Trabaja': ['No', 'Si']}
        )
        
    modelo.add_cpds(cpd_condicion)
    
    # Ejecutar la inferencia por eliminación de variables
    inferencia = VariableElimination(modelo)
    resultado = inferencia.query(variables=['Condicion_Final'], evidence=evidencia_ia)
    
    return {
        "Insuficiente": resultado.values[0],
        "Regular": resultado.values[1],
        "Promocion": resultado.values[2],
        "Observacion": "Cumple con las correlativas de la Res. 2024-723-CS. Análisis probabilístico completado." [cite: 50]
    }