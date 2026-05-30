"""Cálculo de la raíz de Merkle.

Un árbol de Merkle permite **verificar de manera eficiente** que un conjunto de
transacciones no ha sido alterado, sin tener que recalcular el hash de todo el
bloque. Es la estructura que usan Bitcoin y Ethereum (ver unidad 5 del temario,
clase 18).

Construcción:
    1. Se calcula el hash de cada transacción (hojas).
    2. Las hojas se emparejan y se concatenan dos a dos; del par se calcula un
       nuevo hash. Si el número de hojas es impar, la última se duplica.
    3. El proceso se repite hasta obtener un único hash: la **raíz de Merkle**.
"""

from __future__ import annotations

from crypto_module.hashing import sha256_hex


def calcular_raiz_merkle(transacciones: list[str]) -> str:
    """Calcula la raíz de Merkle de una lista de transacciones (representadas en str).

    Si la lista está vacía devuelve el hash del string vacío (convención).
    """
    if not transacciones:
        return sha256_hex("")

    # Capa de hojas: hash de cada transacción.
    nivel = [sha256_hex(t) for t in transacciones]

    while len(nivel) > 1:
        # Si el número de nodos es impar, duplicamos el último (estilo Bitcoin).
        if len(nivel) % 2 == 1:
            nivel.append(nivel[-1])

        siguiente = []
        for i in range(0, len(nivel), 2):
            concatenado = nivel[i] + nivel[i + 1]
            siguiente.append(sha256_hex(concatenado))
        nivel = siguiente

    return nivel[0]
