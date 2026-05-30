"""Pruebas unitarias del generador de dataset sintético."""

import tempfile
from pathlib import Path

import pytest

from data.generador_datos import generar_dataset, ASIGNATURAS


class TestGeneradorDatos:
    def test_cantidad_correcta_de_estudiantes(self):
        registros = generar_dataset(n_estudiantes=100)
        assert len(registros) == 100

    def test_estudiantes_minimos_validados(self):
        with pytest.raises(ValueError):
            generar_dataset(n_estudiantes=10)

    def test_campos_esperados_presentes(self):
        registros = generar_dataset(n_estudiantes=50)
        registro = registros[0]
        for campo in ("id_estudiante", "nombre", "email", "media", "riesgo"):
            assert campo in registro
        for asignatura in ASIGNATURAS:
            assert f"nota_{asignatura}" in registro

    def test_notas_en_rango_valido(self):
        registros = generar_dataset(n_estudiantes=200)
        for r in registros:
            for asignatura in ASIGNATURAS:
                nota = r[f"nota_{asignatura}"]
                assert 0.0 <= nota <= 10.0

    def test_asistencia_y_participacion_en_porcentaje(self):
        registros = generar_dataset(n_estudiantes=200)
        for r in registros:
            assert 0.0 <= r["asistencia_pct"] <= 100.0
            assert 0.0 <= r["participacion_pct"] <= 100.0

    def test_existen_ambas_clases(self):
        """El dataset debe contener estudiantes en riesgo y sin riesgo para entrenar ML."""
        registros = generar_dataset(n_estudiantes=300)
        clases = {r["riesgo"] for r in registros}
        assert clases == {0, 1}

    def test_csv_se_guarda_correctamente(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "test.csv"
            generar_dataset(n_estudiantes=60, ruta_salida=ruta)
            assert ruta.exists()
            contenido = ruta.read_text(encoding="utf-8")
            assert "id_estudiante" in contenido
            assert len(contenido.splitlines()) == 61  # cabecera + 60 filas
