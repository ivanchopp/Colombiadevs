"""Sala por visitante: el código viaja en el enlace (?sala=CODIGO). Spec: PD2."""
from __future__ import annotations

import streamlit as st

from acta.salas import codigo_valido, generar_codigo
from app.config import LARGO_SALA


def sala_actual() -> str | None:
    """Devuelve la sala válida de la URL o de la sesión; None si no hay o es inválida."""
    codigo = st.query_params.get("sala") or st.session_state.get("sala")
    if codigo and codigo_valido(codigo, LARGO_SALA):
        st.session_state["sala"] = codigo
        return codigo
    return None


def crear_sala() -> str:
    codigo = generar_codigo(LARGO_SALA)
    st.session_state["sala"] = codigo
    st.query_params["sala"] = codigo
    return codigo
