# Tareas: archivo de salida de pagos aprobados

Requisitos: `requirements.md` · Diseño: `design.md`. Las horas son **estimaciones mías**.

| # | Tarea | Cubre | Estimado | Estado |
|---|---|---|---|---|
| AST1 | `acta/exportar_pagos.py`: filtro `PAGADA`, columnas, cuenta del registro, `Decimal`, resumen por moneda | AS1, AS2 | 1 h | Hecho |
| AST2 | Verificación de huellas antes de generar y manejo de «sin aprobadas» y «sin cuenta registrada» | AS3.2, AS3.4, AS2.4 | 0,5 h | Hecho |
| AST3 | Panel 2, página Acta: resumen, aviso «no mueve dinero» y botón de descarga | AS3.3, AS3.5, AS3.6 | 0,5 h | Hecho |
| AST4 | `tests/test_pagos_aprobados.py`: un estado de cada tipo, cuenta del registro, fórmulas, cadena rota | AS4 | 1 h | Hecho |

**Total:** unas 3 horas. **Versión mínima:** AST1, AST2 y AST4 (el archivo existe y está probado), con el botón de AST3.

## Depende de

- Nada nuevo. Si las órdenes de compra entran (`specs/ordenes-de-compra/`), se agrega la columna `orden_compra`; mientras tanto va vacía.
