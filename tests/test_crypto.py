"""Pruebas unitarias del módulo de criptografía."""

import pytest
from cryptography.fernet import InvalidToken

from crypto_module import (
    cargar_clave_privada,
    cargar_clave_publica,
    cifrar,
    cifrar_diccionario,
    derivar_clave,
    descifrar,
    descifrar_diccionario,
    firmar,
    generar_clave_aleatoria,
    generar_par_de_claves,
    generar_sal,
    hash_dict,
    serializar_clave_privada,
    serializar_clave_publica,
    sha256_hex,
    verificar,
)


# ---------------------------------------------------------------------------
# Cifrado simétrico
# ---------------------------------------------------------------------------
class TestCifradoSimetrico:
    def test_cifrar_y_descifrar_devuelve_el_texto_original(self):
        clave = generar_clave_aleatoria()
        texto = "Calificación final: 9.5"
        cifrado = cifrar(texto, clave)
        assert cifrado != texto
        assert descifrar(cifrado, clave) == texto

    def test_descifrar_con_clave_incorrecta_lanza_excepcion(self):
        clave_a = generar_clave_aleatoria()
        clave_b = generar_clave_aleatoria()
        cifrado = cifrar("dato sensible", clave_a)
        with pytest.raises(InvalidToken):
            descifrar(cifrado, clave_b)

    def test_token_manipulado_lanza_excepcion(self):
        clave = generar_clave_aleatoria()
        cifrado = cifrar("hola", clave)
        manipulado = cifrado[:-2] + ("aa" if cifrado[-2:] != "aa" else "bb")
        with pytest.raises(InvalidToken):
            descifrar(manipulado, clave)

    def test_derivacion_misma_password_y_sal_produce_misma_clave(self):
        sal = generar_sal()
        clave_1 = derivar_clave("password-segura-123", sal)
        clave_2 = derivar_clave("password-segura-123", sal)
        assert clave_1 == clave_2

    def test_derivacion_distinta_sal_produce_distinta_clave(self):
        clave_1 = derivar_clave("password-segura-123", generar_sal())
        clave_2 = derivar_clave("password-segura-123", generar_sal())
        assert clave_1 != clave_2

    def test_cifrar_diccionario_solo_cifra_campos_indicados(self):
        clave = generar_clave_aleatoria()
        registro = {"id": "EST-001", "nombre": "Lucía Fernández", "media": 7.8}
        cifrado = cifrar_diccionario(registro, ["nombre"], clave)
        assert cifrado["id"] == "EST-001"          # no cifrado
        assert cifrado["media"] == 7.8              # no cifrado
        assert cifrado["nombre"] != "Lucía Fernández"  # cifrado
        # Reversible:
        descifrado = descifrar_diccionario(cifrado, ["nombre"], clave)
        assert descifrado["nombre"] == "Lucía Fernández"


# ---------------------------------------------------------------------------
# Cifrado asimétrico / firmas
# ---------------------------------------------------------------------------
class TestFirmaRSA:
    def test_firma_valida_se_verifica(self):
        priv, pub = generar_par_de_claves()
        mensaje = b"Registro de nota: EST-0042 - matematicas - 8.7"
        firma = firmar(mensaje, priv)
        assert verificar(firma, mensaje, pub) is True

    def test_firma_invalida_con_mensaje_modificado(self):
        priv, pub = generar_par_de_claves()
        firma = firmar(b"mensaje original", priv)
        assert verificar(firma, b"mensaje manipulado", pub) is False

    def test_firma_invalida_con_clave_publica_distinta(self):
        priv_a, _ = generar_par_de_claves()
        _, pub_b = generar_par_de_claves()
        firma = firmar(b"mensaje", priv_a)
        assert verificar(firma, b"mensaje", pub_b) is False

    def test_serializacion_y_carga_de_claves(self):
        priv, pub = generar_par_de_claves()
        pem_priv = serializar_clave_privada(priv)
        pem_pub = serializar_clave_publica(pub)
        priv2 = cargar_clave_privada(pem_priv)
        pub2 = cargar_clave_publica(pem_pub)
        mensaje = b"prueba serializacion"
        firma = firmar(mensaje, priv2)
        assert verificar(firma, mensaje, pub2) is True


# ---------------------------------------------------------------------------
# Hash
# ---------------------------------------------------------------------------
class TestHashing:
    def test_sha256_es_determinista(self):
        assert sha256_hex("hola") == sha256_hex("hola")

    def test_sha256_cambia_con_un_solo_bit(self):
        """Efecto avalancha: un cambio mínimo produce un hash totalmente distinto."""
        h1 = sha256_hex("hola")
        h2 = sha256_hex("Hola")
        assert h1 != h2

    def test_hash_dict_independiente_del_orden_de_claves(self):
        d1 = {"a": 1, "b": 2, "c": 3}
        d2 = {"c": 3, "a": 1, "b": 2}
        assert hash_dict(d1) == hash_dict(d2)

    def test_sha256_longitud_64_caracteres(self):
        assert len(sha256_hex("x")) == 64
