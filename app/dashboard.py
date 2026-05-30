"""Dashboard interactivo de Learning Analytics seguro.

Lanzar con:
    streamlit run app/dashboard.py

Tres vistas según el rol del usuario autenticado:
    - Administrador: métricas globales + integridad de la cadena + auditoría.
    - Docente: lista de alumnos en riesgo + detalle + registro de notas firmadas.
    - Estudiante: solo sus propios datos descifrados con su clave privada.
"""

from __future__ import annotations

import pickle  # nosec B403 - solo deserializamos modelos generados por nuestro propio bootstrap.py
import sys
from datetime import datetime
from pathlib import Path

# Aseguramos que se pueda importar el proyecto cuando se lanza con `streamlit run app/dashboard.py`
RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import pandas as pd
import streamlit as st

from analytics import distribucion_riesgo, matriz_correlacion
from app.operaciones import (
    RUTA_CADENA,
    cargar_o_crear_cadena,
    obtener_operaciones_por_estudiante,
    operacion_consulta_registro,
    operacion_registrar_nota,
)
from app.usuarios import autenticar, cargar_usuarios
from viz import (
    aplicar_estilo,
    grafico_distribucion_notas,
    grafico_distribucion_riesgo,
    grafico_matriz_correlacion,
)


# ---------------------------------------------------------------------------
# Configuración de la página
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Learning Analytics Seguro",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)

RUTA_CSV = RAIZ / "data" / "estudiantes.csv"
RUTA_MODELO = RAIZ / "data" / "modelo_riesgo.pkl"
RUTA_ESCALADOR = RAIZ / "data" / "escalador.pkl"

aplicar_estilo()


# ---------------------------------------------------------------------------
# Cachés
# ---------------------------------------------------------------------------
@st.cache_data
def cargar_dataframe() -> pd.DataFrame:
    if not RUTA_CSV.exists():
        st.error("El dataset no existe. Ejecuta primero `python bootstrap.py`.")
        st.stop()
    return pd.read_csv(RUTA_CSV)


@st.cache_resource
def cargar_modelo():
    if not RUTA_MODELO.exists() or not RUTA_ESCALADOR.exists():
        st.error("El modelo no está entrenado. Ejecuta primero `python bootstrap.py`.")
        st.stop()
    with open(RUTA_MODELO, "rb") as f:
        modelo = pickle.load(f)  # nosec B301 - origen confiable: bootstrap.py local
    with open(RUTA_ESCALADOR, "rb") as f:
        escalador = pickle.load(f)  # nosec B301 - origen confiable: bootstrap.py local
    return modelo, escalador


@st.cache_resource
def cargar_cadena_persistida():
    """La cadena se mantiene viva entre re-runs gracias a cache_resource."""
    return cargar_o_crear_cadena(dificultad=3)


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------
def pantalla_login() -> None:
    st.title("🔐 Learning Analytics Seguro")
    st.caption("Plataforma educativa con criptografía AES, firmas RSA y blockchain SHA-256.")

    col_izq, col_der = st.columns([1, 1])
    with col_izq:
        st.subheader("Iniciar sesión")
        usuario = st.text_input("Usuario", placeholder="admin · profesor.moya · EST-0001")
        contrasena = st.text_input("Contraseña", type="password")
        if st.button("Entrar", type="primary", use_container_width=True):
            usuarios = cargar_usuarios()
            ok, u, pem = autenticar(usuario, contrasena, usuarios)
            if ok:
                st.session_state["autenticado"] = True
                st.session_state["usuario"] = u
                st.session_state["pem_privada"] = pem
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")

    with col_der:
        st.subheader("Credenciales demo")
        st.markdown("""
        | Usuario | Contraseña | Rol |
        |---|---|---|
        | `admin` | `Admin1234!` | Administrador |
        | `profesor.moya` | `Profesor1234!` | Docente |
        | `EST-0001` | `Estudiante1!` | Estudiante |
        | `EST-0128` | `Estudiante1!` | Estudiante (alto riesgo) |
        """)
        st.caption("Las contraseñas se hashean con PBKDF2-HMAC-SHA256 (600 000 iteraciones). "
                   "La clave privada RSA se descifra solo durante la sesión.")


# ---------------------------------------------------------------------------
# Cabecera común tras login
# ---------------------------------------------------------------------------
def barra_lateral() -> None:
    u = st.session_state["usuario"]
    with st.sidebar:
        st.markdown(f"### 👤 {u.usuario}")
        st.caption(f"Rol: **{u.rol}**")
        if u.id_estudiante:
            st.caption(f"ID estudiante: {u.id_estudiante}")
        st.divider()

        cadena = cargar_cadena_persistida()
        ok, mensaje = cadena.verificar_integridad()
        if ok:
            st.success(f"⛓️ Cadena íntegra ({len(cadena)} bloques)")
        else:
            st.error(f"⛓️ Cadena rota: {mensaje}")

        st.divider()
        if st.button("Cerrar sesión", use_container_width=True):
            for k in ("autenticado", "usuario", "pem_privada"):
                st.session_state.pop(k, None)
            st.rerun()


