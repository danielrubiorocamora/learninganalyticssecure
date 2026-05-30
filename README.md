# Learning Analytics seguro con criptografía y blockchain

> Proyecto académico para la asignatura **Análisis de Datos 2, Criptografía, Blockchain y Learning Analytics** de eUniv · Universitas Europaea IMF.

**Autor:** Daniel Rubio Rocamora

Herramienta en Python que integra **Learning Analytics** con **criptografía simétrica/asimétrica** y **blockchain** para proteger la privacidad y garantizar la integridad de registros educativos. La memoria técnica completa está disponible en el PDF que acompaña a este repositorio.

---

## Capacidades del sistema

- **Generación de un dataset sintético** de 300 estudiantes con nombres, calificaciones, asistencia y participación realistas (`Faker` en `es_ES`).
- **Cifrado AES-128** (vía Fernet, `cryptography`) de campos sensibles, con derivación de clave PBKDF2-HMAC-SHA256 a 600 000 iteraciones.
- **Firmas RSA-2048 con padding PSS** en cada operación, garantizando autenticación y no repudio.
- **Cadena de bloques propia** con SHA-256, raíz de Merkle estilo Bitcoin y Proof-of-Work configurable.
- **Modelo de Machine Learning** que compara Regresión Logística y Random Forest para detectar alumnos en riesgo.
- **Dashboard interactivo en Streamlit** con login y tres roles diferenciados (administrador, docente, estudiante).
- **69 pruebas pytest** y auditoría de seguridad con Bandit (0 issues).

## Estructura

```
learning_analytics_secure/
├── crypto_module/       AES, RSA, hashing, PBKDF2
├── blockchain_module/   Bloque, Cadena, Merkle, Proof-of-Work
├── analytics/           Preprocesamiento, EDA, modelo de riesgo
├── viz/                 Gráficos con estética sobria
├── app/                 Dashboard Streamlit + autenticación + operaciones firmadas
├── data/                Dataset y modelos persistidos
├── tests/               69 pruebas pytest
├── docs/                Figuras, capturas y auditoría de seguridad
├── bootstrap.py         Inicializa el sistema en un solo comando
├── demo_*.py            Demostraciones ejecutables de cada bloque funcional
└── INFORME_TECNICO.md   Documento de síntesis (tabla de decisiones, GDPR, problemas)
```

## Requisitos

- Python 3.10 o superior (probado en 3.12 y 3.13).
- Las dependencias se instalan automáticamente desde `requirements.txt`.

## Instalación rápida

```bash
git clone https://github.com/<TU_USUARIO>/learning_analytics_secure.git
cd learning_analytics_secure

# Crear y activar entorno virtual
python -m venv venv

# Linux / macOS
source venv/bin/activate
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt

# Inicializar el sistema (dataset + usuarios + modelo + cadena)
python bootstrap.py

# Lanzar el dashboard
streamlit run app/dashboard.py
```

## Credenciales del entorno demo

| Usuario | Contraseña | Rol |
|---|---|---|
| `admin` | `Admin1234!` | Administrador |
| `profesor.moya` | `Profesor1234!` | Docente |
| `profesor.garcia` | `Profesor1234!` | Docente |
| `EST-0001` | `Estudiante1!` | Estudiante (sin riesgo) |
| `EST-0128` | `Estudiante1!` | Estudiante (alto riesgo) |
| `EST-0210` | `Estudiante1!` | Estudiante (alto riesgo) |

## Scripts de demostración

Cada script se puede ejecutar individualmente para revisar un bloque funcional:

```bash
python demo_integracion.py   # Cifrado + firma + blockchain integrados
python demo_analitica.py     # EDA + ML + genera todas las figuras del PDF
python demo_manipulacion.py  # Simula un ataque a la cadena y captura la detección
python demo_benchmarks.py    # Medición de tiempos de las operaciones criptográficas
```

## Pruebas

```bash
pytest -v                                                          # 69 tests
bandit -r crypto_module blockchain_module analytics app data       # 0 issues
```

## Resultados destacados

- **Modelo ML:** F1 = 0.944 (Regresión Logística), AUC = 0.996 (Random Forest).
- **Cifrado AES:** 0.017 ms por campo.
- **Firma RSA-PSS:** 0.67 ms; verificación: 0.03 ms.
- **Minería PoW** (dificultad 3): 32 ms por bloque.

## Licencia

Uso académico. Consultar el fichero `LICENSE`.
