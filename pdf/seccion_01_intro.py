"""Portada, índice y resumen ejecutivo del PDF."""

from __future__ import annotations

from datetime import date

from pdf.estilos import (
    AZUL_OSCURO,
    ESTILOS,
    bullet,
    caja_destacada,
    espacio,
    parrafo,
    salto_de_pagina,
    titulo_h1,
)
from reportlab.platypus import HRFlowable, Paragraph


def construir_portada() -> list:
    """Construye la portada de la memoria."""
    flowables = []
    flowables.append(espacio(30))
    flowables.append(HRFlowable(width="100%", thickness=2, color=AZUL_OSCURO, spaceAfter=16))
    flowables.append(parrafo("MEMORIA TÉCNICA", "portada_subtitulo"))
    flowables.append(parrafo(
        "Implementación de una<br/>herramienta de Learning Analytics<br/>con criptografía y blockchain",
        "portada_titulo",
    ))
    flowables.append(HRFlowable(width="60%", thickness=1, color=AZUL_OSCURO, spaceAfter=28, spaceBefore=8))

    flowables.append(espacio(8))
    flowables.append(parrafo(
        "<b>Asignatura:</b> Análisis de Datos 2, Criptografía,<br/>"
        "Blockchain y Learning Analytics",
        "portada_meta",
    ))
    flowables.append(espacio(6))
    flowables.append(parrafo("<b>Autor:</b> Daniel Rubio Rocamora", "portada_meta"))
    flowables.append(espacio(2))
    flowables.append(parrafo("<b>Profesor:</b> Juan Moya Sáez", "portada_meta"))
    flowables.append(espacio(2))
    flowables.append(parrafo(
        "<b>Centro:</b> eUniv · Universitas Europaea IMF",
        "portada_meta",
    ))
    flowables.append(espacio(2))
    flowables.append(parrafo(
        f"<b>Curso:</b> 2025 / 2026 &nbsp;&nbsp; <b>Fecha:</b> {date.today().strftime('%d de %B de %Y').replace('January', 'enero').replace('February', 'febrero').replace('March', 'marzo').replace('April', 'abril').replace('May', 'mayo').replace('June', 'junio').replace('July', 'julio').replace('August', 'agosto').replace('September', 'septiembre').replace('October', 'octubre').replace('November', 'noviembre').replace('December', 'diciembre')}",
        "portada_meta",
    ))

    flowables.append(espacio(20))
    flowables.append(HRFlowable(width="100%", thickness=0.5, color=AZUL_OSCURO, spaceAfter=10))
    flowables.append(parrafo(
        "<i>Código fuente disponible en GitHub. Ver Anexo A para el enlace y las instrucciones de despliegue.</i>",
        "cuerpo_pequeno",
    ))

    flowables.append(salto_de_pagina())
    return flowables


def construir_indice() -> list:
    """Construye un índice estático (sin auto-numeración de páginas)."""
    flowables = []
    flowables.append(titulo_h1("Índice"))
    flowables.append(espacio(6))

    estructura = [
        ("1. Resumen ejecutivo", "h1"),
        ("2. Introducción y objetivos", "h1"),
        ("    2.1. Contexto del trabajo", "h2"),
        ("    2.2. Objetivos específicos", "h2"),
        ("    2.3. Público objetivo", "h2"),
        ("3. Marco teórico", "h1"),
        ("    3.1. Learning Analytics", "h2"),
        ("    3.2. Criptografía simétrica y asimétrica", "h2"),
        ("    3.3. Funciones hash y blockchain", "h2"),
        ("4. Arquitectura del sistema", "h1"),
        ("    4.1. Visión general", "h2"),
        ("    4.2. Decisiones técnicas y justificación", "h2"),
        ("5. Implementación", "h1"),
        ("    5.1. Módulo de criptografía", "h2"),
        ("    5.2. Módulo de blockchain", "h2"),
        ("    5.3. Módulo de analítica y modelo ML", "h2"),
        ("    5.4. Dashboard y autenticación con roles", "h2"),
        ("6. Validación experimental", "h1"),
        ("    6.1. Resultados del modelo de Machine Learning", "h2"),
        ("    6.2. Benchmarks de rendimiento", "h2"),
        ("    6.3. Capturas del sistema en funcionamiento", "h2"),
        ("7. Seguridad y demostración de manipulación", "h1"),
        ("    7.1. Vector de ataque simulado", "h2"),
        ("    7.2. Resultado de la auditoría con Bandit", "h2"),
        ("8. Consideraciones éticas y GDPR", "h1"),
        ("9. Problemas encontrados y aprendizajes", "h1"),
        ("10. Conclusiones y mejoras futuras", "h1"),
        ("11. Referencias bibliográficas", "h1"),
        ("Anexo A. Acceso al código fuente", "h1"),
    ]
    for texto, nivel in estructura:
        if nivel == "h1":
            flowables.append(Paragraph(texto, ESTILOS["toc_h1"]))
        else:
            flowables.append(Paragraph(texto, ESTILOS["toc_h2"]))

    flowables.append(salto_de_pagina())
    return flowables


def construir_resumen_ejecutivo() -> list:
    """Sección de resumen ejecutivo, una página."""
    flowables = []
    flowables.append(titulo_h1("1. Resumen ejecutivo"))

    flowables.append(parrafo(
        "Este trabajo presenta el diseño, la implementación y la validación de una "
        "herramienta de Learning Analytics que integra criptografía moderna y blockchain "
        "para proteger la privacidad y garantizar la integridad de los registros "
        "educativos. El sistema está implementado en Python y se materializa en un "
        "dashboard interactivo desarrollado con Streamlit que admite tres roles "
        "diferenciados: administrador, docente y estudiante."
    ))

    flowables.append(parrafo(
        "Los datos educativos sensibles (nombres, correos, calificaciones) se cifran con "
        "AES-128 vía Fernet, las operaciones sobre los registros se firman con RSA-2048 "
        "usando el padding probabilístico PSS, y todas las acciones quedan registradas "
        "en una cadena de bloques propia con SHA-256, raíz de Merkle y Proof-of-Work "
        "configurable. Sobre esta capa segura se construye un modelo de Machine Learning "
        "que predice el riesgo académico, comparando regresión logística y Random Forest."
    ))

    flowables.append(caja_destacada(
        "<b>Resultados destacados:</b> 69 pruebas unitarias en verde, 0 vulnerabilidades "
        "detectadas por Bandit, F1 de 0,944 en el mejor modelo, latencia de cifrado "
        "AES de 0,017 ms por campo, detección satisfactoria de manipulaciones en la "
        "cadena de bloques validada experimentalmente."
    ))

    flowables.append(parrafo(
        "El trabajo aplica de forma práctica el contenido teórico de la asignatura: "
        "matemática discreta y teoría de números (clase 1), fundamentos de criptografía "
        "simétrica y asimétrica (clases 2 a 4), funciones hash (clase 5), blockchain y "
        "sus aplicaciones (clases 6 a 8), minería de datos y aprendizaje supervisado "
        "(clases 9 a 11), y desarrollo de herramientas de Learning Analytics "
        "(clases 22 a 26). Las decisiones técnicas se justifican apoyándose tanto en el "
        "material del curso como en las recomendaciones de OWASP y NIST para producción."
    ))

    flowables.append(salto_de_pagina())
    return flowables
