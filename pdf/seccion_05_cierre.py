"""Secciones 9 (Problemas), 10 (Conclusiones), 11 (Referencias) y Anexo A (GitHub)."""

from __future__ import annotations

from pdf.estilos import (
    bullet,
    caja_destacada,
    espacio,
    parrafo,
    salto_de_pagina,
    tabla,
    titulo_h1,
    titulo_h2,
    titulo_h3,
)


def construir_problemas() -> list:
    flowables = []
    flowables.append(titulo_h1("9. Problemas encontrados y aprendizajes"))

    flowables.append(parrafo(
        "Durante el desarrollo iterativo del proyecto se encontraron varios problemas "
        "interesantes cuya resolución dejó aprendizajes valiosos. Se describen los "
        "más representativos."
    ))

    flowables.append(titulo_h3("9.1. Inconsistencia de dificultad en la cadena al persistir y recargar"))
    flowables.append(parrafo(
        "<b>Síntoma:</b> tras reejecutar el bootstrap varias veces durante el desarrollo "
        "del dashboard, este mostraba <i>“Cadena rota”</i> aunque las pruebas unitarias "
        "pasaban en aislamiento."
    ))
    flowables.append(parrafo(
        "<b>Causa:</b> la función <i>cargar_o_crear_cadena</i> recibía el parámetro "
        "<i>dificultad=3</i> y, al encontrar un fichero JSON existente, sobrescribía "
        "el atributo correspondiente en la cadena cargada. Sin embargo, los bloques "
        "almacenados habían sido minados con dificultad menor en pruebas previas, por "
        "lo que la verificación de Proof-of-Work fallaba al exigir tres ceros iniciales "
        "a hashes que solo tenían dos."
    ))
    flowables.append(parrafo(
        "<b>Solución:</b> se modificó el método para que <b>respete la dificultad "
        "almacenada en el fichero</b> y nunca la sobrescriba al cargar. La dificultad "
        "solo se fija al crear la cadena por primera vez. Para cambiarla, se debe "
        "regenerar la cadena desde cero."
    ))
    flowables.append(parrafo(
        "<b>Aprendizaje:</b> la persistencia y la configuración son dos aspectos "
        "distintos. Sobrescribir la configuración del estado persistido es siempre "
        "una invitación a inconsistencias. La regla general es <i>“el fichero es la "
        "fuente de verdad”</i>: la configuración se aplica al crear, no al cargar."
    ))

    flowables.append(titulo_h3("9.2. Capturas vacías con Playwright"))
    flowables.append(parrafo(
        "<b>Síntoma:</b> las primeras capturas automatizadas del dashboard mostraban "
        "solo el título y un fondo blanco — el contenido no había terminado de "
        "renderizar cuando se tomaba la imagen."
    ))
    flowables.append(parrafo(
        "<b>Causa:</b> Streamlit renderiza progresivamente y los gráficos de Matplotlib "
        "se inyectan a través de llamadas asíncronas. Un <i>wait_for_timeout</i> de 3 "
        "segundos no es suficiente para vistas pesadas como la del administrador, que "
        "carga modelo, dataset y tres gráficos."
    ))
    flowables.append(parrafo(
        "<b>Solución:</b> se combinó <i>page.wait_for_load_state(\"networkidle\")</i> "
        "con un margen explícito de 3,5 segundos tras cada acción y una espera "
        "explícita por el selector del campo de usuario en la pantalla de login. Las "
        "capturas resultantes son consistentes y reproducibles."
    ))

    flowables.append(titulo_h3("9.3. Reproducibilidad de los tests de Machine Learning"))
    flowables.append(parrafo(
        "<b>Síntoma:</b> ocasionalmente, el test que validaba el F1 mínimo de la "
        "regresión logística fallaba con valores ligeramente por debajo del umbral."
    ))
    flowables.append(parrafo(
        "<b>Causa:</b> distintas semillas aleatorias en <i>numpy</i> y en el módulo "
        "<i>random</i> de Python provocaban variaciones en la división estratificada "
        "del dataset entre ejecuciones, lo que cambiaba marginalmente los resultados "
        "del modelo."
    ))
    flowables.append(parrafo(
        "<b>Solución:</b> se definió una semilla común "
        "(<i>SEMILLA = 42</i>) en el módulo de preprocesamiento y se aplicó tanto a "
        "<i>numpy</i> como a <i>random</i> y a <i>Faker</i>. Los resultados son ahora "
        "completamente reproducibles."
    ))
    flowables.append(parrafo(
        "<b>Aprendizaje:</b> la reproducibilidad en proyectos de ML no es accidental; "
        "hay que fijar explícitamente todas las fuentes de aleatoriedad. Esta práctica "
        "es además un requisito implícito de cualquier publicación científica."
    ))

    flowables.append(titulo_h3("9.4. Falsos positivos en el análisis de seguridad"))
    flowables.append(parrafo(
        "<b>Síntoma:</b> Bandit reportaba inicialmente cuatro hallazgos de severidad "
        "media-baja relacionados con <i>pickle</i> y <i>random</i>."
    ))
    flowables.append(parrafo(
        "<b>Causa:</b> ambos usos son legítimos pero requieren contextualización: "
        "<i>pickle.load</i> solo se aplica a modelos generados por el propio "
        "<i>bootstrap.py</i>, y <i>random.choices</i> sirve para generar datos "
        "sintéticos, nunca para fines criptográficos (que sí usan <i>os.urandom</i>)."
    ))
    flowables.append(parrafo(
        "<b>Solución:</b> ambos usos se marcaron con anotaciones "
        "<i># nosec [BXXX]</i> acompañadas de la justificación. Bandit pasó a reportar "
        "<b>0 hallazgos con 4 supresiones documentadas</b>, que es el patrón "
        "recomendado por la industria para falsos positivos confirmados."
    ))
    flowables.append(parrafo(
        "<b>Aprendizaje:</b> ignorar avisos del analizador estático es un error; "
        "documentarlos explícitamente con su justificación es buena ingeniería y deja "
        "trazabilidad para futuros mantenedores."
    ))

    flowables.append(salto_de_pagina())
    return flowables


