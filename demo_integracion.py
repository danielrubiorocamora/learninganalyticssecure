"""Demo de integración Día 1: criptografía + blockchain + datos.

Este script demuestra el flujo completo de la herramienta:
    1. Carga el dataset de estudiantes.
    2. Cifra los campos sensibles (nombre, email) con AES.
    3. Genera un par de claves RSA para un docente y firma cada registro.
    4. Encadena los registros firmados en una blockchain con SHA-256 + PoW.
    5. Verifica la integridad de la cadena.
    6. Simula un ataque de manipulación y comprueba que la cadena lo detecta.

Ejecutar con:
    python demo_integracion.py
"""

from __future__ import annotations

import csv
import time
from pathlib import Path

from blockchain_module import Cadena
from crypto_module import (
    cifrar_diccionario,
    descifrar_diccionario,
    firmar,
    generar_clave_aleatoria,
    generar_par_de_claves,
    serializar_clave_publica,
    verificar,
)


CAMPOS_SENSIBLES = ["nombre", "email"]


def cargar_estudiantes(ruta: Path, n: int = 10) -> list[dict]:
    """Carga los N primeros estudiantes del CSV para la demo."""
    with open(ruta, encoding="utf-8") as f:
        return [fila for i, fila in enumerate(csv.DictReader(f)) if i < n]


def main() -> None:
    print("=" * 72)
    print("  DEMO DE INTEGRACIÓN — Learning Analytics seguro")
    print("=" * 72)

    # ------------------------------------------------------------------
    # 1. Cargar datos
    # ------------------------------------------------------------------
    ruta_csv = Path(__file__).resolve().parent / "data" / "estudiantes.csv"
    estudiantes = cargar_estudiantes(ruta_csv, n=10)
    print(f"\n[1] Cargados {len(estudiantes)} estudiantes desde {ruta_csv.name}")
    print(f"    Ejemplo (en claro): {estudiantes[0]['id_estudiante']} - {estudiantes[0]['nombre']}")

    # ------------------------------------------------------------------
    # 2. Cifrado AES de campos sensibles
    # ------------------------------------------------------------------
    clave_aes = generar_clave_aleatoria()
    estudiantes_cifrados = [cifrar_diccionario(e, CAMPOS_SENSIBLES, clave_aes) for e in estudiantes]
    print(f"\n[2] Cifrados {len(CAMPOS_SENSIBLES)} campos sensibles con AES (Fernet)")
    print(f"    Ejemplo (cifrado): {estudiantes_cifrados[0]['nombre'][:60]}...")
    # Verificamos que el descifrado es reversible.
    descifrado = descifrar_diccionario(estudiantes_cifrados[0], CAMPOS_SENSIBLES, clave_aes)
    print(f"    Tras descifrar:    {descifrado['nombre']}")

    # ------------------------------------------------------------------
    # 3. Firmas digitales RSA
    # ------------------------------------------------------------------
    priv_docente, pub_docente = generar_par_de_claves()
    print(f"\n[3] Generado par de claves RSA-2048 para el docente.")
    print(f"    Clave pública (primeros 60 caracteres):")
    print(f"    {serializar_clave_publica(pub_docente).decode()[:70]}...")

    transacciones_firmadas = []
    for est in estudiantes_cifrados:
        cuerpo = f"{est['id_estudiante']}|{est['nombre']}|{est['media']}"
        firma = firmar(cuerpo.encode("utf-8"), priv_docente)
        transacciones_firmadas.append({
            "id_estudiante": est["id_estudiante"],
            "nombre_cifrado": est["nombre"],
            "media": est["media"],
            "riesgo": est["riesgo"],
            "firma_hex": firma.hex(),
        })
    # Comprobamos una firma como ejemplo.
    ejemplo = transacciones_firmadas[0]
    cuerpo_ejemplo = f"{ejemplo['id_estudiante']}|{ejemplo['nombre_cifrado']}|{ejemplo['media']}"
    firma_bytes = bytes.fromhex(ejemplo["firma_hex"])
    print(f"    Verificación de firma del 1er registro: {verificar(firma_bytes, cuerpo_ejemplo.encode(), pub_docente)}")

    # ------------------------------------------------------------------
    # 4. Encadenamiento en blockchain
    # ------------------------------------------------------------------
    print(f"\n[4] Construyendo blockchain con SHA-256 + Proof-of-Work (dificultad=3)...")
    cadena = Cadena(dificultad=3)
    inicio = time.time()
    # Agrupamos las transacciones en lotes de 5 → 2 bloques.
    for i in range(0, len(transacciones_firmadas), 5):
        lote = transacciones_firmadas[i:i + 5]
        bloque = cadena.anadir_bloque(lote)
        print(f"    Bloque #{bloque.indice} minado (nonce={bloque.nonce}, hash={bloque.hash_actual[:16]}...)")
    print(f"    Tiempo total de minería: {time.time() - inicio:.2f} s")

    # ------------------------------------------------------------------
    # 5. Verificar integridad
    # ------------------------------------------------------------------
    ok, mensaje = cadena.verificar_integridad()
    print(f"\n[5] Verificación de integridad: {'OK' if ok else 'FALLO'}")
    print(f"    {mensaje}")

    # ------------------------------------------------------------------
    # 6. Simular ataque de manipulación
    # ------------------------------------------------------------------
    print(f"\n[6] Simulando un atacante que cambia una nota de 5.0 a 9.9...")
    cadena.bloques[1].transacciones[0]["media"] = "9.9"
    ok, mensaje = cadena.verificar_integridad()
    print(f"    Verificación tras el ataque: {'OK' if ok else 'MANIPULACIÓN DETECTADA'}")
    print(f"    {mensaje}")

    print("\n" + "=" * 72)
    print("  Demo finalizada con éxito.")
    print("=" * 72)


if __name__ == "__main__":
    main()
