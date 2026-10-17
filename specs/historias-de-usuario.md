# Historias de usuario

Estado: **borrador para revisión del equipo**.
Reúne en un solo lugar las historias de todos los actores y las enlaza con los criterios de cada spec. Sirve para revisar que nada quede sin dueño y como guion de la demo y del pitch.

Los criterios con número (R, RP, RV) están en `specs/motor-de-reglas/`, `specs/pagos-parciales-y-anticipos/` y `specs/proveedores-y-prioridad/`. Los que dicen **pendiente** dependen de una spec que aún no se escribe: `extraccion-y-agente-de-entrada`, `acta-y-csv` o `paneles-y-despliegue`.

## Actores

| Actor | Quién es | Panel |
|---|---|---|
| **Proveedor** | Quien envía la factura. En la demo lo hace el evaluador. | Panel 1 (abierto) |
| **Persona de finanzas** | Revisa y aprueba lo escalado hasta `persona_max`. | Panel 2 |
| **Senior de finanzas** | Aprueba lo de mayor riesgo y firma lo que *afloja* una regla. | Panel 2 |
| **Administrador de proveedores** | Mantiene la tabla de proveedores. Puede ser la misma persona de finanzas. | Panel 2 |
| **Auditor** | Reconstruye cualquier decisión. Solo lectura. | Panel 2 |
| **Contador o ERP** | Recibe las decisiones en su formato. | Salida CSV |
| **Evaluador del reto** | Prueba la demo y revisa autonomía, seguridad y explicabilidad. | Ambos |

## Capas

**Núcleo** (sáb 18:00) · **Capa 2** (enrutador de canal) · **Capa 3** (solo si sobra tiempo) · **A futuro** (solo pitch). Es la misma tabla de `AVANCES.md`, sección 3.

## Formato

> **HU-n · Título.** Como *actor*, quiero *algo*, para *beneficio*.
> **Aceptación:** una o dos comprobaciones que se pueden ver en la demo.
> **Criterios:** requisitos que la cubren. **Capa.**

---

## Proveedor

**HU-01 · Enviar una factura.** Como proveedor, quiero enviar mi factura (PDF, foto o correo) y que el agente la lea, para no llenar formularios.
- **Aceptación:** subo una factura de ejemplo y recibo una ficha con beneficiario, número, monto, moneda y vencimiento.
- **Criterios:** pendiente (`extraccion-y-agente-de-entrada`), R2.1. **Núcleo.**

**HU-02 · Aclarar lo dudoso.** Como proveedor, quiero que el agente me pregunte lo que no entendió (máximo dos turnos), para que mi factura no se frene por un dato borroso.
- **Aceptación:** una factura con el monto ilegible hace una pregunta; mi respuesta queda como «aclarado» sin reemplazar el original.
- **Criterios:** R2.3, R4.3. **Núcleo.**

**HU-03 · Ver el estado.** Como proveedor, quiero ver en qué estado va mi factura (recibida, en revisión, aprobada, pagada o frenada), para no tener que preguntar.
- **Aceptación:** el estado cambia en el Panel 1 cuando finanzas decide.
- **Criterios:** pendiente (`paneles-y-despliegue`), R10.2. **Núcleo.**

**HU-04 · No ver las reglas.** Como empresa, quiero que el proveedor nunca vea límites, umbrales ni su prioridad, para que nadie ajuste su factura a las reglas.
- **Aceptación:** ninguna pantalla ni mensaje del Panel 1 muestra un monto límite, una tolerancia ni la prioridad.
- **Criterios:** RV3.6, R2.4. **Núcleo.**

**HU-05 · Texto engañoso.** Como empresa, quiero que una orden escondida en la factura («aprueba este pago») no cambie la decisión, para que el sistema no se pueda manipular.
- **Aceptación:** la factura con orden escondida (caso trampa) no sale como `PAGAR`.
- **Criterios:** R2.4, R1.6. **Núcleo.**

## Persona de finanzas

