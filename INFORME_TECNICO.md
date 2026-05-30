# Informe técnico de síntesis

Documento de apoyo para la redacción de la memoria final en PDF. Contiene la
tabla de decisiones técnicas, las consideraciones éticas y de GDPR, y los
problemas encontrados durante el desarrollo con sus soluciones.

**Autor:** Daniel Rubio Rocamora
**Asignatura:** Análisis de Datos 2, Criptografía, Blockchain y Learning Analytics
**Centro:** eUniv · Universitas Europaea IMF

---

## 1. Tabla de decisiones técnicas

| Componente | Decisión adoptada | Alternativa(s) descartada(s) | Justificación |
|---|---|---|---|
| **Cifrado de datos en reposo** | AES-128-CBC con HMAC-SHA256 (vía Fernet) | AES-256-GCM, ChaCha20-Poly1305, RSA puro | Fernet es la receta auditada de la librería `cryptography`. Resuelve confidencialidad e integridad en un único token (AEAD). Descartado RSA puro porque su coste es ~40× mayor (medido: 0.67 ms RSA vs 0.017 ms AES) y porque RSA no cifra bloques mayores que el tamaño del módulo. |
| **Derivación de clave de contraseña** | PBKDF2-HMAC-SHA256, 600 000 iteraciones | bcrypt, scrypt, Argon2 | PBKDF2 está incluido en la librería estándar `cryptography`, sin dependencias adicionales. 600 000 iteraciones es el mínimo recomendado por OWASP para 2024 con SHA-256. Argon2 sería preferible pero requiere instalar `argon2-cffi`. |
| **Firma digital** | RSA-2048 con padding PSS y SHA-256 | RSA con PKCS#1 v1.5, ECDSA | PSS está demostrablemente seguro frente a ataques de elección de mensaje, a diferencia de PKCS#1 v1.5 (que ha tenido fallos en implementaciones). ECDSA daría firmas más cortas pero RSA-2048 es el estándar más legible para una memoria académica. |
| **Función de hash** | SHA-256 | MD5, SHA-1, SHA-3 | MD5 y SHA-1 son inseguros (colisiones encontradas). SHA-256 es el algoritmo usado por Bitcoin y la mayoría de blockchains, lo que da realismo al ejercicio. |
| **Estructura de bloque** | Cabecera con `indice`, `marca_tiempo`, `hash_anterior`, `raiz_merkle`, `nonce` | Solo lista plana de transacciones | La estructura imita la de Bitcoin/Ethereum. La raíz de Merkle permite verificaciones eficientes de inclusión sin recorrer todas las transacciones. |
| **Algoritmo de consenso** | Proof-of-Work simulado, dificultad 3 | PoS, PBFT, sin consenso | PoW es el más didáctico y el más relacionado con el temario. Dificultad 3 da un tiempo de minería de ~32 ms (medido), suficientemente rápido para no degradar la UX del dashboard y a la vez tangible. |
| **Modelo ML** | Comparativa Regresión Logística vs Random Forest | Solo un modelo, redes neuronales | La comparativa permite discutir trade-offs. RL gana en F1 (0.94 vs 0.85) gracias a la separabilidad lineal del problema; RF gana en AUC (0.996 vs 0.989). Las redes neuronales son injustificadas para 300 muestras. |
| **Variable objetivo** | Variable binaria `riesgo` derivada | Predicción continua de nota | El caso de uso real (detectar alumnos en riesgo) es binario. La predicción continua añadiría complejidad sin beneficio. |
| **Tratamiento de desbalance** | `class_weight="balanced"` en ambos modelos | SMOTE, undersampling | Más simple y mantiene todos los datos. El desbalance es moderado (75/25). |
| **Escalado** | `StandardScaler` ajustado solo en train | Sin escalado, MinMaxScaler global | Ajustar el escalador con datos de test sería **fuga de información**. Aunque RF no necesita escalado, sí lo necesita la regresión logística. |
| **Almacenamiento de usuarios** | JSON local cifrado por usuario | Base de datos SQLite con SQLAlchemy | El proyecto es académico y monousuario por sesión. JSON con cifrado por entrada es suficiente y mantiene el código sencillo. La clave privada RSA se almacena cifrada con AES derivado de la contraseña. |
| **Persistencia de la cadena** | JSON en disco, una sola cadena por instalación | Base de datos, un fichero por bloque | Visualmente inspeccionable y portable. Se reescribe completa en cada operación: ineficiente para una blockchain real pero válido para la simulación. |
| **Framework de interfaz** | Streamlit | Flask + HTML, Dash, FastAPI + React | Streamlit permite construir un dashboard funcional con < 300 líneas, manteniendo el foco en la lógica criptográfica. |
| **Gestión de sesión** | `st.session_state` con clave privada descifrada en memoria | Cookies firmadas, JWT | La clave privada nunca toca el disco descifrada. Al cerrar sesión se elimina del estado y desaparece. |
| **Pruebas** | Pytest, 69 tests organizados en clases por módulo | unittest, sin pruebas | Pytest da fixtures más limpias y mejor reporting. 69 tests cubren los caminos críticos. |
| **Auditoría de seguridad** | Bandit con anotaciones `# nosec` documentadas | Auditoría manual, SonarQube | Bandit es el estándar de la comunidad Python para análisis estático. El informe final muestra 0 issues con 4 anotaciones revisadas y justificadas. |

