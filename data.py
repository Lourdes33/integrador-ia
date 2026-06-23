import pandas as pd
import numpy as np

np.random.seed(42)
# Generamos 3000 registros (simulando historiales de cursado de múltiples alumnos en varias materias)
num_registros = 3000

# 1. Variables de Entrada (Nodos Padre) - Etiquetas exactas de modelo.py
trabaja = np.random.choice(['Si', 'No'], size=num_registros, p=[0.40, 0.60])

# El tiempo de estudio se ve penalizado por el trabajo
dedicacion = []
for t in trabaja:
    if t == 'Si': 
        # Carga laboral reduce el tiempo extra-áulico
        d_nivel = np.random.choice(['Alto', 'Bajo'], p=[0.25, 0.75])
    else:
        d_nivel = np.random.choice(['Alto', 'Bajo'], p=[0.65, 0.35])
    dedicacion.append(d_nivel)

# La base académica previa del alumno
base_academica = np.random.choice(['Alta', 'Media'], size=num_registros, p=[0.45, 0.55])

# 2. Variable Objetivo (Nodo Hijo)
condicion_final = []

for i in range(num_registros):
    t = trabaja[i]
    d = dedicacion[i]
    b = base_academica[i]
    
    # Lógica de distribución: [Insuficiente, Regular, Promocion]
    # ¡Probabilidades polarizadas para forzar el aprendizaje estadístico!
    if b == 'Alta' and d == 'Alto' and t == 'No':
        # El alumno ideal: 85% de chances de promocionar
        p_cond = [0.05, 0.10, 0.85]
    elif b == 'Media' and d == 'Bajo' and t == 'Si':
        # Alumno en riesgo crítico: 85% de chances de quedar libre
        p_cond = [0.85, 0.10, 0.05]
    elif b == 'Alta' and d == 'Alto' and t == 'Si':
        # Trabaja pero tiene base y dedicación: Fuerte tendencia a Regularizar o Promocionar
        p_cond = [0.10, 0.60, 0.30]
    elif b == 'Media' and d == 'Bajo' and t == 'No':
        # No trabaja, pero no estudia y le falta base: Mayoría libre o regular raspando
        p_cond = [0.60, 0.35, 0.05]
    elif b == 'Alta' and d == 'Bajo' and t == 'No':
        # Tiene facilidad pero no dedica tiempo
        p_cond = [0.20, 0.60, 0.20]
    elif b == 'Media' and d == 'Alto' and t == 'Si':
        # Se esfuerza mucho pero el trabajo lo limita
        p_cond = [0.25, 0.65, 0.10]
    elif b == 'Media' and d == 'Alto' and t == 'No':
        # Estudiante promedio esforzado
        p_cond = [0.15, 0.70, 0.15]
    else:
        # Alta, Bajo, Si -> Caso atípico, tendencia al centro
        p_cond = [0.40, 0.50, 0.10]
        
    condicion = np.random.choice(['Insuficiente', 'Regular', 'Promocion'], p=p_cond)
    condicion_final.append(condicion)

# 3. Construcción y Exportación para Entrenamiento
df_entrenamiento = pd.DataFrame({
    'Trabaja': trabaja,
    'Dedicacion': dedicacion,
    'Base_Academica': base_academica,
    'Condicion_Final': condicion_final
})

# Guardamos el CSV que leerá el BayesianEstimator
nombre_archivo = 'dataset_entrenamiento_lsi.csv'
df_entrenamiento.to_csv(nombre_archivo, index=False)

print(f"Dataset generado exitosamente para pgmpy: '{nombre_archivo}'")
print("\nDistribución de la Condición Final:")
print(df_entrenamiento['Condicion_Final'].value_counts(normalize=True) * 100)