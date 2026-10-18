"""Panel 2 · Reglas: ver y cambiar las reglas de pago de la sala (PP8)."""
from decimal import Decimal

import streamlit as st

from agents import reglas_texto
from app.apoyo import ROLES, cambiar_reglas, formato_monto
from app.comun import almacen, barra_lateral, contexto_y_reglas, encabezado, exigir_rol, obtener_sala
from engine.reglas_io import EDITABLES, ErrorDeReglas, cambios_que_aflojan, validar_cambio
from engine.simular import simular

MONTOS = {
    "autopago_max": "Pago automático hasta",
    "persona_max": "La persona de finanzas aprueba hasta (por encima, el senior)",
    "limite_periodo_beneficiario": "Límite por beneficiario en el mes (por encima, el senior)",
    "presupuesto_periodo": "Presupuesto del mes (por encima, se frena)",
}
PORCENTAJES = {
    "tolerancia_ok": "Diferencia aceptada con lo acordado (%)",
    "tolerancia_frenar": "Por encima de esta diferencia, la factura se frena (%)",
}
DIAS = {"ventana_dias": "Margen de días para emparejar con el calendario"}
NOMBRES = {**MONTOS, **PORCENTAJES, **DIAS}


def valor_real(k, v) -> Decimal:
    """Valor del formulario (entero; porcentaje de 0 a 100) -> valor de las reglas (fracción para porcentajes)."""
    return Decimal(v) / 100 if k in PORCENTAJES else Decimal(v)


def mostrar(reglas, k) -> str:
    return formato_valor(k, getattr(reglas, k), reglas.moneda_base)


def formato_valor(k, v, moneda) -> str:
    v = Decimal(str(v))
    if k in MONTOS:
        return formato_monto(v, moneda)
    if k in PORCENTAJES:
        return f"{(v * 100).normalize():f} %"
    return f"±{v} días"


st.set_page_config(page_title="Panel 2 · Reglas", layout="wide")
sala = obtener_sala()
barra_lateral(sala)
encabezado("Panel 2 · Finanzas › Reglas", sala)
rol = exigir_rol()

if mensaje := st.session_state.pop("mensaje_reglas", None):
    st.success(mensaje)

filas = almacen().filas(sala)
ctx, actuales = contexto_y_reglas(filas)

st.subheader(f"Reglas vigentes · versión {actuales.version}")
st.caption("Valores de demostración (supuesto). Un cambio solo vale para esta sala y para las facturas que "
           "lleguen después: las decisiones ya registradas no cambian.")
st.table({"Regla": [NOMBRES[k] for k in EDITABLES], "Valor": [mostrar(actuales, k) for k in EDITABLES]})
st.info(f"Techo duro por pago: {formato_monto(actuales.techo_duro_pago, actuales.moneda_base)}. "
        "Por encima no se paga nunca desde el sistema y no se cambia desde aquí (lo fija ingeniería).")

st.subheader("Pedir un cambio con texto")
st.caption("Escribe qué quieres cambiar. El sistema solo **propone**: rellena el formulario de abajo y nada se aplica "
           "hasta que escribas el motivo y confirmes. " + reglas_texto.EJEMPLO)
pedido = st.text_area("Tu pedido", max_chars=reglas_texto.LARGO_MAX, key="pedido_reglas", label_visibility="collapsed")
if st.button("Entender el pedido"):
    entendido = reglas_texto.entender(pedido, actuales, ctx.tasas)
    st.session_state["propuesta_texto"] = entendido
    st.session_state.pop("revisado_texto", None)
    if entendido.estado == "propuesta":
        for k, v in entendido.valores.items():                 # solo rellena el formulario (AR1.3)
            st.session_state[f"regla_{k}"] = int(v)
propuesta = st.session_state.get("propuesta_texto")
if propuesta is not None:
    with st.container(border=True):
        st.caption(f"Leído {'con IA' if propuesta.lector == 'ia' else 'por patrones (sin IA)'}. Tu pedido:")
        st.text(propuesta.pedido)                              # siempre texto plano (AR3.2)
        if propuesta.estado != "propuesta":
            st.info(propuesta.pregunta or "No entendí el pedido.")
        else:
            st.markdown("**Entendí:**")
            for k, v in propuesta.valores.items():
                st.write(f"- {NOMBRES[k]}: {formato_valor(k, getattr(actuales, k), actuales.moneda_base)}"
                         f" → {formato_valor(k, valor_real(k, v), actuales.moneda_base)}")
            for aviso in propuesta.avisos:
                st.caption(aviso)
            if propuesta.dudosa:
                st.warning("Revisa con cuidado: la propuesta no coincide del todo con tu texto.\n\n"
                           + "\n".join(f"- {s}" for s in propuesta.senales))
                st.checkbox("Revisé que estos son todos los cambios que quería", key="revisado_texto")
        if st.button("Descartar", key="descartar_texto"):
            st.session_state.pop("propuesta_texto", None)
            st.session_state.pop("revisado_texto", None)
            for k in EDITABLES:
                st.session_state.pop(f"regla_{k}", None)
            st.rerun()

