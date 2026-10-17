# Tareas: órdenes de compra y proveedores

Estado: **versión mínima en construcción** (R3 del roadmap, 17 oct): OT1 a OT3 y OT6, con las propuestas por defecto para OCD1, OCD4, OCD5, OCD11 y OCD12 (el dueño las aceptó el 17 oct) y con **órdenes de prueba sintéticas**, porque el archivo `Ordenes_Compra_PO_Prueba.xlsx` no está en el repositorio. Requisitos: `requirements.md` · Diseño: `design.md`.

| # | Tarea | Cubre | Estimación | Estado |
|---|---|---|---|---|
| OT1 | Escribir `importar_compras.py` (lee los .xlsx desde una ruta local; no se suben al repositorio público): genera `proveedores.yaml` y `ordenes_compra.yaml`, valida (OC2.2) y calcula las marcas (OC1.3, OC1.4, OC2.3) | OC1, OC2 | 1 h | **Parcial:** proveedores hechos (`data/proveedores.yaml`, 200 filas, 30 marcados; `tests/test_proveedores.py`). **Órdenes:** `data/ordenes_compra.yaml` es **sintético** (escrito a mano, validado al cargar); falta el importador del .xlsx real cuando el equipo lo entregue |
| OT2 | `engine/compras.py` y modelos: cargar, conservar la última versión válida, contexto con proveedores y órdenes; `Ficha` con `orden_compra` e `id_tributaria` | OC1.5, OC2.1 | 0,75 h | **Hecho** (ver «Ajustes al construir» en `design.md`) |
| OT3 | `engine/revisiones/orden_compra.py` y su lugar en `REVISIONES`; ajustar `frenar.acuerdo` para OC4.1 | OC4 | 1,5 h | **Hecho** |
| OT4 | Estado de la OC desde el acta y `orden_compra` en el payload de `DECISION` y en `facturas.csv` | OC5 | 0,75 h | **Parcial:** el estado «facturada» sale del acta (`contexto_desde_acta`); falta la columna en `facturas.csv` (el payload ya la lleva dentro de `ficha`) |
| OT5 | Agente de entrada: leer y comparar número de OC e identificación tributaria; modo demo con las facturas nuevas | OC3 | 1 h | Pendiente |
| OT6 | Casos de OC7.1 en `casos.yaml`, estrategia de Hypothesis y `tests/test_ordenes_compra.py` | OC7, OC8 | 1 h | **Hecho** con órdenes sintéticas |
| OT7 | Página «Órdenes de compra», OC en el detalle de la factura y 3 facturas de ejemplo con OC en el Panel 1 | OC6 | 1 h | Pendiente |

**Total estimado:** unas 7 horas. **Versión mínima** si falta tiempo: OT1, OT2, OT3 y OT6 (el motor decide con OC y está probado). Sin OT5, la OC solo entra por las fichas de prueba y el modo demo; sin OT7, no se ve en pantalla.

## Orden sugerido

1. El equipo resuelve OCD1, OCD4, OCD5, OCD11 y OCD12 (OCD3 ya se aplicó con la propuesta por defecto: cuenta ficticia).
2. OT1 → OT2 → OT3 → OT6 (núcleo del motor, con `eval.py` en verde).
3. OT4 → OT5 → OT7.

## Trazabilidad

| Requisito | Tarea | Archivo de pruebas |
|---|---|---|
| OC1 | OT1 | `tests/test_proveedores.py` |
| OC2 | OT1, OT2 | `tests/test_ordenes_compra.py` |
| OC3 | OT5 | `tests/test_agente_entrada.py` |
| OC4 | OT3 | `tests/test_ordenes_compra.py`, `casos.yaml` |
| OC5 | OT4 | `tests/test_ordenes_compra.py` |
| OC6 | OT7 | `tests/test_paneles.py` (AppTest) |
| OC7, OC8 | OT6 | `eval.py`, `tests/test_propiedades.py` |
