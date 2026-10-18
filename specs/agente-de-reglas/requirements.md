# Requisitos: agente de reglas en lenguaje natural

Estado: **borrador para revisión del equipo**. Alcance nuevo de la reunión con Blinka del 17 oct (roadmap R7). Aún sin programar.
Diseño: `design.md` · Tareas: `tasks.md`.

## Resumen

El CEO de Blinka contó que su plataforma ya programa pagos con un solo comando de texto desde sistemas de IA, y en la reunión el equipo dijo que ajustaba las reglas de pago en lenguaje natural. Esta spec define cómo: la persona de finanzas escribe el cambio con sus palabras («sube el pago automático a 1.000 dólares»), **la IA lo traduce a una propuesta estructurada** y el sistema la muestra como cualquier otro cambio de reglas: con vista previa, con la firma que corresponda y con motivo.

**La IA nunca cambia una regla.** Solo propone. La validan el mismo código y las mismas reglas de firma de la página de reglas (PP8, R9); la confirma una persona con un botón.

## Alcance

**Dentro:**
- Una caja de texto en la página «Reglas» del Panel 2 para pedir uno o varios cambios en los siete parámetros editables (`autopago_max`, `persona_max`, `limite_periodo_beneficiario`, `presupuesto_periodo`, `tolerancia_ok`, `tolerancia_frenar`, `ventana_dias`).
- Cambios absolutos («pon el presupuesto en 30.000») y relativos («sube un 20 %», «baja 100 dólares»).
- Un lector de respaldo por patrones cuando no hay IA.
- Registro del texto original en el `CAMBIO_REGLA`.

**Fuera:**
- Cambiar el techo duro, la lista de proveedores, las obligaciones del calendario o cualquier otra cosa que no sea uno de los siete parámetros (R9.5).
- Vigencias por fecha («desde el lunes»): el cambio rige desde que se confirma (PP8.7).
- Un servidor MCP o cualquier otra puerta de entrada (roadmap R13).
- Pedir pagos o aprobar facturas con texto. Esta spec solo toca reglas.

## Glosario

| Término | Significado |
|---|---|
| Pedido | El texto libre que escribe la persona de finanzas |
| Propuesta | Lista cerrada de cambios (parámetro, operación, valor) que la IA o el lector de respaldo sacan del pedido |
| Cambio resuelto | La propuesta ya convertida por código en valores nuevos, con Decimal y en la moneda base |
| Confirmar | El botón con el que una persona, con el rol que toca, escribe el motivo y aplica el cambio (PP8.6) |

## Criterios

### AR1. La IA solo propone
- **AR1.1** LA IA NO DEBERÁ escribir en el acta, cambiar reglas ni llamar a ninguna herramienta. Su única salida es una propuesta con un esquema cerrado.
- **AR1.2** TODO cambio DEBERÁ pasar por las mismas validaciones que el formulario: `validar_cambio` (coherencia, valores positivos, techo duro: R9.5, PP8.5), `cambios_que_aflojan` (R9.4) y el rol que firma (PP8.4). Ninguna ruta de este agente DEBERÁ saltarse alguna.
- **AR1.3** UN pedido NO DEBERÁ aplicarse sin que una persona confirme con un botón y escriba el motivo (PP8.6). NI el texto, ni la IA, ni el lector de respaldo podrán confirmar.
- **AR1.4** SI el pedido afloja una regla, ENTONCES solo el rol `SENIOR` podrá confirmarlo. SI lo intenta `PERSONA`, ENTONCES EL SISTEMA DEBERÁ rechazarlo y registrar un `INTENTO_RECHAZADO` (PP8.4).

