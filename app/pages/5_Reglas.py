"""Panel 2 · Reglas: ver y cambiar las reglas de pago de la sala (PP8)."""
from decimal import Decimal

import streamlit as st

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
    if st.button("Confirmar cambio", type="primary"):
        try:
            fila = cambiar_reglas(almacen(), sala, actuales, valores, rol, motivo)
        except ErrorDeReglas as e:
            st.error(str(e))
        except Exception:
            st.error("No se pudo escribir en el acta. Las reglas no cambiaron.")
        else:
            st.session_state["mensaje_reglas"] = f"Reglas cambiadas. Quedó en el acta, fila #{fila.num}."
            for k in EDITABLES:
                st.session_state.pop(f"regla_{k}", None)
            st.session_state.pop("motivo_reglas", None)
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
