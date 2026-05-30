"""Operaciones firmadas en la cadena de bloques.

Cada operación sensible del sistema (registrar nota, consultar registro,
modificar dato) se serializa como transacción, se firma con la clave privada
RSA del usuario emisor, y se añade a la blockchain.

Esto da tres propiedades muy importantes para la herramienta:
    - **Autenticación**: la firma demuestra que el emisor posee la clave privada
      asociada a su identidad pública.
    - **No repudio**: el usuario no puede negar haber realizado la operación una
      vez ha sido encadenada.
    - **Inmutabilidad**: cualquier intento posterior de manipular la transacción
      rompe la cadena y se detecta por `verificar_integridad`.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from blockchain_module import Cadena
from crypto_module import (
    cargar_clave_privada,
    cargar_clave_publica,
    firmar,
    verificar,
)


RUTA_CADENA = Path(__file__).resolve().parent.parent / "data" / "cadena_blockchain.json"


# ---------------------------------------------------------------------------
# Construcción de transacciones firmadas
# ---------------------------------------------------------------------------
def construir_transaccion(
    tipo: str,
    emisor: str,
    payload: dict[str, Any],
    pem_clave_privada: str,
    clave_publica_pem: str,
) -> dict[str, Any]:
    """Construye una transacción serializable y firmada digitalmente.

    Campos:
        - `tipo`: nombre semántico de la operación (p.ej. "registrar_nota").
        - `emisor`: usuario que realiza la operación.
        - `marca_tiempo`: timestamp Unix.
        - `payload`: contenido específico de la operación.
        - `firma_hex`: firma RSA-PSS del cuerpo en hexadecimal.
        - `clave_publica_pem`: clave pública del emisor para verificación.
    """
    cuerpo = {
        "tipo": tipo,
        "emisor": emisor,
        "marca_tiempo": time.time(),
        "payload": payload,
    }
    serializado = json.dumps(cuerpo, sort_keys=True, separators=(",", ":"), default=str)
    clave_privada = cargar_clave_privada(pem_clave_privada.encode("utf-8"))
    firma = firmar(serializado.encode("utf-8"), clave_privada)
    return {
        **cuerpo,
        "firma_hex": firma.hex(),
        "clave_publica_pem": clave_publica_pem,
    }


def verificar_transaccion(transaccion: dict[str, Any]) -> bool:
    """Recalcula la firma de una transacción y comprueba que es válida."""
    if "firma_hex" not in transaccion or "clave_publica_pem" not in transaccion:
        return False
    cuerpo = {
        "tipo": transaccion["tipo"],
        "emisor": transaccion["emisor"],
        "marca_tiempo": transaccion["marca_tiempo"],
        "payload": transaccion["payload"],
    }
    serializado = json.dumps(cuerpo, sort_keys=True, separators=(",", ":"), default=str)
    clave_publica = cargar_clave_publica(transaccion["clave_publica_pem"].encode("utf-8"))
    firma = bytes.fromhex(transaccion["firma_hex"])
    return verificar(firma, serializado.encode("utf-8"), clave_publica)


# ---------------------------------------------------------------------------
# Gestión persistente de la cadena
# ---------------------------------------------------------------------------
def cargar_o_crear_cadena(dificultad: int = 3, ruta: Path = RUTA_CADENA) -> Cadena:
    """Carga la cadena desde disco si existe, o crea una nueva con su bloque génesis.

    Si el fichero existe, se respeta la dificultad con la que fue minada la cadena
    (no se sobrescribe), para no invalidar la verificación de bloques antiguos.
    """
    if ruta.exists():
        return Cadena.cargar_json(ruta)
    cadena = Cadena(dificultad=dificultad)
    cadena.guardar_json(ruta)
    return cadena


def anadir_y_persistir(cadena: Cadena, transacciones: list[dict[str, Any]], ruta: Path = RUTA_CADENA) -> int:
    """Añade un nuevo bloque y guarda la cadena en disco.

    Devuelve el índice del bloque creado.
    """
    bloque = cadena.anadir_bloque(transacciones)
    cadena.guardar_json(ruta)
    return bloque.indice


# ---------------------------------------------------------------------------
# Operaciones de alto nivel para el dashboard
# ---------------------------------------------------------------------------
def operacion_registrar_nota(
    cadena: Cadena,
    emisor: str,
    pem_clave_privada: str,
    clave_publica_pem: str,
    id_estudiante: str,
    asignatura: str,
    nota: float,
) -> int:
    """Crea una transacción 'registrar_nota' firmada y la añade a la blockchain."""
    transaccion = construir_transaccion(
        tipo="registrar_nota",
        emisor=emisor,
        payload={
            "id_estudiante": id_estudiante,
            "asignatura": asignatura,
            "nota": nota,
        },
        pem_clave_privada=pem_clave_privada,
        clave_publica_pem=clave_publica_pem,
    )
    return anadir_y_persistir(cadena, [transaccion])


def operacion_consulta_registro(
    cadena: Cadena,
    emisor: str,
    pem_clave_privada: str,
    clave_publica_pem: str,
    id_estudiante: str,
) -> int:
    """Registra una consulta en la cadena (audit trail GDPR-compliant)."""
    transaccion = construir_transaccion(
        tipo="consulta_registro",
        emisor=emisor,
        payload={"id_estudiante": id_estudiante},
        pem_clave_privada=pem_clave_privada,
        clave_publica_pem=clave_publica_pem,
    )
    return anadir_y_persistir(cadena, [transaccion])


def obtener_operaciones_por_estudiante(cadena: Cadena, id_estudiante: str) -> list[dict]:
    """Devuelve todas las transacciones de la cadena referidas a un estudiante."""
    resultado = []
    for bloque in cadena.bloques:
        for tx in bloque.transacciones:
            payload = tx.get("payload", {})
            if isinstance(payload, dict) and payload.get("id_estudiante") == id_estudiante:
                resultado.append({
                    "bloque": bloque.indice,
                    "tipo": tx.get("tipo"),
                    "emisor": tx.get("emisor"),
                    "marca_tiempo": tx.get("marca_tiempo"),
                    "payload": payload,
                    "firma_valida": verificar_transaccion(tx) if "firma_hex" in tx else None,
                })
    return resultado
