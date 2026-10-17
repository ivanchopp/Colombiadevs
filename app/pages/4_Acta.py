"""Panel 2 · Acta. Solo lectura, con verificación de la cadena (PP6.3)."""
import pandas as pd
import streamlit as st

from acta.verificar import verificar_cadena
from app.apoyo import DECISIONES
from app.comun import almacen, barra_lateral, encabezado, exigir_rol, obtener_sala

st.set_page_config(page_title="Panel 2 · Acta", layout="wide")
sala = obtener_sala()
barra_lateral(sala)
encabezado("Panel 2 · Finanzas › Acta", sala)
exigir_rol()
st.caption("Solo lectura. Cada fila guarda la huella de la anterior, así que cualquier cambio posterior se nota.")


def resumen(f):
    p = f.payload
    if f.tipo == "DECISION":
        return DECISIONES[p["decision"]], p["motivo"], p["version_reglas"]
    if f.tipo in ("APROBACION", "RECHAZO"):
        return ("Aprobada" if f.tipo == "APROBACION" else "Rechazada"), p["motivo"], ""
    if f.tipo == "INTENTO_RECHAZADO":
        return "Intento rechazado", p.get("regla", ""), ""
    return f.tipo.replace("_", " ").capitalize(), p.get("motivo", ""), p.get("version_reglas", "")


filas = almacen().filas(sala)
datos = []
for f in filas:
    decision, regla, version = resumen(f)
    datos.append({"#": f.num, "Hora (UTC)": f.creado_en[11:19], "Factura": f.factura_id or "Regla",
                  "Decisión": decision, "Regla o motivo": regla, "Versión": version,
                  "Quién": f.actor, "Huella": f.huella[:4] + "…" + f.huella[-2:]})
st.dataframe(pd.DataFrame(datos), hide_index=True, use_container_width=True)

v = verificar_cadena(almacen(), sala)
if v.correcta:
    st.success(f"Cadena verificada: {v.filas} de {v.filas} filas con la huella correcta.")
else:
    st.error(f"La cadena se rompe en la fila #{v.primera_fila_mala}.")