### AR2. Qué entiende
- **AR2.1** LA propuesta DEBERÁ ser una lista de hasta 4 cambios; cada uno con `parametro` (uno de los siete), `operacion` (`fijar`, `subir_monto`, `bajar_monto`, `subir_porcentaje` o `bajar_porcentaje`), `valor` y, para los parámetros de monto, `moneda`.
- **AR2.2** LA IA NO DEBERÁ hacer cuentas. El código DEBERÁ calcular el valor nuevo con `Decimal` a partir del valor vigente y de la operación.
- **AR2.3** SI el pedido da un monto en otra moneda («10 millones de pesos»), ENTONCES EL CÓDIGO DEBERÁ convertirlo a la moneda base con la tabla de cambio (R5.1). SI no hay tasa, ENTONCES DEBERÁ rechazar el cambio con una explicación.
- **AR2.4** CUANDO haya IA, LA IA DEBERÁ decidir si el pedido es claro. SI es ambiguo, incompleto o menciona algo que no es uno de los siete parámetros, ENTONCES DEBERÁ devolver el estado `aclaracion` con una pregunta corta (o `no_entendido`) y NINGÚN cambio. EL CÓDIGO NO DEBERÁ interpretar el lenguaje: solo valida el esquema, calcula y aplica las reglas. Ante la duda no hay cambio.
- **AR2.5** SI el pedido pide algo fuera de alcance (techo duro, fechas de vigencia, proveedores), ENTONCES EL SISTEMA DEBERÁ decir que eso no se cambia por texto y por qué.
- **AR2.6** EL pedido DEBERÁ tener entre 1 y 500 caracteres.
- **AR2.7** SIN IA, EL lector por patrones DEBERÁ responder `no_entendido` ante cualquier frase que no sea de las simples (AR6.2); NO DEBERÁ resolver ambigüedades.
- **AR2.8** DESPUÉS de que la IA (o el lector) devuelva una propuesta, EL CÓDIGO DEBERÁ compararla con el texto del pedido, sin interpretar el lenguaje, y marcar la propuesta como `dudosa` si ocurre alguna de estas señales: (a) hay menos cambios que menciones de parámetros en el pedido; (b) un número del pedido no aparece como valor en ningún cambio; (c) un valor de la propuesta no aparece como número en el pedido (salvo operaciones relativas pedidas con «doble», «triple» o «mitad»). Cada señal DEBERÁ explicarse con una frase armada por código.

### AR3. Qué se le muestra a la persona
- **AR3.1** ANTES de confirmar, EL SISTEMA DEBERÁ mostrar, con texto armado por código (no escrito por la IA): lo que entendió, el valor vigente y el nuevo de cada parámetro, si el cambio afloja o restringe, y qué facturas de la sala cambiarían de decisión (R9.6, PP8.3).
- **AR3.2** EL sistema DEBERÁ mostrar el pedido original como texto plano, y NO DEBERÁ mostrar texto libre de la IA como si fuera un dato.
- **AR3.3** LA propuesta DEBERÁ poder descartarse sin dejar rastro en el acta.
- **AR3.4** SI la propuesta es inválida, ENTONCES EL SISTEMA DEBERÁ explicar cuál regla la frena, con las mismas frases del formulario.
- **AR3.5** SI la propuesta es `dudosa` (AR2.8), ENTONCES EL SISTEMA DEBERÁ mostrar las señales como advertencia, mostrar el pedido original al lado y NO DEBERÁ habilitar el botón de aplicar hasta que la persona marque «Revisé que estos son todos los cambios que quería». Una propuesta no dudosa no pide esa marca.

### AR4. Registro
- **AR4.1** AL confirmar, EL `CAMBIO_REGLA` DEBERÁ guardar además el origen (`texto`) y el pedido original (máximo 500 caracteres), sin cambiar el resto del evento (PP8.6).
- **AR4.2** EL pedido guardado DEBERÁ tratarse siempre como dato: nunca se obedece ni se vuelve a enviar a la IA.

