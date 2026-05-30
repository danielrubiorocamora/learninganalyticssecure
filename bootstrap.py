"""Inicialización del sistema: usuarios demo, dataset, modelo y cadena.

Ejecutar UNA vez antes de lanzar el dashboard:
    python bootstrap.py

Este script:
    1. Genera el dataset sintético de estudiantes (si no existe).
    2. Crea los usuarios demo (admin, dos docentes, varios estudiantes).
    3. Entrena el modelo de Random Forest y lo persiste en disco.
    4. Crea la cadena de bloques con el bloque génesis.

Después de ejecutar este script, ya puedes lanzar el dashboard:
    streamlit run app/dashboard.py

USUARIOS DEMO CREADOS:
    admin / Admin1234!                  → administrador
    profesor.moya / Profesor1234!       → docente
    profesor.garcia / Profesor1234!     → docente
    EST-0001 / Estudiante1!             → estudiante
    EST-0042 / Estudiante1!             → estudiante
    EST-0100 / Estudiante1!             → estudiante
    EST-0128 / Estudiante1!             → estudiante  (alto riesgo)
    EST-0210 / Estudiante1!             → estudiante  (alto riesgo)
"""

from __future__ import annotations

import pickle
from pathlib import Path

from analytics import (
    cargar_csv,
    dividir_train_test,
    entrenar_random_forest,
    escalar,
    separar_X_y,
)
from app.operaciones import RUTA_CADENA, cargar_o_crear_cadena
from app.usuarios import bootstrap_usuarios_demo
from data.generador_datos import generar_dataset


RAIZ = Path(__file__).resolve().parent
RUTA_CSV = RAIZ / "data" / "estudiantes.csv"
RUTA_MODELO = RAIZ / "data" / "modelo_riesgo.pkl"
RUTA_ESCALADOR = RAIZ / "data" / "escalador.pkl"


def main() -> None:
    print("=" * 72)
    print("  Bootstrap del sistema — Learning Analytics seguro")
    print("=" * 72)

    # ------------------------------------------------------------------
    # 1. Dataset
    # ------------------------------------------------------------------
    if RUTA_CSV.exists():
        print(f"\n[1] Dataset ya existe en {RUTA_CSV.name}, se reutiliza.")
    else:
        print(f"\n[1] Generando dataset sintético en {RUTA_CSV.name}...")
        generar_dataset(n_estudiantes=300, ruta_salida=RUTA_CSV)
    df = cargar_csv(RUTA_CSV)
    print(f"    {len(df)} estudiantes cargados.")

    # ------------------------------------------------------------------
    # 2. Usuarios demo
    # ------------------------------------------------------------------
    print(f"\n[2] Creando/cargando usuarios demo...")
    usuarios = bootstrap_usuarios_demo(sobrescribir=True)
    print(f"    {len(usuarios)} usuarios listos:")
    for nombre, u in usuarios.items():
        sufijo = f" (vinculado a {u.id_estudiante})" if u.id_estudiante else ""
        print(f"      - {nombre:<20} [{u.rol}]{sufijo}")

    # ------------------------------------------------------------------
    # 3. Modelo ML entrenado
    # ------------------------------------------------------------------
    print(f"\n[3] Entrenando modelo Random Forest...")
    X, y = separar_X_y(df)
    X_tr, X_te, y_tr, y_te = dividir_train_test(X, y)
    X_tr_e, X_te_e, escalador = escalar(X_tr, X_te)
    modelo = entrenar_random_forest(X_tr_e, y_tr)
    with open(RUTA_MODELO, "wb") as f:
        pickle.dump(modelo, f)
    with open(RUTA_ESCALADOR, "wb") as f:
        pickle.dump(escalador, f)
    print(f"    Modelo guardado en {RUTA_MODELO.name}.")
    print(f"    Escalador guardado en {RUTA_ESCALADOR.name}.")

    # ------------------------------------------------------------------
    # 4. Cadena de bloques
    # ------------------------------------------------------------------
    print(f"\n[4] Inicializando cadena de bloques...")
    if RUTA_CADENA.exists():
        RUTA_CADENA.unlink()
    cadena = cargar_o_crear_cadena(dificultad=3)
    print(f"    Cadena creada con bloque génesis (hash: {cadena.bloques[0].hash_actual[:16]}...).")

    print("\n" + "=" * 72)
    print("  Bootstrap completado. Lanza el dashboard con:")
    print("      streamlit run app/dashboard.py")
    print("=" * 72)


if __name__ == "__main__":
    main()
