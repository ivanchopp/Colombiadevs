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
| `motor-de-reglas` | Borrador para revisión |
| `extraccion-y-agente-de-entrada` | Pendiente |
| `acta-y-csv` | Borrador para revisión |
| `paneles-y-despliegue` | Pendiente |

## Reglas de trabajo

1. Un cambio de plan se escribe primero en la spec y después en el código.
2. Las specs no repiten el diseño general: lo enlazan.
3. Las decisiones abiertas están al final de cada `requirements.md`. Se resuelven y se borran de ahí.
4. Los valores de ejemplo (montos, tasas, costos) son de demostración y se marcan como «supuesto».