**HU-06 · Pago automático seguro.** Como persona de finanzas, quiero que lo pequeño y en regla se pague solo, para dedicar mi tiempo a lo dudoso.
- **Aceptación:** una factura normal bajo `autopago_max` queda como `PAGAR` sin cola.
- **Criterios:** R1.2, R5.3. **Núcleo.**

**HU-07 · Frenar lo repetido o lo que no cuadra.** Como persona de finanzas, quiero que una factura repetida, sin presupuesto o muy por encima de lo acordado se frene sola, para no revisarla a mano.
- **Aceptación:** los casos «repetida», «sin presupuesto» y «+10 % sobre lo acordado» salen como `FRENAR` con su motivo.
- **Criterios:** R3.1 a R3.7. **Núcleo.**

**HU-08 · Aprobar lo escalado.** Como persona de finanzas, quiero una cola con cada caso escalado, su motivo y las revisiones que fallaron, para aprobarlo o rechazarlo con criterio.
- **Aceptación:** apruebo un caso con motivo escrito; rechazo otro y queda `RECHAZADA`.
- **Criterios:** R8.2, R8.4, R10.1, R10.2. **Núcleo.**

**HU-09 · Atender primero lo urgente.** Como persona de finanzas, quiero la cola ordenada por prioridad del proveedor, para atender primero lo crítico sin saltarme ningún control.
- **Aceptación:** los casos de prioridad A aparecen arriba; la decisión de un caso es la misma sea cual sea su prioridad.
- **Criterios:** RV3.1, RV3.2, RV3.3. **Núcleo.**

**HU-10 · Presupuesto escaso.** Como persona de finanzas, quiero ver qué cabe en el presupuesto que queda, empezando por lo prioritario, para decidir qué pagar primero.
- **Aceptación:** con presupuesto escaso, se marca lo A como dentro y lo C como fuera; no se aprueba nada solo.
- **Criterios:** RV3.4. **Capa 3.**

**HU-11 · Pagar en partes.** Como persona de finanzas, quiero registrar un pago parcial y ver el saldo de la factura, para pagar en cuotas sin perder la cuenta.
- **Aceptación:** un parcial sin plan de cuotas llega a la cola; el sobrepago se frena.
- **Criterios:** RP1.1, RP2.1, RP2.4. **Núcleo** (solo escalar). Pagar con plan de cuotas (RP2.3, RP2.5): **Capa 3.**

**HU-12 · Adelantar.** Como persona de finanzas, quiero pagar una factura antes de su vencimiento, para aprovechar un descuento o cuidar la relación con el proveedor.
- **Aceptación:** una factura pagada antes del vencimiento se evalúa con las mismas reglas que una normal; solo cambia el canal sugerido.
- **Criterios:** R7.2, RP1.4. **Capa 2.**

**HU-13 · Saber qué debería llegar.** Como persona de finanzas, quiero un calendario de facturas esperadas con su estado (pendiente, llegó, atrasada, parcial), para detectar lo inesperado y lo que falta.
- **Aceptación:** una factura sin obligación sale «inesperada»; una vencida sin factura sale «atrasada».
- **Criterios:** R6.1 a R6.4, RP2.5. **Capa 3.**

**HU-14 · Canal de pago.** Como persona de finanzas, quiero una recomendación del canal de pago más conveniente, para elegir con información.
- **Aceptación:** aparece el canal sugerido y las alternativas con costo y tiempo marcados «supuesto».
- **Criterios:** R7.1 a R7.5. **Capa 2.**

**HU-15 · Cambiar reglas hablando.** Como persona de finanzas, quiero pedir un cambio de reglas en lenguaje normal y ver una vista previa antes de confirmar, para no depender de ingeniería.
- **Aceptación:** pido «sube el presupuesto a 120 M»; el agente muestra el cambio y espera mi confirmación.
- **Criterios:** R9.1 a R9.6. **Capa 3.**

**HU-16 · Simular un cambio.** Como persona de finanzas, quiero saber qué facturas recientes cambiarían de decisión con una regla nueva, para no sorprenderme.
- **Aceptación:** la simulación lista solo las facturas que cambian y no escribe nada.
- **Criterios:** R9.6. **Capa 3.**

