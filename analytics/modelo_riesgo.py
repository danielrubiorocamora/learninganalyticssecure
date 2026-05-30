"""Modelo de predicción de riesgo académico.

Implementa dos clasificadores comparables:
    - Regresión Logística: modelo lineal interpretable, baseline natural.
    - Random Forest: modelo de conjunto no lineal, suele mejorar la precisión.

Para cada modelo se calculan métricas de clasificación binaria:
    - Accuracy: proporción global de aciertos.
    - Precision: de los predichos como "en riesgo", cuántos lo eran realmente.
    - Recall: de los realmente en riesgo, cuántos detecta el modelo (CRÍTICO en
      detección de riesgo: un falso negativo significa NO detectar a un alumno
      que necesita ayuda).
    - F1: media armónica de precision y recall.
    - ROC-AUC: capacidad de discriminación independiente del umbral.

En este dominio (detectar alumnos en riesgo) preferimos modelos que prioricen
**recall** sobre precision: es preferible una falsa alarma a perder un alumno
en problemas.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)

from analytics.preprocesamiento import SEMILLA


@dataclass
class ResultadoModelo:
    """Métricas y artefactos de un modelo entrenado."""
    nombre: str
    modelo: object
    accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: float
    matriz_confusion: np.ndarray
    y_real: np.ndarray
    y_predicho: np.ndarray
    y_probabilidad: np.ndarray  # probabilidades de la clase positiva

    def como_diccionario(self) -> dict:
        """Versión serializable de las métricas (sin objetos numpy/sklearn)."""
        return {
            "nombre": self.nombre,
            "accuracy": round(self.accuracy, 4),
            "precision": round(self.precision, 4),
            "recall": round(self.recall, 4),
            "f1": round(self.f1, 4),
            "roc_auc": round(self.roc_auc, 4),
            "matriz_confusion": self.matriz_confusion.tolist(),
        }


def entrenar_regresion_logistica(X_train, y_train) -> LogisticRegression:
    """Entrena un modelo de regresión logística estándar."""
    modelo = LogisticRegression(
        random_state=SEMILLA,
        max_iter=1000,
        class_weight="balanced",  # compensa el desbalance de clases
    )
    modelo.fit(X_train, y_train)
    return modelo


def entrenar_random_forest(X_train, y_train) -> RandomForestClassifier:
    """Entrena un Random Forest con 100 árboles."""
    modelo = RandomForestClassifier(
        n_estimators=100,
        random_state=SEMILLA,
        class_weight="balanced",
        n_jobs=-1,  # usar todos los núcleos disponibles
    )
    modelo.fit(X_train, y_train)
    return modelo


def evaluar(modelo, X_test, y_test, nombre: str) -> ResultadoModelo:
    """Evalúa un modelo y devuelve sus métricas como `ResultadoModelo`."""
    y_predicho = modelo.predict(X_test)
    y_probabilidad = modelo.predict_proba(X_test)[:, 1]  # prob. clase positiva

    return ResultadoModelo(
        nombre=nombre,
        modelo=modelo,
        accuracy=accuracy_score(y_test, y_predicho),
        precision=precision_score(y_test, y_predicho, zero_division=0),
        recall=recall_score(y_test, y_predicho),
        f1=f1_score(y_test, y_predicho),
        roc_auc=roc_auc_score(y_test, y_probabilidad),
        matriz_confusion=confusion_matrix(y_test, y_predicho),
        y_real=np.asarray(y_test),
        y_predicho=y_predicho,
        y_probabilidad=y_probabilidad,
    )


def comparar_modelos(resultados: list[ResultadoModelo]) -> pd.DataFrame:
    """Tabla comparativa de métricas para incluir en el PDF."""
    filas = [
        {
            "Modelo": r.nombre,
            "Accuracy": round(r.accuracy, 4),
            "Precision": round(r.precision, 4),
            "Recall": round(r.recall, 4),
            "F1": round(r.f1, 4),
            "ROC-AUC": round(r.roc_auc, 4),
        }
        for r in resultados
    ]
    return pd.DataFrame(filas).set_index("Modelo")


def calcular_curva_roc(resultado: ResultadoModelo) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Calcula puntos (fpr, tpr, umbrales) para dibujar la curva ROC."""
    return roc_curve(resultado.y_real, resultado.y_probabilidad)


def importancia_variables(modelo: RandomForestClassifier, nombres_variables: list[str]) -> pd.DataFrame:
    """Devuelve las variables ordenadas por importancia (solo para Random Forest)."""
    if not hasattr(modelo, "feature_importances_"):
        raise TypeError("El modelo no expone feature_importances_.")
    df = pd.DataFrame({
        "variable": nombres_variables,
        "importancia": modelo.feature_importances_,
    })
    return df.sort_values("importancia", ascending=False).reset_index(drop=True)


def predecir_estudiantes_riesgo(modelo, X: pd.DataFrame, ids: list[str], umbral: float = 0.5) -> pd.DataFrame:
    """Aplica el modelo a un conjunto y devuelve los identificados como en riesgo.

    Útil para el dashboard: el docente ve la lista de alumnos a vigilar con su
    probabilidad asociada.
    """
    proba = modelo.predict_proba(X)[:, 1]
    df = pd.DataFrame({
        "id_estudiante": ids,
        "probabilidad_riesgo": proba.round(4),
        "prediccion": (proba >= umbral).astype(int),
    })
    return df.sort_values("probabilidad_riesgo", ascending=False).reset_index(drop=True)