st.subheader("Cambiar reglas")
st.caption(f"Rol: {ROLES[rol]}. Restringir (bajar un valor) lo puede firmar cualquier rol. "
           "Aflojar (subir un valor) solo lo firma el senior de finanzas.")
valores: dict = {}
c1, c2 = st.columns(2)
for i, (k, etiqueta) in enumerate(MONTOS.items()):
    valores[k] = Decimal((c1 if i % 2 == 0 else c2).number_input(
        f"{etiqueta} ({actuales.moneda_base})", min_value=0, step=50, value=int(getattr(actuales, k)),
        key=f"regla_{k}"))
for i, (k, etiqueta) in enumerate(PORCENTAJES.items()):
    # Porcentajes enteros: así el dinero nunca pasa por float.
    valores[k] = Decimal((c1 if i % 2 == 0 else c2).number_input(
        etiqueta, min_value=0, max_value=100, step=1, value=int(getattr(actuales, k) * 100),
        key=f"regla_{k}")) / 100
valores["ventana_dias"] = c1.number_input(DIAS["ventana_dias"], min_value=0, max_value=31, step=1,
                                          value=actuales.ventana_dias, key="regla_ventana_dias")

try:
    nuevas = validar_cambio(actuales, valores)
except ErrorDeReglas as e:
    st.error(str(e))
    st.stop()

cambiados = [k for k in EDITABLES if getattr(nuevas, k) != getattr(actuales, k)]
if not cambiados:
    st.write("Cambia un valor para ver la vista previa.")
else:
    aflojan = cambios_que_aflojan(actuales, nuevas)
    st.markdown("**Vista previa** (todavía no se guarda nada)")
    st.table({"Regla": [NOMBRES[k] for k in cambiados],
              "Antes": [mostrar(actuales, k) for k in cambiados],
              "Después": [mostrar(nuevas, k) for k in cambiados],
              "Efecto": ["Afloja" if k in aflojan else "Restringe" for k in cambiados]})
    if aflojan:
        st.warning("Este cambio **afloja** reglas: deja pasar más pagos sin revisión. Solo el senior puede firmarlo.")
    cambian = simular(filas, ctx, actuales, nuevas)
    if cambian:
        st.markdown(f"Con estas reglas, **{len(cambian)}** factura(s) de la sala se habrían decidido distinto:")
        st.dataframe([{"Factura": c["factura_id"], "Proveedor": c["beneficiario"], "Antes": c["antes"],
                       "Con el cambio": c["despues"], "Motivo": c["motivo"]} for c in cambian],
                     hide_index=True, use_container_width=True)
    else:
        st.write("Ninguna factura ya registrada en la sala habría cambiado de decisión.")
    motivo = st.text_area("Motivo del cambio (obligatorio)", max_chars=500, key="motivo_reglas")
    del_texto = (propuesta is not None and propuesta.estado == "propuesta" and set(cambiados) <= set(propuesta.valores)
                 and all(Decimal(str(valores[k])) == valor_real(k, v) for k, v in propuesta.valores.items()))
    sin_revisar = del_texto and propuesta.dudosa and not st.session_state.get("revisado_texto")
    if sin_revisar:
        st.info("Marca «Revisé que estos son todos los cambios que quería» para poder confirmar.")
    if st.button("Confirmar cambio", type="primary", disabled=bool(sin_revisar)):
        try:
            fila = cambiar_reglas(almacen(), sala, actuales, valores, rol, motivo,
                                  origen="texto" if del_texto else "formulario",
                                  pedido=propuesta.pedido if del_texto else None)
        except ErrorDeReglas as e:
            st.error(str(e))
        except Exception:
            st.error("No se pudo escribir en el acta. Las reglas no cambiaron.")
        else:
            st.session_state["mensaje_reglas"] = f"Reglas cambiadas. Quedó en el acta, fila #{fila.num}."
            for k in EDITABLES:
                st.session_state.pop(f"regla_{k}", None)
            for k in ("motivo_reglas", "propuesta_texto", "revisado_texto", "pedido_reglas"):
                st.session_state.pop(k, None)
            st.rerun()

historial = [f for f in filas if f.tipo == "CAMBIO_REGLA"]
if historial:
    st.subheader("Cambios de reglas en esta sala")
    for f in reversed(historial):
        p = f.payload
        cambios = "; ".join(f"{NOMBRES[k]}: {formato_valor(k, p['antes'][k], actuales.moneda_base)} → {formato_valor(k, p['despues'][k], actuales.moneda_base)}"
                            for k in EDITABLES if Decimal(p["antes"][k]) != Decimal(p["despues"][k]))
        st.text(f"Fila #{f.num} · {f.creado_en[:16].replace('T', ' ')} UTC · {f.actor} · {'afloja' if p['afloja'] else 'restringe'}\n"
                f"{cambios}\nMotivo: {p['motivo']}")
