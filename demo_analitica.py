"""Demo de analítica Día 2: EDA + ML + gráficos.

Ejecuta el pipeline completo de análisis y guarda en `docs/figuras/` todas las
visualizaciones que se usarán en el PDF final. También guarda en
`docs/metricas.json` las cifras numéricas de los modelos para citarlas
directamente en la memoria.

Ejecutar con:
    python demo_analitica.py
"""

from __future__ import annotations

import json
from pathlib import Path

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


RAIZ = Path(__file__).resolve().parent
RUTA_CSV = RAIZ / "data" / "estudiantes.csv"
CARPETA_FIGURAS = RAIZ / "docs" / "figuras"
RUTA_METRICAS = RAIZ / "docs" / "metricas.json"


def main() -> None:
    print("=" * 72)
    print("  DEMO DE ANALÍTICA — Learning Analytics seguro (Día 2)")
    print("=" * 72)
    CARPETA_FIGURAS.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # 1. Carga y exploración
    # ------------------------------------------------------------------
    df = cargar_csv(RUTA_CSV)
    print(f"\n[1] Dataset cargado: {len(df)} estudiantes, {len(df.columns)} columnas")

    print("\n    Distribución de la clase objetivo:")
    print(distribucion_riesgo(df).to_string())

    print("\n    Variables más correlacionadas con 'riesgo':")
    print(variables_mas_correlacionadas_con_riesgo(df, top=5).to_string(index=False))

    # ------------------------------------------------------------------
    # 2. Gráficos de exploración
    # ------------------------------------------------------------------
    print("\n[2] Generando gráficos de EDA...")
    guardar_figura(grafico_distribucion_riesgo(df), CARPETA_FIGURAS / "01_distribucion_riesgo.png")
    guardar_figura(grafico_distribucion_notas(df), CARPETA_FIGURAS / "02_distribucion_notas.png")
    guardar_figura(
        grafico_matriz_correlacion(matriz_correlacion(df)),
        CARPETA_FIGURAS / "03_matriz_correlacion.png",
    )
    print("    - 01_distribucion_riesgo.png")
    print("    - 02_distribucion_notas.png")
    print("    - 03_matriz_correlacion.png")

    # ------------------------------------------------------------------
    # 3. Preprocesamiento
    # ------------------------------------------------------------------
    X, y = separar_X_y(df)
    X_tr, X_te, y_tr, y_te = dividir_train_test(X, y, proporcion_test=0.25)
    X_tr_e, X_te_e, _ = escalar(X_tr, X_te)
    print(f"\n[3] Train/Test divididos: train={len(X_tr)}, test={len(X_te)}")

    # ------------------------------------------------------------------
    # 4. Entrenamiento y evaluación de modelos
    # ------------------------------------------------------------------
    print("\n[4] Entrenando modelos...")
    rl = evaluar(
        entrenar_regresion_logistica(X_tr_e, y_tr),
        X_te_e, y_te,
        "Regresión Logística",
    )
    rf = evaluar(
        entrenar_random_forest(X_tr_e, y_tr),
        X_te_e, y_te,
        "Random Forest",
    )
    comparativa = comparar_modelos([rl, rf])
    print("\n    Comparativa de modelos:")
    print(comparativa.to_string())

    # ------------------------------------------------------------------
    # 5. Gráficos de modelos
    # ------------------------------------------------------------------
    print("\n[5] Generando gráficos de modelos...")
    guardar_figura(
        grafico_matriz_confusion(rl.matriz_confusion, rl.nombre),
        CARPETA_FIGURAS / "04_matriz_confusion_rl.png",
    )
    guardar_figura(
        grafico_matriz_confusion(rf.matriz_confusion, rf.nombre),
        CARPETA_FIGURAS / "05_matriz_confusion_rf.png",
    )
    guardar_figura(
        grafico_curva_roc([rl, rf]),
        CARPETA_FIGURAS / "06_curva_roc.png",
    )
    guardar_figura(
        grafico_comparativa_metricas(comparativa),
        CARPETA_FIGURAS / "07_comparativa_metricas.png",
    )
    df_importancia = importancia_variables(rf.modelo, list(X_tr_e.columns))
    guardar_figura(
        grafico_importancia_variables(df_importancia),
        CARPETA_FIGURAS / "08_importancia_variables.png",
    )
    print("    - 04_matriz_confusion_rl.png")
    print("    - 05_matriz_confusion_rf.png")
    print("    - 06_curva_roc.png")
    print("    - 07_comparativa_metricas.png")
    print("    - 08_importancia_variables.png")

    # ------------------------------------------------------------------
    # 6. Top 10 alumnos en riesgo (para el dashboard)
    # ------------------------------------------------------------------
    df_test = df.loc[X_te.index]
    predicciones = predecir_estudiantes_riesgo(
        rf.modelo,
        X_te_e,
        df_test["id_estudiante"].tolist(),
    )
    top10 = predicciones.head(10)
    print(f"\n[6] Top 10 estudiantes con mayor probabilidad de riesgo (Random Forest):")
    print(top10.to_string(index=False))

    # ------------------------------------------------------------------
    # 7. Guardar métricas para citar en el PDF
    # ------------------------------------------------------------------
    metricas = {
        "n_estudiantes": len(df),
        "n_train": len(X_tr),
        "n_test": len(X_te),
        "distribucion_riesgo": distribucion_riesgo(df).to_dict(),
        "modelos": [rl.como_diccionario(), rf.como_diccionario()],
        "top10_riesgo": top10.to_dict(orient="records"),
        "importancia_variables": df_importancia.to_dict(orient="records"),
    }
    RUTA_METRICAS.write_text(
        json.dumps(metricas, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\n[7] Métricas guardadas en {RUTA_METRICAS.relative_to(RAIZ)}")

    print("\n" + "=" * 72)
    print(f"  Demo Día 2 completada. {8} figuras generadas en docs/figuras/")
    print("=" * 72)


if __name__ == "__main__":
    main()
