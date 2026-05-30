"""Secciones 4 (Arquitectura) y 5 (Implementación) con fragmentos de código."""

from __future__ import annotations

from pdf.estilos import (
    bullet,
    espacio,
    fragmento_codigo,
    parrafo,
    salto_de_pagina,
    tabla,
    titulo_h1,
    titulo_h2,
    titulo_h3,
)


def construir_arquitectura() -> list:
    flowables = []
    flowables.append(titulo_h1("4. Arquitectura del sistema"))

    flowables.append(titulo_h2("4.1. Visión general"))
    flowables.append(parrafo(
        "El sistema está organizado en cuatro capas independientes pero interconectadas, "
        "cada una con su propio paquete Python y su batería de pruebas. La separación "
        "facilita el mantenimiento, la sustitución de implementaciones (por ejemplo, "
        "cambiar AES por ChaCha20 sin tocar el resto del sistema) y la trazabilidad "
        "del flujo de datos."
    ))
    flowables.append(tabla(
        [
            ["Capa", "Paquete", "Responsabilidad principal"],
            ["1. Datos", "data/", "Generación y carga del dataset educativo sintético."],
            ["2. Seguridad", "crypto_module/, blockchain_module/", "Cifrado, firma digital, hashing y blockchain."],
            ["3. Analítica", "analytics/, viz/", "EDA, modelo de ML y visualizaciones."],
            ["4. Presentación", "app/", "Dashboard Streamlit, autenticación y operaciones firmadas."],
        ],
        anchos_relativos=[1, 2.5, 4],
        primera_columna_destacada=True,
    ))
    flowables.append(espacio(6))
    flowables.append(parrafo(
        "El flujo típico de una operación sigue siempre el mismo patrón. Cuando un "
        "docente registra una calificación, el sistema (1) recibe los datos desde la "
        "interfaz, (2) construye una transacción serializada de forma canónica, "
        "(3) la firma con la clave privada RSA del docente, (4) la añade como nuevo "
        "bloque a la cadena, donde se mina con Proof-of-Work, y (5) persiste la cadena "
        "en disco. Posteriormente, cualquier consulta posterior puede verificar "
        "criptográficamente que esa transacción no ha sido manipulada."
    ))

    flowables.append(titulo_h2("4.2. Decisiones técnicas y justificación"))
    flowables.append(parrafo(
        "La siguiente tabla resume las decisiones técnicas más importantes tomadas a "
        "lo largo del desarrollo, junto con las alternativas descartadas y la "
        "justificación que sustenta cada elección."
    ))
    flowables.append(tabla(
        [
            ["Componente", "Decisión", "Justificación"],
            [
                "Cifrado de datos en reposo",
                "AES-128-CBC + HMAC-SHA256 (Fernet)",
                "Receta autenticada (AEAD) auditada de la librería <i>cryptography</i>. "
                "Resuelve confidencialidad e integridad. Aproximadamente 40 veces más "
                "rápido que RSA según los benchmarks (sección 6).",
            ],
            [
                "Derivación de contraseña",
                "PBKDF2-HMAC-SHA256, 600 000 iteraciones",
                "Mínimo recomendado por OWASP para 2024. Disponible sin dependencias "
                "adicionales.",
            ],
            [
                "Firma digital",
                "RSA-2048 con padding PSS y SHA-256",
                "PSS está demostrablemente seguro frente a ataques de mensaje elegido, "
                "a diferencia del antiguo PKCS#1 v1.5.",
            ],
            [
                "Función hash",
                "SHA-256",
                "MD5 y SHA-1 son inseguros (colisiones encontradas). SHA-256 es el "
                "algoritmo de referencia en Bitcoin y la mayoría de blockchains.",
            ],
            [
                "Proof-of-Work",
                "Dificultad 3 (3 ceros iniciales)",
                "Tiempo medio de minería de 32 ms, suficiente para no degradar la "
                "experiencia de usuario y a la vez visible en demostraciones.",
            ],
            [
                "Variable objetivo del modelo",
                "Variable binaria <i>riesgo</i> derivada",
                "El caso de uso real es binario (intervenir o no). La predicción "
                "continua añadiría complejidad sin beneficio.",
            ],
            [
                "Comparativa de modelos",
                "Regresión Logística vs Random Forest",
                "Permite discutir trade-offs. Las redes neuronales son injustificadas "
                "para un dataset de 300 muestras.",
            ],
            [
                "Almacenamiento de usuarios",
                "JSON local con clave privada cifrada en reposo",
                "Suficiente para un proyecto académico monoinstancia. La clave privada "
                "RSA se almacena cifrada con AES derivado de la contraseña.",
            ],
            [
                "Interfaz",
                "Streamlit",
                "Dashboard funcional en menos de 400 líneas, manteniendo el foco en "
                "la lógica criptográfica y no en el frontend.",
            ],
        ],
        anchos_relativos=[1.4, 2, 3],
        primera_columna_destacada=True,
    ))

    flowables.append(salto_de_pagina())
    return flowables


