"""Secciones 6 (Validación), 7 (Seguridad) y 8 (GDPR)."""

from __future__ import annotations

from pathlib import Path

from pdf.estilos import (
    RAIZ,
    bullet,
    caja_destacada,
    espacio,
    figura,
    parrafo,
    salto_de_pagina,
    tabla,
    titulo_h1,
    titulo_h2,
    titulo_h3,
)


CARPETA_FIGURAS = RAIZ / "docs" / "figuras"
CARPETA_CAPTURAS = RAIZ / "docs" / "capturas"


def construir_validacion() -> list:
    flowables = []
    flowables.append(titulo_h1("6. Validación experimental"))

    flowables.append(parrafo(
        "Esta sección presenta los resultados experimentales obtenidos al ejecutar el "
        "sistema sobre un dataset sintético de 300 estudiantes generado por el propio "
        "proyecto. El conjunto se divide en un 75 % para entrenamiento (225 muestras) "
        "y un 25 % para test (75 muestras), manteniendo la estratificación de la "
        "variable objetivo en ambas particiones."
    ))

    flowables.append(titulo_h2("6.1. Resultados del modelo de Machine Learning"))
    flowables.append(parrafo(
        "Se han entrenado dos clasificadores: una <b>Regresión Logística</b> como "
        "baseline lineal interpretable y un <b>Random Forest</b> de 100 árboles como "
        "modelo no lineal de referencia. Ambos se han ajustado con la opción "
        "<i>class_weight=\"balanced\"</i> para compensar el desbalance moderado de las "
        "clases (75 % sin riesgo, 25 % en riesgo)."
    ))
    flowables.append(tabla(
        [
            ["Modelo", "Accuracy", "Precision", "Recall", "F1", "ROC-AUC"],
            ["Regresión Logística", "0,9733", "0,9444", "0,9444", "<b>0,9444</b>", "0,9893"],
            ["Random Forest", "0,9333", "0,9333", "0,7778", "0,8485", "<b>0,9961</b>"],
        ],
        anchos_relativos=[2.5, 1, 1, 1, 1, 1],
        primera_columna_destacada=True,
    ))
    flowables.append(espacio(4))
    flowables.append(parrafo(
        "Sorprendentemente, la Regresión Logística supera al Random Forest en F1, "
        "mientras que este último gana en ROC-AUC. La explicación es que la variable "
        "<i>media</i> está fuertemente correlacionada con el riesgo "
        "(coeficiente de Pearson -0,77), lo que hace que el problema sea casi "
        "linealmente separable. En ese escenario, un modelo lineal con regularización "
        "captura la frontera tan bien como uno más complejo. Esta observación apoya "
        "la heurística clásica de empezar siempre por el modelo más simple."
    ))

    flowables.append(espacio(4))
    flowables.extend(figura(
        CARPETA_FIGURAS / "01_distribucion_riesgo.png",
        ancho_cm=11,
        pie="Figura 1. Distribución de la variable objetivo: 226 estudiantes sin riesgo "
            "y 74 en riesgo.",
    ))
    flowables.extend(figura(
        CARPETA_FIGURAS / "03_matriz_correlacion.png",
        ancho_cm=15,
        pie="Figura 2. Matriz de correlación de Pearson. La variable <i>media</i> "
            "muestra la correlación más fuerte (negativa) con el riesgo.",
    ))

    flowables.append(salto_de_pagina())

    flowables.extend(figura(
        CARPETA_FIGURAS / "06_curva_roc.png",
        ancho_cm=12,
        pie="Figura 3. Curvas ROC superpuestas. Ambos modelos están muy cerca de la "
            "esquina superior izquierda, lo que indica una capacidad de discriminación "
            "casi perfecta.",
    ))

    flowables.extend(figura(
        CARPETA_FIGURAS / "08_importancia_variables.png",
        ancho_cm=13,
        pie="Figura 4. Importancia de variables según Random Forest. La nota media "
            "y el porcentaje de asistencia explican más de la mitad de la varianza.",
    ))

    flowables.append(salto_de_pagina())

    # ------------------------------------------------------------------
    # 6.2. Benchmarks
    # ------------------------------------------------------------------
    flowables.append(titulo_h2("6.2. Benchmarks de rendimiento"))
    flowables.append(parrafo(
        "Cada operación criptográfica relevante se ha medido sobre la misma máquina, "
        "promediando 100 repeticiones (10 para la generación de claves por su mayor "
        "coste). Los resultados confirman las hipótesis de diseño:"
    ))
    flowables.append(tabla(
        [
            ["Operación", "Tiempo medio (ms)"],
            ["Cifrado AES de un campo (Fernet)", "0,017"],
            ["Descifrado AES de un campo", "0,017"],
            ["Generación de par RSA-2048", "43"],
            ["Firma RSA-PSS-SHA256", "0,67"],
            ["Verificación de firma RSA-PSS", "0,03"],
            ["Minería PoW dificultad 2", "1,6"],
            ["Minería PoW dificultad 3 (configuración activa)", "<b>32</b>"],
            ["Minería PoW dificultad 4", "723"],
            ["Predicción ML lote de 75 estudiantes", "6,7"],
            ["Predicción ML para un estudiante", "6,5"],
        ],
        anchos_relativos=[4, 1],
        primera_columna_destacada=True,
    ))
    flowables.append(espacio(6))
    flowables.append(parrafo(
        "Tres observaciones importantes se desprenden de estas mediciones:"
    ))
    flowables.append(bullet(
        "<b>AES es aproximadamente 40 veces más rápido que firmar con RSA.</b> Esto "
        "valida cuantitativamente la decisión de usar AES para cifrar datos y RSA "
        "exclusivamente para firmas. Pretender cifrar 300 registros con RSA tomaría "
        "alrededor de 200 ms, frente a los 5 ms que tarda AES."
    ))
    flowables.append(bullet(
        "<b>Cada incremento de la dificultad de PoW multiplica el tiempo por "
        "aproximadamente 16</b> (16 = 16ⁿ⁺¹ / 16ⁿ, donde 16 corresponde a un dígito "
        "hexadecimal). La dificultad 3 ofrece un equilibrio adecuado entre seguridad "
        "demostrativa y experiencia de usuario."
    ))
    flowables.append(bullet(
        "<b>La predicción del modelo es prácticamente instantánea</b> y permite "
        "actualizar la tabla de alumnos en riesgo del dashboard del docente en tiempo "
        "real sin penalización perceptible."
    ))

    flowables.append(titulo_h2("6.3. Capturas del sistema en funcionamiento"))
    flowables.append(parrafo(
        "Las siguientes capturas, obtenidas automatizadamente con Playwright sobre "
        "el dashboard de Streamlit en modo headless, muestran las cuatro vistas "
        "principales del sistema."
    ))

    flowables.append(salto_de_pagina())

    flowables.extend(figura(
        CARPETA_CAPTURAS / "00_login.png",
        ancho_cm=15,
        pie="Figura 5. Pantalla de inicio de sesión. La tabla de credenciales demo "
            "facilita la evaluación pero quedaría oculta en producción.",
    ))
    flowables.extend(figura(
        CARPETA_CAPTURAS / "01_administrador.png",
        ancho_cm=15,
        pie="Figura 6. Panel del administrador. Muestra métricas globales, el estado "
            "de la cadena en el sidebar y los gráficos agregados (sin datos personales).",
    ))

    flowables.append(salto_de_pagina())

    flowables.extend(figura(
        CARPETA_CAPTURAS / "02_docente.png",
        ancho_cm=15,
        pie="Figura 7. Panel del docente. Lista los diez alumnos con mayor "
            "probabilidad de riesgo y permite registrar calificaciones que se firman "
            "y encadenan automáticamente.",
    ))
    flowables.extend(figura(
        CARPETA_CAPTURAS / "04_estudiante_riesgo.png",
        ancho_cm=15,
        pie="Figura 8. Panel personal de un estudiante en alto riesgo. Solo este "
            "estudiante puede ver su nombre real descifrado durante la sesión.",
    ))

    flowables.append(salto_de_pagina())
    return flowables


