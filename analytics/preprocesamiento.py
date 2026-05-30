"""Preprocesamiento del dataset educativo para el modelo de ML.

Funciones para:
    - Cargar el CSV en un DataFrame de Pandas.
    - Seleccionar variables predictoras (X) y objetivo (y).
    - Separar en train/test de forma estratificada (mantener proporción de clases).
    - Escalar características numéricas con StandardScaler.

Decisión de diseño: las variables identificadoras (id_estudiante, nombre, email) NO
entran al modelo. El nombre además se considera sensible y se cifra antes de cualquier
operación analítica.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


# Columnas que NO entran al modelo (identificadores y campos sensibles).
COLUMNAS_EXCLUIDAS = ["id_estudiante", "nombre", "email"]

# Columna objetivo: variable binaria de riesgo académico.
COLUMNA_OBJETIVO = "riesgo"

SEMILLA = 42


def cargar_csv(ruta: str | Path) -> pd.DataFrame:
    """Carga el CSV de estudiantes y verifica que tenga las columnas esperadas."""
    ruta = Path(ruta)
    if not ruta.exists():
        raise FileNotFoundError(f"No se encuentra el CSV en {ruta}. Genera el dataset primero.")
    df = pd.read_csv(ruta)
    if COLUMNA_OBJETIVO not in df.columns:
        raise ValueError(f"El CSV no contiene la columna objetivo '{COLUMNA_OBJETIVO}'.")
    return df


def separar_X_y(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Devuelve (X, y) listas para entrenar.

    X contiene las variables numéricas predictoras.
    y es el vector binario de riesgo (0 = sin riesgo, 1 = en riesgo).
    """
    columnas_a_descartar = [c for c in COLUMNAS_EXCLUIDAS if c in df.columns]
    X = df.drop(columns=columnas_a_descartar + [COLUMNA_OBJETIVO])
    y = df[COLUMNA_OBJETIVO]
    return X, y


def dividir_train_test(
    X: pd.DataFrame,
    y: pd.Series,
    proporcion_test: float = 0.25,
    semilla: int = SEMILLA,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Divide en train/test de forma estratificada (mantiene la proporción de clases)."""
    return train_test_split(
        X,
        y,
        test_size=proporcion_test,
        random_state=semilla,
        stratify=y,  # importante: mantiene el ratio de clases en train y test
    )


def escalar(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, StandardScaler]:
    """Aplica StandardScaler (z-score) a las características.

    El escalador se ajusta SOLO con los datos de entrenamiento y luego se aplica
    a test. Esto evita la fuga de información (data leakage) del test al modelo.
    """
    escalador = StandardScaler()
    X_train_escalado = pd.DataFrame(
        escalador.fit_transform(X_train),
        columns=X_train.columns,
        index=X_train.index,
    )
    X_test_escalado = pd.DataFrame(
        escalador.transform(X_test),
        columns=X_test.columns,
        index=X_test.index,
    )
    return X_train_escalado, X_test_escalado, escalador
