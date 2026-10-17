# Requisitos: pagos parciales y anticipos

Estado: **borrador para revisión del equipo**.
Amplía `specs/motor-de-reglas/`. No repite sus reglas: solo dice qué cambia cuando el pago **no es el total de una factura**.

## Resumen

Hasta ahora el motor asume una factura y un pago por el monto completo. Esta spec agrega dos casos:

- **Pago parcial:** se paga una parte de una factura real y queda un saldo.
- **Anticipo:** se paga **antes** de que exista la factura (prepago contra un acuerdo u orden de compra).

Pagar una factura real **antes de su vencimiento** no es un caso nuevo: es un pago `TOTAL` común. Solo cambia el canal sugerido y el periodo del presupuesto (ver D3 del motor).

**Alcance de la entrega (dom 18 oct, 8:00):** el comportamiento seguro. **Todo `PARCIAL` y todo `ANTICIPO` se escala**; el resto (pagar un parcial solo con plan de cuotas) queda especificado, no construido.

## Glosario

| Término | Significado |
|---|---|
| `tipo_pago` | `TOTAL`, `PARCIAL` o `ANTICIPO`. |
| `monto_a_pagar` | Lo que se paga ahora. En `TOTAL` es igual al monto de la factura. |
| Saldo pendiente | Monto de la factura menos lo ya pagado o aprobado. Lo da el contexto, no la ficha. |
| Plan de cuotas | Acuerdo registrado de la empresa con el proveedor para pagar una factura en partes. |
| Anticipo | Pago sin factura, contra un acuerdo u orden de compra registrado. |

## Requisitos

### RP1. Seguro por defecto
**Historia:** como persona de finanzas, quiero pagar en partes o adelantar sin perder el control.

- **RP1.1** CUANDO `tipo_pago` sea `PARCIAL` o `ANTICIPO`, EL MOTOR DE REGLAS DEBERÁ devolver `ESCALAR`, nunca `PAGAR`, salvo lo dicho en RP2.3.
- **RP1.2** SI `tipo_pago` falta o no es uno de los tres valores, ENTONCES EL MOTOR DE REGLAS DEBERÁ devolver `ESCALAR` por ficha inválida (R2.1).
- **RP1.3** SI `tipo_pago` es `TOTAL` y `monto_a_pagar` es distinto del monto de la factura, ENTONCES EL MOTOR DE REGLAS DEBERÁ devolver `ESCALAR` con la revisión `FALLA` «monto a pagar no coincide».
- **RP1.4** EL MOTOR DE REGLAS DEBERÁ evaluar un pago solo con `monto_a_pagar` para las reglas de nivel, presupuesto y techo duro (R3.6, R3.7, R5), y con el monto total de la factura para la regla de acuerdo (R3.2 a R3.4).

### RP2. Pagos parciales
**Historia:** como persona de finanzas, quiero pagar una factura en partes y que el saldo quede claro.

- **RP2.1** CUANDO la suma de pagos pagados o aprobados de una factura más `monto_a_pagar` supere el monto de la factura, EL MOTOR DE REGLAS DEBERÁ devolver `FRENAR` con el motivo «sobrepago».
- **RP2.2** EL MOTOR DE REGLAS DEBERÁ calcular la huella de duplicado con beneficiario, número de factura, fecha y **número de pago dentro de la factura**, no con el monto. CUANDO la misma factura reciba un pago con el mismo número de pago, EL MOTOR DE REGLAS DEBERÁ devolver `FRENAR` con el motivo «repetida».
- **RP2.3** CUANDO exista un plan de cuotas registrado para esa factura, el pago coincida con una cuota y todas las demás revisiones sean `OK`, EL MOTOR DE REGLAS DEBERÁ permitir `PAGAR`. *(Especificado, no se construye para la entrega.)*
- **RP2.4** SI no existe plan de cuotas, ENTONCES EL MOTOR DE REGLAS DEBERÁ devolver `ESCALAR` con nivel `PERSONA` como mínimo y el motivo «pago parcial sin plan de cuotas».
- **RP2.5** CUANDO se pague un parcial, EL MOTOR DE REGLAS DEBERÁ mantener la obligación del calendario en el estado «parcial» hasta que el saldo llegue a cero; solo entonces pasará a «llegó» (amplía R6.4).
- **RP2.6** EL MOTOR DE REGLAS DEBERÁ sumar todos los pagos de un beneficiario en el periodo para el nivel (R5.2). **Dividir un pago grande en partes pequeñas NO DEBERÁ bajar el nivel exigido.**

