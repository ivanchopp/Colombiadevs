# Especificaciones

Aquí viven las especificaciones del proyecto, escritas antes de programar. Cada funcionalidad tiene su carpeta con tres archivos:

| Archivo | Para qué sirve |
|---|---|
| `requirements.md` | Qué debe hacer, con criterios en notación EARS |
| `design.md` | Cómo se construye, sin repetir el diseño general |
| `tasks.md` | Tareas con dueño, dependencias y qué prueba las cierra |

El diseño general está en `docs/Ruta-de-una-factura.pdf` y el plan hasta la entrega en `docs/Guia-6-alternativas-actualizada.pdf`.

## Cómo leer los requisitos

Notación EARS en español:

- **CUANDO** un evento, **EL SISTEMA DEBERÁ** una respuesta.
- **SI** una condición, **ENTONCES** una respuesta.

Cada criterio tiene un número (por ejemplo R3.1) y debe tener al menos una prueba automática.

## Estado

| Spec | Estado |
|---|---|
| `motor-de-reglas` | Borrador para revisión (implementado; T11 hecho, falta la parte de conflictos por especificidad de T12) |
| `extraccion-y-agente-de-entrada` | Borrador para revisión (implementado, con XML de Latinoamérica sin IA, EA10 a EA12; **la IA real no lee en producción**, P17; Claude sin probar) |
| `acta-y-csv` | Borrador para revisión (versión mínima en SQLite implementada; faltan PostgreSQL, purga de salas y conciliación) |
| `paneles-y-despliegue` | Borrador para revisión (paneles, página de reglas, página de órdenes de compra y despliegue en Railway hechos; falta la página de conciliación, PT12) |
| `ordenes-de-compra` | Versión mínima en el motor (R3, 17 oct): revisión OC4 con **órdenes sintéticas** y los 156 proveedores válidos como lista permitida; OT5 y OT7 hechas; faltan las órdenes reales (OCD13) y la columna en `facturas.csv` (OT4); 13 decisiones, 9 abiertas |
| `archivo-de-salida` | Borrador para revisión (alcance nuevo de la reunión con Blinka del 17 oct; implementado con columnas supuestas; 4 decisiones abiertas) |
| `agente-de-reglas` | Borrador para revisión (alcance nuevo de la reunión con Blinka, R7; versión sin IA (ART1 a ART4) y lector con IA (ART5, 18 oct) hechos, este último sin probar con la IA real; 6 decisiones abiertas) |

## Reglas de trabajo

1. Un cambio de plan se escribe primero en la spec y después en el código.
2. Las specs no repiten el diseño general: lo enlazan.
3. Las decisiones abiertas están al final de cada `requirements.md`. Se resuelven y se borran de ahí.
4. Los valores de ejemplo (montos, tasas, costos) son de demostración y se marcan como «supuesto».