def construir_conclusiones() -> list:
    flowables = []
    flowables.append(titulo_h1("10. Conclusiones y mejoras futuras"))

    flowables.append(titulo_h2("10.1. Conclusiones"))
    flowables.append(parrafo(
        "El proyecto ha cumplido los objetivos planteados en la sección 2. La "
        "herramienta entregada integra de forma coherente las tres áreas centrales de "
        "la asignatura — criptografía, blockchain y Learning Analytics — en un sistema "
        "funcional, probado y auditado."
    ))
    flowables.append(parrafo("Los principales hitos alcanzados son:"))
    flowables.append(bullet(
        "Implementación correcta y probada de las primitivas criptográficas (AES, RSA, "
        "SHA-256, PBKDF2) usando exclusivamente la librería <i>cryptography</i>, que "
        "es la referencia de la comunidad Python."
    ))
    flowables.append(bullet(
        "Cadena de bloques propia con todas las propiedades esperadas: enlace por "
        "hash, raíz de Merkle, Proof-of-Work y verificación de integridad robusta, "
        "demostrada experimentalmente frente a un ataque simulado."
    ))
    flowables.append(bullet(
        "Modelo de Machine Learning con F1 de 0,944, suficiente para un escenario "
        "real, junto con una comparativa pedagógica entre dos enfoques (lineal y de "
        "ensemble) y la justificación de por qué el modelo simple supera al complejo "
        "en este problema concreto."
    ))
    flowables.append(bullet(
        "Dashboard interactivo con tres roles, autenticación robusta y registro "
        "automático de operaciones firmadas en la blockchain — todo ello en menos "
        "de 400 líneas de Streamlit."
    ))
    flowables.append(bullet(
        "Suite de 69 pruebas pytest y auditoría Bandit limpia, con documentación "
        "completa de todas las decisiones técnicas tomadas."
    ))
    flowables.append(parrafo(
        "A nivel personal, el proyecto ha consolidado mi comprensión de los "
        "trade-offs prácticos entre criptografía simétrica y asimétrica, la utilidad "
        "real de las funciones hash más allá de las contraseñas, y la importancia de "
        "abordar la privacidad por diseño en cualquier herramienta que maneje datos "
        "educativos. La iteración por bloques (criptografía, blockchain, analítica, "
        "interfaz, seguridad) ha resultado especialmente productiva: cada nueva capa "
        "se construyó sobre fundamentos ya probados, lo que minimizó el coste de los "
        "errores."
    ))

    flowables.append(titulo_h2("10.2. Mejoras futuras"))
    flowables.append(parrafo(
        "El proyecto se presta a numerosas extensiones que ampliarían su alcance "
        "técnico y su validez en escenarios reales:"
    ))
    flowables.append(bullet(
        "<b>Integración con una blockchain real.</b> Sustituir la cadena local por "
        "una integración con Ethereum (a través de Web3.py) o con Hyperledger Fabric. "
        "Esto convertiría el sistema en distribuido y eliminaría el riesgo del borrado "
        "completo del fichero, que es la principal limitación actual."
    ))
    flowables.append(bullet(
        "<b>Cifrado homomórfico para analítica privada.</b> Aplicar esquemas como "
        "Paillier o CKKS permitiría calcular estadísticas agregadas sobre datos "
        "cifrados, sin que el servidor llegue a verlos en claro. Esto habilitaría "
        "casos de uso interinstitucionales sin requerir compartir datos."
    ))
    flowables.append(bullet(
        "<b>Modelos de ML más sofisticados.</b> Para datasets más grandes (varios "
        "miles de estudiantes) tendría sentido probar XGBoost, LightGBM o redes "
        "neuronales con embeddings de variables categóricas, además de explorar "
        "técnicas de interpretación local como SHAP."
    ))
    flowables.append(bullet(
        "<b>Autenticación multifactor.</b> Combinar la contraseña con un segundo "
        "factor (TOTP) y soporte de WebAuthn elevaría considerablemente la robustez "
        "del control de acceso."
    ))
    flowables.append(bullet(
        "<b>Argon2 en lugar de PBKDF2.</b> Sustituir la función de derivación de "
        "claves por Argon2id, que es el ganador del Password Hashing Competition de "
        "2015 y resistente a ataques con ASICs y GPUs especializadas."
    ))
    flowables.append(bullet(
        "<b>Implementación del derecho al olvido.</b> Diseñar el almacenamiento "
        "de modo que el borrado de datos personales no rompa la cadena (separando el "
        "hash del contenido en colecciones independientes), tal y como exige el "
        "artículo 17 del GDPR."
    ))
    flowables.append(bullet(
        "<b>Despliegue en contenedor.</b> Empaquetar el sistema con Docker y "
        "describir el despliegue con docker-compose, para facilitar la replicabilidad "
        "y eventualmente la transición a Kubernetes."
    ))

    flowables.append(salto_de_pagina())
    return flowables


