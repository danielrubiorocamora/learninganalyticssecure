"""Captura automática de screenshots del dashboard para el PDF.

Arranca Streamlit en segundo plano, navega con Chromium en headless, hace login
con cada uno de los tres roles y captura screenshots de tamaño A4 horizontal.

Este script solo se usa internamente para generar las capturas del informe.
"""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

from playwright.sync_api import Page, sync_playwright


RAIZ = Path(__file__).resolve().parent
CARPETA_CAPTURAS = RAIZ / "docs" / "capturas"
CARPETA_CAPTURAS.mkdir(parents=True, exist_ok=True)

PUERTO = 8503
URL = f"http://localhost:{PUERTO}"

# Dimensiones del viewport. 1280x900 da buenas proporciones para PDF A4.
ANCHO = 1280
ALTO = 900


def esperar(page: Page, segundos: float) -> None:
    page.wait_for_timeout(int(segundos * 1000))


def esperar_a_que_streamlit_termine(page: Page) -> None:
    """Espera a que el componente 'running' de Streamlit desaparezca."""
    # Streamlit muestra un indicador "RUNNING..." mientras procesa.
    # Esperamos a que termine y damos un margen extra para que los gráficos pinten.
    try:
        page.wait_for_load_state("networkidle", timeout=15000)
    except Exception:
        pass
    esperar(page, 3.5)


def hacer_login(page: Page, usuario: str, contrasena: str) -> None:
    """Rellena el formulario de login y entra."""
    page.goto(URL)
    esperar_a_que_streamlit_termine(page)

    inputs_texto = page.locator('input[aria-label="Usuario"]')
    inputs_pass = page.locator('input[aria-label="Contraseña"]')
    inputs_texto.first.fill(usuario)
    inputs_pass.first.fill(contrasena)

    page.get_by_role("button", name="Entrar").first.click()
    esperar_a_que_streamlit_termine(page)
    # Margen extra para que carguen modelos y gráficos
    esperar(page, 2)


def hacer_logout(page: Page) -> None:
    """Pulsa el botón Cerrar sesión de la barra lateral."""
    try:
        page.get_by_role("button", name="Cerrar sesión").click()
        esperar_a_que_streamlit_termine(page)
    except Exception:
        pass


def capturar(page: Page, nombre: str, full_page: bool = True) -> Path:
    ruta = CARPETA_CAPTURAS / f"{nombre}.png"
    page.screenshot(path=str(ruta), full_page=full_page)
    print(f"    ✓ {nombre}.png")
    return ruta


def main() -> None:
    # ------------------------------------------------------------------
    # 1. Arrancar Streamlit en segundo plano
    # ------------------------------------------------------------------
    print("[1] Arrancando Streamlit en puerto", PUERTO, "...")
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
        # Esperamos a que el servidor responda
        time.sleep(6)

        # ------------------------------------------------------------------
        # 2. Capturar con Playwright
        # ------------------------------------------------------------------
        with sync_playwright() as p:
            navegador = p.chromium.launch(headless=True)
            contexto = navegador.new_context(
                viewport={"width": ANCHO, "height": ALTO},
                device_scale_factor=2,  # retina, para mejor calidad de PDF
            )
            page = contexto.new_page()

            print("[2] Capturando pantalla de LOGIN...")
            page.goto(URL)
            esperar_a_que_streamlit_termine(page)
            # Esperamos a que aparezca el campo Usuario en pantalla
            try:
                page.wait_for_selector('input[aria-label="Usuario"]', timeout=10000)
                esperar(page, 1.5)
            except Exception:
                pass
            capturar(page, "00_login")

            print("[3] Capturando vista de ADMINISTRADOR...")
            hacer_login(page, "admin", "Admin1234!")
            capturar(page, "01_administrador")

            print("[4] Capturando vista de DOCENTE...")
            hacer_logout(page)
            hacer_login(page, "profesor.moya", "Profesor1234!")
            capturar(page, "02_docente")

            print("[5] Capturando vista de ESTUDIANTE (sin riesgo)...")
            hacer_logout(page)
            hacer_login(page, "EST-0001", "Estudiante1!")
            capturar(page, "03_estudiante_sin_riesgo")

            print("[6] Capturando vista de ESTUDIANTE (alto riesgo)...")
            hacer_logout(page)
            hacer_login(page, "EST-0128", "Estudiante1!")
            capturar(page, "04_estudiante_riesgo")

            navegador.close()
    finally:
        proceso.terminate()
        proceso.wait(timeout=5)

    print("\nTodas las capturas guardadas en", CARPETA_CAPTURAS)


if __name__ == "__main__":
    main()
