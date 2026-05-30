"""Paquete analytics: EDA, preprocesamiento, modelo de riesgo."""

from analytics.eda import (
    distribucion_riesgo,
    matriz_correlacion,
    resumen_estadistico,
    variables_mas_correlacionadas_con_riesgo,
)
from analytics.modelo_riesgo import (
    ResultadoModelo,
    calcular_curva_roc,
    comparar_modelos,
    entrenar_random_forest,
    entrenar_regresion_logistica,
    evaluar,
    importancia_variables,
    predecir_estudiantes_riesgo,
)
from analytics.preprocesamiento import (
    COLUMNA_OBJETIVO,
    COLUMNAS_EXCLUIDAS,
    cargar_csv,
    dividir_train_test,
    escalar,
    separar_X_y,
)

__all__ = [
    # eda
    "resumen_estadistico",
    "distribucion_riesgo",
    "matriz_correlacion",
    "variables_mas_correlacionadas_con_riesgo",
    # preprocesamiento
    "cargar_csv",
    "separar_X_y",
    "dividir_train_test",
    "escalar",
    "COLUMNAS_EXCLUIDAS",
    "COLUMNA_OBJETIVO",
    # modelos
    "ResultadoModelo",
    "entrenar_regresion_logistica",
    "entrenar_random_forest",
    "evaluar",
    "comparar_modelos",
    "calcular_curva_roc",
    "importancia_variables",
    "predecir_estudiantes_riesgo",
]
