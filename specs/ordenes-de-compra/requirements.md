# Requisitos: órdenes de compra y proveedores

Estado: **borrador para revisión del equipo**. Alcance nuevo pedido el 17 oct, 14:20.
Base: los archivos de prueba que entregó el equipo, `Listado_Proveedores_Prueba.xlsx` (30 proveedores; reemplazado el 17 oct a las 15:37 por una versión de 200 y a las 18:42 por el **listado de proveedores válidos, 156**) y `Ordenes_Compra_PO_Prueba.xlsx` (30 órdenes), y las specs `motor-de-reglas` y `extraccion-y-agente-de-entrada`.

## Resumen

Una **orden de compra** (OC) es una compra que la empresa **autorizó antes** de que llegue la factura. Cuando una factura cita una OC, el motor de reglas comprueba que la orden exista, que sea del mismo proveedor, que no se haya facturado ya y que el monto cuadre con lo autorizado. La OC no reemplaza ninguna otra revisión: ante cualquier duda, el resultado sigue siendo `ESCALAR`, nunca `PAGAR`.

Esta spec también reemplaza la lista de beneficiarios de ejemplo por un **registro de proveedores** con identificación tributaria (NIT, RFC o RUC).

## Alcance

**Dentro:**
- Cargar el registro de proveedores y el de órdenes de compra desde los archivos del equipo, validando su coherencia.
- Que el agente de entrada lea el número de OC y la identificación tributaria de la factura.
- Una revisión nueva del motor que contrasta la factura con su OC.
- Marcar una OC como facturada cuando una factura la consume.
- Ver las órdenes y su estado en el Panel 2.
- Casos de prueba a partir de la columna `Simulacion_Discrepancia`.

**Fuera:**
- Crear, aprobar o editar órdenes de compra desde la aplicación (llegan ya autorizadas en el archivo).
- Órdenes con varias líneas, entregas parciales o recepción de mercancía (*three-way match*).
- Validar el dígito de verificación de un NIT, RFC o RUC contra la autoridad tributaria (DIAN, SAT, SUNAT, SRI).
- Mover dinero real.

## Glosario

| Término | Significado |
|---|---|
| Orden de compra (OC) | Compra autorizada antes de la factura: número, proveedor, artículo, cantidad, precio, subtotal, IVA y total |
| OC abierta | Ninguna factura la ha consumido todavía |
| OC facturada | Una factura ya la usó y fue pagada, aprobada o quedó pendiente |
| Identificación tributaria | NIT (Colombia), RFC (México) o RUC (Perú, Ecuador) del proveedor |
| Registro de proveedores | Lista permitida de quién puede cobrar (reemplaza la lista de `registros.yaml`) |

## Parámetros por defecto (supuestos)

| Parámetro | Valor | Uso |
|---|---|---|
| `tolerancia_ok`, `tolerancia_frenar` | Los mismos de `reglas.yaml` (5 % y 10 %) | Diferencia aceptada entre el total de la factura y el de la OC |
| `oc_obligatoria` | `false` | Si es `true`, una factura sin OC se escala |
| Moneda de las OC | COP (ver decisión OCD1) | Los archivos dicen «Pesos» sin código |

## Requisitos

Notación EARS en español: «CUANDO <evento>, EL SISTEMA DEBERÁ <respuesta>». También «SI <condición>, ENTONCES …».

### OC1. Registro de proveedores
**Historia:** como persona de finanzas, quiero que solo cobren los proveedores que la empresa registró, identificados por su número tributario.

- **OC1.1** EL SISTEMA DEBERÁ cargar el registro de proveedores con estos campos: `id`, `nombre`, `pais`, `id_tributaria`, `tipo_id` (NIT, RFC o RUC) y `cuenta`. Todos son ficticios y se marcan como «supuesto».
- **OC1.2** EL SISTEMA NO DEBERÁ cargar dirección, teléfono ni correo de los proveedores: el motor no los usa y no hace falta guardarlos. Los archivos originales NO DEBERÁN subirse al repositorio, que es público.
- **OC1.3** CUANDO dos o más proveedores compartan la misma `id_tributaria`, EL SISTEMA DEBERÁ marcarlos a todos como «identificación repetida».
- **OC1.4** CUANDO una `id_tributaria` no tenga el formato de su `tipo_id` (NIT: 9 dígitos, guion y dígito; RFC: 12 o 13 caracteres alfanuméricos; RUC: 11 dígitos en Perú o 13 en Ecuador), EL SISTEMA DEBERÁ marcarla como «identificación inválida».
- **OC1.5** SI el registro no se puede leer o no cumple el esquema, ENTONCES EL SISTEMA DEBERÁ conservar la última versión válida y reportar el error, como con las reglas (R9.1).

