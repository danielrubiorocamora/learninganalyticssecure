"""Análisis exploratorio del dataset educativo.

Funciones para resumir el dataset:
    - Estadísticas descriptivas por variable.
    - Distribución de la clase objetivo (riesgo).
    - Matriz de correlación entre variables numéricas.
    - Identificación de variables más correlacionadas con el riesgo.
"""

from __future__ import annotations

import pandas as pd


def resumen_estadistico(df: pd.DataFrame) -> pd.DataFrame:
    """Estadísticas descriptivas (count, mean, std, min, percentiles, max)."""
    return df.describe().round(2)


def distribucion_riesgo(df: pd.DataFrame) -> pd.DataFrame:
    """Conteos y porcentajes de la clase objetivo."""
    conteos = df["riesgo"].value_counts().sort_index()
    porcentajes = (conteos / len(df) * 100).round(2)
    return pd.DataFrame({
        "n_estudiantes": conteos,
        "porcentaje": porcentajes,
    }).rename(index={0: "Sin riesgo", 1: "En riesgo"})


def matriz_correlacion(df: pd.DataFrame, columnas_excluir: list[str] | None = None) -> pd.DataFrame:
    """Matriz de correlación de Pearson entre variables numéricas."""
    excluir = columnas_excluir or ["id_estudiante", "nombre", "email"]
    df_num = df.drop(columns=[c for c in excluir if c in df.columns], errors="ignore")
    df_num = df_num.select_dtypes(include="number")
    return df_num.corr().round(3)


def variables_mas_correlacionadas_con_riesgo(df: pd.DataFrame, top: int = 5) -> pd.DataFrame:
    """Devuelve las variables más correlacionadas (en valor absoluto) con `riesgo`."""
    corr = matriz_correlacion(df)
    if "riesgo" not in corr.columns:
        raise ValueError("La columna 'riesgo' no está en la matriz de correlación.")
    fila = corr["riesgo"].drop("riesgo")
    fila_abs = fila.abs().sort_values(ascending=False)
    return pd.DataFrame({
        "variable": fila_abs.index[:top],
        "correlacion_con_riesgo": fila.loc[fila_abs.index[:top]].round(3).values,
    })
