"""Panel 1: abierto al proveedor. Sin datos internos ni reglas (PD3)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st  # noqa: E402

from app import textos  # noqa: E402
from app.componentes.sala import crear_sala, sala_actual  # noqa: E402

st.set_page_config(page_title="Envía tu factura", page_icon="🧾")
st.title("Envía tu factura")
st.info(textos.AVISO_FICTICIO)
for paso in textos.GUIA_PASOS:
    st.write(paso)

sala = sala_actual()
if sala is None:
    if st.query_params.get("sala"):
        st.warning(textos.SALA_INVALIDA)
    if st.button("Crear sala"):
        sala = crear_sala()
        st.rerun()
else:
    st.success(f"Sala: {sala}")
    st.markdown(f"[Abrir panel de Finanzas](/Finanzas?sala={sala})")
    st.caption("Subir facturas: pendiente (tarea PT3).")
