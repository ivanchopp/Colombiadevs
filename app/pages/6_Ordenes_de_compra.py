"""Panel 2 · Órdenes de compra (PP9.1). El estado de cada orden lo calcula el motor desde el acta (OC5)."""
import pandas as pd
import streamlit as st

from acta.estado import facturas_por_estado
from app.apoyo import ordenes_con_estado
from app.comun import almacen, barra_lateral, contexto_y_reglas, encabezado, exigir_rol, obtener_sala

st.set_page_config(page_title="Panel 2 · Órdenes de compra", layout="wide")
sala = obtener_sala()
barra_lateral(sala)
encabezado("Panel 2 · Finanzas › Órdenes de compra", sala)
exigir_rol()

filas = almacen().filas(sala)
ctx, _ = contexto_y_reglas(filas)
ordenes = ordenes_con_estado(ctx, facturas_por_estado(filas))

st.caption("Compras que la empresa autorizó antes de la factura. Las órdenes de esta demo son de ejemplo (supuesto). "
           "Una orden cuenta como facturada cuando una factura pagada o escalada la usó; si la factura se frena o "
           "se rechaza, la orden sigue abierta.")
if not ordenes:
    st.info("No hay órdenes de compra cargadas. Toda factura que cite una orden se escala al senior.")
    st.stop()

c1, c2, c3 = st.columns(3)
c1.metric("Órdenes", len(ordenes))
c2.metric("Abiertas", sum(o["estado"] == "abierta" for o in ordenes))
c3.metric("Facturadas", sum(o["estado"] == "facturada" for o in ordenes))

tabla = pd.DataFrame(ordenes).rename(columns={
    "numero": "Orden", "proveedor": "Proveedor", "articulo": "Artículo", "total": "Total", "estado": "Estado",
    "factura": "Factura que la usó", "estado_factura": "Estado de la factura", "advertencia": "Advertencia"})
st.dataframe(tabla, hide_index=True, use_container_width=True)       # texto plano, nunca HTML (PP7.3)
