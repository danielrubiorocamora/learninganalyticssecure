"""Mediciones de rendimiento del sistema.

Mide y guarda en JSON los tiempos de las operaciones más importantes:
    - Cifrado / descifrado AES (Fernet) de un campo.
    - Generación de par de claves RSA-2048.
    - Firma y verificación RSA-PSS.
    - Minería de un bloque a dificultades 2, 3 y 4.
    - Predicción del modelo de riesgo (lote completo de test).

Los resultados se guardan en `docs/seguridad/benchmarks.json` y se usan en
la sección de justificación técnica del PDF.
"""

from __future__ import annotations

import json
import statistics
import time
from pathlib import Path

import pandas as pd

from analytics import (
    cargar_csv,
    dividir_train_test,
    entrenar_random_forest,
    escalar,
    separar_X_y,
)
from blockchain_module import Cadena
from crypto_module import (
    cifrar,
    descifrar,
    firmar,
    generar_clave_aleatoria,
    generar_par_de_claves,
    verificar,
)


RAIZ = Path(__file__).resolve().parent
RUTA_RESULTADOS = RAIZ / "docs" / "seguridad" / "benchmarks.json"
RUTA_RESULTADOS.parent.mkdir(parents=True, exist_ok=True)


def medir(funcion, repeticiones: int = 100) -> dict[str, float]:
    """Ejecuta una función N veces y devuelve estadísticas en milisegundos."""
    tiempos = []
    for _ in range(repeticiones):
        t0 = time.perf_counter()
        funcion()
        tiempos.append((time.perf_counter() - t0) * 1000)
    return {
        "media_ms": round(statistics.mean(tiempos), 4),
        "mediana_ms": round(statistics.median(tiempos), 4),
        "min_ms": round(min(tiempos), 4),
        "max_ms": round(max(tiempos), 4),
        "stdev_ms": round(statistics.stdev(tiempos), 4) if len(tiempos) > 1 else 0.0,
        "n_repeticiones": repeticiones,
    }