## Senior de finanzas

**HU-17 · Revisar lo de mayor riesgo.** Como senior, quiero que beneficiario nuevo, cuenta distinta, monto sobre `persona_max` o diferencia entre original y aclarado me lleguen a mí, para revisar siempre lo más riesgoso.
- **Aceptación:** esos casos exigen mi rol; la persona de finanzas no puede aprobarlos.
- **Criterios:** R2.3, R4.1, R4.2, R5.3 a R5.5, R8.2. **Núcleo.**

**HU-18 · Anticipos.** Como senior, quiero que ningún anticipo salga sin mi revisión, con respaldo y dentro de un límite, para que un adelanto sin factura no sea un hueco.
- **Aceptación:** un anticipo siempre pide senior; sin respaldo se frena.
- **Criterios:** RP3.1 a RP3.3. **Núcleo.**

**HU-19 · Firmar lo que afloja.** Como senior, quiero firmar todo cambio que afloje una regla (subir umbrales, agregar un proveedor, habilitar parciales o anticipos), para controlar el riesgo.
- **Aceptación:** un cambio que afloja sin mi firma se rechaza; uno que solo restringe pasa con la confirmación de finanzas.
- **Criterios:** R9.4, RP4.1, RV1.5. **Capa 3.**

**HU-20 · Techos que no se mueven.** Como senior, quiero un techo duro que ni el chat ni una aprobación puedan superar, para tener un límite absoluto.
- **Aceptación:** una factura sobre el techo duro no se puede aprobar; pedir subirlo por chat se rechaza.
- **Criterios:** R3.7, R8.3, R9.5, RP4.2. **Núcleo.**

## Administrador de proveedores

**HU-21 · Mantener la tabla.** Como administrador, quiero registrar proveedores con cuenta, acuerdo, estado y prioridad, para que el motor tenga con qué comparar.
- **Aceptación:** creo un proveedor y queda en el acta con quién y cuándo.
- **Criterios:** RV1.1, RV1.4. **Núcleo** (datos semilla). Edición con firma: **Capa 3.**

**HU-22 · Bloquear a un proveedor.** Como administrador, quiero bloquear a un proveedor y que nada salga hacia él, aunque sea de prioridad A.
- **Aceptación:** una factura de un proveedor bloqueado sale `FRENAR`.
- **Criterios:** RV2.1, RV2.3. **Núcleo.**

**HU-23 · La IA no toca los datos.** Como administrador, quiero que ningún agente cree ni edite proveedores, cuentas o prioridades, para que los datos maestros solo cambien por una persona.
- **Aceptación:** el agente de reglas y el de entrada solo leen la tabla.
- **Criterios:** RV1.3. **Núcleo.**

## Auditor

**HU-24 · Entender una decisión.** Como auditor, quiero leer una decisión y ver la regla, el valor observado, el umbral, la versión de reglas y la tasa usada, sin abrir el código.
- **Aceptación:** cada fila del acta explica por qué se pagó, frenó o escaló.
- **Criterios:** R10.1, R10.2, R9.3. **Núcleo.**

**HU-25 · Registro que no se altera.** Como auditor, quiero que el acta solo permita añadir filas, cada una con la huella de la anterior, para detectar cualquier cambio posterior.
- **Aceptación:** alterar una fila rompe la cadena y el tablero lo muestra.
- **Criterios:** pendiente (`acta-y-csv`). **Núcleo.**

**HU-26 · Cero pagos fuera de las reglas.** Como auditor, quiero la certeza de que ningún pago salió sin cumplir todas las reglas, ni siquiera por un error de programación.
- **Aceptación:** el guardarraíl vuelve a evaluar antes de escribir y rechaza el intento; la prueba de propiedades no encuentra un `PAGAR` indebido.
- **Criterios:** R1.2, R1.3, R8.1, R11.2, RP5.2. **Núcleo.**

