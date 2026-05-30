"""Pruebas del sistema de autenticación y operaciones firmadas."""

import json
import tempfile
from pathlib import Path

import pytest

from app.operaciones import (
    cargar_o_crear_cadena,
    construir_transaccion,
    obtener_operaciones_por_estudiante,
    operacion_registrar_nota,
    verificar_transaccion,
)
from app.usuarios import (
    LITERAL_VERIFICACION,
    USUARIOS_DEMO,
    autenticar,
    bootstrap_usuarios_demo,
    cargar_usuarios,
    guardar_usuarios,
    registrar_usuario,
)


# ---------------------------------------------------------------------------
# Gestión de usuarios y autenticación
# ---------------------------------------------------------------------------
class TestUsuarios:
    def test_registrar_usuario_valido(self):
        u = registrar_usuario("test", "ClavSegura1!", "docente")
        assert u.usuario == "test"
        assert u.rol == "docente"
        assert u.id_estudiante is None
        assert len(u.sal_hex) == 32  # 16 bytes en hex
        assert "-----BEGIN PUBLIC KEY-----" in u.clave_publica_pem

    def test_registrar_usuario_rol_invalido_lanza_error(self):
        with pytest.raises(ValueError):
            registrar_usuario("test", "ClavSegura1!", "supervisor")

    def test_registrar_usuario_password_corta_lanza_error(self):
        with pytest.raises(ValueError):
            registrar_usuario("test", "abc", "docente")

    def test_registrar_estudiante_sin_id_lanza_error(self):
        with pytest.raises(ValueError):
            registrar_usuario("est-x", "ClavSegura1!", "estudiante", id_estudiante=None)

    def test_registrar_usuario_duplicado_lanza_error(self):
        existentes = {"test": registrar_usuario("test", "ClavSegura1!", "docente")}
        with pytest.raises(ValueError):
            registrar_usuario("test", "OtraPass2!", "administrador", usuarios_existentes=existentes)

    def test_autenticar_credenciales_correctas(self):
        u = registrar_usuario("profe", "ClavSegura1!", "docente")
        usuarios = {"profe": u}
        ok, usuario_aut, pem = autenticar("profe", "ClavSegura1!", usuarios)
        assert ok is True
        assert usuario_aut.usuario == "profe"
        # La clave privada descifrada debe ser un PEM válido.
        assert "-----BEGIN PRIVATE KEY-----" in pem

    def test_autenticar_contrasena_incorrecta(self):
        u = registrar_usuario("profe", "ClavSegura1!", "docente")
        usuarios = {"profe": u}
        ok, _, _ = autenticar("profe", "ClavIncorrecta!", usuarios)
        assert ok is False

    def test_autenticar_usuario_inexistente(self):
        ok, _, _ = autenticar("no_existe", "lo_que_sea", {})
        assert ok is False

    def test_persistencia_de_usuarios(self):
        u = registrar_usuario("profe", "ClavSegura1!", "docente")
        usuarios = {"profe": u}
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            ruta = Path(f.name)
        try:
            guardar_usuarios(usuarios, ruta)
            cargados = cargar_usuarios(ruta)
            assert "profe" in cargados
            ok, _, _ = autenticar("profe", "ClavSegura1!", cargados)
            assert ok is True
        finally:
            ruta.unlink(missing_ok=True)

    def test_bootstrap_demo_crea_todos_los_usuarios(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            ruta = Path(f.name)
        try:
            ruta.unlink()  # nos aseguramos de partir de cero
            usuarios = bootstrap_usuarios_demo(ruta, sobrescribir=True)
            assert len(usuarios) == len(USUARIOS_DEMO)
            assert "admin" in usuarios
            # Verificar que el admin se puede autenticar.
            ok, _, _ = autenticar("admin", "Admin1234!", usuarios)
            assert ok is True
        finally:
            ruta.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Operaciones firmadas en la blockchain
# ---------------------------------------------------------------------------
class TestOperacionesFirmadas:
    @pytest.fixture
    def usuario_docente(self):
        return registrar_usuario("docente.test", "ClavSegura1!", "docente")

    @pytest.fixture
    def credenciales_docente(self, usuario_docente):
        usuarios = {"docente.test": usuario_docente}
        _, _, pem = autenticar("docente.test", "ClavSegura1!", usuarios)
        return usuario_docente, pem

    def test_construir_transaccion_se_puede_verificar(self, credenciales_docente):
        u, pem = credenciales_docente
        tx = construir_transaccion(
            tipo="registrar_nota",
            emisor=u.usuario,
            payload={"id": "EST-0001", "nota": 8.5},
            pem_clave_privada=pem,
            clave_publica_pem=u.clave_publica_pem,
        )
        assert verificar_transaccion(tx) is True

    def test_verificar_transaccion_falla_si_se_manipula_payload(self, credenciales_docente):
        u, pem = credenciales_docente
        tx = construir_transaccion(
            tipo="registrar_nota",
            emisor=u.usuario,
            payload={"id": "EST-0001", "nota": 5.0},
            pem_clave_privada=pem,
            clave_publica_pem=u.clave_publica_pem,
        )
        # Un atacante cambia la nota tras la firma.
        tx["payload"]["nota"] = 9.9
        assert verificar_transaccion(tx) is False

    def test_registrar_nota_anade_bloque_a_la_cadena(self, credenciales_docente):
        u, pem = credenciales_docente
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            ruta = Path(f.name)
        try:
            ruta.unlink()
            cadena = cargar_o_crear_cadena(dificultad=2, ruta=ruta)
            n_inicial = len(cadena)
            indice = operacion_registrar_nota(
                cadena=cadena,
                emisor=u.usuario,
                pem_clave_privada=pem,
                clave_publica_pem=u.clave_publica_pem,
                id_estudiante="EST-0001",
                asignatura="matematicas",
                nota=8.5,
            )
            assert len(cadena) == n_inicial + 1
            assert indice == n_inicial
            # Verificar integridad.
            ok, _ = cadena.verificar_integridad()
            assert ok is True
        finally:
            ruta.unlink(missing_ok=True)

    def test_obtener_operaciones_por_estudiante(self, credenciales_docente):
        u, pem = credenciales_docente
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            ruta = Path(f.name)
        try:
            ruta.unlink()
            cadena = cargar_o_crear_cadena(dificultad=2, ruta=ruta)
            operacion_registrar_nota(cadena, u.usuario, pem, u.clave_publica_pem, "EST-0001", "lengua", 7.0)
            operacion_registrar_nota(cadena, u.usuario, pem, u.clave_publica_pem, "EST-0002", "lengua", 5.0)
            operacion_registrar_nota(cadena, u.usuario, pem, u.clave_publica_pem, "EST-0001", "ingles", 8.0)
            ops_001 = obtener_operaciones_por_estudiante(cadena, "EST-0001")
            assert len(ops_001) == 2
            # Cada operación tiene firma válida.
            assert all(op["firma_valida"] is True for op in ops_001)
        finally:
            ruta.unlink(missing_ok=True)