def construir_referencias() -> list:
    flowables = []
    flowables.append(titulo_h1("11. Referencias bibliográficas"))

    flowables.append(parrafo("<b>Material del curso (eUniv · Universitas Europaea IMF)</b>"))
    flowables.append(bullet("Unidad 1. <i>Introducción a la matemática discreta y teoría de números.</i>"))
    flowables.append(bullet("Unidad 2. <i>Fundamentos de criptografía.</i>"))
    flowables.append(bullet("Unidad 3. <i>Funciones hash y encriptación simétrica.</i>"))
    flowables.append(bullet("Unidad 4. <i>Criptografía asimétrica.</i>"))
    flowables.append(bullet("Unidad 5. <i>Introducción a blockchain.</i>"))
    flowables.append(bullet("Unidad 6. <i>Aplicaciones de blockchain.</i>"))
    flowables.append(bullet("Unidad 7. <i>Minería en blockchain: conceptos y consenso distribuido.</i>"))
    flowables.append(bullet("Unidad 8. <i>Fundamentos de minería de datos.</i>"))
    flowables.append(bullet("Unidad 9. <i>Extracción de información supervisada y no supervisada.</i>"))
    flowables.append(bullet("Unidad 10. <i>Visualización e interpretación de datos.</i>"))
    flowables.append(bullet("Unidad 11. <i>Introducción a Learning Analytics.</i>"))
    flowables.append(bullet("Unidad 12. <i>Desarrollo de herramientas de Learning Analytics.</i>"))

    flowables.append(espacio(6))
    flowables.append(parrafo("<b>Documentación técnica y estándares</b>"))
    flowables.append(bullet(
        "Python Cryptographic Authority. <i>cryptography library documentation.</i> "
        "https://cryptography.io/en/latest/"
    ))
    flowables.append(bullet(
        "Python Software Foundation. <i>hashlib — Secure hashes and message digests.</i> "
        "https://docs.python.org/3/library/hashlib.html"
    ))
    flowables.append(bullet(
        "Pandas Development Team. <i>pandas documentation.</i> "
        "https://pandas.pydata.org/docs/"
    ))
    flowables.append(bullet(
        "Scikit-learn Developers. <i>scikit-learn: Machine Learning in Python.</i> "
        "https://scikit-learn.org/stable/documentation.html"
    ))
    flowables.append(bullet(
        "Streamlit Inc. <i>Streamlit documentation.</i> "
        "https://docs.streamlit.io/"
    ))
    flowables.append(bullet(
        "PyCQA. <i>Bandit — A security linter from PyCQA.</i> "
        "https://bandit.readthedocs.io/"
    ))

    flowables.append(espacio(6))
    flowables.append(parrafo("<b>Buenas prácticas, normativa y guías</b>"))
    flowables.append(bullet(
        "OWASP Foundation. <i>Password Storage Cheat Sheet.</i> "
        "https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html"
    ))
    flowables.append(bullet(
        "NIST. <i>SP 800-57 — Recommendation for Key Management.</i>"
    ))
    flowables.append(bullet(
        "Unión Europea. <i>Reglamento (UE) 2016/679 (Reglamento General de Protección "
        "de Datos).</i> https://eur-lex.europa.eu/eli/reg/2016/679"
    ))
    flowables.append(bullet(
        "JISC. <i>Code of Practice for Learning Analytics.</i> "
        "https://www.jisc.ac.uk/guides/code-of-practice-for-learning-analytics"
    ))
    flowables.append(bullet(
        "Nakamoto, S. (2008). <i>Bitcoin: A Peer-to-Peer Electronic Cash System.</i> "
        "https://bitcoin.org/bitcoin.pdf"
    ))
    flowables.append(bullet(
        "Rivest, R., Shamir, A., Adleman, L. (1978). <i>A method for obtaining "
        "digital signatures and public-key cryptosystems.</i> Communications of the "
        "ACM, 21(2), 120-126."
    ))

    flowables.append(salto_de_pagina())
    return flowables


