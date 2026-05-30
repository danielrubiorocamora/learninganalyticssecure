"""Cadena de bloques: gestión, verificación de integridad y persistencia.

Esta es la pieza que garantiza la **inmutabilidad** de los registros educativos
mediante el patrón de enlace por hash. Si un atacante modifica una transacción
pasada, el hash del bloque cambia y rompe el enlace `hash_anterior` de los bloques
siguientes; el método `verificar_integridad()` detecta esa rotura.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from blockchain_module.bloque import Bloque


HASH_GENESIS = "0" * 64


class Cadena:
    """Una cadena de bloques sencilla con Proof-of-Work configurable."""

    def __init__(self, dificultad: int = 3) -> None:
        """Crea la cadena con un bloque génesis."""
        if dificultad < 1 or dificultad > 6:
            raise ValueError("La dificultad recomendada está entre 1 y 6.")
        self.dificultad = dificultad
        self.bloques: list[Bloque] = []
        self._crear_genesis()

    # ------------------------------------------------------------------
    # Construcción
    # ------------------------------------------------------------------
    def _crear_genesis(self) -> None:
        """Crea el bloque génesis (sin transacciones, hash_anterior = ceros)."""
        genesis = Bloque(
            indice=0,
            transacciones=[{"mensaje": "Bloque génesis - Learning Analytics Seguro"}],
            hash_anterior=HASH_GENESIS,
        )
        genesis.minar(self.dificultad)
        self.bloques.append(genesis)

    @property
    def ultimo_bloque(self) -> Bloque:
        return self.bloques[-1]

    def anadir_bloque(self, transacciones: list[dict[str, Any]]) -> Bloque:
        """Crea, mina y añade un bloque nuevo con las transacciones indicadas."""
        if not transacciones:
            raise ValueError("Un bloque debe contener al menos una transacción.")
        nuevo = Bloque(
            indice=len(self.bloques),
            transacciones=transacciones,
            hash_anterior=self.ultimo_bloque.hash_actual,
        )
        nuevo.minar(self.dificultad)
        self.bloques.append(nuevo)
        return nuevo

    # ------------------------------------------------------------------
    # Verificación de integridad
    # ------------------------------------------------------------------
    def verificar_integridad(self) -> tuple[bool, str]:
        """Recorre la cadena y devuelve (ok, descripcion).

        Comprueba:
            1. Que cada hash recalculado coincide con el almacenado.
            2. Que cada bloque enlaza con el `hash_actual` del anterior.
            3. Que cada hash cumple la dificultad (Proof-of-Work).
            4. Que la raíz de Merkle es coherente con las transacciones.
        """
        from blockchain_module.merkle import calcular_raiz_merkle

        prefijo = "0" * self.dificultad

        for i, bloque in enumerate(self.bloques):
            # (1) Hash recalculado coincide con el almacenado.
            if bloque.calcular_hash() != bloque.hash_actual:
                return False, f"Hash inválido en bloque {i}: ha sido manipulado."

            # (2) Enlace con el bloque anterior.
            if i == 0:
                if bloque.hash_anterior != HASH_GENESIS:
                    return False, "El bloque génesis tiene hash anterior incorrecto."
            else:
                if bloque.hash_anterior != self.bloques[i - 1].hash_actual:
                    return False, f"Bloque {i}: el hash_anterior no enlaza con el bloque previo."

            # (3) PoW.
            if not bloque.hash_actual.startswith(prefijo):
                return False, f"Bloque {i}: no cumple la dificultad de PoW."

            # (4) Raíz de Merkle.
            esperada = calcular_raiz_merkle(
                [json.dumps(t, sort_keys=True, default=str) for t in bloque.transacciones]
            )
            if esperada != bloque.raiz_merkle:
                return False, f"Bloque {i}: la raíz de Merkle no coincide con las transacciones."

        return True, f"Cadena íntegra: {len(self.bloques)} bloques verificados."

    # ------------------------------------------------------------------
    # Persistencia
    # ------------------------------------------------------------------
    def guardar_json(self, ruta: str | Path) -> None:
        """Guarda la cadena en un fichero JSON legible."""
        datos = {
            "dificultad": self.dificultad,
            "bloques": [b.to_dict() for b in self.bloques],
        }
        Path(ruta).write_text(
            json.dumps(datos, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8",
        )

    @classmethod
    def cargar_json(cls, ruta: str | Path) -> "Cadena":
        """Carga una cadena previamente guardada en JSON."""
        datos = json.loads(Path(ruta).read_text(encoding="utf-8"))
        cadena = cls.__new__(cls)
        cadena.dificultad = datos["dificultad"]
        cadena.bloques = [Bloque.from_dict(b) for b in datos["bloques"]]
        return cadena

    def __len__(self) -> int:
        return len(self.bloques)
