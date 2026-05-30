"""Cifrado simétrico con AES-128-CBC + HMAC-SHA256 (a través de Fernet).

Fernet es una receta de cifrado autenticado de la librería `cryptography` que internamente usa:
    - AES-128 en modo CBC para confidencialidad.
    - HMAC-SHA256 para integridad/autenticación (AEAD).
    - PKCS7 padding y un IV aleatorio por cada cifrado.

Justificación de uso (ver memoria, sección 6):
    - Es el patrón industrial para cifrar datos en reposo de tamaño pequeño/medio
      (campos sensibles de un registro educativo).
    - Resuelve el problema del cifrado asimétrico cuando el volumen es grande: AES es
      órdenes de magnitud más rápido que RSA y el coste no escala con el tamaño del
      mensaje (ver unidad 3 del temario).
    - Al incluir HMAC garantiza que el texto cifrado no haya sido manipulado: añade el
      principio de **integridad** además de la **confidencialidad**.
"""

from __future__ import annotations

import base64
import os

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


# Número de iteraciones de PBKDF2. OWASP recomienda >= 600.000 para SHA-256 en 2024.
ITERACIONES_PBKDF2 = 600_000
LONGITUD_SAL_BYTES = 16
LONGITUD_CLAVE_BYTES = 32  # 256 bits, longitud que Fernet espera tras base64


def generar_sal() -> bytes:
    """Genera una sal aleatoria criptográficamente segura."""
    return os.urandom(LONGITUD_SAL_BYTES)


def derivar_clave(password: str, sal: bytes) -> bytes:
    """Deriva una clave Fernet a partir de una contraseña y una sal.

    Aplica PBKDF2-HMAC-SHA256 con un número alto de iteraciones para frenar ataques
    de fuerza bruta. La salida se codifica en base64 url-safe porque es el formato
    que Fernet acepta.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=LONGITUD_CLAVE_BYTES,
        salt=sal,
        iterations=ITERACIONES_PBKDF2,
    )
    clave_bruta = kdf.derive(password.encode("utf-8"))
    return base64.urlsafe_b64encode(clave_bruta)


def generar_clave_aleatoria() -> bytes:
    """Genera una clave Fernet aleatoria (256 bits) lista para usar."""
    return Fernet.generate_key()


def cifrar(texto_plano: str, clave: bytes) -> str:
    """Cifra un texto y devuelve el resultado como cadena (token Fernet en base64)."""
    if not isinstance(texto_plano, str):
        raise TypeError("Solo se admite texto plano de tipo str.")
    f = Fernet(clave)
    token = f.encrypt(texto_plano.encode("utf-8"))
    return token.decode("utf-8")


def descifrar(token: str, clave: bytes) -> str:
    """Descifra un token Fernet y devuelve el texto plano.

    Si la clave es incorrecta o el token está manipulado se lanza InvalidToken.
    """
    if not isinstance(token, str):
        raise TypeError("Solo se admite token de tipo str.")
    f = Fernet(clave)
    try:
        texto = f.decrypt(token.encode("utf-8"))
    except InvalidToken as exc:
        raise InvalidToken(
            "Token inválido: clave incorrecta o datos manipulados."
        ) from exc
    return texto.decode("utf-8")


def cifrar_diccionario(registro: dict, campos_sensibles: list[str], clave: bytes) -> dict:
    """Devuelve una copia del diccionario con los campos indicados cifrados.

    Útil para anonimizar un registro educativo antes de almacenarlo o exportarlo.
    """
    salida = dict(registro)
    for campo in campos_sensibles:
        if campo in salida and salida[campo] is not None:
            salida[campo] = cifrar(str(salida[campo]), clave)
    return salida


def descifrar_diccionario(registro: dict, campos_sensibles: list[str], clave: bytes) -> dict:
    """Inverso de `cifrar_diccionario`: descifra los campos indicados."""
    salida = dict(registro)
    for campo in campos_sensibles:
        if campo in salida and salida[campo] is not None:
            salida[campo] = descifrar(str(salida[campo]), clave)
    return salida