### OC2. Registro de órdenes de compra
**Historia:** como persona de finanzas, quiero cargar las compras ya autorizadas para que las facturas se comparen con ellas.

- **OC2.1** EL SISTEMA DEBERÁ cargar cada OC con: `numero`, `proveedor_id`, `id_tributaria`, `articulo`, `cantidad`, `precio_unitario`, `subtotal`, `iva`, `total` y `moneda`. Los montos van en `Decimal`.
- **OC2.2** EL SISTEMA DEBERÁ rechazar al cargar una OC cuyo `numero` esté repetido, cuyo `proveedor_id` no exista, o en la que `cantidad × precio_unitario` no dé `subtotal` o `subtotal + iva` no dé `total`, y reportar cuál falló.
- **OC2.3** CUANDO la `id_tributaria` de una OC difiera de la de su proveedor en el registro, EL SISTEMA DEBERÁ marcar la OC como «no coincide con el proveedor».
- **OC2.4** LA columna `Simulacion_Discrepancia` del archivo NO DEBERÁ entrar al registro: es la respuesta esperada de las pruebas y va solo a los casos (OC7).

### OC3. Lectura de la factura
**Historia:** como motor de reglas, quiero saber qué OC cita la factura y quién la emite.

- **OC3.1** EL AGENTE DE ENTRADA DEBERÁ extraer, además de los campos de EA2.1, el número de OC y la identificación tributaria del emisor, cuando aparezcan. SI no aparecen, ENTONCES quedan vacíos y nunca se estiman.
- **OC3.2** LA segunda lectura (EA3) DEBERÁ comparar también el número de OC y la identificación tributaria cuando la factura los traiga.
- **OC3.3** EL AGENTE NO DEBERÁ recibir el registro de órdenes ni el de proveedores, ni revelar al proveedor si una OC existe, su monto o su estado (EA2.4, PP2.1).
- **OC3.4** CUANDO el proveedor aporte el número de OC por chat, EL SISTEMA DEBERÁ marcarlo con origen `aclarado` (EA5).

### OC4. Revisión de la orden de compra (motor de reglas)
**Historia:** como persona de finanzas, quiero que una factura que cita una compra autorizada se compare con ella, y que cualquier diferencia se frene o se escale.

- **OC4.1** CUANDO la factura cite una OC que existe, está abierta, es del mismo proveedor (`id_tributaria` igual en la factura, la OC y el registro) y su total no supera el de la OC más `tolerancia_ok`, EL MOTOR DE REGLAS DEBERÁ marcar la revisión `OK`. Esa OC hace las veces de acuerdo: no aplica el `AVISO` «sin acuerdo registrado» (R3.5).
- **OC4.2** SI la OC citada no existe, ENTONCES EL MOTOR DE REGLAS DEBERÁ devolver `ESCALAR` con nivel `SENIOR` y el motivo «orden de compra inexistente».
- **OC4.3** SI la OC pertenece a otro proveedor, o la `id_tributaria` de la factura no coincide con la de la OC o la del registro, ENTONCES EL MOTOR DE REGLAS DEBERÁ devolver `ESCALAR` con nivel `SENIOR` y el motivo «identificación tributaria no coincide».
- **OC4.4** SI el proveedor está marcado con «identificación repetida» o «identificación inválida» (OC1.3, OC1.4), o la OC con «no coincide con el proveedor» (OC2.3), ENTONCES EL MOTOR DE REGLAS DEBERÁ devolver `ESCALAR` con nivel `SENIOR`.
- **OC4.5** CUANDO el total de la factura supere el de la OC más `tolerancia_ok` sin pasar de `tolerancia_frenar`, EL MOTOR DE REGLAS DEBERÁ marcar `AVISO` y devolver `ESCALAR` con nivel `PERSONA`. CUANDO supere `tolerancia_frenar`, DEBERÁ devolver `FRENAR` con el motivo «no cuadra con la orden de compra».
- **OC4.6** SI la OC ya fue facturada por otra factura, ENTONCES EL MOTOR DE REGLAS DEBERÁ devolver `FRENAR` con el motivo «orden de compra ya facturada».
- **OC4.7** SI la moneda de la factura difiere de la de la OC, ENTONCES EL MOTOR DE REGLAS DEBERÁ comparar en moneda base (R5.1), y SI falta la tasa, devolver `ESCALAR`.
- **OC4.8** CUANDO la factura no cite ninguna OC, EL MOTOR DE REGLAS DEBERÁ seguir con las revisiones actuales (acuerdo y calendario). SI `oc_obligatoria` es `true`, ENTONCES DEBERÁ marcar `AVISO` «sin orden de compra» y escalar a `PERSONA`.
- **OC4.9** UNA OC válida NO DEBERÁ saltarse ninguna otra revisión: duplicado, cuenta, presupuesto, techo duro, límite por periodo y niveles por monto (R3 a R5) siguen aplicando.
- **OC4.10** CUANDO un número de OC venga solo de una aclaración del proveedor, EL MOTOR DE REGLAS DEBERÁ marcar `AVISO` (como R2.5), salvo que la OC exista, sea de ese proveedor y el monto cuadre.

