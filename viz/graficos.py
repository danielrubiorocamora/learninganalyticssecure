"""Visualizaciones para el PDF y el dashboard.

Paleta sobria profesional (azul oscuro / gris / blanco), tipografía serif para
los títulos de gráficos para mantener coherencia con el PDF.

Todas las funciones devuelven el objeto `Figure` de Matplotlib, lo que permite:
    - Guardarlo a fichero con `fig.savefig(...)`.
    - Embebebrlo en Streamlit con `st.pyplot(fig)`.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


# ---------------------------------------------------------------------------
# Paleta y estilo
# ---------------------------------------------------------------------------
AZUL_OSCURO = "#1f4e79"
AZUL_MEDIO = "#4a90c2"
AZUL_CLARO = "#a8c8e0"
GRIS = "#6c757d"
GRIS_CLARO = "#dee2e6"
ROJO = "#c0392b"      # solo para alertas (riesgo)
VERDE = "#2e7d32"     # solo para confirmaciones (sin riesgo)
BLANCO = "#ffffff"


def aplicar_estilo() -> None:
    """Aplica la configuración global de Matplotlib (paleta sobria académica)."""
    plt.rcParams.update({
        "font.family": "serif",
        "font.size": 10,
        "axes.titlesize": 12,
        "axes.titleweight": "bold",
        "axes.labelsize": 10,
        "axes.edgecolor": GRIS,
        "axes.linewidth": 0.8,
        "axes.grid": True,
        "grid.color": GRIS_CLARO,
        "grid.linewidth": 0.5,
        "grid.alpha": 0.7,
        "figure.facecolor": BLANCO,
        "axes.facecolor": BLANCO,
        "savefig.dpi": 150,
        "savefig.bbox": "tight",
    })


# ---------------------------------------------------------------------------
# Gráficos
# ---------------------------------------------------------------------------
def grafico_distribucion_riesgo(df: pd.DataFrame) -> plt.Figure:
    """Barras: cuántos estudiantes hay en cada clase."""
    aplicar_estilo()
    conteos = df["riesgo"].value_counts().sort_index()
    etiquetas = ["Sin riesgo", "En riesgo"]
    colores = [VERDE, ROJO]

    fig, ax = plt.subplots(figsize=(6, 4))
    barras = ax.bar(etiquetas, conteos, color=colores, edgecolor="white", linewidth=1.5)
    for barra, valor in zip(barras, conteos):
        ax.text(
            barra.get_x() + barra.get_width() / 2,
            barra.get_height() + 2,
            f"{valor}\n({valor/conteos.sum()*100:.1f}%)",
            ha="center",
            fontsize=10,
            color=GRIS,
        )
    ax.set_title("Distribución de la clase objetivo (riesgo académico)")
    ax.set_ylabel("Número de estudiantes")
    ax.set_ylim(0, conteos.max() * 1.2)
    return fig


def grafico_distribucion_notas(df: pd.DataFrame) -> plt.Figure:
    """Histograma de la nota media coloreado por riesgo."""
    aplicar_estilo()
    fig, ax = plt.subplots(figsize=(7, 4))

    sin = df.loc[df["riesgo"] == 0, "media"]
    con = df.loc[df["riesgo"] == 1, "media"]
    ax.hist(sin, bins=20, alpha=0.75, color=VERDE, edgecolor="white", label="Sin riesgo")
    ax.hist(con, bins=20, alpha=0.75, color=ROJO, edgecolor="white", label="En riesgo")
    ax.axvline(5.0, color=GRIS, linestyle="--", linewidth=1, label="Aprobado (5.0)")
    ax.set_title("Distribución de la nota media por estado de riesgo")
    ax.set_xlabel("Nota media (0–10)")
    ax.set_ylabel("Número de estudiantes")
    ax.legend(frameon=False)
    return fig


def grafico_matriz_correlacion(matriz: pd.DataFrame) -> plt.Figure:
    """Heatmap de la matriz de correlación con colormap divergente azul/blanco/rojo."""
    aplicar_estilo()
    fig, ax = plt.subplots(figsize=(9, 7))
    sns.heatmap(
        matriz,
        annot=True,
        fmt=".2f",
        cmap="RdBu_r",
        center=0,
        vmin=-1,
        vmax=1,
        cbar_kws={"shrink": 0.8, "label": "Correlación de Pearson"},
        linewidths=0.5,
        linecolor=BLANCO,
        ax=ax,
        annot_kws={"size": 8},
    )
    ax.set_title("Matriz de correlación de variables del dataset")
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
    return fig


def grafico_importancia_variables(df_importancia: pd.DataFrame) -> plt.Figure:
    """Barras horizontales con la importancia de cada variable según Random Forest."""
    aplicar_estilo()
    df = df_importancia.iloc[::-1]  # invertimos para que la más importante quede arriba
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.barh(df["variable"], df["importancia"], color=AZUL_OSCURO, edgecolor="white")
    ax.set_title("Importancia de variables (Random Forest)")
    ax.set_xlabel("Importancia")
    ax.grid(axis="x", linestyle="--", alpha=0.5)
    ax.grid(axis="y", visible=False)
    return fig


def grafico_matriz_confusion(matriz: np.ndarray, nombre_modelo: str) -> plt.Figure:
    """Heatmap 2x2 de la matriz de confusión del modelo."""
    aplicar_estilo()
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.heatmap(
        matriz,
        annot=True,
        fmt="d",
        cmap="Blues",
        cbar=False,
        linewidths=0.8,
        linecolor=BLANCO,
        xticklabels=["Sin riesgo", "En riesgo"],
        yticklabels=["Sin riesgo", "En riesgo"],
        ax=ax,
        annot_kws={"size": 14, "weight": "bold"},
    )
    ax.set_title(f"Matriz de confusión — {nombre_modelo}")
    ax.set_xlabel("Predicción")
    ax.set_ylabel("Valor real")
    return fig


def grafico_curva_roc(resultados: list) -> plt.Figure:
    """Curva ROC superpuesta para todos los modelos comparados."""
    from analytics.modelo_riesgo import calcular_curva_roc

    aplicar_estilo()
    fig, ax = plt.subplots(figsize=(6, 5))
    colores = [AZUL_OSCURO, ROJO]
    for resultado, color in zip(resultados, colores):
        fpr, tpr, _ = calcular_curva_roc(resultado)
        ax.plot(
            fpr,
            tpr,
            color=color,
            linewidth=2,
            label=f"{resultado.nombre} (AUC = {resultado.roc_auc:.3f})",
        )
    ax.plot([0, 1], [0, 1], color=GRIS, linestyle="--", linewidth=1, label="Aleatorio")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.02)
    ax.set_title("Curva ROC — comparación de modelos")
    ax.set_xlabel("Tasa de falsos positivos")
    ax.set_ylabel("Tasa de verdaderos positivos")
    ax.legend(loc="lower right", frameon=False)
    return fig


def grafico_comparativa_metricas(df_comparativa: pd.DataFrame) -> plt.Figure:
    """Barras agrupadas con las métricas de cada modelo."""
    aplicar_estilo()
    fig, ax = plt.subplots(figsize=(8, 5))
    df_comparativa.plot(
        kind="bar",
        ax=ax,
        color=[AZUL_OSCURO, AZUL_MEDIO, AZUL_CLARO, GRIS, ROJO],
        edgecolor="white",
        width=0.8,
    )
    ax.set_title("Comparativa de métricas por modelo")
    ax.set_ylabel("Puntuación (0–1)")
    ax.set_xlabel("")
    ax.set_ylim(0, 1.05)
    plt.xticks(rotation=0)
    ax.legend(loc="lower right", frameon=False, ncol=5, fontsize=9)
    return fig


def guardar_figura(fig: plt.Figure, ruta: str | Path) -> Path:
    """Guarda la figura en disco y devuelve la ruta resultante."""
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(ruta)
    plt.close(fig)
    return ruta