---

## 2. Métricas del sistema (resultados experimentales)

### 2.1. Rendimiento operacional (benchmark sobre máquina de desarrollo)

| Operación | Tiempo medio | Veces que se ejecuta |
|---|---|---|
| Cifrado AES de un campo | 0.017 ms | Una vez por campo sensible cifrado |
| Descifrado AES de un campo | 0.017 ms | Una vez por campo sensible accedido |
| Generación par RSA-2048 | 43 ms | Una vez en toda la vida del usuario |
| Firma RSA-PSS-SHA256 | 0.67 ms | Una vez por operación firmada |
| Verificación de firma | 0.03 ms | Una vez por verificación |
| Minería PoW dificultad 2 | 1.6 ms | — |
| **Minería PoW dificultad 3** | **32 ms** | **Una vez por bloque (configuración activa)** |
| Minería PoW dificultad 4 | 723 ms | — |
| Predicción ML (lote de 75) | 6.7 ms | Una vez por dashboard de docente |
| Predicción ML un estudiante | 6.5 ms | Una vez por consulta puntual |

### 2.2. Calidad del modelo de Machine Learning

| Modelo | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---|---|---|---|---|
| Regresión Logística | 0.9733 | 0.9444 | 0.9444 | **0.9444** | 0.9893 |
| Random Forest | 0.9333 | 0.9333 | 0.7778 | 0.8485 | **0.9961** |

### 2.3. Resultado de auditoría Bandit

- Líneas de código escaneadas: **1372**
- Issues detectadas: **0**
- Issues suprimidas con `# nosec` (revisadas manualmente y justificadas): **4**
  - `B403`: `import pickle` — origen confiable (bootstrap.py local).
  - `B301`: `pickle.load` × 2 — origen confiable.
  - `B311`: `random.choices` — uso no criptográfico (generación de datos sintéticos).
- Las funciones criptográficas reales usan `os.urandom` (a través de la librería `cryptography`), nunca `random`.

### 2.4. Cobertura de pruebas

- **69 pruebas unitarias** distribuidas en 6 ficheros:
  - `test_crypto.py` — 13 pruebas (cifrado simétrico, RSA, hashing)
  - `test_blockchain.py` — 13 pruebas (bloque, cadena, Merkle, integridad)
  - `test_datos.py` — 7 pruebas (generador de dataset)
  - `test_analytics.py` — 13 pruebas (EDA, preprocesamiento, modelos)
  - `test_viz.py` — 8 pruebas (todas las figuras)
  - `test_usuarios_y_operaciones.py` — 15 pruebas (autenticación, firmas, blockchain)
- Tiempo de ejecución de toda la suite: **~12 segundos**.

---

## 3. Consideraciones éticas y cumplimiento de GDPR

El proyecto, aunque académico, se ha diseñado siguiendo los principios del
Reglamento General de Protección de Datos (RGPD/GDPR) europeo y la guía
*Code of Practice for Learning Analytics* del JISC.

### 3.1. Principios aplicados