### RP3. Anticipos
**Historia:** como senior de finanzas, quiero que ningún adelanto sin factura salga sin mi revisión.

- **RP3.1** CUANDO `tipo_pago` sea `ANTICIPO`, EL MOTOR DE REGLAS DEBERÁ devolver `ESCALAR` con nivel `SENIOR`, sin importar el monto. Un anticipo nunca es autopago.
- **RP3.2** SI no existe un acuerdo u orden de compra registrado para el anticipo, ENTONCES EL MOTOR DE REGLAS DEBERÁ devolver `FRENAR` con el motivo «anticipo sin respaldo».
- **RP3.3** CUANDO la suma de anticipos abiertos de un beneficiario supere `anticipo_max_beneficiario`, EL MOTOR DE REGLAS DEBERÁ devolver `FRENAR` con el motivo «supera el límite de anticipos».
- **RP3.4** CUANDO llegue la factura que respalda un anticipo, EL MOTOR DE REGLAS DEBERÁ descontar el anticipo del saldo antes de calcular lo que falta por pagar. *(Especificado, no se construye.)*
- **RP3.5** EL MOTOR DE REGLAS DEBERÁ contar el anticipo contra el presupuesto del periodo en que **sale**, no en el de la factura futura.

### RP4. Reglas y control
- **RP4.1** CUANDO un cambio de reglas habilite pagos parciales o anticipos para un beneficiario, EL MOTOR DE REGLAS DEBERÁ tratarlo como regla que **afloja** y exigir la firma del senior (R9.4).
- **RP4.2** El techo duro (R3.7, R8.3) aplica a `monto_a_pagar` y también a la suma de pagos de una misma factura.
- **RP4.3** Ninguna aprobación humana podrá cambiar `tipo_pago`, `monto_a_pagar` ni el beneficiario de la ficha (amplía R8.5).
- **RP4.4** EL MOTOR DE REGLAS DEBERÁ mostrar en cada revisión de esta spec el valor observado y el umbral, igual que las demás (R10.1).

### RP5. Calidad
- **RP5.1** Cada criterio DEBERÁ tener al menos una prueba automática.
- **RP5.2** PARA cualquier ficha `PARCIAL` o `ANTICIPO` generada al azar, la decisión NO DEBERÁ ser `PAGAR` mientras RP2.3 no esté construido (prueba de propiedades).
- **RP5.3** PARA cualquier secuencia de parciales de una misma factura, la suma pagada o aprobada NO DEBERÁ superar el monto de la factura.

## Cambios a la spec del motor de reglas

Según la regla «un cambio de plan se escribe primero en la spec»:

| Criterio del motor | Cambio |
|---|---|
| R3.1 | La huella deja de usar el monto y usa el número de pago (RP2.2). |
| R6.1, R6.3, R6.4 | La obligación admite estado «parcial» (RP2.5). |
| R8.5 | También protege `tipo_pago` y `monto_a_pagar` (RP4.3). |

## Datos de demostración (supuesto)

| Parámetro | Valor | Uso |
|---|---|---|
| `anticipo_max_beneficiario` | 20.000.000 | Suma máxima de anticipos abiertos por beneficiario |

## Decisiones abiertas

| # | Pregunta | Propuesta por defecto |
|---|---|---|
| DP1 | ¿Un parcial con plan de cuotas puede ser autopago? | Sí, si coincide con la cuota y está bajo `autopago_max` (RP2.3). No se construye para la entrega. |
| DP2 | ¿Un anticipo cuenta ya como gasto del periodo? | Sí, cuenta cuando sale (RP3.5). |
| DP3 | ¿Quién registra los planes de cuotas y las órdenes de compra? | Una persona de finanzas, como dato de la empresa. La IA no los crea ni los edita. |
