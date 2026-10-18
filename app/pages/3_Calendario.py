"""Panel 2 · Calendario mes a mes (PP6.2, PP6.4)."""
from datetime import date

import streamlit as st

from acta.estado import facturas_por_estado
from app.apoyo import estados_calendario, inesperadas, meses_del_calendario, monto_legible, semanas_del_mes
from app.comun import almacen, barra_lateral, contexto_y_reglas, encabezado, exigir_rol, obtener_sala

MESES = ["", "enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre",
         "octubre", "noviembre", "diciembre"]
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
MARCA = {"llegó": "✔ llegó", "pendiente": "… pendiente", "atrasada": "! atrasada"}

st.set_page_config(page_title="Panel 2 · Calendario", layout="wide")
sala = obtener_sala()
barra_lateral(sala)
encabezado("Panel 2 · Finanzas › Calendario", sala)
exigir_rol()

filas = almacen().filas(sala)
facturas = facturas_por_estado(filas)
ctx, reglas = contexto_y_reglas(filas)
eventos = estados_calendario(ctx, reglas)
por_dia: dict[date, list] = {}
for e in eventos:
    por_dia.setdefault(e["fecha"], []).append(e)

meses = meses_del_calendario(eventos, ctx.hoy)
por_defecto = (min(e["fecha"] for e in eventos).year, min(e["fecha"] for e in eventos).month)
if st.session_state.get("mes_calendario") not in meses:
    st.session_state["mes_calendario"] = por_defecto if por_defecto in meses else meses[0]


def mover(paso: int):
    st.session_state["mes_calendario"] = meses[meses.index(st.session_state["mes_calendario"]) + paso]


actual = st.session_state["mes_calendario"]
c_ant, c_sel, c_sig = st.columns([1, 3, 1], vertical_alignment="bottom")
c_ant.button("◀ Anterior", on_click=mover, args=(-1,), disabled=actual == meses[0], use_container_width=True)
c_sig.button("Siguiente ▶", on_click=mover, args=(1,), disabled=actual == meses[-1], use_container_width=True)
anio, mes = c_sel.selectbox("Mes", meses, key="mes_calendario", format_func=lambda m: f"{MESES[m[1]].capitalize()} {m[0]}")

st.subheader(f"{MESES[mes].capitalize()} {anio} · días hábiles")
st.caption("✔ llegó · … pendiente · ! atrasada. Una factura inesperada no se rechaza: se escala. "
           "Fechas y montos esperados son de ejemplo (supuesto).")
if not any(d.year == anio and d.month == mes for d in por_dia):
    st.info("No hay obligaciones esperadas este mes (datos de ejemplo, supuesto).")

columnas = st.columns(5)
for i, nombre in enumerate(DIAS):
    columnas[i].markdown(f"**{nombre}**")
for semana in semanas_del_mes(anio, mes):
    columnas = st.columns(5)
    for i, dia in enumerate(semana):
        with columnas[i].container(border=True, height=120):
            st.caption(f"{dia.day} {MESES[dia.month][:3]}" + ("" if dia.month == mes else " ·"))
            for e in (por_dia.get(dia, []) if dia.month == mes else []):         # solo las del mes que se ve
                st.text(f"{e['proveedor']}\n{MARCA[e['estado']]}")

st.subheader("Fuera del calendario")
fuera = inesperadas(facturas)
if not fuera:
    st.write("No hay facturas inesperadas.")
for f in fuera:
    st.text(f"{f.factura_id} · {f.decision['beneficiario']} · "
            f"{monto_legible(f.decision)} · inesperada: se escala")
