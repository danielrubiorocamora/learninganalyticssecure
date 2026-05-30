"""Pruebas unitarias del módulo de visualización.

Las pruebas verifican que las funciones devuelven objetos `Figure` válidos y que
las figuras se pueden guardar a fichero sin error. No comprobamos los píxeles
porque el contenido visual no es testeable de forma robusta.
"""

import tempfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # backend sin GUI (necesario en entornos sin display)

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest

from analytics import (
    dividir_train_test,
    entrenar_random_forest,
    entrenar_regresion_logistica,
    escalar,
    evaluar,
    importancia_variables,
    matriz_correlacion,
    separar_X_y,
)
from data.generador_datos import generar_dataset
from viz import (
    grafico_comparativa_metricas,
    grafico_curva_roc,
    grafico_distribucion_notas,
    grafico_distribucion_riesgo,
    grafico_importancia_variables,
    grafico_matriz_confusion,
    grafico_matriz_correlacion,
    guardar_figura,
)


@pytest.fixture(scope="module")
def df():
    return pd.DataFrame(generar_dataset(n_estudiantes=150))


@pytest.fixture(scope="module")
def resultados_modelos(df):
    X, y = separar_X_y(df)
    X_tr, X_te, y_tr, y_te = dividir_train_test(X, y)
    X_tr_e, X_te_e, _ = escalar(X_tr, X_te)
    rl = evaluar(entrenar_regresion_logistica(X_tr_e, y_tr), X_te_e, y_te, "Regresión Logística")
    rf = evaluar(entrenar_random_forest(X_tr_e, y_tr), X_te_e, y_te, "Random Forest")
    return rl, rf


class TestGraficos:
    def test_distribucion_riesgo(self, df):
        fig = grafico_distribucion_riesgo(df)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_distribucion_notas(self, df):
        fig = grafico_distribucion_notas(df)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_matriz_correlacion(self, df):
        m = matriz_correlacion(df)
        fig = grafico_matriz_correlacion(m)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_importancia_variables(self, df, resultados_modelos):
        _, rf = resultados_modelos
        X, _ = separar_X_y(df)
        # Reentrenamos con escalado equivalente para el test
        df_imp = importancia_variables(rf.modelo, list(X.columns))
        fig = grafico_importancia_variables(df_imp)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_matriz_confusion(self, resultados_modelos):
        _, rf = resultados_modelos
        fig = grafico_matriz_confusion(rf.matriz_confusion, rf.nombre)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_curva_roc(self, resultados_modelos):
        fig = grafico_curva_roc(list(resultados_modelos))
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_comparativa_metricas(self, resultados_modelos):
        from analytics import comparar_modelos
        df_comp = comparar_modelos(list(resultados_modelos))
        fig = grafico_comparativa_metricas(df_comp)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_guardar_figura_escribe_fichero(self, df):
        fig = grafico_distribucion_riesgo(df)
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "test.png"
            ruta_guardada = guardar_figura(fig, ruta)
            assert ruta_guardada.exists()
            assert ruta_guardada.stat().st_size > 1000  # debe ser un PNG razonable