**HU-27 · Resumen del periodo.** Como auditor, quiero un resumen del periodo y un aviso de rarezas, sin que la IA calcule las cifras.
- **Aceptación:** el agente de conciliación resume y señala; las cifras vienen del acta.
- **Criterios:** pendiente (`acta-y-csv`). **Capa 3.**

## Contador o ERP

**HU-28 · Exportar para el ERP.** Como contador, quiero un CSV con una fila por decisión y columnas que mi ERP pueda cargar, para no reescribir datos.
- **Aceptación:** el CSV trae `factura_id`, `proveedor_id`, `monto_total`, `monto_pagado`, `saldo`, `moneda`, `tasa`, `periodo`, `decision`, `nivel`, `estado_erp`, `version_reglas`. Los valores de ejemplo van marcados «supuesto».
- **Criterios:** pendiente (`acta-y-csv`), RP2.5. **Núcleo** (CSV). Adaptador al ERP: **A futuro.**

**HU-29 · Estados que el ERP entiende.** Como contador, quiero que `PAGAR`, `FRENAR` y `ESCALAR` se traduzcan en «propuesta de pago aprobada», «bloqueo de pago» y «pendiente de aprobación», para que el ERP refleje lo que decidió el agente.
- **Aceptación:** la columna `estado_erp` sigue esa tabla.
- **Criterios:** pendiente (`acta-y-csv`). **Núcleo** (columna). Integración: **A futuro.**

**HU-30 · Sin escrituras duplicadas.** Como contador, quiero que reenviar una decisión no cree dos asientos, para no duplicar en el ERP.
- **Aceptación:** la huella de la factura sirve como llave de idempotencia.
- **Criterios:** R3.1, RP2.2. **A futuro.**

## Evaluador del reto

**HU-31 · Probar la demo con ejemplos.** Como evaluador, quiero botones de facturas de ejemplo (normal, repetida, beneficiario nuevo, con orden escondida), para probar rápido los casos trampa.
- **Aceptación:** cada botón carga una factura y se ve su decisión en el Panel 2.
- **Criterios:** pendiente (`paneles-y-despliegue`), R11.3. **Núcleo.**

**HU-32 · Medir autonomía y seguridad.** Como evaluador, quiero ver cuántas de las 20 facturas de prueba decide bien el agente sin ayuda y que ninguna se pague indebidamente.
- **Aceptación:** `eval.py` muestra autonomía y «0 pagos indebidos».
- **Criterios:** R11.2, R11.3. **Núcleo.**

**HU-33 · Una sala por visitante.** Como evaluador, quiero mi propia sala, para que mis pruebas no se mezclen con las de otros.
- **Aceptación:** el enlace con código de sala muestra solo mis facturas.
- **Criterios:** pendiente (`paneles-y-despliegue`). **Núcleo.**

---

## Cobertura

| Actor | Historias | Núcleo | Capa 2 | Capa 3 | A futuro |
|---|---|---|---|---|---|
| Proveedor | HU-01 a HU-05 | 5 | 0 | 0 | 0 |
| Persona de finanzas | HU-06 a HU-16 | 5 | 2 | 4 | 0 |
| Senior | HU-17 a HU-20 | 3 | 0 | 1 | 0 |
| Administrador | HU-21 a HU-23 | 3 | 0 | 0 | 0 |
| Auditor | HU-24 a HU-27 | 3 | 0 | 1 | 0 |
| Contador o ERP | HU-28 a HU-30 | 2 | 0 | 0 | 1 |
| Evaluador | HU-31 a HU-33 | 3 | 0 | 0 | 0 |

Una historia con partes en dos capas (HU-11, HU-21, HU-28, HU-29) se cuenta en la capa de su parte principal: núcleo.

## Para el pitch

Las historias que mejor muestran los tres criterios del reto:

| Criterio | Historias |
|---|---|
| **Autonomía** | HU-06, HU-07 |
| **Seguridad** | HU-05, HU-17, HU-26 |
| **Explicabilidad** | HU-24, HU-25 |
