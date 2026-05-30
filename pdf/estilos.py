"""Estilos y utilidades compartidos por el generador del PDF.

Define la paleta sobria, los estilos de párrafo, los encabezados y los flowables
auxiliares (código, tablas, separadores) que se usan en todas las secciones de
la memoria.
"""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)


RAIZ = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Paleta
# ---------------------------------------------------------------------------
AZUL_OSCURO = colors.HexColor("#1f4e79")
AZUL_MEDIO = colors.HexColor("#4a90c2")
AZUL_CLARO = colors.HexColor("#dbe7f3")
GRIS_TEXTO = colors.HexColor("#333333")
GRIS_MEDIO = colors.HexColor("#6c757d")
GRIS_CLARO = colors.HexColor("#dee2e6")
GRIS_FONDO_CODIGO = colors.HexColor("#f4f6f8")
ROJO_ATENCION = colors.HexColor("#c0392b")
VERDE_OK = colors.HexColor("#2e7d32")

# ---------------------------------------------------------------------------
# Geometría de página
# ---------------------------------------------------------------------------
MARGEN_IZQ = 2.4 * cm
MARGEN_DER = 2.4 * cm
MARGEN_SUP = 2.5 * cm
MARGEN_INF = 2.5 * cm
ANCHO_UTIL = A4[0] - MARGEN_IZQ - MARGEN_DER


# ---------------------------------------------------------------------------
# Estilos de párrafo
# ---------------------------------------------------------------------------
def construir_estilos() -> dict:
    """Devuelve un diccionario con todos los estilos personalizados."""
    base = getSampleStyleSheet()
    estilos: dict[str, ParagraphStyle] = {}

    estilos["portada_titulo"] = ParagraphStyle(
        "PortadaTitulo",
        parent=base["Title"],
        fontName="Times-Bold",
        fontSize=28,
        leading=34,
        textColor=AZUL_OSCURO,
        alignment=TA_LEFT,
        spaceAfter=20,
    )
    estilos["portada_subtitulo"] = ParagraphStyle(
        "PortadaSubtitulo",
        parent=base["Title"],
        fontName="Times-Italic",
        fontSize=16,
        leading=22,
        textColor=GRIS_MEDIO,
        alignment=TA_LEFT,
        spaceAfter=40,
    )
    estilos["portada_meta"] = ParagraphStyle(
        "PortadaMeta",
        parent=base["Normal"],
        fontName="Times-Roman",
        fontSize=12,
        leading=18,
        textColor=GRIS_TEXTO,
        alignment=TA_LEFT,
    )

    estilos["h1"] = ParagraphStyle(
        "Heading1Personal",
        parent=base["Heading1"],
        fontName="Times-Bold",
        fontSize=18,
        leading=24,
        textColor=AZUL_OSCURO,
        spaceBefore=18,
        spaceAfter=14,
        keepWithNext=True,
    )
    estilos["h2"] = ParagraphStyle(
        "Heading2Personal",
        parent=base["Heading2"],
        fontName="Times-Bold",
        fontSize=14,
        leading=20,
        textColor=AZUL_OSCURO,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True,
    )
    estilos["h3"] = ParagraphStyle(
        "Heading3Personal",
        parent=base["Heading3"],
        fontName="Times-Bold",
        fontSize=12,
        leading=16,
        textColor=GRIS_TEXTO,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True,
    )

    estilos["cuerpo"] = ParagraphStyle(
        "Cuerpo",
        parent=base["Normal"],
        fontName="Times-Roman",
        fontSize=11,
        leading=16,
        textColor=GRIS_TEXTO,
        alignment=TA_JUSTIFY,
        spaceAfter=8,
        firstLineIndent=0,
    )
    estilos["cuerpo_centrado"] = ParagraphStyle(
        "CuerpoCentrado",
        parent=estilos["cuerpo"],
        alignment=TA_CENTER,
    )
    estilos["cuerpo_pequeno"] = ParagraphStyle(
        "CuerpoPequeno",
        parent=estilos["cuerpo"],
        fontSize=9,
        leading=12,
        textColor=GRIS_MEDIO,
        alignment=TA_LEFT,
    )
    estilos["pie_figura"] = ParagraphStyle(
        "PieFigura",
        parent=base["Normal"],
        fontName="Times-Italic",
        fontSize=9,
        leading=12,
        textColor=GRIS_MEDIO,
        alignment=TA_CENTER,
        spaceBefore=4,
        spaceAfter=14,
    )
    estilos["bullet"] = ParagraphStyle(
        "BulletPersonal",
        parent=estilos["cuerpo"],
        leftIndent=18,
        bulletIndent=4,
        spaceAfter=4,
    )
    estilos["cita"] = ParagraphStyle(
        "Cita",
        parent=estilos["cuerpo"],
        fontName="Times-Italic",
        leftIndent=20,
        rightIndent=20,
        textColor=GRIS_MEDIO,
        spaceBefore=6,
        spaceAfter=10,
    )
    estilos["codigo_titulo"] = ParagraphStyle(
        "CodigoTitulo",
        parent=base["Normal"],
        fontName="Times-Bold",
        fontSize=10,
        textColor=AZUL_OSCURO,
        spaceBefore=10,
        spaceAfter=4,
    )
    estilos["toc_h1"] = ParagraphStyle(
        "TOCh1",
        parent=base["Normal"],
        fontName="Times-Bold",
        fontSize=11,
        leading=15,
        textColor=AZUL_OSCURO,
        spaceBefore=6,
    )
    estilos["toc_h2"] = ParagraphStyle(
        "TOCh2",
        parent=base["Normal"],
        fontName="Times-Roman",
        fontSize=10,
        leading=14,
        leftIndent=16,
        textColor=GRIS_TEXTO,
    )

    return estilos