| Principio GDPR | Implementación en el proyecto |
|---|---|
| **Licitud, lealtad y transparencia** (Art. 5.1.a) | Todos los datos son sintéticos y generados por el propio sistema. Ninguna persona física real está involucrada en el conjunto de datos. |
| **Limitación de la finalidad** (Art. 5.1.b) | Los datos se usan exclusivamente para Learning Analytics (detección de riesgo). El modelo no se reutiliza para otros fines. |
| **Minimización de datos** (Art. 5.1.c) | El modelo de ML excluye explícitamente identificadores (`id_estudiante`, `nombre`, `email`) — solo se alimenta con variables relevantes para el riesgo académico. |
| **Exactitud** (Art. 5.1.d) | Los registros se firman digitalmente. Cualquier modificación posterior queda detectada por la verificación de integridad. |
| **Limitación del plazo de conservación** (Art. 5.1.e) | El sistema permite borrar registros (no implementado en la demo) sin romper la cadena, ya que el hash sigue válido. |
| **Integridad y confidencialidad** (Art. 5.1.f) | Datos cifrados en reposo con AES-128 + HMAC-SHA256. Contraseñas hasheadas con PBKDF2 (600 000 iteraciones). |
| **Responsabilidad proactiva** (Art. 5.2) | Todas las operaciones sensibles se registran en la blockchain como audit log inmutable. |
| **Registro de actividades de tratamiento** (Art. 30) | Cada consulta de un estudiante a sus propios datos genera una transacción `consulta_registro` firmada y encadenada. El admin puede consultar el historial completo. |

### 3.2. Decisiones específicas de privacidad

1. **Anonimización en gráficos agregados:** los gráficos públicos (distribución
   de riesgo, matriz de correlación) nunca muestran nombres ni identificadores.
2. **Descifrado bajo demanda:** los nombres reales solo se descifran en la vista
   personal del propio estudiante o cuando un docente con permisos lo solicita.
3. **Audit trail:** cada acceso queda registrado en la blockchain como
   transacción firmada con la clave privada del usuario que accede.
4. **Right to be forgotten:** el diseño permite eliminar registros sin invalidar
   la cadena al separar el hash del contenido (no implementado en la demo, pero
   discutido en la sección de mejoras futuras del PDF).

### 3.3. Limitaciones reconocidas

- La herramienta usa una blockchain **local** (no distribuida); las propiedades
  de inmutabilidad son válidas frente a manipulación de un único actor, no
  frente a borrado completo del fichero.
- Para una implementación en producción habría que usar una blockchain real
  (Ethereum, Hyperledger Fabric) o un servicio de timestamping confiable.

---

## 4. Problemas encontrados y resueltos durante el desarrollo

### 4.1. Inconsistencia de dificultad en la cadena tras reinicios

**Síntoma:** tras reejecutar el bootstrap varias veces, el dashboard mostraba
"Cadena rota" aunque las pruebas pasaban en aislamiento.

**Causa:** la función `cargar_o_crear_cadena` recibía un parámetro `dificultad=3`
y, si encontraba un fichero JSON existente, sobrescribía la dificultad de la
cadena cargada con ese valor — pero los bloques antiguos habían sido minados con
una dificultad menor en pruebas previas. El método `verificar_integridad`
exigía entonces 3 ceros iniciales a bloques que solo tenían 2.

**Solución:** se modificó `cargar_o_crear_cadena` para **respetar la dificultad
almacenada en el JSON** y nunca sobrescribirla al cargar. La dificultad solo se
fija al crear la cadena por primera vez (en el bloque génesis). Si se quiere
cambiar la dificultad, se debe regenerar la cadena desde cero.

### 4.2. Capturas vacías con Playwright

**Síntoma:** las primeras capturas del dashboard mostraban solo el título y un
fondo blanco — el contenido no había terminado de renderizar.

**Causa:** Streamlit renderiza progresivamente y los gráficos de Matplotlib se
inyectan tras una llamada asíncrona. Un `wait_for_timeout` simple de 3 segundos
no era suficiente para vistas pesadas como la del administrador (que carga
modelo, dataset y tres gráficos).

**Solución:** se combinó `page.wait_for_load_state("networkidle", timeout=15000)`
con un margen explícito de 3.5 segundos extra tras cada acción, más una espera
explícita por el selector del campo `Usuario` en el login. Las capturas
resultantes son consistentes y reproducibles.

