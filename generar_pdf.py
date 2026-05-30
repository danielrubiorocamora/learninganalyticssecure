"""Generador principal de la memoria en PDF.

Ejecutar con:
    python generar_pdf.py

Genera `docs/Memoria_Daniel_Rubio_Rocamora.pdf`.
"""

from __future__ import annotations

from pathlib import Path

from pdf.estilos import (
    AZUL_OSCURO,
    GRIS_MEDIO,
    MARGEN_DER,
    MARGEN_INF,
    MARGEN_IZQ,
    MARGEN_SUP,
)
from pdf.seccion_01_intro import (
    construir_indice,
    construir_portada,
    construir_resumen_ejecutivo,
)
from pdf.seccion_02_marco import (
    construir_introduccion,
    construir_marco_teorico,
)
from pdf.seccion_03_implementacion import (
    construir_arquitectura,
    construir_implementacion,
)
from pdf.seccion_04_validacion import (
    construir_gdpr,
    construir_seguridad,
    construir_validacion,
)
from pdf.seccion_05_cierre import (
    construir_anexo_github,
    construir_conclusiones,
    construir_problemas,
    construir_referencias,
)
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate


RAIZ = Path(__file__).resolve().parent
RUTA_SALIDA = RAIZ / "docs" / "Memoria_Daniel_Rubio_Rocamora.pdf"


def cabecera_y_pie(canvas_obj: canvas.Canvas, doc) -> None:
    """Dibuja la cabecera y el pie de cada página (excepto la portada)."""
    if doc.page == 1:
        return  # sin cabecera en la portada
    canvas_obj.saveState()

    # Cabecera: línea + texto
    canvas_obj.setStrokeColor(AZUL_OSCURO)
    canvas_obj.setLineWidth(0.6)
    canvas_obj.line(
        MARGEN_IZQ,
        A4[1] - MARGEN_SUP + 0.5 * cm,
        A4[0] - MARGEN_DER,
        A4[1] - MARGEN_SUP + 0.5 * cm,
    )
    canvas_obj.setFont("Times-Roman", 9)
    canvas_obj.setFillColor(GRIS_MEDIO)
    canvas_obj.drawString(
        MARGEN_IZQ,
        A4[1] - MARGEN_SUP + 0.7 * cm,
        "Memoria técnica · Learning Analytics seguro con criptografía y blockchain",
    )
    canvas_obj.drawRightString(
        A4[0] - MARGEN_DER,
        A4[1] - MARGEN_SUP + 0.7 * cm,
        "Daniel Rubio Rocamora · eUniv",
    )

    # Pie: línea + número de página
    canvas_obj.setLineWidth(0.4)
    canvas_obj.line(
        MARGEN_IZQ,
        MARGEN_INF - 0.7 * cm,
        A4[0] - MARGEN_DER,
        MARGEN_INF - 0.7 * cm,
    )
    canvas_obj.setFont("Times-Roman", 9)
    canvas_obj.setFillColor(GRIS_MEDIO)
    canvas_obj.drawRightString(
        A4[0] - MARGEN_DER,
        MARGEN_INF - 1.0 * cm,
        f"Página {doc.page}",
    )
    canvas_obj.drawString(
        MARGEN_IZQ,
        MARGEN_INF - 1.0 * cm,
        "Asignatura: Análisis de Datos 2, Criptografía, Blockchain y Learning Analytics",
    )

    canvas_obj.restoreState()


def main() -> None:
    RUTA_SALIDA.parent.mkdir(parents=True, exist_ok=True)
    print(f"Generando PDF en {RUTA_SALIDA}...")

    doc = BaseDocTemplate(
        str(RUTA_SALIDA),
        pagesize=A4,
        leftMargin=MARGEN_IZQ,
        rightMargin=MARGEN_DER,
        topMargin=MARGEN_SUP,
        bottomMargin=MARGEN_INF,
        title="Memoria técnica - Learning Analytics seguro",
        author="Daniel Rubio Rocamora",
        subject="Análisis de Datos 2, Criptografía, Blockchain y Learning Analytics",
        creator="Daniel Rubio Rocamora",
    )

    frame = Frame(
        doc.leftMargin,
        doc.bottomMargin,
        doc.width,
        doc.height,
        id="normal",
    )
    plantilla = PageTemplate(id="conCabecera", frames=frame, onPage=cabecera_y_pie)
    doc.addPageTemplates([plantilla])

    # ------------------------------------------------------------------
    # Ensamblar todos los flowables en orden
    # ------------------------------------------------------------------
    flowables = []
    flowables += construir_portada()
    flowables += construir_indice()
    flowables += construir_resumen_ejecutivo()
    flowables += construir_introduccion()
    flowables += construir_marco_teorico()
    flowables += construir_arquitectura()
    flowables += construir_implementacion()
    flowables += construir_validacion()
    flowables += construir_seguridad()
    flowables += construir_gdpr()
    flowables += construir_problemas()
    flowables += construir_conclusiones()
    flowables += construir_referencias()
    flowables += construir_anexo_github()

    print(f"  Flowables a renderizar: {len(flowables)}")
    doc.build(flowables)
    tamano_kb = RUTA_SALIDA.stat().st_size // 1024
    print(f"✓ PDF generado: {RUTA_SALIDA.name} ({tamano_kb} KB)")


if __name__ == "__main__":
    main()
