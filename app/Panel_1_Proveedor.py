"""Panel 1 · Proveedor. Abierto. Nunca muestra reglas, límites ni motivos internos (PP2)."""
import streamlit as st

from acta.estado import estado_publico, facturas_por_estado
from app.apoyo import formato_monto
from app.comun import almacen, barra_lateral, encabezado, obtener_sala
from data.demo_semilla import ORIGEN

FACTURAS_MAX = 5
PASOS = ["recibida", "datos confirmados", "en revisión", "resuelta"]

st.set_page_config(page_title="Panel 1 · Proveedor", layout="wide")
sala = obtener_sala()
barra_lateral(sala)
encabezado("Panel 1 · Portal del proveedor", sala)

filas = almacen().filas(sala)
facturas = facturas_por_estado(filas)
propias = [f for f in facturas.values() if f.decision.get("origen") != ORIGEN]
st.info(f"Demo con datos ficticios. Has usado {len(propias)} de {FACTURAS_MAX} facturas permitidas.")

izq, der = st.columns(2)
with izq:
    st.subheader("Envía una factura")
    st.file_uploader("Arrastra aquí un PDF, una foto o un correo", type=["pdf", "jpg", "png", "eml"],
                     disabled=True, help="Disponible cuando esté listo el agente de entrada.")
    st.caption("PDF, JPG, PNG o EML · máx. 5 MB")
    st.markdown("**Probar con una factura de ejemplo**")
    cols = st.columns(4)
    for col, nombre in zip(cols, ["Normal", "Repetida", "Beneficiario nuevo", "Con orden escondida"]):
        col.button(nombre, disabled=True, use_container_width=True)
    st.caption("Los botones se activan cuando el agente de entrada y el motor de reglas estén conectados.")

with der:
    st.subheader("Estado de tus facturas")
    if not facturas:
        st.write("Aún no has enviado facturas.")
    for f in sorted(facturas.values(), key=lambda x: x.fila_decision):
        publico = estado_publico(f)
        with st.container(border=True):
            st.text(f"{f.factura_id} · {f.decision['beneficiario']} · "
                    f"{formato_monto(f.decision['monto'], f.decision['moneda'])}")
            hasta = PASOS.index(publico)
            st.text("  →  ".join(("● " if i <= hasta else "○ ") + p.capitalize() for i, p in enumerate(PASOS)))
            if publico == "en revisión":
                st.caption("Te avisaremos cuando haya una respuesta.")

st.divider()
st.link_button("Abrir panel de finanzas", f"/Tablero?sala={sala}")
