# Tareas: base de proveedores y prioridad

Estado: **borrador para revisión del equipo**.
Requisitos: `requirements.md` · Diseño: `design.md`.

Horas **estimadas por mí**. Se integra con T1 y T2 de `specs/motor-de-reglas/tasks.md`. Dueños: **A** motor · **C** pantallas · **D** datos.

## Prioridad

| Capa | Qué incluye | Cuándo |
|---|---|---|
| **Núcleo** | PV1 y PV2: modelo, datos semilla y revisión de estado | Con la Ola 0 y 1 del motor |
| **Núcleo (pantalla)** | PV3: ordenar cola y calendario | Con el Panel 2 |
| **Capa 3** | PV4: reparto de presupuesto; edición con firma | Solo si sobra tiempo |

## Tareas

### PV1. Modelo y datos semilla
- **Dueño:** D · **Estimación:** 1 h · **Capa:** núcleo
- Crear `Proveedor` y `data/proveedores.yaml` (12 proveedores). Cambiar `Contexto` para usar la tabla. Se hace dentro de T1 y T2.
- **Cubre:** RV1.1, RV1.2
- **Listo cuando:** el archivo carga con el modelo y un campo extra se rechaza.

### PV2. Revisión de estado
- **Dueño:** A · **Estimación:** 0,5 h · **Capa:** núcleo
- Crear `proveedor_estado` con `FRENAR` para bloqueado y `ESCALAR` senior para nuevo o inexistente.
- **Cubre:** RV2.1 a RV2.3
- **Listo cuando:** un proveedor bloqueado con prioridad A frena.

### PV3. Orden por prioridad
- **Dueño:** C · **Estimación:** 0,5 h · **Capa:** núcleo
- Ordenar la cola de aprobación y el calendario por `(prioridad, vence, monto)`. No mostrar la prioridad en el Panel 1.
- **Cubre:** RV3.1, RV3.3, RV3.5, RV3.6
- **Listo cuando:** la cola muestra primero lo A, y el Panel 1 no lo menciona.

### PV4. Propiedad de no relajar
- **Dueño:** A · **Estimación:** 0,5 h · **Capa:** núcleo
- Prueba de Hypothesis de RV3.2 y prueba de arquitectura de que `engine/` no usa `prioridad`.
- **Cubre:** RV3.2, RV4.2
- **Listo cuando:** pasa con 200 ejemplos.

### PV5. Reparto de presupuesto
- **Dueño:** C · **Estimación:** 1 h · **Capa:** capa 3
- Crear `app/presupuesto.py` (RV3.4).
- **Listo cuando:** con presupuesto escaso, lo A queda dentro y lo C fuera, sin aprobar nada.

### PV6. Edición con firma
- **Dueño:** C y A · **Estimación:** 1,5 h · **Capa:** capa 3
- Formulario para crear o cambiar proveedores, con firma según RV1.4, RV1.5 y RV3.7.
- **Listo cuando:** cambiar una cuenta sin senior se rechaza y queda en el acta.

## Trazabilidad

| Criterio | Tarea |
|---|---|
| RV1.1, RV1.2 | PV1 |
| RV1.3 | PV1 (solo lectura en los agentes) |
| RV1.4, RV1.5, RV3.7 | PV6 |
| RV2.1 a RV2.3 | PV2 |
| RV3.1, RV3.3, RV3.5, RV3.6 | PV3 |
| RV3.2, RV4.2 | PV4 |
| RV3.4 | PV5 |
| RV4.1 | todas |