# ---------------------------------------------------------------------------
# VISTA ADMINISTRADOR
# ---------------------------------------------------------------------------
def vista_administrador() -> None:
    st.title("📊 Panel de Administrador")
    st.caption("Métricas globales, integridad del sistema y auditoría.")

    df = cargar_dataframe()
    cadena = cargar_cadena_persistida()
    usuarios = cargar_usuarios()

    # ---- Métricas principales ----
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Estudiantes", len(df))
    col2.metric("En riesgo", int(df["riesgo"].sum()), f"{df['riesgo'].mean()*100:.1f}%")
    col3.metric("Bloques en cadena", len(cadena))
    col4.metric("Usuarios registrados", len(usuarios))

    st.divider()

    # ---- Gráficos globales ----
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Distribución de riesgo")
        st.pyplot(grafico_distribucion_riesgo(df))

    with col2:
        st.subheader("Distribución de notas por riesgo")
        st.pyplot(grafico_distribucion_notas(df))

    st.subheader("Matriz de correlación")
    st.pyplot(grafico_matriz_correlacion(matriz_correlacion(df)))

    st.divider()

    # ---- Integridad de la cadena ----
    st.subheader("🔍 Verificación de integridad")
    ok, mensaje = cadena.verificar_integridad()
    if ok:
        st.success(mensaje)
    else:
        st.error(mensaje)

    # ---- Vista detallada de la cadena ----
    st.subheader("⛓️ Cadena de bloques")
    filas_cadena = []
    for b in cadena.bloques:
        filas_cadena.append({
            "Índice": b.indice,
            "Marca de tiempo": datetime.fromtimestamp(b.marca_tiempo).strftime("%Y-%m-%d %H:%M:%S"),
            "Transacciones": len(b.transacciones),
            "Nonce": b.nonce,
            "Hash actual": b.hash_actual[:24] + "…",
            "Hash anterior": b.hash_anterior[:24] + "…",
        })
    st.dataframe(pd.DataFrame(filas_cadena), use_container_width=True, hide_index=True)

    # ---- Gestión de usuarios ----
    st.subheader("👥 Usuarios del sistema")
    filas_usuarios = [{
        "Usuario": nombre,
        "Rol": u.rol,
        "ID estudiante": u.id_estudiante or "—",
        "Clave pública (preview)": u.clave_publica_pem.split("\n")[1][:40] + "…",
    } for nombre, u in usuarios.items()]
    st.dataframe(pd.DataFrame(filas_usuarios), use_container_width=True, hide_index=True)


# ---------------------------------------------------------------------------
# VISTA DOCENTE
# ---------------------------------------------------------------------------
def vista_docente() -> None:
    st.title("🎓 Panel del Docente")
    st.caption("Detección de alumnos en riesgo y registro de notas con firma digital.")

    df = cargar_dataframe()
    modelo, escalador = cargar_modelo()
    cadena = cargar_cadena_persistida()
    u = st.session_state["usuario"]

    # ---- Predicción de riesgo para todos los alumnos ----
    columnas_X = [c for c in df.columns if c not in ("id_estudiante", "nombre", "email", "riesgo")]
    X_escalado = escalador.transform(df[columnas_X])
    df_pred = df[["id_estudiante", "media", "asistencia_pct", "participacion_pct"]].copy()
    df_pred["probabilidad_riesgo"] = modelo.predict_proba(X_escalado)[:, 1]
    df_pred["riesgo_predicho"] = (df_pred["probabilidad_riesgo"] >= 0.5).astype(int)

    col1, col2, col3 = st.columns(3)
    col1.metric("Alumnos asignados", len(df_pred))
    col2.metric("En riesgo (predicción)", int(df_pred["riesgo_predicho"].sum()))
    col3.metric("Media de la clase", f"{df['media'].mean():.2f}")

    st.divider()

    # ---- Top alumnos en riesgo ----
    st.subheader("⚠️ Top 10 alumnos con mayor probabilidad de riesgo")
    top10 = df_pred.nlargest(10, "probabilidad_riesgo").reset_index(drop=True)
    top10_display = top10.copy()
    top10_display["probabilidad_riesgo"] = top10_display["probabilidad_riesgo"].apply(lambda x: f"{x*100:.1f}%")
    st.dataframe(top10_display, use_container_width=True, hide_index=True)

    st.divider()

    # ---- Registrar nota (operación firmada) ----
    st.subheader("✍️ Registrar nueva nota (firmada y encadenada)")
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        id_alumno = st.selectbox("Alumno", df["id_estudiante"].tolist())
    with col2:
        asignatura = st.selectbox(
            "Asignatura",
            ["matematicas", "lengua", "ingles", "ciencias", "historia"],
        )
    with col3:
        nota = st.number_input("Nota", min_value=0.0, max_value=10.0, value=7.0, step=0.1)

    if st.button("Registrar y firmar", type="primary"):
        indice = operacion_registrar_nota(
            cadena=cadena,
            emisor=u.usuario,
            pem_clave_privada=st.session_state["pem_privada"],
            clave_publica_pem=u.clave_publica_pem,
            id_estudiante=id_alumno,
            asignatura=asignatura,
            nota=nota,
        )
        st.success(f"Nota registrada y minada en el bloque #{indice} de la cadena.")
        st.rerun()

    st.divider()

    # ---- Distribución global ----
    st.subheader("Distribución de notas")
    st.pyplot(grafico_distribucion_notas(df))