def construir_implementacion() -> list:
    flowables = []
    flowables.append(titulo_h1("5. Implementación"))
    flowables.append(parrafo(
        "El proyecto suma 1 372 líneas de código Python distribuidas en 18 ficheros. "
        "Por motivos de extensión, en esta memoria se reproducen únicamente los "
        "fragmentos más representativos de cada módulo, comentados. El código fuente "
        "completo está disponible en el repositorio GitHub indicado en el Anexo A, "
        "donde también figuran las instrucciones de despliegue."
    ))

    # ------------------------------------------------------------
    # 5.1. Cripto
    # ------------------------------------------------------------
    flowables.append(titulo_h2("5.1. Módulo de criptografía"))
    flowables.append(parrafo(
        "El módulo <b>crypto_module</b> expone tres submódulos: cifrado simétrico (AES "
        "vía Fernet), cifrado asimétrico (RSA-2048) y funciones hash (SHA-256). La "
        "derivación de claves a partir de contraseñas se realiza con PBKDF2:"
    ))
    flowables.extend(fragmento_codigo(
        '''def derivar_clave(password: str, sal: bytes) -> bytes:
    """Deriva una clave Fernet a partir de una contraseña y una sal.

    Aplica PBKDF2-HMAC-SHA256 con un número alto de iteraciones para frenar
    ataques de fuerza bruta. La salida se codifica en base64 url-safe porque
    es el formato que Fernet acepta.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=LONGITUD_CLAVE_BYTES,
        salt=sal,
        iterations=ITERACIONES_PBKDF2,  # 600 000
    )
    clave_bruta = kdf.derive(password.encode("utf-8"))
    return base64.urlsafe_b64encode(clave_bruta)''',
        "Listado 1. Derivación de clave con PBKDF2 (crypto_module/cifrado_simetrico.py)",
    ))
    flowables.append(parrafo(
        "Las firmas digitales utilizan padding PSS, que es la opción recomendada por "
        "NIST por su seguridad demostrable. Tanto la firma como su verificación se "
        "encapsulan en funciones puras que reciben el material clave por parámetro:"
    ))
    flowables.extend(fragmento_codigo(
        '''def firmar(mensaje: bytes, clave_privada) -> bytes:
    """Firma un mensaje con RSA-PSS + SHA-256."""
    return clave_privada.sign(
        mensaje,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )


def verificar(firma: bytes, mensaje: bytes, clave_publica) -> bool:
    """Verifica una firma. Devuelve True si es válida, False en caso contrario."""
    try:
        clave_publica.verify(
            firma, mensaje,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256(),
        )
        return True
    except InvalidSignature:
        return False''',
        "Listado 2. Firma y verificación RSA-PSS (crypto_module/cifrado_asimetrico.py)",
    ))

    flowables.append(salto_de_pagina())

    # ------------------------------------------------------------
    # 5.2. Blockchain
    # ------------------------------------------------------------
    flowables.append(titulo_h2("5.2. Módulo de blockchain"))
    flowables.append(parrafo(
        "La cadena de bloques es la pieza que materializa la <b>inmutabilidad</b> de "
        "los registros. Cada bloque enlaza con el anterior mediante el hash de su "
        "cabecera, y el método <i>minar</i> implementa Proof-of-Work iterando sobre el "
        "campo <i>nonce</i> hasta encontrar un hash que cumpla la dificultad exigida:"
    ))
    flowables.extend(fragmento_codigo(
        '''def minar(self, dificultad: int) -> None:
    """Proof-of-Work: encuentra un nonce que produzca un hash con N ceros iniciales.

    `dificultad` indica el número de caracteres hex iniciales que deben ser '0'.
    Para fines didácticos se recomienda mantenerlo bajo (3 o 4); cada incremento
    multiplica aproximadamente por 16 el tiempo medio de minería.
    """
    prefijo_objetivo = "0" * dificultad
    while not self.hash_actual.startswith(prefijo_objetivo):
        self.nonce += 1
        self.hash_actual = self.calcular_hash()''',
        "Listado 3. Algoritmo de Proof-of-Work (blockchain_module/bloque.py)",
    ))
    flowables.append(parrafo(
        "La verificación de integridad recorre la cadena entera comprobando "
        "simultáneamente cuatro propiedades: que cada hash recalculado coincida con el "
        "almacenado, que cada bloque enlace correctamente con el anterior, que cada hash "
        "cumpla la dificultad de PoW y que la raíz de Merkle sea coherente con las "
        "transacciones del bloque. Cualquier discrepancia detiene la verificación y "
        "devuelve un mensaje descriptivo:"
    ))
    flowables.extend(fragmento_codigo(
        '''def verificar_integridad(self) -> tuple[bool, str]:
    """Recorre la cadena y devuelve (ok, descripcion)."""
    prefijo = "0" * self.dificultad
    for i, bloque in enumerate(self.bloques):
        # (1) Hash recalculado coincide con el almacenado
        if bloque.calcular_hash() != bloque.hash_actual:
            return False, f"Hash inválido en bloque {i}: ha sido manipulado."
        # (2) Enlace con el bloque anterior
        if i > 0 and bloque.hash_anterior != self.bloques[i - 1].hash_actual:
            return False, f"Bloque {i}: el hash_anterior no enlaza con el previo."
        # (3) PoW
        if not bloque.hash_actual.startswith(prefijo):
            return False, f"Bloque {i}: no cumple la dificultad de PoW."
        # (4) Raíz de Merkle
        esperada = calcular_raiz_merkle([json.dumps(t, sort_keys=True, default=str)
                                          for t in bloque.transacciones])
        if esperada != bloque.raiz_merkle:
            return False, f"Bloque {i}: la raíz de Merkle no coincide."
    return True, f"Cadena íntegra: {len(self.bloques)} bloques verificados."''',
        "Listado 4. Verificación integral de la cadena (blockchain_module/cadena.py)",
    ))

    flowables.append(salto_de_pagina())

    # ------------------------------------------------------------
    # 5.3. Analítica
    # ------------------------------------------------------------
    flowables.append(titulo_h2("5.3. Módulo de analítica y modelo ML"))
    flowables.append(parrafo(
        "El módulo <b>analytics</b> implementa el pipeline completo de Machine Learning, "
        "desde la limpieza hasta la evaluación. El preprocesamiento garantiza que las "
        "variables identificadoras (id, nombre, email) nunca lleguen al modelo, y "
        "aplica un escalado <i>StandardScaler</i> ajustado únicamente sobre los datos "
        "de entrenamiento para evitar la fuga de información (<i>data leakage</i>)."
    ))
    flowables.extend(fragmento_codigo(
        '''def entrenar_random_forest(X_train, y_train) -> RandomForestClassifier:
    """Entrena un Random Forest con 100 árboles."""
    modelo = RandomForestClassifier(
        n_estimators=100,
        random_state=SEMILLA,
        class_weight="balanced",  # compensa el desbalance moderado de clases
        n_jobs=-1,                # usar todos los núcleos
    )
    modelo.fit(X_train, y_train)
    return modelo


def evaluar(modelo, X_test, y_test, nombre: str) -> ResultadoModelo:
    """Calcula las métricas estándar de clasificación binaria."""
    y_predicho = modelo.predict(X_test)
    y_probabilidad = modelo.predict_proba(X_test)[:, 1]
    return ResultadoModelo(
        nombre=nombre, modelo=modelo,
        accuracy=accuracy_score(y_test, y_predicho),
        precision=precision_score(y_test, y_predicho, zero_division=0),
        recall=recall_score(y_test, y_predicho),
        f1=f1_score(y_test, y_predicho),
        roc_auc=roc_auc_score(y_test, y_probabilidad),
        matriz_confusion=confusion_matrix(y_test, y_predicho),
        ...
    )''',
        "Listado 5. Entrenamiento y evaluación del modelo (analytics/modelo_riesgo.py)",
    ))

    # ------------------------------------------------------------
    # 5.4. Dashboard
    # ------------------------------------------------------------
    flowables.append(titulo_h2("5.4. Dashboard y autenticación con roles"))
    flowables.append(parrafo(
        "Cada usuario del sistema dispone de un par de claves RSA generadas en el "
        "momento del alta. La clave privada se almacena cifrada con AES derivado de la "
        "contraseña del usuario, de modo que <b>solo el propio usuario puede "
        "descifrarla durante la sesión</b>. El alta combina ambos elementos:"
    ))
    flowables.extend(fragmento_codigo(
        '''def registrar_usuario(usuario: str, contrasena: str, rol: str, ...) -> Usuario:
    """Crea un nuevo usuario con clave RSA + contraseña hasheada."""
    sal = generar_sal()
    clave_simetrica = derivar_clave(contrasena, sal)

    # Generamos el par RSA del usuario
    clave_privada, clave_publica = generar_par_de_claves()
    pem_publica = serializar_clave_publica(clave_publica).decode("utf-8")
    pem_privada = serializar_clave_privada(clave_privada).decode("utf-8")

    # La clave privada se almacena cifrada con AES derivado de la contraseña
    pem_privada_cifrada = cifrar(pem_privada, clave_simetrica)

    # Token de verificación: cifra un literal conocido para validar la contraseña
    token_verificacion = cifrar(LITERAL_VERIFICACION, clave_simetrica)

    return Usuario(usuario=usuario, rol=rol, sal_hex=sal.hex(),
                   clave_verificacion=token_verificacion,
                   clave_publica_pem=pem_publica,
                   clave_privada_cifrada_pem=pem_privada_cifrada, ...)''',
        "Listado 6. Alta de usuarios con claves RSA y AES (app/usuarios.py)",
    ))
    flowables.append(parrafo(
        "Cada operación que el usuario realiza sobre el sistema se materializa como "
        "una <b>transacción firmada</b> que se añade a la blockchain. Esta función "
        "construye la transacción canónica y la firma con la clave privada activa "
        "durante la sesión:"
    ))
    flowables.extend(fragmento_codigo(
        '''def construir_transaccion(tipo: str, emisor: str, payload: dict, ...) -> dict:
    """Construye una transacción serializable y firmada digitalmente."""
    cuerpo = {
        "tipo": tipo,
        "emisor": emisor,
        "marca_tiempo": time.time(),
        "payload": payload,
    }
    serializado = json.dumps(cuerpo, sort_keys=True,
                              separators=(",", ":"), default=str)
    clave_privada = cargar_clave_privada(pem_clave_privada.encode("utf-8"))
    firma = firmar(serializado.encode("utf-8"), clave_privada)
    return {**cuerpo,
            "firma_hex": firma.hex(),
            "clave_publica_pem": clave_publica_pem}''',
        "Listado 7. Construcción de una transacción firmada (app/operaciones.py)",
    ))

    flowables.append(salto_de_pagina())
    return flowables
