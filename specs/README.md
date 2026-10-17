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
| `motor-de-reglas` | Borrador para revisión (implementado, falta T11 y T12 completo) |
| `extraccion-y-agente-de-entrada` | Borrador para revisión (implementado en modo demo; falta probar con la API real) |
| `acta-y-csv` | Borrador para revisión |
| `paneles-y-despliegue` | Borrador para revisión (paneles y página de reglas programados; despliegue pendiente) |
| `ordenes-de-compra` | Versión mínima construida el 17 oct (R3): proveedores y revisión OC4 en el motor, con órdenes sintéticas; faltan OT5, OT7 y el importador de las órdenes reales |
| `archivo-de-salida` | Borrador para revisión (alcance nuevo de la reunión con Blinka del 17 oct, 17:02; sin programar; 4 decisiones abiertas) |

## Reglas de trabajo

1. Un cambio de plan se escribe primero en la spec y después en el código.
2. Las specs no repiten el diseño general: lo enlazan.
3. Las decisiones abiertas están al final de cada `requirements.md`. Se resuelven y se borran de ahí.
4. Los valores de ejemplo (montos, tasas, costos) son de demostración y se marcan como «supuesto».