def main() -> None:
    resultados: dict = {}

    print("=" * 72)
    print("  BENCHMARKS — Learning Analytics seguro")
    print("=" * 72)

    # ------------------------------------------------------------------
    # 1. AES (Fernet)
    # ------------------------------------------------------------------
    print("\n[1] AES (Fernet) — cifrado/descifrado")
    clave_aes = generar_clave_aleatoria()
    texto = "Daniel Rubio Rocamora · alumno0001@euniv.edu · calificación 9.5"
    cifrado_inicial = cifrar(texto, clave_aes)
    resultados["aes_cifrar_un_campo"] = medir(lambda: cifrar(texto, clave_aes), 1000)
    resultados["aes_descifrar_un_campo"] = medir(lambda: descifrar(cifrado_inicial, clave_aes), 1000)
    print(f"    Cifrar:    {resultados['aes_cifrar_un_campo']['media_ms']:.4f} ms")
    print(f"    Descifrar: {resultados['aes_descifrar_un_campo']['media_ms']:.4f} ms")

    # ------------------------------------------------------------------
    # 2. RSA-2048
    # ------------------------------------------------------------------
    print("\n[2] RSA-2048 — generación, firma y verificación")
    resultados["rsa_generacion_par_claves"] = medir(lambda: generar_par_de_claves(), 10)
    priv, pub = generar_par_de_claves()
    mensaje = b"Operacion firmada por el docente"
    firma_inicial = firmar(mensaje, priv)
    resultados["rsa_firma"] = medir(lambda: firmar(mensaje, priv), 100)
    resultados["rsa_verificacion"] = medir(lambda: verificar(firma_inicial, mensaje, pub), 100)
    print(f"    Generar par claves: {resultados['rsa_generacion_par_claves']['media_ms']:.2f} ms")
    print(f"    Firmar:             {resultados['rsa_firma']['media_ms']:.4f} ms")
    print(f"    Verificar:          {resultados['rsa_verificacion']['media_ms']:.4f} ms")

    # ------------------------------------------------------------------
    # 3. Minería de bloques a diferentes dificultades
    # ------------------------------------------------------------------
    print("\n[3] Proof-of-Work — minería por dificultad")
    for dif in (2, 3, 4):
        tiempos_dif = []
        for _ in range(5):
            cadena = Cadena(dificultad=dif)
            t0 = time.perf_counter()
            cadena.anadir_bloque([{"prueba": f"transaccion_{i}"} for i in range(3)])
            tiempos_dif.append((time.perf_counter() - t0) * 1000)
        resultados[f"pow_dificultad_{dif}"] = {
            "media_ms": round(statistics.mean(tiempos_dif), 2),
            "min_ms": round(min(tiempos_dif), 2),
            "max_ms": round(max(tiempos_dif), 2),
            "n_repeticiones": len(tiempos_dif),
        }
        print(f"    Dificultad {dif}: {resultados[f'pow_dificultad_{dif}']['media_ms']:.2f} ms (media)")

    # ------------------------------------------------------------------
    # 4. Predicción ML
    # ------------------------------------------------------------------
    print("\n[4] Modelo Random Forest — predicción sobre lote completo")
    df = cargar_csv(RAIZ / "data" / "estudiantes.csv")
    X, y = separar_X_y(df)
    X_tr, X_te, y_tr, y_te = dividir_train_test(X, y)
    X_tr_e, X_te_e, _ = escalar(X_tr, X_te)
    modelo = entrenar_random_forest(X_tr_e, y_tr)
    resultados["ml_prediccion_lote_test"] = medir(lambda: modelo.predict_proba(X_te_e), 100)
    resultados["ml_prediccion_un_estudiante"] = medir(
        lambda: modelo.predict_proba(X_te_e.iloc[[0]]),
        100,
    )
    print(f"    Predicción lote (75 estudiantes): {resultados['ml_prediccion_lote_test']['media_ms']:.4f} ms")
    print(f"    Predicción 1 estudiante:          {resultados['ml_prediccion_un_estudiante']['media_ms']:.4f} ms")

    # ------------------------------------------------------------------
    # 5. Persistencia
    # ------------------------------------------------------------------
    RUTA_RESULTADOS.write_text(
        json.dumps(resultados, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\nResultados guardados en {RUTA_RESULTADOS.relative_to(RAIZ)}")

    # ------------------------------------------------------------------
    # 6. Resumen en formato tabla para el PDF
    # ------------------------------------------------------------------
    print("\n" + "=" * 72)
    print("  TABLA RESUMEN (citable en el PDF)")
    print("=" * 72)
    print(f"\n{'Operación':<45} {'Tiempo medio':>15}")
    print("-" * 60)
    print(f"{'Cifrado AES de un campo':<45} {resultados['aes_cifrar_un_campo']['media_ms']:>10.4f} ms")
    print(f"{'Descifrado AES de un campo':<45} {resultados['aes_descifrar_un_campo']['media_ms']:>10.4f} ms")
    print(f"{'Generación par claves RSA-2048':<45} {resultados['rsa_generacion_par_claves']['media_ms']:>10.2f} ms")
    print(f"{'Firma RSA-PSS-SHA256':<45} {resultados['rsa_firma']['media_ms']:>10.4f} ms")
    print(f"{'Verificación de firma RSA-PSS':<45} {resultados['rsa_verificacion']['media_ms']:>10.4f} ms")
    print(f"{'Minería PoW dificultad 2':<45} {resultados['pow_dificultad_2']['media_ms']:>10.2f} ms")
    print(f"{'Minería PoW dificultad 3':<45} {resultados['pow_dificultad_3']['media_ms']:>10.2f} ms")
    print(f"{'Minería PoW dificultad 4':<45} {resultados['pow_dificultad_4']['media_ms']:>10.2f} ms")
    print(f"{'Predicción ML lote (75 estudiantes)':<45} {resultados['ml_prediccion_lote_test']['media_ms']:>10.4f} ms")
    print(f"{'Predicción ML un estudiante':<45} {resultados['ml_prediccion_un_estudiante']['media_ms']:>10.4f} ms")


if __name__ == "__main__":
    main()
