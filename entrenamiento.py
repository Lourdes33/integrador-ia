import pandas as pd
from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.estimators import BayesianEstimator
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import warnings

# Suprimir warnings de pgmpy para una salida más limpia en consola
warnings.filterwarnings("ignore")

# 1. Cargar el dataset completo
df = pd.read_csv('dataset_entrenamiento_lsi.csv')

# 2. Dividir en Entrenamiento (80%) y Prueba (20%)
df_train, df_test = train_test_split(df, test_size=0.2, random_state=42)

print("🎓 INICIANDO EVALUACIÓN DEL MODELO BAYESIANO (CRISP-DM: Fase 5)")
print("-" * 60)
print(f"Total de registros históricos: {len(df)}")
print(f"Registros para entrenamiento (Aprender): {len(df_train)}")
print(f"Registros para prueba (Evaluar): {len(df_test)}\n")

# 3. Construir la estructura de la red
estructura = [
    ('Trabaja', 'Condicion_Final'), 
    ('Dedicacion', 'Condicion_Final'),
    ('Base_Academica', 'Condicion_Final')
]
modelo = DiscreteBayesianNetwork(estructura)

# 4. Entrenar el modelo SÓLO con el 80% de los datos
estimador = BayesianEstimator(modelo, df_train)
cpds_aprendidos = estimador.get_parameters(prior_type="BDeu", equivalent_sample_size=10)
modelo.add_cpds(*cpds_aprendidos)

# 5. Preparar los datos de prueba (Ocultamos la columna objetivo)
X_test = df_test.drop(columns=['Condicion_Final'])
y_true = df_test['Condicion_Final'] # La verdad absoluta

# 6. Realizar predicciones
print("La IA está realizando predicciones sobre los casos de prueba...")
# El método predict toma las evidencias y devuelve la clase con mayor probabilidad
y_pred_df = modelo.predict(X_test)
y_pred = y_pred_df['Condicion_Final']

# 7. Calcular métricas de evaluación
accuracy = accuracy_score(y_true, y_pred)
etiquetas = ["Insuficiente", "Regular", "Promocion"]
matriz = confusion_matrix(y_true, y_pred, labels=etiquetas)

print(f"\n--- RESULTADOS DE LA EVALUACIÓN ---")
print(f"Precisión (Accuracy) Global: {accuracy * 100:.2f}%\n")

print("Matriz de Confusión:")
# Formateo amigable de la matriz usando pandas
df_matriz = pd.DataFrame(matriz, 
                         index=["Real: Insuf", "Real: Reg", "Real: Prom"], 
                         columns=["Pred: Insuf", "Pred: Reg", "Pred: Prom"])
print(df_matriz)

print("\n📄 Reporte de Clasificación Detallado:")
print(classification_report(y_true, y_pred, target_names=etiquetas))