# ---------------------------------------------------------------------------
# VISTA ESTUDIANTE
# ---------------------------------------------------------------------------
def vista_estudiante() -> None:
    u = st.session_state["usuario"]
    df = cargar_dataframe()
    cadena = cargar_cadena_persistida()

    estudiante = df.loc[df["id_estudiante"] == u.id_estudiante]
    if estudiante.empty:
        st.error(f"No se encuentran datos del estudiante {u.id_estudiante}.")
        return
    estudiante = estudiante.iloc[0]

    st.title(f"👨‍🎓 Hola, {estudiante['nombre']}")
    st.caption(f"Identificador: {u.id_estudiante}  ·  Sesión segura con clave RSA propia.")

    # Registrar la consulta del estudiante a sus propios datos en la cadena (audit GDPR).
    operacion_consulta_registro(
        cadena=cadena,
        emisor=u.usuario,
        pem_clave_privada=st.session_state["pem_privada"],
        clave_publica_pem=u.clave_publica_pem,
        id_estudiante=u.id_estudiante,
    )

    # ---- Resumen ----
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Nota media", f"{estudiante['media']:.2f}", f"{estudiante['media'] - df['media'].mean():+.2f} vs clase")
    col2.metric("Asistencia", f"{estudiante['asistencia_pct']:.1f}%")
    col3.metric("Participación", f"{estudiante['participacion_pct']:.1f}%")
    col4.metric(
        "Estado",
        "⚠️ En riesgo" if estudiante["riesgo"] == 1 else "✅ Sin riesgo",
    )

    st.divider()

    # ---- Notas por asignatura ----
    st.subheader("Mis notas por asignatura")
    asignaturas = ["matematicas", "lengua", "ingles", "ciencias", "historia"]
    notas_df = pd.DataFrame({
        "Asignatura": [a.capitalize() for a in asignaturas],
        "Mi nota": [estudiante[f"nota_{a}"] for a in asignaturas],
        "Media de la clase": [round(df[f"nota_{a}"].mean(), 2) for a in asignaturas],
    })
    st.dataframe(notas_df, use_container_width=True, hide_index=True)
    st.bar_chart(notas_df.set_index("Asignatura"))

    st.divider()

    # ---- Historial de operaciones en la cadena ----
    st.subheader("⛓️ Historial de mi expediente en la blockchain")
    operaciones = obtener_operaciones_por_estudiante(cadena, u.id_estudiante)
    if not operaciones:
        st.info("Aún no hay operaciones registradas en la cadena referidas a este expediente.")
    else:
        filas = []
        for op in operaciones:
            filas.append({
                "Bloque": op["bloque"],
                "Tipo": op["tipo"],
                "Emisor": op["emisor"],
                "Fecha": datetime.fromtimestamp(op["marca_tiempo"]).strftime("%Y-%m-%d %H:%M:%S"),
                "Firma válida": "✅" if op.get("firma_valida") else ("—" if op.get("firma_valida") is None else "❌"),
            })
        st.dataframe(pd.DataFrame(filas), use_container_width=True, hide_index=True)

    st.caption(
        "Cada consulta a este expediente queda registrada como transacción firmada en la cadena, "
        "cumpliendo el principio de **trazabilidad** de GDPR (artículo 30 — registro de actividades de tratamiento)."
    )


# ---------------------------------------------------------------------------
# Enrutador principal
# ---------------------------------------------------------------------------
def main() -> None:
    if not st.session_state.get("autenticado"):
        pantalla_login()
        return

    barra_lateral()
    rol = st.session_state["usuario"].rol
    if rol == "administrador":
        vista_administrador()
    elif rol == "docente":
        vista_docente()
    elif rol == "estudiante":
        vista_estudiante()
    else:
        st.error(f"Rol desconocido: {rol}")


if __name__ == "__main__":
    main()