def construir_seguridad() -> list:
    flowables = []
    flowables.append(titulo_h1("7. Seguridad y demostración de manipulación"))

    flowables.append(titulo_h2("7.1. Vector de ataque simulado"))
    flowables.append(parrafo(
        "Para demostrar empíricamente la propiedad de inmutabilidad, se ha "
        "implementado un script (<i>demo_manipulacion.py</i>) que simula un atacante "
        "con permisos de escritura sobre el fichero JSON de la cadena. El ataque "
        "modifica directamente el contenido de una transacción ya minada — concretamente "
        "una calificación, intentando cambiar una nota baja por un 10,0:"
    ))
    flowables.append(caja_destacada(
        "<b>Antes del ataque (registro legítimo firmado por el docente):</b><br/>"
        "{\"id_estudiante\": \"EST-0128\", \"asignatura\": \"matematicas\", \"nota\": 3.5}<br/><br/>"
        "<b>Después del ataque (manipulado por el atacante):</b><br/>"
        "{\"id_estudiante\": \"EST-0128\", \"asignatura\": \"matematicas\", \"nota\": 10.0}"
    ))
    flowables.append(parrafo(
        "Al recargar el dashboard, el sidebar del administrador muestra inmediatamente "
        "el aviso <i>\"Cadena rota\"</i> con la causa exacta del problema: la raíz de "
        "Merkle del bloque alterado ya no coincide con sus transacciones."
    ))
    flowables.extend(figura(
        CARPETA_CAPTURAS / "05_manipulacion_detectada.png",
        ancho_cm=15,
        pie="Figura 9. Detección de manipulación en vivo. El sidebar muestra "
            "<i>“Cadena rota: Bloque 1: la raíz de Merkle no coincide con las "
            "transacciones”</i> a los pocos segundos del ataque.",
    ))
    flowables.append(parrafo(
        "Esta demostración confirma que el sistema cumple su objetivo principal: "
        "<b>aunque un atacante consiga acceso de escritura al almacenamiento, no "
        "puede modificar el contenido de un registro sin que la manipulación sea "
        "detectada en la siguiente verificación de integridad.</b>"
    ))

    flowables.append(salto_de_pagina())

    flowables.append(titulo_h2("7.2. Resultado de la auditoría con Bandit"))
    flowables.append(parrafo(
        "Se ha ejecutado Bandit, el analizador estático de seguridad estándar de la "
        "comunidad Python, sobre los cinco paquetes del proyecto. La ejecución inicial "
        "reportó cuatro hallazgos, todos analizados como falsos positivos en el "
        "contexto específico del proyecto:"
    ))
    flowables.append(tabla(
        [
            ["Código", "Severidad", "Ubicación", "Análisis"],
            [
                "B403", "Baja",
                "app/dashboard.py — <i>import pickle</i>",
                "Solo se usa para cargar el modelo ML generado por el propio "
                "bootstrap.py, nunca datos de origen externo.",
            ],
            [
                "B301", "Media",
                "app/dashboard.py — <i>pickle.load</i> (x2)",
                "Mismo razonamiento: origen confiable y local.",
            ],
            [
                "B311", "Baja",
                "data/generador_datos.py — <i>random.choices</i>",
                "Se usa para generar datos sintéticos, no para fines criptográficos. "
                "Las funciones criptográficas reales usan <i>os.urandom</i>.",
            ],
        ],
        anchos_relativos=[1, 1.4, 2.5, 4],
        primera_columna_destacada=True,
    ))
    flowables.append(espacio(6))
    flowables.append(parrafo(
        "Tras documentar cada hallazgo con anotaciones <i># nosec</i> que incluyen el "
        "código del check y una justificación, la ejecución final reporta:"
    ))
    flowables.append(caja_destacada(
        "<b>Resultados de Bandit:</b><br/>"
        "• Líneas de código escaneadas: 1372<br/>"
        "• Vulnerabilidades detectadas: <b>0</b><br/>"
        "• Hallazgos revisados manualmente y suprimidos: 4<br/>"
        "• Total de pruebas activas: 81<br/><br/>"
        "Esta es la práctica recomendada en la industria para falsos positivos confirmados: "
        "no se ocultan los hallazgos, se documentan explícitamente.",
    ))

    flowables.append(salto_de_pagina())
    return flowables


