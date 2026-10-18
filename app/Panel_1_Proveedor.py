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
st.info(f"Datos ficticios, solo para práctica. Has usado {len(facturas)} de {flujo.facturas_max()} facturas permitidas.")
if not flujo.modo_demo():
    st.caption(f"Lectura de facturas con IA: {flujo.lectura_ia.descripcion_proveedor()}.")
else:
    st.caption("Modo demo: sin conexión a la IA. Los archivos se leen solo con patrones de texto, por lo que "
               "pasan a revisión de una persona. Para ver por qué, agrega ?diagnostico=1 al enlace.")

if st.query_params.get("diagnostico"):
    d = flujo.lectura_ia.diagnostico()
    with st.container(border=True):
        st.markdown("**Diagnóstico de la IA** (solo estados y nombres; nunca el valor de una clave)")
        lineas = [f"Proveedor activo: {d['proveedor'] or 'ninguno (modo demo)'}", f"Motivo: {d['razon']}", ""]
        lineas += [f"{n}: {e}" for n, e in d["claves"].items()]
        lineas += [f"{n}: {v}" for n, v in d["ajustes"].items()]
        if d["parecidas"]:
            lineas += ["", "Variables con nombre parecido pero distinto (¿error de escritura?): "
                       + ", ".join(d["parecidas"])]
        lineas += ["", *[f"Despliegue · {k}: {v}" for k, v in d["despliegue"].items()]]
        st.text("\n".join(lineas))
        f = flujo.lectura_ia.ULTIMA_FALLA
        st.text("Última falla de lectura con IA: "
                + (f"{f['cuando']} · {f['proveedor']} · {f['mensaje']}" if f["cuando"] else "ninguna desde el último arranque"))
        if f["cuando"] and (pista := flujo.lectura_ia.pista_de_falla(f["mensaje"])):
            st.warning(pista)                                           # EA2b.12
        if not flujo.modo_demo() and st.button("Probar la conexión con la IA ahora"):    # EA2b.11: una llamada
            r = flujo.lectura_ia.probar_conexion()
            st.text(f"{'OK' if r['ok'] else 'FALLA'} · {r['proveedor']} ({r['modelo']})\n{r['detalle']}"
                    + (("\nModelos disponibles: " + ", ".join(r["modelos"])) if r["modelos"] else ""))
            if not r["ok"] and (pista := flujo.lectura_ia.pista_de_falla(r["detalle"])):
                st.warning(pista)                                       # EA2b.12

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
    archivo = st.file_uploader("Arrastra aquí un PDF, una foto, un correo o un XML",
                               type=["pdf", "jpg", "jpeg", "png", "eml", "txt", "xml"])
    st.caption("PDF, JPG, PNG, EML o XML de factura electrónica (Colombia, Perú, México, Ecuador, Uruguay, Brasil, Chile, Costa Rica, Paraguay; otros formatos se revisan a mano) · máx. 5 MB")
    if archivo is not None and st.button("Enviar esta factura", type="primary"):
        intentar(flujo.recibir, almacen(), sala, archivo.name, archivo.getvalue())
    with st.expander("Archivos de muestra (ficticios)"):
        st.caption("Descarga uno y súbelo arriba. El sistema lo lee y decide solo.")
        for clave in ejemplos.EJEMPLOS:
            nombre, datos = ejemplos.leer_ejemplo(clave)
            st.download_button(ejemplos.ROTULOS[clave], datos, file_name=nombre, mime="text/plain",
                               key=f"muestra_{clave}", use_container_width=True)

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
