"""Pruebas unitarias del módulo de analítica."""

from pathlib import Path

import pandas as pd
import pytest

from analytics import (
    cargar_csv,
    comparar_modelos,
    dividir_train_test,
    distribucion_riesgo,
    entrenar_random_forest,
    entrenar_regresion_logistica,
    escalar,
    evaluar,
    importancia_variables,
    matriz_correlacion,
    predecir_estudiantes_riesgo,
    resumen_estadistico,
    separar_X_y,
    variables_mas_correlacionadas_con_riesgo,
)
from data.generador_datos import generar_dataset


@pytest.fixture(scope="module")
def csv_temporal(tmp_path_factory):
    """Genera un CSV sintético una sola vez para todos los tests del módulo."""
    ruta = tmp_path_factory.mktemp("data") / "estudiantes_test.csv"
    generar_dataset(n_estudiantes=200, ruta_salida=ruta)
    return ruta


@pytest.fixture(scope="module")
def df(csv_temporal):
    return cargar_csv(csv_temporal)


# ---------------------------------------------------------------------------
# Preprocesamiento
# ---------------------------------------------------------------------------
class TestPreprocesamiento:
    def test_cargar_csv_no_existente_lanza_error(self):
        with pytest.raises(FileNotFoundError):
            cargar_csv(Path("/no/existe/jamas.csv"))

    def test_separar_X_y_excluye_identificadores(self, df):
        X, y = separar_X_y(df)
        for prohibida in ("id_estudiante", "nombre", "email", "riesgo"):
            assert prohibida not in X.columns
        assert y.name == "riesgo"
        assert len(X) == len(y)

    def test_dividir_train_test_estratificado(self, df):
        X, y = separar_X_y(df)
        X_tr, X_te, y_tr, y_te = dividir_train_test(X, y, proporcion_test=0.25)
        # Proporciones aproximadas:
        assert abs(len(X_te) / len(X) - 0.25) < 0.05
        # Estratificación: las proporciones de clase no deben divergir mucho.
        ratio_global = y.mean()
        assert abs(y_tr.mean() - ratio_global) < 0.05
        assert abs(y_te.mean() - ratio_global) < 0.05

    def test_escalar_produce_media_cero_y_std_uno_aprox(self, df):
        X, y = separar_X_y(df)
        X_tr, X_te, _, _ = dividir_train_test(X, y)
        X_tr_e, X_te_e, _ = escalar(X_tr, X_te)
        # En train, cada columna debe tener media ~ 0 y std ~ 1.
        for col in X_tr_e.columns:
            assert abs(X_tr_e[col].mean()) < 1e-6
            assert abs(X_tr_e[col].std() - 1.0) < 0.05


# ---------------------------------------------------------------------------
# EDA
# ---------------------------------------------------------------------------
class TestEDA:
    def test_resumen_devuelve_dataframe(self, df):
        resumen = resumen_estadistico(df)
        assert isinstance(resumen, pd.DataFrame)
        assert "media" in resumen.columns

    def test_distribucion_riesgo_porcentajes_suman_100(self, df):
        dist = distribucion_riesgo(df)
        assert abs(dist["porcentaje"].sum() - 100.0) < 0.01

    def test_matriz_correlacion_es_cuadrada(self, df):
        m = matriz_correlacion(df)
        assert m.shape[0] == m.shape[1]
        # Diagonal = 1 (corr de cada variable consigo misma)
        for c in m.columns:
            assert abs(m.loc[c, c] - 1.0) < 1e-9

    def test_top_variables_correlacionadas(self, df):
        top = variables_mas_correlacionadas_con_riesgo(df, top=3)
        assert len(top) == 3
        # Deben ser variables del dataset, no la propia 'riesgo'.
        assert "riesgo" not in top["variable"].values


# ---------------------------------------------------------------------------
# Modelos
# ---------------------------------------------------------------------------
class TestModelos:
    @pytest.fixture
    def datos_entrenados(self, df):
        X, y = separar_X_y(df)
        X_tr, X_te, y_tr, y_te = dividir_train_test(X, y)
        X_tr_e, X_te_e, _ = escalar(X_tr, X_te)
        return X_tr_e, X_te_e, y_tr, y_te

    def test_regresion_logistica_alcanza_minimo_de_calidad(self, datos_entrenados):
        X_tr, X_te, y_tr, y_te = datos_entrenados
        modelo = entrenar_regresion_logistica(X_tr, y_tr)
        resultado = evaluar(modelo, X_te, y_te, "Regresión Logística")
        # El dataset es muy aprendible; cualquier valor decente debería superar 0.7 en F1.
        assert resultado.f1 > 0.7
        assert resultado.recall > 0.7

    def test_random_forest_alcanza_minimo_de_calidad(self, datos_entrenados):
        X_tr, X_te, y_tr, y_te = datos_entrenados
        modelo = entrenar_random_forest(X_tr, y_tr)
        resultado = evaluar(modelo, X_te, y_te, "Random Forest")
        assert resultado.f1 > 0.7
        assert resultado.roc_auc > 0.85

    def test_comparativa_devuelve_dataframe_con_los_modelos(self, datos_entrenados):
        X_tr, X_te, y_tr, y_te = datos_entrenados
        rl = evaluar(entrenar_regresion_logistica(X_tr, y_tr), X_te, y_te, "RL")
        rf = evaluar(entrenar_random_forest(X_tr, y_tr), X_te, y_te, "RF")
        tabla = comparar_modelos([rl, rf])
        assert "RL" in tabla.index
        assert "RF" in tabla.index
        assert {"Accuracy", "F1", "ROC-AUC"}.issubset(tabla.columns)

    def test_importancia_variables_suma_uno(self, datos_entrenados):
        X_tr, X_te, y_tr, y_te = datos_entrenados
        modelo = entrenar_random_forest(X_tr, y_tr)
        df_imp = importancia_variables(modelo, list(X_tr.columns))
        assert abs(df_imp["importancia"].sum() - 1.0) < 1e-6

    def test_predecir_estudiantes_riesgo_devuelve_ordenado(self, datos_entrenados):
        X_tr, X_te, y_tr, _ = datos_entrenados
        modelo = entrenar_random_forest(X_tr, y_tr)
        ids = [f"EST-TEST-{i}" for i in range(len(X_te))]
        pred = predecir_estudiantes_riesgo(modelo, X_te, ids)
        # Las probabilidades deben venir en orden descendente.
        diferencias = pred["probabilidad_riesgo"].diff().dropna()
        assert (diferencias <= 1e-9).all()
