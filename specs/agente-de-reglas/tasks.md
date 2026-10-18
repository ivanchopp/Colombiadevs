# Tareas: agente de reglas en lenguaje natural

Requisitos: `requirements.md` · Diseño: `design.md`. Las horas son **estimaciones mías**. Una tarea está lista cuando las pruebas de sus criterios pasan.

| # | Tarea | Cubre | Estimado | Estado |
|---|---|---|---|---|
| ART1 | `agents/reglas_texto.py`: modelos cerrados, `resolver` con `Decimal`, conversión de moneda y redondeo, y `comprobar_coherencia` | AR1, AR2, AR2.8 | 2 h | Hecho |
| ART2 | Lector por patrones para pedidos simples y respuesta «no entendí» con ejemplo | AR6, AR2.4, AR2.5 | 1 h | Hecho |
| ART3 | Página «Reglas»: caja de texto, «Entender», resumen por código, relleno del formulario y marca de revisión si la propuesta es dudosa | AR3, AR1.3 | 1,25 h | Hecho |
| ART4 | Origen y pedido en el `CAMBIO_REGLA` (`cambiar_reglas(origen, pedido)`) | AR4 | 0,5 h | Hecho |
| ART5 | Lector con IA (Gemini o Claude, salida estructurada), bloque de datos, sin valores vigentes, tope por sala, degradación a patrones | AR5, AR7 | 1,5 h | Pendiente |
| ART6 | Tabla de 15 pedidos, tabla de propuestas dudosas, cliente falso, prueba de propiedades y mutaciones | AR8 | 1,75 h | **Parcial:** tabla de 17 pedidos, dudosas, propiedades y 6 mutaciones hechas; falta el cliente falso de IA (con ART5) |

**Total:** unas 8 horas. **Versión mínima si falta tiempo:** ART1, ART2, ART3, ART4 y la parte de ART6 que cubre esos criterios (unas 5 h). Funciona sin IA y deja la IA como segunda etapa (ART5), sin tocar la ruta hacia el acta.

## Orden y dependencias

ART1 → ART2 → ART3 → ART4 → ART6 (parcial) → ART5 → ART6 (completo). Nada de esto toca el motor: usa `validar_cambio`, `cambios_que_aflojan`, `simular` y `cambiar_reglas` tal como están.
