"""Secciones 2 (Introducción y objetivos) y 3 (Marco teórico)."""

from __future__ import annotations

from pdf.estilos import (
    bullet,
    espacio,
    parrafo,
    salto_de_pagina,
    tabla,
    titulo_h1,
    titulo_h2,
)


def construir_introduccion() -> list:
    flowables = []
    flowables.append(titulo_h1("2. Introducción y objetivos"))

    flowables.append(titulo_h2("2.1. Contexto del trabajo"))
    flowables.append(parrafo(
        "Las plataformas educativas en línea generan, día a día, grandes volúmenes de "
        "datos relativos al rendimiento, la participación y la trayectoria académica de "
        "los estudiantes. Estos datos son enormemente valiosos para la mejora de la "
        "calidad docente (Learning Analytics), pero a la vez son extremadamente "
        "sensibles: incluyen calificaciones, hábitos de estudio e información personal "
        "identificable. Una herramienta que pretenda explotar analíticamente esta "
        "información necesita, por tanto, integrar mecanismos sólidos de protección de "
        "datos y de garantía de su integridad."
    ))
    flowables.append(parrafo(
        "La asignatura aborda esta intersección desde tres ángulos complementarios: "
        "la criptografía como mecanismo para preservar la confidencialidad y la "
        "autenticidad, el blockchain como tecnología de inmutabilidad e "
        "auditabilidad, y el Learning Analytics como disciplina que aplica la "
        "minería de datos y el aprendizaje automático al ámbito educativo."
    ))

    flowables.append(titulo_h2("2.2. Objetivos específicos"))
    flowables.append(parrafo("El proyecto persigue los siguientes objetivos concretos:"))
    objetivos = [
        "Implementar un módulo de cifrado simétrico para proteger los campos sensibles "
        "del registro educativo en reposo, derivando la clave a partir de la contraseña "
        "del usuario con PBKDF2.",
        "Construir un módulo de criptografía asimétrica RSA-2048 que permita firmar "
        "digitalmente cada operación del sistema, garantizando autenticación y no repudio.",
        "Desarrollar una cadena de bloques propia con SHA-256 y Proof-of-Work, que sirva "
        "como registro inmutable y auditable de todas las acciones realizadas sobre los "
        "expedientes.",
        "Entrenar y comparar dos modelos de Machine Learning para la detección de "
        "estudiantes en riesgo académico, evaluando su desempeño con métricas estándar.",
        "Integrar todo lo anterior en un dashboard interactivo (Streamlit) con tres "
        "roles diferenciados y permisos coherentes con el principio de mínimo privilegio.",
        "Validar la herramienta con pruebas unitarias automatizadas y un análisis de "
        "seguridad estático mediante Bandit.",
        "Documentar todas las decisiones técnicas y discutir las implicaciones éticas "
        "y legales (GDPR) del tratamiento de datos educativos.",
    ]
    for o in objetivos:
        flowables.append(bullet(o))

    flowables.append(titulo_h2("2.3. Público objetivo"))
    flowables.append(parrafo(
        "La herramienta está diseñada para ser utilizada por tres tipos de usuario "
        "dentro de una institución educativa, cada uno con un nivel de acceso "
        "diferenciado y con su propia vista del dashboard:"
    ))
    flowables.append(tabla(
        [
            ["Rol", "Casos de uso principales", "Nivel de acceso"],
            [
                "Administrador",
                "Supervisar el estado global del sistema, comprobar la integridad de "
                "la cadena de bloques en tiempo real, auditar el log de operaciones y "
                "gestionar los usuarios registrados.",
                "Datos agregados y anonimizados de todos los estudiantes.",
            ],
            [
                "Docente",
                "Identificar alumnos en riesgo, registrar calificaciones firmadas "
                "digitalmente y consultar las predicciones del modelo de ML para "
                "intervenir a tiempo.",
                "Datos personales y académicos de los alumnos de su grupo.",
            ],
            [
                "Estudiante",
                "Consultar sus propias calificaciones, su porcentaje de asistencia y "
                "su histórico de operaciones en la cadena de bloques (transparencia "
                "GDPR).",
                "Exclusivamente sus propios datos, descifrados con su clave privada.",
            ],
        ],
        anchos_relativos=[1.4, 4, 2.2],
        primera_columna_destacada=True,
    ))

    flowables.append(salto_de_pagina())
    return flowables


