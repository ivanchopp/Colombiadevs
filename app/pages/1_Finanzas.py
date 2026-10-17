"""Panel 2: Finanzas, con rol. Pestañas pendientes (PT5 a PT10)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st  # noqa: E402

from app import textos  # noqa: E402
from app.componentes.rol import rol_actual  # noqa: E402
from app.componentes.sala import sala_actual  # noqa: E402

st.set_page_config(page_title="Finanzas", page_icon="💼")
st.title("Panel de Finanzas")
st.info(textos.AVISO_FICTICIO)
sala = sala_actual()
if sala is None:
    st.warning(textos.SALA_INVALIDA)
    st.stop()
rol = rol_actual()
st.caption(f"Sala {sala} · {rol}")
for pestana, nombre in zip(st.tabs(["Tablero", "Cola", "Acta", "Reglas"]), ["Tablero", "Cola", "Acta", "Reglas"]):
    with pestana:
        st.write(f"{nombre}: pendiente.")
