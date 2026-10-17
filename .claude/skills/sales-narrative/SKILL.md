---
name: sales-narrative
description: Arma el pitch de ventas de Colombiadevs (el agente que decide pagar, frenar o escalar facturas) con la narrativa de 8 pasos de April Dunford, adaptada al reto Blinka y a las reglas del proyecto. Úsala cuando se pida el pitch, el guion de la demo, las diapositivas de venta, el discurso ante el jurado, "cómo lo vendemos" o revisar un pitch existente, aunque no se nombre la skill. Para la forma de contar los casos, apóyate en la skill `storytelling`.
---

# Narrativa de venta de Colombiadevs

Adaptada de `sales-narrative` (guia-matthieu/clawfu-skills, licencia MIT; método de April Dunford, *Sales Pitch*, 2023). Se quitó lo genérico de SaaS y se añadieron las reglas del proyecto.

**Antes de escribir, lee `AVANCES.md`** (qué es y en qué estado está) y corre `python3 eval.py` para tener las cifras reales del día.

## Reglas del pitch (no se negocian)

El pitch es parte del proyecto: aplican las mismas reglas que al código.

1. **Solo cifras que se puedan mostrar.** Autonomía, pagos indebidos y explicabilidad salen de la salida de `eval.py` ese mismo día, nunca de memoria. Si el número cambia, el pitch cambia.
2. **Honestidad sobre la evidencia.** Las 20 facturas de `data/casos.yaml` se escribieron junto con el motor (pendiente P15 de `AVANCES.md`). Di «20 de 20 en nuestro set de prueba», no «precisión del 100 %». Los umbrales (3 M, 10 M, 50 M, 100 M COP) son valores de demostración: llámalos «supuesto».
3. **Sin clientes, citas ni resultados inventados.** No existen clientes. La prueba (paso 6) es la demo en vivo y el acta, no un caso de éxito ficticio.
4. **La IA nunca decide un pago.** Es el mensaje central, no un detalle. La IA lee y redacta; decide el motor de reglas, que es código. Nunca digas que «la IA aprueba pagos».
5. **No se mueve dinero.** Dilo tal cual: «pagar» es un pago de práctica que queda en el acta. No prometas integración real con Blinka.
6. **Lo que no existe no se vende.** No presentes como hecho el agente de reglas en lenguaje natural, la conciliación ni el sello público (son capa 3 o futuro). Si se mencionan, van como «a futuro». Verifica el estado en `AVANCES.md`. El agente de entrada aún no se probó con una API real: en la demo corre en modo demo si no hay clave, y hay que decirlo.
7. **Español claro, sin jerga.** Cero «disruptivo», «revolucionario» o «100 % seguro».

## Los 8 pasos aplicados a este proyecto

**Fase 1 — La preparación (el contexto antes del producto)**

| Paso | Qué dice | Material del proyecto |
|---|---|---|
| 1. La observación | Una verdad del cliente que genera tensión | Las empresas con pagos a Latinoamérica reciben facturas por correo, PDF y foto, en cualquier formato, y alguien tiene que decidir cuáles pagar. |
| 2. Las alternativas | Cómo lo resuelven hoy y por qué falla | Revisión manual (lenta, se cuelan duplicados); reglas fijas en el ERP (no leen una factura en PDF); «dejar que un chatbot pague» (riesgo inaceptable: puede ser engañado por un texto escondido en la factura). |
| 3. El mundo perfecto | Los criterios de compra que favorecen lo que sí hacemos | Que lea cualquier factura; que **nunca pague fuera de las reglas**; que ante la duda **llame a una persona**; que cada decisión se explique sin abrir código. |

**Fase 2 — El desarrollo (la solución)**

| Paso | Qué dice | Material del proyecto |
|---|---|---|
| 4. La presentación | Producto, categoría y vínculo con el paso 3, en 30 segundos | «Un agente que revisa facturas y decide pagar, frenar o escalar. La IA lee; un motor de reglas, sin IA, decide.» |
| 5. El valor diferenciado | Cada criterio del paso 3, con el atributo que lo cumple | Ver la tabla de abajo. |
| 6. La prueba | Evidencia verificable, no testimonios | Demo en vivo con las facturas de ejemplo, `eval.py` y el acta con cadena de huellas. |
| 7. Las objeciones | Responder antes de que pregunten | Ver abajo. |
| 8. La petición | Un siguiente paso concreto | Para el jurado: probar la demo con su propia factura. Para una empresa: un piloto con datos ficticios, y definir juntos sus reglas. |

### Paso 5: criterio → atributo → valor

| Mundo perfecto | Cómo lo hacemos | Valor |
|---|---|---|
| Lee cualquier factura | Agente de entrada con segunda lectura independiente (patrones de texto) y hasta 2 preguntas al proveedor | Si las dos lecturas no coinciden, no se paga solo |
| Nunca paga fuera de reglas | Decide el motor (código); el guardarraíl revalida y rechaza cualquier pago fuera de reglas; fallo seguro = `ESCALAR` | Cero pagos indebidos, también por error del sistema |
| Pide ayuda cuando dudan | Dos niveles de aprobación (persona y senior), separación de funciones y motivo obligatorio | La persona correcta decide lo que le toca |
| Explica cada decisión | Acta de solo añadir, cada fila con la huella de la anterior; CSV y tablero | Se audita sin abrir el código |
| Resiste engaños | Detección de órdenes escondidas sin IA; la factura se trata como dato no confiable | Una factura no puede dar instrucciones |

### Paso 7: objeciones previstas

- **«¿Y si la IA se equivoca al leer?»** Hay segunda lectura sin IA; si no coinciden o hay duda, escala. Equivocarse cuesta una revisión humana, no un pago.
- **«¿Y si alguien esconde una orden en la factura?»** Es uno de los casos de prueba (C11): se detecta sin IA y se escala.
- **«¿Es de verdad autónomo si escala tanto?»** Se mide con `eval.py` (autonomía), junto con seguridad y explicabilidad. Escalar en la duda es una decisión de diseño, no una falla.
- **«¿Funciona con dinero real?»** No, y es intencional en esta entrega: pagos de práctica con datos ficticios.

## Cómo usarla

- **Construir:** pide producto, público (jurado del hackathon, empresa, inversionista) y duración. Entrega los 8 pasos con tiempos, y marca con «supuesto» o «a futuro» lo que corresponda.
- **Revisar un pitch existente:** compáralo con los 8 pasos y con las reglas de arriba; señala lo que falte, esté desordenado o no se pueda demostrar.
- **Orden:** nunca abras con pantallas del producto. Primero tensión (pasos 1 a 3), después producto (paso 4).
- **Formatos:** el guion va en Markdown; para diapositivas, usa la skill `pptx` con este guion como base.
- **Verificación:** al terminar, pasa el cambio por la skill `verificador` y actualiza `AVANCES.md`.

## Lista de revisión antes de entregar

- [ ] Cada cifra coincide con la salida de `eval.py` de hoy
- [ ] Ninguna cita, cliente ni resultado inventado
- [ ] Lo que no está construido dice «a futuro»
- [ ] Dice claro que la IA no decide pagos y que no se mueve dinero real
- [ ] El producto aparece después de la tensión
- [ ] Hay una petición concreta al final
