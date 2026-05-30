"""Criptografía asimétrica RSA: generación de claves, firma y verificación.

Se usa RSA-2048 con padding PSS y SHA-256 para firmas digitales. Esta combinación es
la recomendada por NIST y por OWASP para nuevas aplicaciones.

Justificación de uso (ver memoria, sección 6):
    - RSA permite **autenticación** y **no repudio**: el receptor puede verificar
      con la clave pública que el firmante posee la clave privada correspondiente.
    - No se usa RSA para cifrar los datos educativos masivos porque su coste
      computacional es órdenes de magnitud mayor que AES y porque RSA solo cifra
      bloques de tamaño limitado por el módulo n (ver unidad 4 y clase 13).
    - El patrón aplicado es el estándar industrial: **cifrado híbrido** — AES para
      los datos y RSA para firmar las operaciones (huella en la blockchain).
"""

from __future__ import annotations

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.exceptions import InvalidSignature


TAMANO_CLAVE_RSA = 2048  # NIST recomienda >= 2048 hasta 2030


def generar_par_de_claves(tamano: int = TAMANO_CLAVE_RSA) -> tuple:
    """Devuelve (clave_privada, clave_publica) como objetos de la librería cryptography."""
    clave_privada = rsa.generate_private_key(
        public_exponent=65537,
        key_size=tamano,
    )
    clave_publica = clave_privada.public_key()
    return clave_privada, clave_publica


def serializar_clave_privada(clave_privada, password: bytes | None = None) -> bytes:
    """Serializa la clave privada en formato PEM, opcionalmente cifrada con contraseña."""
    if password:
        algoritmo = serialization.BestAvailableEncryption(password)
    else:
        algoritmo = serialization.NoEncryption()
    return clave_privada.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=algoritmo,
    )


def serializar_clave_publica(clave_publica) -> bytes:
    """Serializa la clave pública en formato PEM (legible y portable)."""
    return clave_publica.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


def cargar_clave_privada(pem: bytes, password: bytes | None = None):
    """Carga una clave privada desde su forma PEM."""
    return serialization.load_pem_private_key(pem, password=password)


def cargar_clave_publica(pem: bytes):
    """Carga una clave pública desde su forma PEM."""
    return serialization.load_pem_public_key(pem)


def firmar(mensaje: bytes, clave_privada) -> bytes:
    """Firma un mensaje (bytes) con RSA-PSS + SHA-256.

    Se usa PSS (Probabilistic Signature Scheme) porque es el esquema demostrablemente
    seguro frente a ataques de elección de mensaje y reemplaza al antiguo PKCS#1 v1.5.
    """
    return clave_privada.sign(
        mensaje,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )


def verificar(firma: bytes, mensaje: bytes, clave_publica) -> bool:
    """Verifica una firma. Devuelve True si es válida, False en caso contrario."""
    try:
        clave_publica.verify(
            firma,
            mensaje,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        return True
    except InvalidSignature:
        return False