ESTILOS = construir_estilos()


# ---------------------------------------------------------------------------
# Helpers de flowables
# ---------------------------------------------------------------------------
def parrafo(texto: str, estilo: str = "cuerpo"):
    """Construye un Paragraph con el estilo indicado."""
    return Paragraph(texto, ESTILOS[estilo])


def titulo_h1(texto: str):
    return parrafo(texto, "h1")


def titulo_h2(texto: str):
    return parrafo(texto, "h2")


def titulo_h3(texto: str):
    return parrafo(texto, "h3")


def espacio(altura_mm: float = 4):
    return Spacer(1, altura_mm * mm)


def salto_de_pagina():
    return PageBreak()


def bullet(texto: str):
    return Paragraph(f"• {texto}", ESTILOS["bullet"])


def fragmento_codigo(codigo: str, titulo: str | None = None) -> list:
    """Devuelve flowables para un fragmento de código con título opcional."""
    flowables = []
    if titulo:
        flowables.append(Paragraph(titulo, ESTILOS["codigo_titulo"]))
    estilo_codigo = ParagraphStyle(
        "PreformattedPersonal",
        fontName="Courier",
        fontSize=8.5,
        leading=11,
        leftIndent=8,
        rightIndent=8,
        textColor=GRIS_TEXTO,
        backColor=GRIS_FONDO_CODIGO,
        borderColor=GRIS_CLARO,
        borderWidth=0.5,
        borderPadding=6,
        spaceBefore=2,
        spaceAfter=10,
    )
    flowables.append(Preformatted(codigo.rstrip(), estilo_codigo))
    return flowables


def figura(ruta: Path, ancho_cm: float = 14, pie: str | None = None) -> list:
    """Inserta una imagen escalada a `ancho_cm`, con pie de figura opcional."""
    if not Path(ruta).exists():
        return [parrafo(f"<i>[Figura no encontrada: {Path(ruta).name}]</i>")]
    img = Image(str(ruta), width=ancho_cm * cm, height=ancho_cm * cm * 0.65, kind="proportional")
    img.hAlign = "CENTER"
    flowables = [img]
    if pie:
        flowables.append(Paragraph(pie, ESTILOS["pie_figura"]))
    return flowables


def tabla(
    datos: list[list],
    anchos_relativos: list[float] | None = None,
    fila_cabecera: bool = True,
    primera_columna_destacada: bool = False,
) -> Table:
    """Construye una Table de ReportLab con estilo coherente con el resto del PDF."""
    if anchos_relativos:
        total = sum(anchos_relativos)
        anchos = [ANCHO_UTIL * (r / total) for r in anchos_relativos]
    else:
        anchos = None

    # Convertir strings a Paragraphs para que admitan word-wrap
    datos_procesados = []
    for fila_idx, fila in enumerate(datos):
        nueva_fila = []
        for col_idx, celda in enumerate(fila):
            if isinstance(celda, str):
                if fila_cabecera and fila_idx == 0:
                    estilo = ParagraphStyle(
                        "CeldaCabecera",
                        fontName="Times-Bold",
                        fontSize=10,
                        leading=13,
                        textColor=colors.white,
                        alignment=TA_LEFT,
                    )
                elif primera_columna_destacada and col_idx == 0:
                    estilo = ParagraphStyle(
                        "CeldaPrimera",
                        fontName="Times-Bold",
                        fontSize=9.5,
                        leading=13,
                        textColor=AZUL_OSCURO,
                        alignment=TA_LEFT,
                    )
                else:
                    estilo = ParagraphStyle(
                        "CeldaCuerpo",
                        fontName="Times-Roman",
                        fontSize=9.5,
                        leading=13,
                        textColor=GRIS_TEXTO,
                        alignment=TA_LEFT,
                    )
                nueva_fila.append(Paragraph(celda, estilo))
            else:
                nueva_fila.append(celda)
        datos_procesados.append(nueva_fila)

    t = Table(datos_procesados, colWidths=anchos, repeatRows=1 if fila_cabecera else 0)
    estilo_tabla = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("GRID", (0, 0), (-1, -1), 0.3, GRIS_CLARO),
    ]
    if fila_cabecera:
        estilo_tabla.append(("BACKGROUND", (0, 0), (-1, 0), AZUL_OSCURO))
    estilo_tabla.append(("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, GRIS_FONDO_CODIGO]))
    t.setStyle(TableStyle(estilo_tabla))
    return t


def caja_destacada(texto: str, color_fondo=AZUL_CLARO, color_borde=AZUL_MEDIO) -> Table:
    """Caja de texto destacado (para resúmenes ejecutivos, notas, etc.)."""
    estilo_interior = ParagraphStyle(
        "CajaInterior",
        fontName="Times-Roman",
        fontSize=10.5,
        leading=15,
        textColor=GRIS_TEXTO,
        alignment=TA_JUSTIFY,
    )
    contenido = [[Paragraph(texto, estilo_interior)]]
    t = Table(contenido, colWidths=[ANCHO_UTIL])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), color_fondo),
        ("BOX", (0, 0), (-1, -1), 1, color_borde),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    return t
