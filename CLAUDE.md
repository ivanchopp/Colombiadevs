# Indicaciones para Claude Code

**Antes de hacer cualquier cosa, lee `AVANCES.md`.** Explica el proyecto, lo que ya se hizo, lo pendiente y lo que sigue. Después lee `specs/README.md` y la spec de la parte en la que vayas a trabajar.

## Lo esencial

- Es un agente que decide si **pagar, frenar o escalar** cada factura según reglas de la empresa. **No mueve dinero real** y solo usa datos ficticios.
- **La IA nunca decide un pago.** Lee, pregunta, resume y propone. Decide el **motor de reglas**, que es código sin IA. Ante la duda: `ESCALAR`, nunca `PAGAR`.
- Un pago fuera de las reglas descalifica el proyecto. Cada decisión debe poder explicarse.
- Entrega: **dom 18 oct 2026, 8:00 a. m. (hora Bogotá).**
- Escribe en español.

## Al terminar un cambio

Actualiza `AVANCES.md` (última actualización, registro de cambios, pendientes y próximas tareas). Si cambia un plan, escribe primero la spec y después el código. Antes de commitear, pasa el cambio por la skill `verificador` (`.claude/skills/verificador/`).
