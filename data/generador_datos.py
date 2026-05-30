"""Generador de un dataset sintético de estudiantes.

Genera un CSV con las características típicas de un sistema educativo:
identificador, nombre real, email, calificaciones de varias asignaturas,
porcentajes de asistencia, participación, entregas tardías y un campo derivado
`riesgo` que indica si el estudiante está en riesgo académico.

Se usa la librería `Faker` con locale `es_ES` para generar nombres y correos
realistas en español. Los datos son **completamente sintéticos**: no se utiliza
ningún dato real de personas, lo que cumple por diseño con GDPR.
"""

from __future__ import annotations

import csv
import random
from pathlib import Path

import numpy as np
from faker import Faker


# Reproducibilidad
SEMILLA = 42
random.seed(SEMILLA)
np.random.seed(SEMILLA)
faker = Faker("es_ES")
Faker.seed(SEMILLA)


ASIGNATURAS = [
    "matematicas",
    "lengua",
    "ingles",
    "ciencias",
    "historia",
]


def _calificacion(media: float, desviacion: float = 1.8) -> float:
    """Genera una nota entre 0 y 10 con una distribución normal acotada."""
    nota = np.random.normal(media, desviacion)
    return float(np.clip(round(nota, 2), 0.0, 10.0))


def _calcular_riesgo(media: float, asistencia: float, participacion: float, tardias: int) -> int:
    """Devuelve 1 si el estudiante está en riesgo, 0 en caso contrario.

    La lógica refleja patrones realistas pero sigue siendo determinista para que
    el modelo de ML tenga señal aprendible.
    """
    puntuacion = 0
    if media < 5.0:
        puntuacion += 2
    elif media < 6.0:
        puntuacion += 1
    if asistencia < 75:
        puntuacion += 2
    elif asistencia < 85:
        puntuacion += 1
    if participacion < 40:
        puntuacion += 1
    if tardias >= 5:
        puntuacion += 1
    return 1 if puntuacion >= 3 else 0


def generar_dataset(n_estudiantes: int = 300, ruta_salida: str | Path | None = None) -> list[dict]:
    """Genera la lista de estudiantes y opcionalmente la guarda en CSV."""
    if n_estudiantes < 50:
        raise ValueError("Para que el modelo ML tenga sentido se recomiendan >= 50 estudiantes.")

    registros = []
    for i in range(1, n_estudiantes + 1):
        # Tres perfiles: alto rendimiento (30%), medio (50%), bajo (20%).
        # nosec B311 - random.choices se usa solo para generar datos sintéticos,
        # nunca para fines criptográficos (claves, sales y nonces usan os.urandom).
        perfil = random.choices(  # nosec B311
            population=["alto", "medio", "bajo"],
            weights=[0.30, 0.50, 0.20],
            k=1,
        )[0]
        if perfil == "alto":
            base = 8.0
        elif perfil == "medio":
            base = 6.3
        else:
            base = 4.2

        calificaciones = {asig: _calificacion(base) for asig in ASIGNATURAS}
        media = round(sum(calificaciones.values()) / len(calificaciones), 2)
        asistencia = float(np.clip(np.random.normal(85 if perfil != "bajo" else 70, 10), 30, 100))
        participacion = float(np.clip(np.random.normal(70 if perfil != "bajo" else 40, 18), 0, 100))
        tardias = int(np.clip(np.random.poisson(2 if perfil != "bajo" else 5), 0, 20))
        horas_estudio_semanal = float(np.clip(np.random.normal(10 if perfil != "bajo" else 4, 3), 0, 30))

        nombre = faker.name()
        email = f"alumno{i:04d}@euniv.edu"
        registro = {
            "id_estudiante": f"EST-{i:04d}",
            "nombre": nombre,
            "email": email,
            **{f"nota_{asig}": calificaciones[asig] for asig in ASIGNATURAS},
            "media": media,
            "asistencia_pct": round(asistencia, 2),
            "participacion_pct": round(participacion, 2),
            "entregas_tardias": tardias,
            "horas_estudio_semanal": round(horas_estudio_semanal, 1),
            "riesgo": _calcular_riesgo(media, asistencia, participacion, tardias),
        }
        registros.append(registro)

    if ruta_salida is not None:
        ruta_salida = Path(ruta_salida)
        ruta_salida.parent.mkdir(parents=True, exist_ok=True)
        with open(ruta_salida, "w", encoding="utf-8", newline="") as f:
            escritor = csv.DictWriter(f, fieldnames=list(registros[0].keys()))
            escritor.writeheader()
            escritor.writerows(registros)

    return registros


if __name__ == "__main__":
    ruta = Path(__file__).resolve().parent / "estudiantes.csv"
    datos = generar_dataset(300, ruta)
    n_riesgo = sum(1 for r in datos if r["riesgo"] == 1)
    print(f"Dataset generado: {len(datos)} estudiantes en {ruta}")
    print(f"  - En riesgo:   {n_riesgo} ({n_riesgo/len(datos)*100:.1f}%)")
    print(f"  - Sin riesgo:  {len(datos)-n_riesgo} ({(len(datos)-n_riesgo)/len(datos)*100:.1f}%)")
