from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
from plan_estudios import PLAN_LSI_2023

def discretizar_contexto(horas_trabajo, horas_estudio):
    """
    Convierte las variables numéricas continuas a los estados binarios 
    ('No'/'Si' y 'Bajo'/'Alto') que espera la Red Bayesiana.
    """
    # Discretización del Trabajo
    if horas_trabajo == 0:
        estado_trabajo = "No"
    else:
        estado_trabajo = "Si"
        
    # Discretización del Estudio (Umbral de dedicación)
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
    # Creamos una red con los nodos padres reales que tiene esa materia según el plan
    nodos_padres = []
    evidencia_ia = {'Trabaja': trabaja, 'Dedicacion': dedicacion}
    
    # Usamos la primera materia correlativa regular como el "indicador de base académica"
    if materia_info["aprobadas"]:
        materia_base = max(
            materia_info["aprobadas"],
            key=lambda m: notas_alumno.get(m, 6)
            )
    else:
        materia_base = None
        
    if materia_base:
        nodos_padres.append('Base_Academica')

        nota_base = notas_alumno.get(materia_base, 6)

        evidencia_ia['Base_Academica'] = clasificar_base_academica(nota_base)
        base_academica = clasificar_base_academica(nota_base)
        evidencia_ia['Base_Academica'] = base_academica
    # Construcción del grafo de influencia para la materia consultada
    estructura = [('Trabaja', 'Condicion_Final'), ('Dedicacion', 'Condicion_Final')]
    if materia_base:
        estructura.append(('Base_Academica', 'Condicion_Final'))
        
    modelo = DiscreteBayesianNetwork(estructura)
    
    # Definición de las CPDs genéricas de contexto
    cpd_trabaja = TabularCPD(variable='Trabaja', variable_card=2, values=[[0.7], [0.3]], state_names={'Trabaja': ['No', 'Si']})
    cpd_dedicacion = TabularCPD(variable='Dedicacion', variable_card=2, values=[[0.4], [0.6]], state_names={'Dedicacion': ['Bajo', 'Alto']})
    modelo.add_cpds(cpd_trabaja, cpd_dedicacion)
    
    if materia_base:
        cpd_base = TabularCPD(variable='Base_Academica', variable_card=2, values=[[0.5], [0.5]], state_names={'Base_Academica': ['Media', 'Alta']})
        modelo.add_cpds(cpd_base)
        
        # TABLA CORREGIDA (Con materia base)
        # Columnas en orden de pgmpy: 
        # [Media,Bajo,No], [Media,Bajo,Si], [Media,Alto,No], [Media,Alto,Si], [Alta,Bajo,No], [Alta,Bajo,Si], [Alta,Alto,No], [Alta,Alto,Si]
        cpd_condicion = TabularCPD(
            variable='Condicion_Final', variable_card=3,
            values=[
                # Insuficiente (Sube si trabaja o si la dedicación/base es baja)
                [0.55, 0.65, 0.25, 0.40, 0.35, 0.50, 0.05, 0.15],
                # Regular
                [0.40, 0.32, 0.60, 0.50, 0.45, 0.42, 0.45, 0.55],
                # Promocion (Baja si trabaja)
                [0.05, 0.03, 0.15, 0.10, 0.20, 0.08, 0.50, 0.30]
            ],
            evidence=['Base_Academica', 'Dedicacion', 'Trabaja'], evidence_card=[2, 2, 2],
            state_names={'Condicion_Final': ['Insuficiente', 'Regular', 'Promocion'],
                         'Base_Academica': ['Media', 'Alta'], 'Dedicacion': ['Bajo', 'Alto'], 'Trabaja': ['No', 'Si']}
        )
    else:
        # TABLA CORREGIDA (Para materias de primer año sin correlativas previas)
        # Columnas en orden de pgmpy:
        # [Bajo, No], [Bajo, Si], [Alto, No], [Alto, Si]
        cpd_condicion = TabularCPD(
            variable='Condicion_Final', variable_card=3,
            values=[
                # Insuficiente (Sube si trabaja)
                [0.45, 0.60, 0.10, 0.25], 
                # Regular
                [0.50, 0.38, 0.45, 0.55], 
                # Promocion (Baja si trabaja)
                [0.05, 0.02, 0.45, 0.20]  
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
        "BaseAcademica": base_academica if materia_base else "No aplica",
        "NotaBase": nota_base if materia_base else "No aplica",
        "Observacion": "Cumple con las correlativas de la Res. 2024-723-CS. Análisis probabilístico completado."
    }