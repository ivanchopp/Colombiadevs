"""Panel 2 · Tablero. Las cifras salen del acta (PP4)."""
import pandas as pd
import streamlit as st

from acta.estado import facturas_por_estado
from acta.exportar_csv import exportar_eventos, exportar_facturas
from acta.tablero import cifras, comprobar_consistencia
from app.apoyo import DECISIONES, estados_calendario, formato_monto, monto_legible, quien_aprueba
from app.comun import (SEGUNDOS_REFRESCO, almacen, barra_lateral, contexto_y_reglas, encabezado,
                       exigir_rol, obtener_sala)

st.set_page_config(page_title="Panel 2 · Tablero", layout="wide")
sala = obtener_sala()
barra_lateral(sala)
encabezado("Panel 2 · Finanzas › Tablero", sala)
rol = exigir_rol()

ICONO = {"PAGADA": "Pagada", "FRENADA": "Frenada", "PENDIENTE": "Escalada", "RECHAZADA": "Rechazada"}


@st.fragment(run_every=SEGUNDOS_REFRESCO)
def tablero():
    filas = almacen().filas(sala)
    facturas = facturas_por_estado(filas)
    ctx, reglas = contexto_y_reglas(filas)
    atrasadas = sum(e["estado"] == "atrasada" for e in estados_calendario(ctx, reglas))
    c = cifras(filas, atrasadas, reglas.presupuesto_periodo)

    if not comprobar_consistencia(filas):
        st.error("Aviso: el tablero y el CSV no coinciden con el acta. No confíes en estas cifras.")

    m = st.columns(4)
    m[0].metric("Pagadas", c.pagadas)
    m[1].metric("Frenadas", c.frenadas)
    m[2].metric("Pendientes de aprobación", c.pendientes)
    m[3].metric("Esperadas atrasadas", c.atrasadas)
    st.progress(min(float(c.porcentaje) / 100, 1.0),
                text=f"Gasto del periodo frente al límite: {formato_monto(c.gasto, reglas.moneda_base)} de "
                     f"{formato_monto(c.presupuesto, reglas.moneda_base)} · {c.porcentaje} %")
    st.caption(f"Todo en {reglas.moneda_base} como moneda base · tasas de cambio, canales y costos de ejemplo "
               f"(supuestos) · actualizado {c.actualizado[11:19]} UTC")

    datos = [{
        "Factura": f.factura_id,
        "Proveedor": f.decision["beneficiario"],
        "Monto": monto_legible(f.decision),
        "Decisión": ICONO[f.estado],
        "Aprueba": quien_aprueba(f),
        "Motivo": f.decision["motivo"],
        "Canal sugerido": (f.respuesta or {}).get("canal_elegido") or f.decision.get("canal_sugerido")
                          or ("Al aprobar" if f.estado == "PENDIENTE" else "—"),
    } for f in sorted(facturas.values(), key=lambda x: x.fila_decision)]
    st.dataframe(pd.DataFrame(datos), hide_index=True, use_container_width=True)

    d1, d2, _ = st.columns([1, 1, 3])
    d1.download_button("Descargar facturas.csv", exportar_facturas(filas), "facturas.csv", "text/csv")
    d2.download_button("Descargar eventos.csv", exportar_eventos(filas), "eventos.csv", "text/csv")

    st.subheader("Detalle de una factura")
    elegida = st.selectbox("Factura", list(facturas), label_visibility="collapsed", key="detalle")
    if elegida:
        f = facturas[elegida]
        izq, der = st.columns(2)
        with izq:
            st.caption("Ficha")
            st.json(f.decision.get("ficha", {}))
        with der:
            st.caption(f"Revisiones del motor de reglas · {f.decision['version_reglas']} · "
                       f"decisión #{f.fila_decision}")
            for r in f.decision["revisiones"]:
                st.text(f"{r['resultado']:<6} {r['mensaje']}")
            st.text(f"Resultado: {DECISIONES[f.decision['decision']]}"
                    + (f" · nivel {f.decision['nivel'].lower()}" if f.decision["nivel"] != "NINGUNO" else ""))


tablero()
