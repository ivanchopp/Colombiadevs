"""Piezas compartidas por los dos paneles: sala por enlace, almacén y selector de rol."""
import streamlit as st

from acta import salas
from acta.almacen import AlmacenSqlite
from acta.estado import facturas_por_estado
from engine.contexto import contexto_desde_acta
from engine.reglas_io import cargar_contexto_base, cargar_reglas, hoy_bogota, reglas_de_sala
from app.apoyo import ROLES, cola_para_rol, pendientes_por_rol

SEGUNDOS_REFRESCO = 5


@st.cache_resource
def almacen() -> AlmacenSqlite:
    return AlmacenSqlite()


def obtener_sala() -> str:
    """Toma la sala del enlace (?sala=). Si falta o no existe, crea una nueva (PP1)."""
    codigo = st.query_params.get("sala") or st.session_state.get("sala")
    if codigo and salas.codigo_valido(codigo) and almacen().sala_existe(codigo):
        sala = codigo
    else:
        sala = salas.crear(almacen())
        if codigo:
            st.warning("No encontré esa sala; creé una nueva con datos de ejemplo.")
    st.session_state["sala"] = sala
    st.query_params["sala"] = sala
    return sala


def _etiqueta_rol(rol: str, pendientes: dict[str, int]) -> str:
    n = pendientes.get(rol, 0)
    return f"{ROLES[rol]} 🔴 {n}" if n else ROLES[rol]               # PP3.3: punto rojo con el número


def exigir_rol() -> str:
    """Selector de rol de demostración. Entra como persona de finanzas y recuerda lo elegido (PP3.1)."""
    claves = list(ROLES)
    actual = st.session_state.get("rol")
    actual = actual if actual in claves else "PERSONA"
    facturas = facturas_por_estado(almacen().filas(st.session_state["sala"]))
    pendientes = pendientes_por_rol(facturas)
    elegido = st.segmented_control(
        "Entrar como", claves, format_func=lambda r: _etiqueta_rol(r, pendientes),
        default=actual, key="selector_rol") or actual               # si se deselecciona, se queda el anterior
    st.session_state["rol"] = elegido
    en_cola = sum(1 for f in cola_para_rol(facturas, elegido) if not f.decision.get("ficha_invalida"))   # PP3.4
    if elegido and en_cola:
        st.sidebar.markdown(f"🔴 **{en_cola}** aprobación(es) pendiente(s) en la cola")
    return elegido


def encabezado(titulo: str, sala: str):
    c1, c2 = st.columns([3, 1])
    c1.title(titulo)
    c2.caption(f"Sala {sala} · datos ficticios")


def barra_lateral(sala: str):
    st.sidebar.caption(f"Sala {sala}")
    st.sidebar.caption("Demo con datos ficticios. Tasas, canales y costos son de ejemplo (supuesto).")


def contexto_y_reglas(filas):
    """Contexto del motor armado desde el acta de la sala, y las reglas vigentes hoy en esa sala (PP8.7)."""
    hoy = hoy_bogota()
    return contexto_desde_acta(cargar_contexto_base(hoy), filas), reglas_de_sala(cargar_reglas(hoy)[0], filas)
