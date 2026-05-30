"""Pruebas unitarias del módulo blockchain."""

import json
import tempfile
from pathlib import Path

import pytest

from blockchain_module import Bloque, Cadena, HASH_GENESIS, calcular_raiz_merkle


# ---------------------------------------------------------------------------
# Raíz de Merkle
# ---------------------------------------------------------------------------
class TestMerkle:
    def test_lista_vacia_devuelve_un_hash(self):
        assert len(calcular_raiz_merkle([])) == 64

    def test_misma_entrada_misma_raiz(self):
        txs = ["tx1", "tx2", "tx3"]
        assert calcular_raiz_merkle(txs) == calcular_raiz_merkle(txs)

    def test_alterar_una_transaccion_cambia_la_raiz(self):
        original = calcular_raiz_merkle(["tx1", "tx2", "tx3"])
        alterado = calcular_raiz_merkle(["tx1", "tx2-MODIFICADA", "tx3"])
        assert original != alterado

    def test_numero_impar_de_transacciones_funciona(self):
        # No debe lanzar excepción: se duplica la última.
        raiz = calcular_raiz_merkle(["a", "b", "c"])
        assert len(raiz) == 64


# ---------------------------------------------------------------------------
# Cadena de bloques
# ---------------------------------------------------------------------------
class TestCadena:
    @pytest.fixture
    def cadena(self):
        return Cadena(dificultad=2)  # dificultad baja para que los tests sean rápidos

    def test_cadena_nueva_tiene_bloque_genesis(self, cadena):
        assert len(cadena) == 1
        genesis = cadena.bloques[0]
        assert genesis.indice == 0
        assert genesis.hash_anterior == HASH_GENESIS

    def test_anadir_bloque_incrementa_la_cadena(self, cadena):
        cadena.anadir_bloque([{"tipo": "registro_nota", "id": "EST-0001", "nota": 8.5}])
        assert len(cadena) == 2
        assert cadena.bloques[1].hash_anterior == cadena.bloques[0].hash_actual

    def test_anadir_bloque_sin_transacciones_lanza_error(self, cadena):
        with pytest.raises(ValueError):
            cadena.anadir_bloque([])

    def test_proof_of_work_se_aplica(self, cadena):
        bloque = cadena.anadir_bloque([{"x": 1}])
        assert bloque.hash_actual.startswith("00")  # dificultad = 2

    def test_verificar_integridad_de_cadena_valida(self, cadena):
        cadena.anadir_bloque([{"tipo": "registro", "valor": 1}])
        cadena.anadir_bloque([{"tipo": "registro", "valor": 2}])
        ok, mensaje = cadena.verificar_integridad()
        assert ok is True
        assert "íntegra" in mensaje

    def test_detecta_manipulacion_de_transaccion(self, cadena):
        cadena.anadir_bloque([{"tipo": "registro", "valor": 1}])
        cadena.anadir_bloque([{"tipo": "registro", "valor": 2}])
        # Manipulamos una transacción del bloque 1.
        cadena.bloques[1].transacciones[0]["valor"] = 999
        ok, mensaje = cadena.verificar_integridad()
        assert ok is False
        # Como la transacción se modifica sin recalcular nada, la raíz de Merkle ya no
        # coincide con las transacciones actuales (o el hash queda fuera de cuadre).
        assert ("Merkle" in mensaje) or ("Hash" in mensaje) or ("hash" in mensaje)

    def test_detecta_rotura_del_enlace_hash_anterior(self, cadena):
        cadena.anadir_bloque([{"tipo": "registro", "valor": 1}])
        cadena.anadir_bloque([{"tipo": "registro", "valor": 2}])
        # Reescribimos el hash_actual del bloque 1 (sin recalcular nada).
        cadena.bloques[1].hash_actual = "f" * 64
        ok, _ = cadena.verificar_integridad()
        assert ok is False

    def test_dificultad_fuera_de_rango_lanza_error(self):
        with pytest.raises(ValueError):
            Cadena(dificultad=0)
        with pytest.raises(ValueError):
            Cadena(dificultad=99)

    def test_guardar_y_cargar_cadena(self, cadena):
        cadena.anadir_bloque([{"tipo": "registro", "valor": 1}])
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            ruta = f.name
        try:
            cadena.guardar_json(ruta)
            cadena2 = Cadena.cargar_json(ruta)
            assert len(cadena2) == len(cadena)
            ok, _ = cadena2.verificar_integridad()
            assert ok is True
        finally:
            Path(ruta).unlink(missing_ok=True)
