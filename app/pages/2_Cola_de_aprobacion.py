"""Panel 2 · Cola de aprobación. Cada rol ve solo lo que le toca (PP5)."""
import streamlit as st

from acta.estado import facturas_por_estado
from app.apoyo import CANALES, ROLES, AprobacionRechazada, cola_para_rol, formato_monto, responder
from app.comun import almacen, barra_lateral, encabezado, exigir_rol, obtener_sala

st.set_page_config(page_title="Panel 2 · Cola de aprobación", layout="wide")
sala = obtener_sala()
barra_lateral(sala)
encabezado("Panel 2 · Finanzas › Cola de aprobación", sala)
rol = exigir_rol()
st.caption(f"Rol: {ROLES[rol]}. Para aprobar o rechazar hay que escribir un motivo, que queda en el acta. "
           "Aprobar es un pago de práctica: no se mueve dinero.")

if mensaje := st.session_state.pop("mensaje_cola", None):
    st.success(mensaje)

cola = cola_para_rol(facturas_por_estado(almacen().filas(sala)), rol)
if not cola:
    st.write("No hay casos pendientes para tu rol.")

for f in cola:
    d = f.decision
    with st.container(border=True):
        st.text(f"{f.factura_id} · {d['beneficiario']} · nivel {d['nivel'].lower()}")
        st.text(f"Monto: {formato_monto(d['monto'], d['moneda'])}"
                + (f" (≈ {formato_monto(d['monto_base'], 'COP')})" if d["moneda"] != "COP" else "")
                + f" · vence {d['vence']}")
        st.text(f"Motivo: {d['motivo']}")
        for r in d["revisiones"]:
            if r["resultado"] != "OK":
                st.text(f"  {r['resultado']}: {r['mensaje']}")
        motivo = st.text_area("Motivo de tu decisión (obligatorio)", key=f"motivo_{f.factura_id}",
                              max_chars=500)
        canal = st.selectbox("Canal de pago (si apruebas)", CANALES, key=f"canal_{f.factura_id}",
                             index=CANALES.index(d["canal_sugerido"]) if d.get("canal_sugerido") in CANALES
                             else 0)
        b1, b2, _ = st.columns([1, 1, 4])
        for boton, aprobar in ((b1.button("Aprobar", key=f"ap_{f.factura_id}", type="primary"), True),
                               (b2.button("Rechazar", key=f"re_{f.factura_id}"), False)):
            if boton:
                try:
                    fila = responder(almacen(), sala, f, rol, aprobar, motivo, canal)
                except AprobacionRechazada as e:
                    st.error(str(e))
                except Exception:
                    st.error("No se pudo escribir en el acta. No se registró ningún pago.")
                else:
                    st.session_state["mensaje_cola"] = (
                        f"{f.factura_id} {'aprobada (pago de práctica)' if aprobar else 'rechazada'}. "
                        f"Quedó en el acta, fila #{fila.num}.")
                    st.rerun()
