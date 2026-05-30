"""Paquete de criptografía: cifrado simétrico, asimétrico y hashing."""

from crypto_module.cifrado_simetrico import (
    cifrar,
    cifrar_diccionario,
    derivar_clave,
    descifrar,
    descifrar_diccionario,
    generar_clave_aleatoria,
    generar_sal,
)
from crypto_module.cifrado_asimetrico import (
    cargar_clave_privada,
    cargar_clave_publica,
    firmar,
    generar_par_de_claves,
    serializar_clave_privada,
    serializar_clave_publica,
    verificar,
)
from crypto_module.hashing import hash_archivo, hash_dict, sha256_hex

__all__ = [
    # simétrico
    "cifrar",
    "descifrar",
    "cifrar_diccionario",
    "descifrar_diccionario",
    "derivar_clave",
    "generar_clave_aleatoria",
    "generar_sal",
    # asimétrico
    "generar_par_de_claves",
    "serializar_clave_privada",
    "serializar_clave_publica",
    "cargar_clave_privada",
    "cargar_clave_publica",
    "firmar",
    "verificar",
    # hash
    "sha256_hex",
    "hash_dict",
    "hash_archivo",
]