def construir_anexo_github() -> list:
    flowables = []
    flowables.append(titulo_h1("Anexo A. Acceso al código fuente"))

    flowables.append(parrafo(
        "El código fuente completo del proyecto, junto con los datos sintéticos, las "
        "figuras generadas, las capturas del dashboard y los informes de auditoría, se "
        "encuentra disponible en GitHub:"
    ))

    flowables.append(caja_destacada(
        "<b>Repositorio:</b><br/>"
        "<font face=\"Courier\">https://github.com/danielrubiorocamora/learninganalyticssecure</font><br/><br/>"
    ))

    flowables.append(titulo_h2("Estructura del repositorio"))
    flowables.append(tabla(
        [
            ["Carpeta / fichero", "Contenido"],
            ["crypto_module/", "AES (Fernet), RSA-2048 con PSS, SHA-256, PBKDF2."],
            ["blockchain_module/", "Clase Bloque, Cadena, raíz de Merkle, Proof-of-Work."],
            ["analytics/", "EDA, preprocesamiento, modelo de riesgo, evaluación."],
            ["viz/", "Funciones de visualización con la paleta sobria del PDF."],
            ["app/", "Dashboard Streamlit, autenticación, operaciones firmadas."],
            ["data/", "Generador de dataset sintético (los datos no se versionan)."],
            ["tests/", "69 pruebas pytest distribuidas en seis ficheros."],
            ["docs/", "Figuras, capturas, informe Bandit, benchmarks (no versionados)."],
            ["pdf/", "Generador de esta memoria en PDF (ReportLab)."],
            ["bootstrap.py", "Script de inicialización del sistema."],
            ["demo_integracion.py", "Demo de criptografía + blockchain + datos."],
            ["demo_analitica.py", "Demo de EDA + ML + generación de figuras."],
            ["demo_manipulacion.py", "Demo de detección de manipulación."],
            ["demo_benchmarks.py", "Mediciones de rendimiento."],
            ["INFORME_TECNICO.md", "Documento técnico de síntesis."],
            ["README.md", "Instrucciones de despliegue."],
            ["requirements.txt", "Dependencias Python."],
            ["LICENSE", "Términos de uso académico."],
        ],
        anchos_relativos=[2.5, 5],
        primera_columna_destacada=True,
    ))

    flowables.append(titulo_h2("Despliegue rápido"))
    flowables.append(parrafo(
        "Una vez clonado el repositorio, todo el sistema se levanta en cuatro pasos:"
    ))
    flowables.append(caja_destacada(
        '<font face="Courier" size="10">'
        "git clone https://github.com/danielrubiorocamora/learninganalyticssecure.git<br/>"
        "cd learning_analytics_secure<br/>"
        "python -m venv venv &amp;&amp; source venv/bin/activate&nbsp;&nbsp;&nbsp;"
        "<i># o venv\\Scripts\\Activate.ps1 en Windows</i><br/>"
        "pip install -r requirements.txt<br/>"
        "python bootstrap.py<br/>"
        "streamlit run app/dashboard.py</font>"
    ))
    flowables.append(parrafo(
        "El dashboard se abrirá automáticamente en el navegador. Las credenciales demo "
        "(usuario / contraseña / rol) figuran en la pantalla de login y en el README."
    ))

    flowables.append(titulo_h2("Verificación y auditoría"))
    flowables.append(parrafo(
        "Los siguientes comandos reproducen los resultados expuestos en la sección 6:"
    ))
    flowables.append(caja_destacada(
        '<font face="Courier" size="10">'
        "pytest -v&nbsp;&nbsp;&nbsp;&nbsp;<i># 69 tests en verde</i><br/>"
        "python demo_benchmarks.py&nbsp;&nbsp;&nbsp;&nbsp;<i># mediciones de rendimiento</i><br/>"
        "python demo_manipulacion.py&nbsp;&nbsp;&nbsp;&nbsp;<i># demo de ataque + captura</i><br/>"
        "bandit -r crypto_module blockchain_module analytics app data&nbsp;&nbsp;&nbsp;&nbsp;<i># 0 issues</i></font>"
    ))

    return flowables
