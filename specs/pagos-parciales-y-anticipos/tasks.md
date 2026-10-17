# Tareas: pagos parciales y anticipos

Estado: **borrador para revisión del equipo**.
Requisitos: `requirements.md` · Diseño: `design.md`.

Horas **estimadas por mí**. Depende de T1, T2, T4 y T5 de `specs/motor-de-reglas/tasks.md`. Dueños: **A** motor · **D** datos.

## Prioridad

| Capa | Qué incluye | Cuándo |
|---|---|---|
| **Núcleo (mínimo)** | PP1 a PP3: campos nuevos, parciales y anticipos siempre escalan, sobrepago frena | Con la Ola 1 del motor |
| **Capa 3** | PP4: pagar un parcial con plan de cuotas (RP2.3), descontar anticipos (RP3.4) | Solo si sobra tiempo |
| **A futuro** | Calendario con estado «parcial» completo | Pitch |

## Tareas

### PP1. Campos nuevos y huella
- **Dueño:** A · **Estimación:** 0,5 h · **Capa:** núcleo
- Agregar `tipo_pago`, `monto_a_pagar` y `numero_pago` a `Ficha`, y cambiar la huella.
- **Cubre:** RP1.2, RP1.3, RP2.2
- **Listo cuando:** una ficha sin `tipo_pago` se rechaza y dos parciales de la misma factura tienen huellas distintas.

### PP2. Revisiones de pagos
- **Dueño:** A · **Estimación:** 1 h · **Capa:** núcleo
- Crear `engine/revisiones/pagos.py` con las seis revisiones del diseño.
- **Cubre:** RP1.1, RP1.4, RP2.1, RP2.4, RP2.6, RP3.1 a RP3.3, RP3.5, RP4.2
- **Listo cuando:** sus pruebas pasan y ningún parcial ni anticipo sale como `PAGAR`.

### PP3. Datos y casos trampa
- **Dueño:** D · **Estimación:** 0,5 h · **Capa:** núcleo
- Agregar a `data/` un caso de parcial sin plan, uno de sobrepago, uno de anticipo sin respaldo y uno de parcial repetido. Marcar `anticipo_max_beneficiario` como «supuesto».
- **Cubre:** RP5.1
- **Listo cuando:** `eval.py` muestra los cuatro con la decisión esperada.

### PP4. Propiedades
- **Dueño:** A · **Estimación:** 0,5 h · **Capa:** núcleo
- Pruebas de Hypothesis para RP5.2 y RP5.3.
- **Listo cuando:** pasan con 200 ejemplos.

### PP5. Firma por regla que afloja
- **Dueño:** A · **Estimación:** 0,25 h · **Capa:** capa 3
- Que habilitar parciales o anticipos cuente como «afloja» en `reglas_io.py`.
- **Cubre:** RP4.1 · Depende de T12 del motor.

### PP6. Parcial con plan de cuotas
- **Dueño:** A · **Estimación:** 1,5 h · **Capa:** capa 3
- Implementar RP2.3, RP2.5 y RP3.4.
- **Listo cuando:** un parcial que coincide con su cuota da `PAGAR` y uno que no, `ESCALAR`.

## Trazabilidad

| Criterio | Tarea |
|---|---|
| RP1.1 a RP1.4 | PP1, PP2 |
| RP2.1, RP2.2, RP2.4, RP2.6 | PP1, PP2 |
| RP2.3, RP2.5 | PP6 |
| RP3.1 a RP3.3, RP3.5 | PP2 |
| RP3.4 | PP6 |
| RP4.1 | PP5 |
| RP4.2 a RP4.4 | PP2 |
| RP5.1 a RP5.3 | PP3, PP4 |