### OC5. Consumo de la orden
**Historia:** como auditor, quiero saber qué factura usó cada orden.

- **OC5.1** EL SISTEMA DEBERÁ calcular el estado de cada OC a partir del acta, sin guardarlo aparte: «abierta», o «facturada» con la factura que la usó.
- **OC5.2** UNA OC DEBERÁ quedar facturada cuando una decisión la use con resultado `PAGAR`, o con `ESCALAR` pendiente o aprobado. SI la decisión fue `FRENAR` o el caso se rechazó, ENTONCES la OC sigue abierta.
- **OC5.3** EL evento `DECISION` del acta DEBERÁ guardar el número de OC usado (AC3.1).

### OC6. Pantallas
**Historia:** como persona de finanzas, quiero ver las órdenes autorizadas y cuáles ya se facturaron.

- **OC6.1** EL PANEL 2 DEBERÁ tener una página «Órdenes de compra» con cada OC: número, proveedor, artículo, total, estado y factura que la usó.
- **OC6.2** EL detalle de una factura DEBERÁ mostrar la OC que cita y el resultado de la revisión OC4.
- **OC6.3** EL PANEL 1 NO DEBERÁ mostrar órdenes, montos autorizados ni si una OC existe (PP2.1).
- **OC6.4** EL PANEL 1 DEBERÁ ofrecer facturas de ejemplo con OC: una que cuadra, una con el monto alterado y una con identificación tributaria incorrecta.

### OC7. Casos de prueba
- **OC7.1** `casos.yaml` DEBERÁ incluir al menos estos casos con su decisión esperada:

| Caso | Base | Decisión esperada |
|---|---|---|
| OC que cuadra, monto bajo | PO-2026-001 | `PAGAR` |
| Identificación tributaria incorrecta | PO-2026-005 | `ESCALAR` · `SENIOR` |
| Monto alterado +15 % | PO-2026-010 | `FRENAR` |
| Monto alterado +15 % | PO-2026-015 | `FRENAR` |
| Monto +8 % | Cualquier OC | `ESCALAR` · `PERSONA` |
| OC inexistente | `PO-2026-999` | `ESCALAR` · `SENIOR` |
| OC ya facturada | Dos facturas sobre PO-2026-002 | La segunda `FRENAR` |
| OC de otro proveedor | Factura de proveedor 3 citando PO-2026-004 | `ESCALAR` · `SENIOR` |

- **OC7.2** `eval.py` DEBERÁ seguir dando cero pagos indebidos con los casos nuevos.

### OC8. Calidad
- **OC8.1** Cada criterio de esta spec DEBERÁ tener al menos una prueba automática.
- **OC8.2** LA prueba de propiedades (R11.2) DEBERÁ incluir fichas con OC inexistente, ajena, facturada o con monto alterado, y ninguna DEBERÁ dar `PAGAR`.

## Cambios que esta spec le pide a otras