def construir_gdpr() -> list:
    flowables = []
    flowables.append(titulo_h1("8. Consideraciones éticas y GDPR"))

    flowables.append(parrafo(
        "Aunque se trata de un proyecto académico y todos los datos utilizados son "
        "sintéticos, se ha procurado diseñar el sistema siguiendo los principios del "
        "Reglamento General de Protección de Datos (Reglamento UE 2016/679) y las "
        "recomendaciones de la guía <i>Code of Practice for Learning Analytics</i> del "
        "JISC. Esta sección resume cómo se han aplicado los principales artículos "
        "del Reglamento."
    ))

    flowables.append(tabla(
        [
            ["Principio del GDPR", "Implementación en el proyecto"],
            [
                "Licitud, lealtad y transparencia (Art. 5.1.a)",
                "Todos los datos son sintéticos y generados por el propio sistema. "
                "Ninguna persona real está involucrada.",
            ],
            [
                "Limitación de la finalidad (Art. 5.1.b)",
                "Los datos se utilizan exclusivamente para detección de riesgo "
                "académico. El modelo no se reutiliza para otros fines.",
            ],
            [
                "Minimización de datos (Art. 5.1.c)",
                "El modelo de ML excluye explícitamente identificadores "
                "(<i>id_estudiante</i>, <i>nombre</i>, <i>email</i>) y se alimenta "
                "solo con variables relevantes para el riesgo.",
            ],
            [
                "Exactitud (Art. 5.1.d)",
                "Los registros se firman digitalmente. Cualquier modificación "
                "posterior queda detectada por la verificación de integridad.",
            ],
            [
                "Conservación (Art. 5.1.e)",
                "El diseño permite borrar registros sin romper la cadena, ya que "
                "el hash del bloque seguiría siendo válido.",
            ],
            [
                "Integridad y confidencialidad (Art. 5.1.f)",
                "Datos cifrados en reposo con AES-128 + HMAC. Contraseñas con "
                "PBKDF2 a 600 000 iteraciones.",
            ],
            [
                "Responsabilidad proactiva (Art. 5.2)",
                "Todas las operaciones sensibles se registran en la blockchain como "
                "log inmutable y auditable.",
            ],
            [
                "Registro de actividades (Art. 30)",
                "Cada consulta de un estudiante a sus propios datos genera una "
                "transacción <i>consulta_registro</i> firmada y encadenada.",
            ],
        ],
        anchos_relativos=[3, 5],
        primera_columna_destacada=True,
    ))

    flowables.append(espacio(8))
    flowables.append(titulo_h3("Decisiones específicas de privacidad"))
    flowables.append(bullet(
        "<b>Anonimización en gráficos agregados:</b> los gráficos públicos (distribución "
        "de riesgo, matriz de correlación) no muestran nombres ni identificadores."
    ))
    flowables.append(bullet(
        "<b>Descifrado bajo demanda:</b> los nombres reales solo se descifran en la "
        "vista personal del propio estudiante o cuando un docente con permisos lo "
        "solicita expresamente."
    ))
    flowables.append(bullet(
        "<b>Audit trail criptográfico:</b> cada acceso a un expediente queda registrado "
        "como transacción firmada en la blockchain, lo que satisface el principio de "
        "trazabilidad del artículo 30 sin depender de la confianza en el sistema de "
        "logs convencional."
    ))

    flowables.append(titulo_h3("Limitaciones reconocidas"))
    flowables.append(parrafo(
        "La herramienta utiliza una blockchain <b>local y centralizada</b> (un único "
        "fichero JSON en el servidor). Las propiedades de inmutabilidad son válidas "
        "frente a manipulación de un único actor que disponga de acceso de escritura, "
        "pero no frente al borrado completo del fichero. Para una implementación en "
        "producción habría que recurrir a una blockchain distribuida (Ethereum o "
        "Hyperledger Fabric) o a un servicio de <i>timestamping</i> confiable de "
        "terceros, como se discute en la sección de mejoras futuras."
    ))

    flowables.append(salto_de_pagina())
    return flowables
