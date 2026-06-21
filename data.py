import pandas as pd
import numpy as np

np.random.seed(42)
num_alumnos = 1000

# 1. Variables de Entrada (Nodos Padre)
nivel_matematica = np.random.choice(['Alto', 'Medio', 'Bajo'], size=num_alumnos, p=[0.20, 0.50, 0.30])
situacion_laboral = np.random.choice(['Trabaja', 'No_Trabaja'], size=num_alumnos, p=[0.40, 0.60])

# El tiempo de estudio extra es fundamental y se ve afectado por el trabajo
horas_estudio_extra = []
for trab in situacion_laboral:
    if trab == 'Trabaja': # Si maneja sistemas internos o archivos en horario laboral, el tiempo libre baja
        horas = np.random.choice(['Alta', 'Media', 'Baja'], p=[0.10, 0.40, 0.50])
    else:
        horas = np.random.choice(['Alta', 'Media', 'Baja'], p=[0.40, 0.45, 0.15])
    horas_estudio_extra.append(horas)

# 2. Variables Intermedias (Rendimiento Académico)
estado_101 = [] # Algoritmos y Estructuras de Datos I
estado_103 = [] # Algoritmos y Estructuras de Datos II
estado_201 = [] # Paradigmas y Lenguajes
estado_carrera = []

for i in range(num_alumnos):
    h_extra = horas_estudio_extra[i]
    
    # --- Asignatura 101: Algoritmos I (Sin correlativas previas) ---
    if h_extra == 'Alta':
        p_101 = [0.70, 0.25, 0.05] # [Aprobada, Regular, Libre]
    elif h_extra == 'Media':
        p_101 = [0.40, 0.40, 0.20]
    else:
        p_101 = [0.10, 0.30, 0.60]
    
    alg_1 = np.random.choice(['Aprobada', 'Regular', 'Libre'], p=p_101)
    estado_101.append(alg_1)
    
    # --- Asignatura 103: Algoritmos II ---
    # Regla: Para cursar (Regular) requiere 101. Para rendir (Aprobada) requiere 101.
    if alg_1 == 'Libre':
        alg_2 = 'No_Cursada' # La correlatividad bloquea el avance
    else:
        # Si regularizó o aprobó 101, puede cursar 103. 
        # Pero si solo está Regular en 101, difícilmente apruebe 103 de una.
        if alg_1 == 'Aprobada' and h_extra in ['Alta', 'Media']:
            p_103 = [0.60, 0.30, 0.10]
        else:
            p_103 = [0.15, 0.50, 0.35]
        alg_2 = np.random.choice(['Aprobada', 'Regular', 'Libre'], p=p_103)
    estado_103.append(alg_2)

    # --- Asignatura 201: Paradigmas y Lenguajes ---
    # Regla: Para cursar Regular requiere 103. Para Aprobada requiere 101 y 103 Aprobadas.
    if alg_2 in ['Libre', 'No_Cursada']:
        paradigmas = 'No_Cursada'
    else:
        # Para aprobar Paradigmas, NECESITA tener 101 y 103 aprobadas previamente.
        if alg_1 == 'Aprobada' and alg_2 == 'Aprobada':
            if h_extra == 'Alta':
                p_201 = [0.65, 0.30, 0.05]
            else:
                p_201 = [0.40, 0.45, 0.15]
        else:
            # Si le falta aprobar 101 o 103, el tope máximo es quedar Regular en 201.
            p_201 = [0.0, 0.70, 0.30] 
        
        paradigmas = np.random.choice(['Aprobada', 'Regular', 'Libre'], p=p_201)
    estado_201.append(paradigmas)

    # --- Variable Objetivo Final (Éxito del tramo inicial) ---
    if paradigmas == 'Aprobada':
        estado_final = 'Exitoso'
    elif paradigmas == 'Regular' or alg_2 == 'Aprobada':
        estado_final = 'Retraso_Leve'
    elif alg_1 in ['Aprobada', 'Regular']:
        estado_final = 'Retraso_Grave'
    else:
        estado_final = 'Abandono'
        
    estado_carrera.append(estado_final)

# 3. Exportación
df = pd.DataFrame({
    'Situacion_Laboral': situacion_laboral,
    'Horas_Estudio_Extra': horas_estudio_extra,
    '101_Algoritmos_I': estado_101,
    '103_Algoritmos_II': estado_103,
    '201_Paradigmas': estado_201,
    'Estado_Tramo_Inicial': estado_carrera
})

df.to_csv('dataset_red_bayesiana_correlativas.csv', index=False)
print(f"Dataset generado. Distribución de estado final:\n{df['Estado_Tramo_Inicial'].value_counts()}")