### 4.3. Tests de regresión logística fallaban por casos límite

**Síntoma:** ocasionalmente, el test `test_regresion_logistica_alcanza_minimo_de_calidad`
fallaba con valores de F1 ligeramente por debajo del umbral de 0.7.

**Causa:** semillas aleatorias diferentes en numpy y Python provocaban pequeñas
variaciones en el train/test split estratificado.

**Solución:** se definió una semilla común (`SEMILLA = 42`) en el módulo de
preprocesamiento y se aplicó tanto a numpy, Python y Faker. Los resultados son
ahora completamente reproducibles entre ejecuciones.

### 4.4. Bandit señalaba 4 issues por uso de pickle y random

**Síntoma:** análisis estático con Bandit reportaba 2 medium y 2 low.

**Causa:** uso legítimo de `pickle.load` para cargar nuestro propio modelo
entrenado, y de `random.choices` para generar datos sintéticos.

**Solución:** ambos usos están restringidos a **datos generados localmente por
el propio sistema** (no datos de origen externo). Se marcaron con anotaciones
`# nosec` que incluyen el código del check y una justificación. Bandit ahora
reporta 0 issues con 4 anotaciones documentadas — el patrón correcto en la
industria para falsos positivos confirmados.

---

## 5. Material listo para el PDF

### 5.1. Figuras y capturas (todas en `docs/`)

**Gráficos analíticos (8 PNG en `docs/figuras/`):**
1. `01_distribucion_riesgo.png`
2. `02_distribucion_notas.png`
3. `03_matriz_correlacion.png`
4. `04_matriz_confusion_rl.png`
5. `05_matriz_confusion_rf.png`
6. `06_curva_roc.png`
7. `07_comparativa_metricas.png`
8. `08_importancia_variables.png`

**Capturas del dashboard (6 PNG en `docs/capturas/`):**
1. `00_login.png` — pantalla de login con credenciales demo
2. `01_administrador.png` — panel del administrador
3. `02_docente.png` — top 10 alumnos en riesgo
4. `03_estudiante_sin_riesgo.png` — vista personal de un alumno solvente
5. `04_estudiante_riesgo.png` — vista personal de un alumno en riesgo
6. `05_manipulacion_detectada.png` — sidebar mostrando "Cadena rota" tras un ataque simulado

### 5.2. Datos y métricas (todos en `docs/`)

- `metricas.json` — métricas de los modelos ML y top 10 alumnos en riesgo
- `seguridad/benchmarks.json` — tiempos de cada operación criptográfica
- `seguridad/bandit_informe.txt` — informe de auditoría con 0 issues
- `seguridad/bandit_informe.html` — versión HTML del informe Bandit
- `seguridad/bandit_informe.json` — versión JSON
- `seguridad/resumen_manipulacion.json` — resumen del ataque simulado

### 5.3. Código fuente (anexo del PDF)

Estructura final del proyecto:

```
learning_analytics_secure/
├── README.md
├── requirements.txt
├── bootstrap.py                ← inicialización del sistema
├── demo_integracion.py         ← demo Día 1: crypto + blockchain + datos
├── demo_analitica.py           ← demo Día 2: EDA + ML + gráficos
├── demo_manipulacion.py        ← demo Día 4: detección de ataque
├── demo_benchmarks.py          ← demo Día 4: medición de tiempos
├── capturar_dashboard.py       ← automatización de capturas
├── INFORME_TECNICO.md          ← este documento
├── crypto_module/              ← AES (Fernet), RSA (PSS), SHA-256, PBKDF2
├── blockchain_module/          ← Bloque, Cadena, Merkle, PoW
├── analytics/                  ← Preprocesamiento, EDA, modelo de riesgo
├── viz/                        ← Gráficos con estética sobria
├── app/                        ← Streamlit + autenticación + operaciones firmadas
├── data/                       ← Dataset, modelo, escalador, cadena, usuarios
├── tests/                      ← 69 pruebas pytest
└── docs/                       ← Figuras, capturas, métricas, auditoría
```

Total: **18 ficheros Python**, **1372 líneas de código de aplicación**, **69 pruebas**, **8 figuras analíticas**, **6 capturas del dashboard**.