1. **`motor-de-reglas`:** una revisión nueva (OC4) entre beneficiario (R4) y acuerdo (R3.2); la ficha gana `orden_compra` e `id_tributaria`; `origen_campos` admite `orden_compra`. R4.1 usa el registro de proveedores.
2. **`extraccion-y-agente-de-entrada`:** EA2.1 y EA3 suman los dos campos nuevos (OC3).
3. **`acta-y-csv`:** el payload de `DECISION` y `facturas.csv` suman `orden_compra`.
4. **`paneles-y-despliegue`:** página de órdenes y ejemplos nuevos (OC6).

## Decisiones abiertas

| # | Pregunta | Propuesta por defecto |
|---|---|---|
| OCD1 | Los archivos dicen «Pesos» para proveedores de México, Colombia, Perú y Ecuador. ¿Qué moneda es? | **COP** para todas, marcado «supuesto». Con COP, todos los totales (11.136 a 45.936) quedan bajo el pago automático de 3 M: una OC que cuadra se pagaría sola. Si eran miles de pesos o la moneda de cada país, hay que decirlo antes de cargar |
| OCD2 | Todas las OC usan IVA del 16 %, aunque Colombia tiene 19 %, Perú 18 % (IGV) y Ecuador 15 %. ¿Se valida la tasa por país? | **No.** Se toman los valores como vienen y solo se comprueba que `subtotal + iva = total` |
| OCD3 | El listado no trae cuenta bancaria, y R4.2 escala al senior toda factura sin cuenta registrada. ¿Qué cuenta usamos? | **Agregar una cuenta ficticia a cada proveedor** al cargar, marcada «supuesto». Sin eso, ninguna factura de estos proveedores se pagaría sola |
| OCD4 | ¿Los 30 proveedores reemplazan a los 9 beneficiarios actuales o se suman? | **Se suman.** Los 20 casos actuales, el calendario y las 4 facturas de ejemplo dependen de los 9 |
| OCD5 | ~~Proveedores que comparten la identificación `FALLA-999999-X`~~ | **Resuelta (17 oct, 18:42):** el equipo entregó el listado de proveedores válidos (156) sin esos proveedores. Una factura de cualquiera de ellos queda fuera de la lista permitida y se escala al senior (R4.1) |
| OCD11 | ~~RUC cortos de Perú y Ecuador~~ | **Resuelta (17 oct, 18:42):** quedaron fuera del listado de válidos. El de 156 no tiene ninguna identificación repetida ni con formato inválido |
| OCD12 | En el listado de 200, los proveedores de las órdenes tienen **otro ID** (por ejemplo, PO-2026-001 cita el ID 1, que ahora es otro proveedor; el suyo es el 103). Nombre e identificación tributaria sí coinciden en las 30 órdenes. ¿Cómo se enlazan? | **Por nombre** (único en el listado), comprobando que la identificación tributaria coincida. El `ID_Proveedor` del archivo de órdenes se ignora |
| OCD13 | **Ninguno de los 30 proveedores de las órdenes de compra está en el listado de válidos** (por nombre ni por identificación tributaria; los 156 restantes sí estaban en el de 200, con otro ID). Con este listado, toda factura que cite cualquiera de las 30 órdenes se escalaría al senior por proveedor no permitido. ¿Es intencional (las órdenes son trampas) o falta un archivo de órdenes nuevo con proveedores válidos? | **Pedir un archivo de órdenes nuevo** con proveedores del listado de válidos. Mientras tanto no se cargan las órdenes (OT1 sigue parcial) |
| OCD6 | Varios proveedores comparten dirección, teléfono y correo con otro de distinto número tributario (1, 6, 11…). ¿Se marca como riesgo? | **No en esta spec.** No se cargan esos datos (OC1.2). Detectar proveedores parecidos es una decisión de fraude, fuera del reto |
| OCD7 | ¿La OC es obligatoria para pagar? | **No** (`oc_obligatoria: false`). Sin OC, sigue el flujo actual |
| OCD8 | Una OC ya autorizada, ¿permite pagar sola por encima del pago automático? | **No.** Los niveles por monto siguen aplicando (OC4.9). Cambiarlo afloja una regla y requiere al senior |
| OCD9 | Las OC no traen fecha ni vigencia. ¿Vencen? | **No** en esta versión. Se puede agregar `vigente_hasta` después |
| OCD10 | ¿Los nombres, NIT, RFC, RUC y correos del archivo son ficticios? | **Se asumen ficticios**, como exige el proyecto. Confirmarlo, porque algunos tienen formato válido |
