"""Funciones hash criptográficas para verificación de integridad.

Se usa SHA-256 porque:
    - Es el algoritmo que utiliza Bitcoin y la mayoría de blockchains públicas.
    - Tiene resistencia a colisiones, preimagen y segunda preimagen probada en la
      práctica (ver unidad 3 del temario).
    - Es lo bastante rápido para iterar en la simulación de Proof-of-Work.

Se evita explícitamente MD5 y SHA-1 porque ambos han sido rotos para colisiones.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any


def sha256_hex(datos: bytes | str) -> str:
    """Calcula el SHA-256 de unos datos y devuelve el resultado en hexadecimal."""
    if isinstance(datos, str):
        datos = datos.encode("utf-8")
    return hashlib.sha256(datos).hexdigest()


def hash_dict(diccionario: dict[str, Any]) -> str:
    """Calcula un hash determinista para un diccionario.

    Se serializa a JSON con `sort_keys=True` para que el resultado sea independiente
    del orden de inserción de las claves: dos diccionarios equivalentes producen el
    mismo hash. Imprescindible para que la cadena de bloques sea verificable.
    """
    serializado = json.dumps(diccionario, sort_keys=True, separators=(",", ":"), default=str)
    return sha256_hex(serializado)


def hash_archivo(ruta: str, bloque: int = 65536) -> str:
    """Calcula el SHA-256 de un fichero por bloques (eficiente para ficheros grandes)."""
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        while True:
            trozo = f.read(bloque)
            if not trozo:
                break
            h.update(trozo)
    return h.hexdigest()
