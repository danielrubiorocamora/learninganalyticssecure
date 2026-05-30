"""Demostración visual de la detección de manipulación.

Este script:
    1. Asegura que el sistema está limpio (re-ejecuta bootstrap si es necesario).
    2. Genera unas pocas operaciones legítimas (logins y un registro de nota).
    3. Manipula la cadena directamente en disco (simulando un atacante con acceso
       al fichero de almacenamiento).
    4. Captura el dashboard mostrando el error "Cadena rota" en el sidebar.

El resultado (`docs/capturas/05_manipulacion_detectada.png`) es la prueba visual
de que el sistema detecta la manipulación incluso cuando el atacante tiene
permisos de escritura sobre el almacenamiento.
"""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

from playwright.sync_api import Page, sync_playwright


RAIZ = Path(__file__).resolve().parent
CARPETA_CAPTURAS = RAIZ / "docs" / "capturas"
RUTA_CADENA = RAIZ / "data" / "cadena_blockchain.json"

PUERTO = 8504
URL = f"http://localhost:{PUERTO}"


def esperar(page: Page, segundos: float) -> None:
    page.wait_for_timeout(int(segundos * 1000))


def manipular_cadena_en_disco() -> dict:
    """Simula un atacante que modifica una transacción de un bloque guardado.

    El atacante cambia una nota de un estudiante en la cadena directamente en
    el fichero JSON, intentando ocultar el ataque. La firma de cuyo bloque
    quedará incoherente con su contenido — el sistema lo detectará.

    Devuelve un resumen del ataque realizado.
    """
    print("[Atacante] Leyendo cadena de bloques desde disco...")
    datos = json.loads(RUTA_CADENA.read_text(encoding="utf-8"))

    # Buscamos un bloque con transacciones reales (no el génesis).
    bloque_objetivo = None
    for b in datos["bloques"]:
        if b["indice"] > 0 and b["transacciones"]:
            bloque_objetivo = b
            break
    if bloque_objetivo is None:
        raise RuntimeError("No hay bloques con transacciones para manipular.")

    tx = bloque_objetivo["transacciones"][0]
    payload = tx.get("payload", {})
    valor_original = json.dumps(payload, ensure_ascii=False)
    print(f"[Atacante] Bloque #{bloque_objetivo['indice']} encontrado.")
    print(f"[Atacante] Payload original: {valor_original}")

    # Manipulación: si hay una nota, la subimos a 10. Si no, cambiamos algún campo.
    if "nota" in payload:
        payload["nota"] = 10.0
        descripcion = f"nota cambiada de la original a 10.0"
    else:
        payload["payload_manipulado"] = True
        descripcion = "se ha inyectado un campo nuevo al payload"

    RUTA_CADENA.write_text(
        json.dumps(datos, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    print(f"[Atacante] Manipulación completada: {descripcion}.")
    return {
        "indice_bloque": bloque_objetivo["indice"],
        "descripcion": descripcion,
        "payload_original": valor_original,
        "payload_manipulado": json.dumps(payload, ensure_ascii=False),
    }


def generar_operaciones_legitimas() -> None:
    """Genera unas pocas operaciones reales para que haya algo que manipular."""
    print("[Sistema] Generando operaciones legítimas...")
    from app.operaciones import (
        cargar_o_crear_cadena,
        operacion_registrar_nota,
    )
    from app.usuarios import autenticar, cargar_usuarios

    cadena = cargar_o_crear_cadena()
    usuarios = cargar_usuarios()

    # El profesor registra dos notas.
    ok, u, pem = autenticar("profesor.moya", "Profesor1234!", usuarios)
    assert ok, "El login del profesor demo ha fallado."

    operacion_registrar_nota(
        cadena, u.usuario, pem, u.clave_publica_pem,
        id_estudiante="EST-0128", asignatura="matematicas", nota=3.5,
    )
    operacion_registrar_nota(
        cadena, u.usuario, pem, u.clave_publica_pem,
        id_estudiante="EST-0210", asignatura="lengua", nota=4.2,
    )
    print(f"[Sistema] Cadena ahora tiene {len(cadena)} bloques.")


def capturar_dashboard_tras_ataque(resumen_ataque: dict) -> Path:
    """Lanza Streamlit y captura el panel del administrador con el aviso de cadena rota."""
    print(f"[Captura] Arrancando Streamlit en puerto {PUERTO}...")
    proceso = subprocess.Popen(
        [
            "streamlit", "run", "app/dashboard.py",
            "--server.headless", "true",
            "--server.port", str(PUERTO),
            "--browser.gatherUsageStats", "false",
        ],
        cwd=RAIZ,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        time.sleep(6)
        with sync_playwright() as p:
            navegador = p.chromium.launch(headless=True)
            contexto = navegador.new_context(
                viewport={"width": 1280, "height": 900},
                device_scale_factor=2,
            )
            page = contexto.new_page()

            # Login como admin
            page.goto(URL)
            esperar(page, 5)
            page.locator('input[aria-label="Usuario"]').first.fill("admin")
            page.locator('input[aria-label="Contraseña"]').first.fill("Admin1234!")
            page.get_by_role("button", name="Entrar").first.click()
            esperar(page, 5)

            ruta = CARPETA_CAPTURAS / "05_manipulacion_detectada.png"
            page.screenshot(path=str(ruta), full_page=True)
            print(f"[Captura] ✓ {ruta.name}")

            navegador.close()
    finally:
        proceso.terminate()
        proceso.wait(timeout=5)

    return ruta


def main() -> None:
    print("=" * 72)
    print("  DEMO DE MANIPULACIÓN — Detección de ataque en la blockchain")
    print("=" * 72)

    # 1. Aseguramos un estado limpio
    if not RUTA_CADENA.exists():
        print("\n[Init] La cadena no existe. Lanzando bootstrap.py...")
        subprocess.check_call(["python", "bootstrap.py"], cwd=RAIZ)

    # 2. Generamos operaciones reales para que el ataque tenga sentido
    print("\n[1] Estado inicial: generando operaciones legítimas")
    generar_operaciones_legitimas()

    # 3. Atacante manipula la cadena
    print("\n[2] El atacante manipula la cadena directamente en disco")
    resumen = manipular_cadena_en_disco()

    # 4. Capturamos el dashboard
    print("\n[3] El sistema detecta la manipulación")
    ruta = capturar_dashboard_tras_ataque(resumen)

    # 5. Guardamos el resumen
    resumen_ruta = CARPETA_CAPTURAS.parent / "seguridad" / "resumen_manipulacion.json"
    resumen_ruta.write_text(json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n" + "=" * 72)
    print(f"  Captura: {ruta.relative_to(RAIZ)}")
    print(f"  Resumen: {resumen_ruta.relative_to(RAIZ)}")
    print("=" * 72)


if __name__ == "__main__":
    main()
