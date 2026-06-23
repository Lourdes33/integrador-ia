import pandas as pd
from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.estimators import BayesianEstimator
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import warnings
from pgmpy.estimators import MaximumLikelihoodEstimator
import seaborn as sns
import matplotlib.pyplot as plt

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

# 4. Entrenar el modelo SÓLO con el 80% de los datos (Usando MLE)
estimador = MaximumLikelihoodEstimator(modelo, df_train)
modelo.add_cpds(*estimador.get_parameters())

# 5. Preparar los datos de prueba forzando el reseteo de índices
X_test = df_test.drop(columns=['Condicion_Final']).reset_index(drop=True)
y_true = df_test['Condicion_Final'].reset_index(drop=True).tolist() 

# 6. Realizar predicciones
print("La IA está realizando predicciones sobre los casos de prueba...")
y_pred_df = modelo.predict(X_test)
y_pred = y_pred_df['Condicion_Final'].tolist()

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


print("\n🎨 Generando y guardando el gráfico de la Matriz de Confusión...")

# 1. Configurar el tamaño y estilo de la figura
plt.figure(figsize=(8, 6))

# 2. Crear el mapa de calor usando la variable 'matriz' que ya calculó scikit-learn
ax = sns.heatmap(
    matriz, 
    annot=True,          # Muestra los números adentro de los cuadrados
    fmt='d',             # Formato entero (sin decimales)
    cmap='Blues',        # Paleta de colores académicos (azul)
    xticklabels=etiquetas, 
    yticklabels=etiquetas,
    cbar_kws={'label': 'Cantidad de Alumnos Predichos'}
)

# 3. Configuraciones visuales y de texto para el informe formal
plt.title('Matriz de Confusión - Red Bayesiana Optimizada (MLE)', fontsize=14, fontweight='bold', pad=15)
plt.ylabel('Condición Real (Dato Histórico)', fontsize=12, fontweight='bold')
plt.xlabel('Condición Predicha (Inferencia de la IA)', fontsize=12, fontweight='bold')

# 4. Ajustar los márgenes automáticamente
plt.tight_layout()

# 5. Guardar el gráfico en alta calidad (300 DPI es el estándar para impresión/PDF)
plt.savefig("matriz_confusion_optimizada.png", format="png", dpi=300)

print("¡Gráfico guardado exitosamente en tu carpeta como 'matriz_confusion_optimizada.png'!")

# 6. Mostrar la ventana emergente
plt.show()