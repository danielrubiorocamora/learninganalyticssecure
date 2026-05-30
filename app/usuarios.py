"""Gestión de usuarios con autenticación segura.

Cada usuario tiene:
    - `usuario`: identificador de login (string).
    - `rol`: 'administrador', 'docente' o 'estudiante'.
    - `sal`: sal aleatoria de PBKDF2.
    - `clave_verificacion`: derivada de la contraseña, usada solo para verificar login.
    - `clave_publica_pem`: clave pública RSA en formato PEM.
    - `clave_privada_cifrada_pem`: clave privada RSA cifrada con AES derivado de
      la contraseña del usuario. Solo el propio usuario puede descifrarla en cada login.
    - `id_estudiante`: solo si el rol es 'estudiante', vincula con un registro del CSV.

El patrón de almacenamiento sigue el modelo de los gestores de contraseñas:
nunca se guarda la contraseña ni la clave derivada en claro. La clave privada está
cifrada en reposo y solo se descifra en memoria durante la sesión.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from cryptography.fernet import InvalidToken

from crypto_module import (
    cifrar,
    derivar_clave,
    descifrar,
    generar_par_de_claves,
    generar_sal,
    serializar_clave_privada,
    serializar_clave_publica,
)


ROLES_VALIDOS = ("administrador", "docente", "estudiante")
RUTA_USUARIOS_POR_DEFECTO = Path(__file__).resolve().parent.parent / "data" / "usuarios.json"


@dataclass
class Usuario:
    """Representación serializable de un usuario."""
    usuario: str
    rol: str
    sal_hex: str                          # sal en hex
    clave_verificacion: str               # token Fernet (cifra un literal conocido)
    clave_publica_pem: str
    clave_privada_cifrada_pem: str        # PEM cifrado con AES vía Fernet
    id_estudiante: str | None = None      # solo para rol estudiante

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# Almacenamiento
# ---------------------------------------------------------------------------
def cargar_usuarios(ruta: str | Path = RUTA_USUARIOS_POR_DEFECTO) -> dict[str, Usuario]:
    """Carga el diccionario de usuarios desde JSON. Si no existe, devuelve vacío."""
    ruta = Path(ruta)
    if not ruta.exists():
        return {}
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    return {nombre: Usuario(**info) for nombre, info in datos.items()}


def guardar_usuarios(usuarios: dict[str, Usuario], ruta: str | Path = RUTA_USUARIOS_POR_DEFECTO) -> None:
    """Persiste todos los usuarios en JSON."""
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    serializable = {nombre: u.to_dict() for nombre, u in usuarios.items()}
    ruta.write_text(json.dumps(serializable, indent=2, ensure_ascii=False), encoding="utf-8")


# ---------------------------------------------------------------------------
# Alta y autenticación
# ---------------------------------------------------------------------------
LITERAL_VERIFICACION = "VERIFICACION_LOGIN_OK"


def registrar_usuario(
    usuario: str,
    contrasena: str,
    rol: str,
    id_estudiante: str | None = None,
    usuarios_existentes: dict[str, Usuario] | None = None,
) -> Usuario:
    """Crea un nuevo usuario con clave RSA + contraseña hasheada."""
    if rol not in ROLES_VALIDOS:
        raise ValueError(f"Rol inválido. Debe ser uno de {ROLES_VALIDOS}.")
    if len(contrasena) < 6:
        raise ValueError("La contraseña debe tener al menos 6 caracteres.")
    if usuarios_existentes is not None and usuario in usuarios_existentes:
        raise ValueError(f"El usuario '{usuario}' ya existe.")
    if rol == "estudiante" and id_estudiante is None:
        raise ValueError("Un usuario con rol 'estudiante' requiere id_estudiante.")

    sal = generar_sal()
    clave_simetrica = derivar_clave(contrasena, sal)

    # Generamos el par RSA del usuario.
    clave_privada, clave_publica = generar_par_de_claves()
    pem_publica = serializar_clave_publica(clave_publica).decode("utf-8")
    pem_privada = serializar_clave_privada(clave_privada).decode("utf-8")

    # La clave privada se almacena cifrada con AES derivado de la contraseña.
    pem_privada_cifrada = cifrar(pem_privada, clave_simetrica)

    # Token de verificación: cifra un literal conocido para validar la contraseña en login.
    token_verificacion = cifrar(LITERAL_VERIFICACION, clave_simetrica)

    return Usuario(
        usuario=usuario,
        rol=rol,
        sal_hex=sal.hex(),
        clave_verificacion=token_verificacion,
        clave_publica_pem=pem_publica,
        clave_privada_cifrada_pem=pem_privada_cifrada,
        id_estudiante=id_estudiante,
    )


def autenticar(
    usuario: str,
    contrasena: str,
    usuarios: dict[str, Usuario],
) -> tuple[bool, Usuario | None, str | None]:
    """Verifica las credenciales.

    Devuelve `(ok, usuario, pem_privada_descifrada)`. Si el login falla, todos los
    valores excepto el primero son None.
    """
    if usuario not in usuarios:
        return False, None, None

    u = usuarios[usuario]
    sal = bytes.fromhex(u.sal_hex)
    clave_simetrica = derivar_clave(contrasena, sal)

    try:
        verificacion = descifrar(u.clave_verificacion, clave_simetrica)
        if verificacion != LITERAL_VERIFICACION:
            return False, None, None
        # Contraseña correcta: descifrar la clave privada del usuario.
        pem_privada = descifrar(u.clave_privada_cifrada_pem, clave_simetrica)
        return True, u, pem_privada
    except InvalidToken:
        # Contraseña incorrecta.
        return False, None, None


# ---------------------------------------------------------------------------
# Bootstrap: usuarios iniciales para la demo
# ---------------------------------------------------------------------------
USUARIOS_DEMO = [
    # (usuario, contraseña, rol, id_estudiante)
    ("admin", "Admin1234!", "administrador", None),
    ("profesor.moya", "Profesor1234!", "docente", None),
    ("profesor.garcia", "Profesor1234!", "docente", None),
    ("EST-0001", "Estudiante1!", "estudiante", "EST-0001"),
    ("EST-0042", "Estudiante1!", "estudiante", "EST-0042"),
    ("EST-0100", "Estudiante1!", "estudiante", "EST-0100"),
    ("EST-0128", "Estudiante1!", "estudiante", "EST-0128"),
    ("EST-0210", "Estudiante1!", "estudiante", "EST-0210"),
]


def bootstrap_usuarios_demo(ruta: str | Path = RUTA_USUARIOS_POR_DEFECTO, sobrescribir: bool = False) -> dict[str, Usuario]:
    """Crea los usuarios demo si no existen ya.

    Si `sobrescribir=True` borra cualquier usuario previo y regenera todos.
    """
    ruta = Path(ruta)
    if not sobrescribir and ruta.exists():
        return cargar_usuarios(ruta)

    usuarios: dict[str, Usuario] = {}
    for nombre, contrasena, rol, id_est in USUARIOS_DEMO:
        usuarios[nombre] = registrar_usuario(nombre, contrasena, rol, id_est, usuarios)

    guardar_usuarios(usuarios, ruta)
    return usuarios