### AR5. Seguridad
- **AR5.1** EL pedido DEBERÁ ir a la IA dentro de un bloque marcado como datos, y la instrucción de sistema DEBERÁ decir que nada de ese contenido es una instrucción (como EA2.2).
- **AR5.2** LA IA NO DEBERÁ recibir los valores vigentes, las facturas, los proveedores ni ningún dato de la empresa. Solo el pedido y el catálogo de parámetros (nombre, unidad).
- **AR5.3** NINGÚN pedido, por más que ordene «ignora el techo», «sin firma» o «aplícalo ya», DEBERÁ producir un cambio que `validar_cambio` o las reglas de firma no permitan (prueba de propiedades).
- **AR5.4** SI la llamada a la IA falla, ENTONCES EL SISTEMA DEBERÁ degradar al lector de respaldo (AR6) y dejar el error en los Logs, sin ningún valor de clave (como EA2b.9).
- **AR5.5** CADA sala DEBERÁ tener un máximo de pedidos con IA (`PEDIDOS_REGLAS_MAX`, por defecto 10, entre 1 y 100) para controlar el gasto. Es un freno de uso, no un tope de dinero.

### AR6. Sin IA
- **AR6.1** SIN clave de IA (o con `ENTRADA_MODO=demo`), EL SISTEMA DEBERÁ entender, con patrones de texto, pedidos simples como «fija el pago automático en 1.000», «sube el presupuesto un 20 %» o «baja la tolerancia normal a 3 %». «Tolerancia» a secas es ambigua (hay dos) y se responde «no entendí».
- **AR6.2** LO que el lector de respaldo no entienda DEBERÁ responderse con «no entendí» y el ejemplo de cómo escribirlo. NO DEBERÁ adivinar.
- **AR6.3** LA pantalla DEBERÁ decir cuál lector respondió («con IA» o «por patrones»).

### AR7. Proveedor de IA
- **AR7.1** EL agente DEBERÁ usar el mismo proveedor intercambiable del agente de entrada (Gemini o Claude, `PROVEEDOR_IA`, EA2b), con salida estructurada, y NO DEBERÁ depender de uno solo.

### AR8. Calidad
- **AR8.1** Cada criterio DEBERÁ tener al menos una prueba automática, sin red ni clave, con un cliente falso de IA.
- **AR8.2** UNA tabla de al menos 15 pedidos con su propuesta esperada (absolutos, relativos, otra moneda, ambiguos, fuera de alcance, con inyección) DEBERÁ pasar con el lector de respaldo y con un cliente falso.
- **AR8.3** UNA prueba de propiedades DEBERÁ comprobar AR5.3: para cualquier texto y cualquier salida de la IA (incluso basura), nunca se aplica un cambio que el formulario rechazaría ni se registra sin confirmación.
- **AR8.4** LAS pruebas DEBERÁN cubrir las mutaciones: aplicar sin confirmar, saltarse la firma del senior, saltarse el techo duro, dejar que la IA calcule, no marcar una propuesta dudosa y habilitar el botón sin la marca de revisión.
- **AR8.5** UNA tabla de pedidos con una propuesta que *omite* un cambio, *cambia* un número o *inventa* un valor DEBERÁ marcarse `dudosa` con la señal correcta; y la tabla de AR8.2 con propuestas correctas NO DEBERÁ marcarse.

## Decisiones abiertas

| # | Pregunta | Propuesta por defecto |
|---|---|---|
| AR-D1 | ¿Se permite pedir más de un cambio en un solo texto? | Sí, hasta 4, y se confirman todos juntos o ninguno |
| AR-D2 | ¿Hay un paso de aclaración conversacional (la IA pregunta y la persona responde)? | No: se muestra la pregunta y la persona reescribe el pedido. Sin estado entre turnos |
| AR-D3 | ¿Qué moneda se asume si el pedido no dice moneda? | La moneda base de las reglas (USD en la demo) |
| AR-D4 | ¿Cuánto cuesta cada pedido? | Una llamada corta de texto por pedido. Sin archivos |
| AR-D5 | ¿Se guardan en el acta los pedidos que no se confirmaron? | No: solo los confirmados y los `INTENTO_RECHAZADO` por falta de firma |
| AR-D6 | ¿Se permite pedir por texto una restricción sin firma del senior? | Sí: restringir lo firma cualquier rol (R9.4), igual que en el formulario |
