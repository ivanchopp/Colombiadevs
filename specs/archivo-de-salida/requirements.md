# Requisitos: archivo de salida de pagos aprobados

Estado: **implementado el 17 oct** (borrador para revisión del equipo; columnas supuestas). Alcance nuevo de la reunión con Blinka del 17 oct, 17:02.
Diseño: `design.md` · Tareas: `tasks.md`.

## Resumen

Blinka confirmó cómo se cierra el flujo: **el sistema genera un archivo con las facturas aprobadas, automática o manualmente, y Blinka hace los pagos a los proveedores desde la cuenta del cliente.** Nosotros no movemos dinero: decidimos y entregamos la lista.

Hoy solo exportamos `facturas.csv` y `eventos.csv` (spec `acta-y-csv`). Son de **auditoría**: traen todas las decisiones y no traen la cuenta bancaria de destino. Esta spec agrega un tercer archivo, `pagos_aprobados.csv`, que es la **instrucción de pago** para Blinka.

## Alcance

**Dentro:**
- Un archivo CSV solo con las facturas aprobadas (por el motor o por una persona), generado desde el acta.
- Un botón en el Panel 2 para descargarlo, con un resumen de lo que contiene.
- Pruebas de que nada fuera de las reglas entra al archivo.

**Fuera:**
- Mover dinero, llamar a la API de Blinka o conectar con una cuenta bancaria.
- El formato exacto que use Blinka: **no se conoce** (decisión abierta AS-D1). Se parte de columnas supuestas.
- Marcar las facturas como «ya enviadas a Blinka» en el acta (AS-D3).

## Glosario

| Término | Significado |
|---|---|
| Factura aprobada | Factura en estado `PAGADA` del acta: el motor decidió `PAGAR`, o una persona la aprobó con una `APROBACION` válida |
| Aprobación automática | `PAGAR` del motor sin intervención de una persona |
| Aprobación manual | `APROBACION` registrada por una persona con el rol correcto |
| Instrucción de pago | Una fila del archivo: a quién, cuánto, en qué moneda y por qué canal debe pagar Blinka |

## Criterios

### AS1. Qué entra al archivo
- **AS1.1** EL archivo DEBERÁ incluir únicamente las facturas en estado `PAGADA`.
- **AS1.2** NO DEBERÁ incluir facturas `FRENADA`, `RECHAZADA` ni `PENDIENTE`, ni las de ficha inválida (R8.6).
- **AS1.3** CADA fila DEBERÁ indicar si la aprobación fue `AUTOMATICA` o `MANUAL`, y quién aprobó (rol y actor) cuando fue manual.
- **AS1.4** SI una factura tuvo un `INTENTO_RECHAZADO`, ENTONCES el intento NO DEBERÁ cambiar si la factura entra o no: solo cuenta su estado final en el acta.

### AS2. Qué trae cada fila
- **AS2.1** LAS columnas DEBERÁN ser (supuesto, AS-D1): `lote_id`, `factura_id`, `numero_factura`, `beneficiario`, `id_tributaria`, `cuenta_destino`, `monto`, `moneda`, `monto_base`, `canal`, `orden_compra`, `tipo_aprobacion`, `aprobado_por`, `rol_aprobador`, `aprobado_utc`, `fila_acta`, `huella_corta`, `supuesto`.
- **AS2.2** `monto` y `moneda` DEBERÁN ser los de la factura (lo que Blinka paga), no el monto convertido a la moneda base. El monto base va en una columna aparte para conciliar.
- **AS2.3** `canal` DEBERÁ ser el canal elegido por la persona; si la aprobación fue automática, el canal sugerido por el motor. SI no hay canal, ENTONCES la celda queda vacía; NO DEBERÁ inventarse.
- **AS2.4** `cuenta_destino` DEBERÁ ser la cuenta **registrada** del beneficiario en el registro de proveedores. NUNCA DEBERÁ tomarse de un texto que el proveedor escribió en el chat ni de una instrucción dentro de la factura. SI no hay cuenta registrada, ENTONCES la factura NO DEBERÁ entrar al archivo y DEBERÁ aparecer en el resumen como «sin cuenta registrada» (ante la duda, fuera: R2).
- **AS2.5** CADA celda de texto DEBERÁ neutralizar fórmulas de hoja de cálculo, igual que el CSV de auditoría (AC5.5).
- **AS2.6** TODOS los valores de ejemplo DEBERÁN llevar la marca `supuesto` mientras el formato de Blinka no esté confirmado.

### AS3. Generación y entrega
- **AS3.1** EL archivo DEBERÁ generarse solo a partir del acta (AC5.1), con el mismo orden de filas del acta.
- **AS3.2** ANTES de generarlo, EL SISTEMA DEBERÁ verificar la cadena de huellas del acta. SI la verificación falla, ENTONCES NO DEBERÁ generar el archivo y DEBERÁ mostrar el error.
- **AS3.3** EL Panel 2 DEBERÁ mostrar, antes de la descarga, cuántas instrucciones hay y el total por moneda, y DEBERÁ decir que **el sistema no mueve dinero: el archivo lo ejecuta Blinka**.
- **AS3.4** SI no hay facturas aprobadas, ENTONCES EL Panel 2 DEBERÁ decirlo y NO DEBERÁ ofrecer un archivo vacío.
- **AS3.5** `lote_id` DEBERÁ ser el mismo para todas las filas de una descarga y DEBERÁ incluir la sala y la fecha-hora UTC.
- **AS3.6** EL nombre del archivo DEBERÁ ser `pagos_aprobados_<sala>_<fecha>.csv`.

### AS4. Seguridad
- **AS4.1** EL archivo NO DEBERÁ contener motivos internos, reglas ni umbrales.
- **AS4.2** NINGUNA ruta de código DEBERÁ agregar al archivo una factura que el acta no tenga como `PAGADA`. UNA prueba DEBERÁ comprobarlo con facturas en cada estado.
- **AS4.3** LAS pruebas DEBERÁN cubrir: solo `PAGADA` entra; la cuenta viene del registro; fórmulas neutralizadas; cadena rota sin archivo; sin aprobadas sin archivo; montos con `Decimal`.

## Decisiones abiertas

| # | Pregunta | Propuesta |
|---|---|---|
| AS-D1 | ¿Qué columnas y qué formato exige Blinka? Las notas de la reunión no lo dicen | Pedirlo a Blinka; mientras tanto, las columnas de AS2.1 marcadas como supuesto |
| AS-D2 | ¿Qué cuenta se usa cuando el proveedor cambió su cuenta y una persona aprobó la factura? | La registrada; el cambio de cuenta se resuelve actualizando el registro de proveedores, no desde la factura |
| AS-D3 | ¿Se deja constancia en el acta de cada descarga (lote, cantidad, huella del archivo) para que la misma factura no se envíe dos veces? | Sí, con un evento nuevo en una segunda etapa. Requiere cambiar el esquema del acta |
| AS-D4 | ¿Un solo archivo por sala o uno por moneda? | Uno solo, con la columna `moneda` |