def construir_marco_teorico() -> list:
    flowables = []
    flowables.append(titulo_h1("3. Marco teórico"))

    flowables.append(parrafo(
        "Esta sección sintetiza los fundamentos teóricos que sustentan las decisiones "
        "técnicas del proyecto. Para cada bloque se cita el material del curso que "
        "lo introduce y se complementa con la bibliografía estándar de referencia."
    ))

    # -------------------- 3.1. Learning Analytics --------------------
    flowables.append(titulo_h2("3.1. Learning Analytics"))
    flowables.append(parrafo(
        "Learning Analytics (LA) es la disciplina interdisciplinar que combina "
        "técnicas de minería de datos, inteligencia artificial, estadística y "
        "psicopedagogía para analizar cómo los estudiantes interactúan con los "
        "entornos educativos. Sus principales aplicaciones, tal y como se introducen "
        "en la unidad 11 del temario, son:"
    ))
    flowables.append(bullet(
        "<b>Identificación temprana de estudiantes en riesgo:</b> detectar patrones "
        "de bajo rendimiento o abandono antes de que ocurran problemas graves. Este es "
        "precisamente el caso de uso central del proyecto."
    ))
    flowables.append(bullet(
        "<b>Personalización del aprendizaje:</b> adaptar el contenido y las estrategias "
        "pedagógicas a las necesidades individuales de cada estudiante."
    ))
    flowables.append(bullet(
        "<b>Optimización de recursos educativos:</b> mejorar el diseño de los cursos y "
        "el uso eficiente de los materiales de aprendizaje."
    ))
    flowables.append(bullet(
        "<b>Retroalimentación basada en datos:</b> proporcionar información objetiva "
        "tanto a docentes como a estudiantes sobre el progreso y el rendimiento académico."
    ))
    flowables.append(parrafo(
        "Dentro de LA, la detección de riesgo se aborda típicamente como un problema "
        "de clasificación binaria supervisada, donde la variable objetivo indica si un "
        "estudiante terminará en una situación de fracaso académico. Es justamente el "
        "planteamiento que se sigue en este trabajo."
    ))

    # -------------------- 3.2. Criptografía --------------------
    flowables.append(titulo_h2("3.2. Criptografía simétrica y asimétrica"))
    flowables.append(parrafo(
        "La criptografía moderna se sustenta sobre dos paradigmas complementarios. "
        "La <b>criptografía simétrica</b>, tratada en la unidad 3 del temario, utiliza "
        "una única clave compartida tanto para cifrar como para descifrar. Es muy "
        "rápida y adecuada para grandes volúmenes de datos, pero requiere un canal "
        "seguro previo para intercambiar la clave. El estándar actual es AES "
        "(Advanced Encryption Standard), disponible en variantes de 128, 192 y 256 bits."
    ))
    flowables.append(parrafo(
        "La <b>criptografía asimétrica</b>, presentada en la unidad 4, utiliza un par "
        "de claves matemáticamente relacionadas: una clave pública, que puede "
        "compartirse libremente, y una clave privada, que debe mantenerse en secreto. "
        "Este enfoque resuelve el problema del intercambio inicial de claves y habilita "
        "dos primitivas fundamentales:"
    ))
    flowables.append(bullet(
        "<b>Cifrado y descifrado:</b> el emisor cifra el mensaje con la clave pública "
        "del destinatario; solo este, con su clave privada, puede descifrarlo."
    ))
    flowables.append(bullet(
        "<b>Firma digital y verificación:</b> el firmante usa su clave privada para "
        "generar una firma sobre un mensaje; cualquiera con su clave pública puede "
        "verificarla y comprobar así la autenticidad e integridad del mensaje."
    ))
    flowables.append(parrafo(
        "El algoritmo asimétrico más utilizado en la actualidad es RSA "
        "(Rivest-Shamir-Adleman, 1977), cuya seguridad se basa en la dificultad de "
        "factorizar números grandes en sus factores primos. En este proyecto se utiliza "
        "RSA-2048 con padding PSS (Probabilistic Signature Scheme), que es la "
        "recomendación de NIST y OWASP para nuevas aplicaciones."
    ))
    flowables.append(parrafo(
        "En la práctica, ambos paradigmas se combinan en lo que se conoce como "
        "<b>cifrado híbrido</b>: AES protege los datos por su rapidez, mientras que "
        "RSA se utiliza para firmar las operaciones y para cifrar (o derivar) la clave "
        "AES cuando es necesario transportarla. Este patrón es justamente el que se "
        "aplica en la herramienta presentada."
    ))

    # -------------------- 3.3. Hash y blockchain --------------------
    flowables.append(titulo_h2("3.3. Funciones hash y blockchain"))
    flowables.append(parrafo(
        "Una <b>función hash criptográfica</b> es una función determinista que toma "
        "un mensaje de longitud arbitraria y devuelve un valor de longitud fija. Una "
        "buena función hash debe cumplir tres propiedades: resistencia a colisiones "
        "(es computacionalmente inviable encontrar dos mensajes distintos con el mismo "
        "hash), resistencia a la preimagen (dado un hash, es inviable encontrar el "
        "mensaje original) y efecto avalancha (un cambio mínimo en la entrada produce "
        "un hash completamente diferente). El estándar utilizado en este proyecto es "
        "SHA-256, el mismo algoritmo en el que se basa Bitcoin."
    ))
    flowables.append(parrafo(
        "Una <b>blockchain</b>, tal y como se describe en la unidad 5 del temario, es "
        "una estructura de datos compuesta por bloques enlazados en los que cada bloque "
        "contiene el hash del bloque anterior. Esto crea una cadena en la que la "
        "modificación de cualquier bloque pasado invalidaría los hashes de todos los "
        "bloques posteriores. Si además se requiere que el hash de cada bloque cumpla "
        "una condición específica (por ejemplo, comenzar con N ceros), se obtiene un "
        "mecanismo de Proof-of-Work que dificulta exponencialmente reescribir el "
        "histórico."
    ))
    flowables.append(parrafo(
        "Los bloques pueden contener múltiples transacciones, organizadas habitualmente "
        "en un árbol de Merkle (unidad 5). La raíz de Merkle resume todas las "
        "transacciones del bloque y permite verificar de forma eficiente la inclusión "
        "de una transacción sin tener que descargar el bloque entero. Este patrón se ha "
        "reproducido fielmente en la implementación."
    ))

    flowables.append(salto_de_pagina())
    return flowables
