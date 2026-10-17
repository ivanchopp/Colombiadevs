"""Panel 2 · Calendario del mes (PP6.2)."""
from datetime import date, timedelta

import streamlit as st

from acta.estado import facturas_por_estado
from app.apoyo import estados_calendario, formato_monto, inesperadas
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

mes, anio = eventos[0]["fecha"].month, eventos[0]["fecha"].year
st.subheader(f"{MESES[mes].capitalize()} {anio} · días hábiles")
st.caption("✔ llegó · … pendiente · ! atrasada. Una factura inesperada no se rechaza: se escala. "
           "Fechas y montos esperados son de ejemplo (supuesto).")

primero = date(anio, mes, 1)
lunes = primero - timedelta(days=primero.weekday())
columnas = st.columns(5)
for i, nombre in enumerate(DIAS):
    columnas[i].markdown(f"**{nombre}**")
while lunes.month <= mes or lunes.year < anio:
    columnas = st.columns(5)
    for i in range(5):
        dia = lunes + timedelta(days=i)
        with columnas[i].container(border=True, height=120):
            st.caption(f"{dia.day} {MESES[dia.month][:3]}" + ("" if dia.month == mes else " ·"))
            for e in por_dia.get(dia, []):
                st.text(f"{e['proveedor']}\n{MARCA[e['estado']]}")
    lunes += timedelta(days=7)
    if lunes.month != mes and lunes > primero + timedelta(days=31):
        break

st.subheader("Fuera del calendario")
fuera = inesperadas(facturas)
if not fuera:
    st.write("No hay facturas inesperadas.")
for f in fuera:
    st.text(f"{f.factura_id} · {f.decision['beneficiario']} · "
            f"{formato_monto(f.decision['monto'], f.decision['moneda'])} · inesperada: se escala")
