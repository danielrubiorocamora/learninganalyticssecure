"""Paquete viz: visualizaciones con estética sobria académica."""

from viz.graficos import (
    aplicar_estilo,
    grafico_comparativa_metricas,
    grafico_curva_roc,
    grafico_distribucion_notas,
    grafico_distribucion_riesgo,
    grafico_importancia_variables,
    grafico_matriz_confusion,
    grafico_matriz_correlacion,
    guardar_figura,
)

__all__ = [
    "aplicar_estilo",
    "grafico_distribucion_riesgo",
    "grafico_distribucion_notas",
    "grafico_matriz_correlacion",
    "grafico_importancia_variables",
    "grafico_matriz_confusion",
    "grafico_curva_roc",
    "grafico_comparativa_metricas",
    "guardar_figura",
]
