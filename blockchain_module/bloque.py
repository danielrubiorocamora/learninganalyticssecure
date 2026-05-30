"""Definición de la clase `Bloque`.

Cada bloque enlaza con el anterior a través del campo `hash_anterior`, lo que crea
una cadena verificable. Si se modifica un solo bit en un bloque pasado, el hash
cambia y rompe el enlace con todos los bloques posteriores (efecto avalancha:
ver clase 18 del temario).

Estructura:
    - `indice`: posición del bloque en la cadena.
    - `marca_tiempo`: timestamp Unix de creación.
    - `transacciones`: lista de transacciones serializables (cada una es un dict).
    - `hash_anterior`: hash del bloque previo (`"0" * 64` para el bloque génesis).
    - `raiz_merkle`: raíz de Merkle de las transacciones.
    - `nonce`: número que se ajusta durante la minería para alcanzar la dificultad.
    - `hash_actual`: SHA-256 del resto de campos.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from typing import Any

from blockchain_module.merkle import calcular_raiz_merkle
from crypto_module.hashing import sha256_hex


@dataclass
class Bloque:
    indice: int
    transacciones: list[dict[str, Any]]
    hash_anterior: str
    marca_tiempo: float = field(default_factory=time.time)
    nonce: int = 0
    raiz_merkle: str = ""
    hash_actual: str = ""

    def __post_init__(self) -> None:
        if not self.raiz_merkle:
            self.raiz_merkle = calcular_raiz_merkle(
                [json.dumps(t, sort_keys=True, default=str) for t in self.transacciones]
            )
        if not self.hash_actual:
            self.hash_actual = self.calcular_hash()

    def cabecera_serializada(self) -> str:
        """Serialización canónica de la cabecera del bloque, sin `hash_actual`."""
        cabecera = {
            "indice": self.indice,
            "marca_tiempo": self.marca_tiempo,
            "hash_anterior": self.hash_anterior,
            "raiz_merkle": self.raiz_merkle,
            "nonce": self.nonce,
        }
        return json.dumps(cabecera, sort_keys=True, separators=(",", ":"))

    def calcular_hash(self) -> str:
        """Recalcula el hash del bloque a partir de su contenido actual."""
        return sha256_hex(self.cabecera_serializada())

    def minar(self, dificultad: int) -> None:
        """Proof-of-Work: encuentra un nonce que produzca un hash con N ceros iniciales.

        `dificultad` indica el número de caracteres hex iniciales que deben ser '0'.
        Para fines didácticos se recomienda mantenerlo bajo (3–4); cada incremento
        multiplica aprox. por 16 el tiempo medio.
        """
        prefijo_objetivo = "0" * dificultad
        while not self.hash_actual.startswith(prefijo_objetivo):
            self.nonce += 1
            self.hash_actual = self.calcular_hash()

    def to_dict(self) -> dict[str, Any]:
        """Serialización para guardar/exportar el bloque."""
        return asdict(self)

    @classmethod
    def from_dict(cls, datos: dict[str, Any]) -> "Bloque":
        """Reconstruye un Bloque desde un diccionario sin recalcular hash/raíz."""
        return cls(
            indice=datos["indice"],
            transacciones=datos["transacciones"],
            hash_anterior=datos["hash_anterior"],
            marca_tiempo=datos["marca_tiempo"],
            nonce=datos["nonce"],
            raiz_merkle=datos["raiz_merkle"],
            hash_actual=datos["hash_actual"],
        )
