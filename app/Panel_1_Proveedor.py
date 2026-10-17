"""Panel 1 · Proveedor. Abierto. Nunca muestra reglas, límites ni motivos internos (PP2)."""
import streamlit as st

from agents import ejemplos, flujo
from agents.estado import EstadoEntrada
from app.apoyo import formato_monto
from app.comun import almacen, barra_lateral, encabezado, obtener_sala

PASOS = ["recibida", "datos confirmados", "en revisión", "resuelta"]

st.set_page_config(page_title="Panel 1 · Proveedor", layout="wide")
sala = obtener_sala()
barra_lateral(sala)
encabezado("Panel 1 · Portal del proveedor", sala)

estados = EstadoEntrada(almacen())
facturas = estados.listar(sala)
st.info(f"Demo con datos ficticios. Has usado {len(facturas)} de {flujo.FACTURAS_MAX} facturas permitidas.")
if flujo.modo_demo():
    st.caption("Modo demo: sin conexión a la IA. Las facturas de ejemplo usan lecturas guardadas y los archivos "
               "propios se leen solo con patrones de texto, por lo que pasan a revisión de una persona.")

if aviso := st.session_state.pop("aviso_panel1", None):
    st.error(aviso)


def intentar(accion, *args, **kw):
    try:
        e = accion(*args, **kw)
        st.session_state["factura_activa"] = e["factura_id"]
    except flujo.EntradaRechazada as err:
        st.session_state["aviso_panel1"] = str(err)
    st.rerun()


izq, der = st.columns(2)
with izq:
    st.subheader("Envía una factura")
    archivo = st.file_uploader("Arrastra aquí un PDF, una foto o un correo",
                               type=["pdf", "jpg", "jpeg", "png", "eml", "txt"])
    st.caption("PDF, JPG, PNG o EML · máx. 5 MB")
    if archivo is not None and st.button("Enviar esta factura", type="primary"):
        intentar(flujo.recibir, almacen(), sala, archivo.name, archivo.getvalue())
    st.markdown("**Probar con una factura de ejemplo**")
    for col, (clave, nombre) in zip(st.columns(4), ejemplos.EJEMPLOS.items()):
        if col.button(nombre, key=f"ej_{clave}", use_container_width=True):
            intentar(flujo.recibir_ejemplo, almacen(), sala, clave)

with der:
    st.subheader("Estado de tus facturas")
    if not facturas:
        st.write("Aún no has enviado facturas.")
    for e in facturas:
        publico = flujo.estado_para_proveedor(almacen(), sala, e)
        L = e["lectura"]
        with st.container(border=True):
            marca = formato_monto(L["monto"], L["moneda"]) if L.get("monto") and L.get("moneda") else ""
            st.text(f"{e['factura_id']} · {L.get('beneficiario') or 'Factura'} · {marca}")
            hasta = PASOS.index(publico)
            st.text("  →  ".join(("● " if i <= hasta else "○ ") + p.capitalize() for i, p in enumerate(PASOS)))
            if st.button("Abrir chat", key=f"chat_{e['factura_id']}"):
                st.session_state["factura_activa"] = e["factura_id"]
                st.rerun()

activa = st.session_state.get("factura_activa")
actual = next((e for e in facturas if e["factura_id"] == activa), None)
if actual:
    st.divider()
    st.subheader(f"Chat · {actual['factura_id']}")
    for rol, texto in actual["chat"]:
        with st.chat_message("user" if rol == "proveedor" else "assistant"):
            st.text(texto)                              # siempre texto plano (PP7.3)
    if actual["estado"] == "recibida" and actual["pendientes"]:
        if mensaje := st.chat_input("Escribe tu respuesta…", max_chars=500):
            intentar(flujo.responder, almacen(), sala, actual["factura_id"], mensaje)

st.divider()
st.link_button("Abrir panel de finanzas", f"/Tablero?sala={sala}")
