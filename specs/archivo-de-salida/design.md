# Diseño: archivo de salida de pagos aprobados

Requisitos: `requirements.md`. El diseño general (acta, estado, CSV) está en `specs/acta-y-csv/design.md`; aquí solo lo nuevo.

## Dónde vive

- `acta/exportar_pagos.py` (nuevo): `exportar_pagos(filas_acta, registro, sala_id, ahora) -> (bytes, resumen)`. Usa `facturas_por_estado` y `_escribir` / `seguro` de `acta/exportar_csv.py`; no duplica la neutralización de fórmulas.
- `app/pages/4_Acta.py`: junto a los botones de `facturas.csv` y `eventos.csv`, el resumen (AS3.3) y el botón de descarga.

## Flujo

1. Se verifican las huellas del acta (`acta/verificar.py`). Si fallan, se muestra el error y no se sigue (AS3.2).
2. `facturas_por_estado(filas)` entrega el estado final de cada factura; se filtra `estado == "PAGADA"` (AS1.1).
3. `tipo_aprobacion`: `MANUAL` si la factura tiene `respuesta` (una `APROBACION`), `AUTOMATICA` si no.
4. `cuenta_destino` sale del registro de proveedores (`data/proveedores.yaml`, que el motor ya usa: OC1.6), con la clave del beneficiario. Sin cuenta, la factura queda fuera y se cuenta aparte (AS2.4).
5. Montos con `Decimal`; el resumen suma por moneda.
6. Una factura sin `canal_elegido` usa `canal_sugerido` del payload de la decisión, o queda vacía (AS2.3).

## Por qué no es el `facturas.csv`

`facturas.csv` es el registro de auditoría de **todo** lo decidido, con motivos y reglas. Mezclarlo con la instrucción de pago haría que una fila frenada o rechazada pudiera acabar en manos de quien paga. Son dos archivos con dos públicos.

## Riesgos

| Riesgo | Mitigación |
|---|---|
| Que entre una factura no aprobada | Filtro único por estado `PAGADA` del acta y prueba AS4.2 |
| Cuenta alterada desde la factura o el chat | La cuenta sale solo del registro (AS2.4) |
| Fórmulas en celdas | Reutiliza `seguro()` (AS2.5) |
| Enviar dos veces la misma factura | Decisión AS-D3; hasta entonces el lote lleva fecha-hora y el resumen avisa |
